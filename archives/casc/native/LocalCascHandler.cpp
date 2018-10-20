

#include "LocalCascHandler.h"
#include "TokenConfig.h"
#include "String.h"
#include "BlteHandler.h"
#include "Jenkins96.h"

#include <sstream>
#include <fstream>
#include <algorithm>

#ifdef _WIN32
#include <windows.h>
#else
#include <dirent.h>
#endif

LocalCascHandler::LocalCascHandler() : mBuildId(-1) {

}

LocalCascHandler::~LocalCascHandler() {
    for(std::map<uint32_t, DataStream*>::iterator itr = mDataStreams.begin(); itr != mDataStreams.end(); ++itr) {
        delete itr->second;
    }

    mDataStreams.clear();
}

void LocalCascHandler::initialize(const std::string& path) {
    mRootPath = path;

    TokenConfig buildConfig;
    buildConfig.parse(tryFindBuildInfo());
    std::pair<std::string, int> activeBuild = selectBuild(buildConfig);
    if(activeBuild.first.empty()) {
        throw std::runtime_error("No active build found");
    }

    const std::string buildKey = activeBuild.first;
    mBuildId = activeBuild.second;

    loadBuildConfig(buildKey);
    loadIndexFiles();
    parseIndexFiles();
    parseEncodingFile();
    parseRootFile();
}

BinaryReader LocalCascHandler::tryFindBuildInfo() {
    std::stringstream stream;
    stream << mRootPath;
#ifdef _WIN32
    stream << "\\";
#else
    stream << "/";
#endif
    stream << ".build.info";
    return openFileInMemory(stream.str());
}

BinaryReader LocalCascHandler::openFileInMemory(const std::string &path) {
    std::ifstream inStream(path.c_str(), std::ios::binary);
    if(!inStream.is_open()) {
        throw std::runtime_error("File not found");
    }

    inStream.seekg(0, std::ios::end);
    const std::size_t size = static_cast<std::size_t>(inStream.tellg());
    inStream.seekg(0, std::ios::beg);
    std::vector<uint8_t> fileData(size);
    if(!inStream.read(reinterpret_cast<char*>(fileData.data()), fileData.size())) {
        throw std::runtime_error("Unable to read from file");
    }

    inStream.close();
    return BinaryReader(fileData);
}

std::pair<std::string, int> LocalCascHandler::selectBuild(const TokenConfig &buildConfig) {
    for(uint32_t i = 0; i < buildConfig.size(); ++i) {
        std::map<std::string, std::string> build = buildConfig[i];
        std::string version = build["Version"];
        bool active = std::atoi(build["Active"].c_str()) != 0;
        int32_t buildId = -1;
        std::vector<std::string> parts = String::split(build["Version"], '.');
        if(parts.size() == 4) {
            buildId = std::atoi(parts[3].c_str());
        }

        std::string buildKey = build["Build Key"];
        if(active) {
            return std::make_pair(buildKey, buildId);
        }
    }

    return std::pair<std::string, int>();
}

void LocalCascHandler::loadBuildConfig(const std::string &buildKey) {
    std::stringstream stream;
    stream << mRootPath << "/data/config/" << buildKey.substr(0, 2) << "/" << buildKey.substr(2, 2) << "/" << buildKey;
    mBuildConfig.parse(openFileInMemory(stream.str()));
}

void LocalCascHandler::loadIndexFiles() {
    std::vector<std::string> indexLists[16];
    std::stringstream stream;
    stream << mRootPath << "/data/data";
    std::vector<DirectoryEntry> files = listFiles(stream.str());
    for(std::vector<DirectoryEntry>::iterator itr = files.begin(); itr != files.end(); ++itr) {
        const DirectoryEntry& entry = *itr;
        if(entry.extension.empty() || entry.extension != ".idx") {
            continue;
        }

        const int prefix = std::strtol(entry.fileName.substr(0, 2).c_str(), NULL, 16);
        if(prefix >= 0x10 || prefix < 0) {
            continue;
        }

        indexLists[prefix].push_back(entry.fileName);
    }

    for(uint32_t i = 0; i < 16; ++i) {
        std::sort(indexLists[i].begin(), indexLists[i].end());
        mIndexFiles.push_back(*indexLists[i].rbegin());
    }
}

