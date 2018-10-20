

#ifndef CYTHON_CASC_LOCALCASCHANDLER_H
#define CYTHON_CASC_LOCALCASCHANDLER_H

#include <string>
#include <cstring>
#include <stdint.h>

#include "EncodingFileParser.h"
#include "RootFileParser.h"
#include "KeyValueConfig.h"
#include "DataStream.h"

class TokenConfig;

struct DirectoryEntry {
    std::string fileName;
    std::string extension;
};

class LocalCascHandler {
public:
    typedef void (*tTextCallback)(const char*);
private:

    std::vector<std::string> mIndexFiles;
    std::map<FileKeyMd5, IndexEntry, FileKeyMd5::Less> mIndexEntries;
    std::map<FileKeyMd5, EncodingEntry, FileKeyMd5::Less> mEncodingEntries;
    std::multimap<uint64_t, FileKeyMd5> mRootData;
    std::multimap<uint32_t, FileKeyMd5> mFileDataMap;

    std::map<uint32_t, DataStream*> mDataStreams;

    std::string mRootPath;
    int mBuildId;

    KeyValueConfig mBuildConfig;

    BinaryReader openFileInMemory(const std::string& path);

    BinaryReader tryFindBuildInfo();

    std::pair<std::string, int> selectBuild(const TokenConfig& buildConfig);
    void loadBuildConfig(const std::string& buildKey);
    void loadIndexFiles();
    void parseIndexFiles();
    void parseEncodingFile();
    void parseRootFile();

    std::vector<DirectoryEntry> listFiles(const std::string& directory);

    void unhex(const std::string& hexData, void* buffer, std::size_t maxBuffer);

    IndexEntry getIndexEntry(const FileKeyMd5& key) const;
    bool tryGetIndexEntry(const FileKeyMd5& key, IndexEntry& indexEntry);

    BinaryReader openFile(const IndexEntry& indexEntry) const;

    void* toPointer(const BinaryReader& reader, int& size);

public:
    explicit LocalCascHandler();
    ~LocalCascHandler();

    void initialize(const std::string& path);

    bool fileExists(const std::string &name);
    bool fileDataIdExists(uint32_t fileDataId);

    void* openFile(const std::string& name, int& fileSize);
    void* openFileByFileId(uint32_t fileDataId, int& fileSize);
};


#endif //CYTHON_CASC_LOCALCASCHANDLER_H