std::vector<DirectoryEntry> LocalCascHandler::listFiles(const std::string &directory) {
    std::vector<std::string> files;
#ifdef _WIN32
    const char separator = '\\';
    std::stringstream pattern;
    pattern << directory << "\\*.*";
    WIN32_FIND_DATA findData;
    ZeroMemory(&findData, sizeof findData);
    HANDLE hFindFile = FindFirstFile(pattern.str().c_str(), &findData);
    BOOL result;
    if(hFindFile != INVALID_HANDLE_VALUE) {
        do {
            if((findData.dwFileAttributes & FILE_ATTRIBUTE_NORMAL) != 0) {
                files.push_back(findData.cFileName);
            }
            result = FindNextFile(hFindFile, &findData);
        } while(result != FALSE);
    }
    FindClose(hFindFile);
#else
    const char separator = '/';
    DIR* dir = opendir(directory.c_str());
    while(dir != NULL) {
        struct dirent* dp = readdir(dir);
        if(dp != NULL) {
            if(dp->d_type == DT_REG) {
                files.push_back(dp->d_name);
            }
        } else {
            break;
        }
    }

    closedir(dir);
#endif

    std::vector<DirectoryEntry> ret;
    for(std::vector<std::string>::iterator itr = files.begin(); itr != files.end(); ++itr) {
        std::string file = *itr;
        std::string::size_type index = file.rfind('.');
        DirectoryEntry entry;
        if(index != std::string::npos) {
            entry.extension = String::toLower(file.substr(index));
        }

        index = file.rfind(separator);
        if(index != std::string::npos) {
            entry.fileName = file.substr(index + 1);
        } else {
            entry.fileName = file;
        }

        ret.push_back(entry);
    }

    return ret;
}

void LocalCascHandler::parseIndexFiles() {
    for(uint32_t i = 0; i < mIndexFiles.size(); ++i) {
        const std::string& indexFile = mIndexFiles[i];
        std::stringstream stream;
        stream << mRootPath << "/data/data/" << indexFile;
        BinaryReader reader = openFileInMemory(stream.str());
        const uint32_t len = reader.read<uint32_t>();
        reader.seek((8 + len + 0x0F) & 0xFFFFFFF0);
        const uint32_t dataLen = reader.read<uint32_t>();
        reader.seekMod(4);

        const uint32_t numBlocks = dataLen / 18;
        for(uint32_t i = 0; i < numBlocks; ++i) {
            FileKeyMd5 key;
            reader.read(&key, 9);
            const uint32_t indexHigh = reader.read<uint8_t>();
            const uint32_t indexLow = reader.readIntBE();

            const uint32_t size = reader.read<uint32_t>();
            const uint32_t index = (indexHigh << 2) | ((indexLow & 0xC0000000) >> 30);
            const uint32_t offset = (indexLow & 0x3FFFFFFF);
            if(mIndexEntries.find(key) != mIndexEntries.end()) {
                continue;
            }

            mIndexEntries.insert(std::make_pair(key, IndexEntry(index, offset, size)));

            if(mDataStreams.find(index) == mDataStreams.end()) {
                mDataStreams.insert(std::make_pair(index, new DataStream(mRootPath, index)));
            }
        }
    }
}

void LocalCascHandler::parseEncodingFile() {
    const std::vector<std::string> encodingKeys = mBuildConfig["encoding"];
    if(encodingKeys.size() != 2) {
        throw std::runtime_error("Invalid build config. Did not get 2 entries for 'encoding' key");
    }

    FileKeyMd5 encodingKey;
    unhex(encodingKeys[1], &encodingKey, sizeof encodingKey);
    BinaryReader blteEncoding = openFile(getIndexEntry(encodingKey));
    BinaryReader encodingData = BinaryReader(BlteHandler(blteEncoding).getDecompressedData());
    EncodingFileParser(mEncodingEntries).parse(encodingData);
}

void LocalCascHandler::unhex(const std::string &hexData, void *buffer, std::size_t maxBuffer) {
    uint32_t maxEntry = std::min<uint32_t>(static_cast<const uint32_t &>(maxBuffer),
                                           static_cast<const uint32_t &>(hexData.size() / 2));

    uint8_t* ptr = reinterpret_cast<uint8_t*>(buffer);

    for(uint32_t i = 0; i < maxEntry; ++i) {
        ptr[i] = static_cast<uint8_t>(std::strtol(hexData.substr(i * 2, 2).c_str(), NULL, 16));
    }
}

IndexEntry LocalCascHandler::getIndexEntry(const FileKeyMd5 &key) const {
    FileKeyMd5 shortKey;
    memcpy(&shortKey, &key, 9);
    return mIndexEntries.at(shortKey);
}

BinaryReader LocalCascHandler::openFile(const IndexEntry &indexEntry) const {
    std::map<uint32_t, DataStream*>::const_iterator itr = mDataStreams.find(indexEntry.index);
    if(itr == mDataStreams.end()) {
        throw std::runtime_error("No data stream for index entry found");
    }

    return itr->second->read(indexEntry.offset + 30, indexEntry.size - 30);
}

void LocalCascHandler::parseRootFile() {
    std::vector<std::string> rootKeys = mBuildConfig["root"];
    if(rootKeys.empty()) {
        throw std::runtime_error("Invalid build config, not root key found");
    }

    FileKeyMd5 key;
    unhex(rootKeys[0], &key, sizeof key);
    std::map<FileKeyMd5, EncodingEntry, FileKeyMd5::Less>::iterator itr = mEncodingEntries.find(key);
    if(itr == mEncodingEntries.end()) {
        throw std::runtime_error("No encoding entry for root file found");
    }

    BinaryReader blteEncoding = openFile(getIndexEntry(itr->second.key));
    BinaryReader rootData = BinaryReader(BlteHandler(blteEncoding).getDecompressedData());
    RootFileParser(mRootData, mFileDataMap).parse(rootData, LocaleFlags::ALL);
}

bool LocalCascHandler::tryGetIndexEntry(const FileKeyMd5 &key, IndexEntry &indexEntry) {
    FileKeyMd5 shortKey;
    memcpy(&shortKey, &key, 9);
    std::map<FileKeyMd5, IndexEntry, FileKeyMd5::Less>::iterator itr = mIndexEntries.find(shortKey);
    if(itr == mIndexEntries.end()) {
        return false;
    }

    indexEntry = itr->second;
    return true;
}

bool LocalCascHandler::fileExists(const std::string &name) {
    typedef std::multimap<uint64_t, FileKeyMd5>::iterator tRootIterator;

    std::string upperName = String::toUpper(name);
    upperName = String::replaceAll(upperName, '/', '\\');
    const uint64_t hash = Jenkins96().computeHash(upperName);
    std::pair<tRootIterator, tRootIterator> rootEntries = mRootData.equal_range(hash);
    if(std::distance(rootEntries.first, rootEntries.second) <= 0) {
        return false;
    }

    for(tRootIterator rootItr = rootEntries.first; rootItr != rootEntries.second; ++rootItr) {
        std::map<FileKeyMd5, EncodingEntry>::iterator encodingItr = mEncodingEntries.find(rootItr->second);
        if(encodingItr == mEncodingEntries.end()) {
            continue;
        }

        IndexEntry indexEntry;
        if(!tryGetIndexEntry(encodingItr->second.key, indexEntry)) {
            continue;
        }

        return true;
    }

    return false;
}

void* LocalCascHandler::openFile(const std::string &name, int& fileSize) {
    typedef std::multimap<uint64_t, FileKeyMd5>::iterator tRootIterator;

    std::string upperName = String::toUpper(name);
    upperName = String::replaceAll(upperName, '/', '\\');
    const uint64_t hash = Jenkins96().computeHash(upperName);
    std::pair<tRootIterator, tRootIterator> rootEntries = mRootData.equal_range(hash);
    if(std::distance(rootEntries.first, rootEntries.second) <= 0) {
        throw std::runtime_error("File not found");
    }

    for(tRootIterator rootItr = rootEntries.first; rootItr != rootEntries.second; ++rootItr) {
        std::map<FileKeyMd5, EncodingEntry>::iterator encodingItr = mEncodingEntries.find(rootItr->second);
        if(encodingItr == mEncodingEntries.end()) {
            continue;
        }

        IndexEntry indexEntry;
        if(!tryGetIndexEntry(encodingItr->second.key, indexEntry)) {
            continue;
        }

        BinaryReader blteReader = openFile(indexEntry);
        return toPointer(BinaryReader(BlteHandler(blteReader).getDecompressedData()), fileSize);
    }

    throw std::runtime_error("File not found");
}

void* LocalCascHandler::openFileByFileId(uint32_t fileDataId, int& fileSize) {
    typedef std::multimap<uint32_t, FileKeyMd5>::iterator tRootIterator;
    std::pair<tRootIterator, tRootIterator> rootEntries = mFileDataMap.equal_range(fileDataId);
    if(std::distance(rootEntries.first, rootEntries.second) <= 0) {
        throw std::runtime_error("File not found");
    }

    for(tRootIterator rootItr = rootEntries.first; rootItr != rootEntries.second; ++rootItr) {
        std::map<FileKeyMd5, EncodingEntry>::iterator encodingItr = mEncodingEntries.find(rootItr->second);
        if(encodingItr == mEncodingEntries.end()) {
            continue;
        }

        IndexEntry indexEntry;
        if(!tryGetIndexEntry(encodingItr->second.key, indexEntry)) {
            continue;
        }

        BinaryReader blteReader = openFile(indexEntry);
        return toPointer(BinaryReader(BlteHandler(blteReader).getDecompressedData()), fileSize);
    }

    throw std::runtime_error("File not found");
}

void *LocalCascHandler::toPointer(const BinaryReader &reader, int& size) {
    void* memory = malloc(reader.getData().size());
    memcpy(memory, reader.getData().data(), reader.getData().size());
    size = static_cast<int>(reader.getData().size());
    return memory;
}

bool LocalCascHandler::fileDataIdExists(uint32_t fileDataId) {
    typedef std::multimap<uint32_t, FileKeyMd5>::iterator tRootIterator;
    std::pair<tRootIterator, tRootIterator> rootEntries = mFileDataMap.equal_range(fileDataId);
    if(std::distance(rootEntries.first, rootEntries.second) <= 0) {
        return false;
    }

    for(tRootIterator rootItr = rootEntries.first; rootItr != rootEntries.second; ++rootItr) {
        std::map<FileKeyMd5, EncodingEntry>::iterator encodingItr = mEncodingEntries.find(rootItr->second);
        if(encodingItr == mEncodingEntries.end()) {
            continue;
        }

        IndexEntry indexEntry;
        if(!tryGetIndexEntry(encodingItr->second.key, indexEntry)) {
            continue;
        }

        return true;
    }

    return false;
}
