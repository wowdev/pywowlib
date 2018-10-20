

#include "EncodingFileParser.h"

EncodingFileParser::EncodingFileParser(tEncodingMap &encodingMap) :
        mEncodingEntries(encodingMap) {

}

void EncodingFileParser::parse(BinaryReader& reader) {
    reader.seek(9);
    const uint32_t numEntriesA = reader.readIntBE();
    reader.seekMod(5);
    const uint32_t stringBlock = reader.readIntBE();
    reader.seekMod(stringBlock + numEntriesA * 32);

    std::size_t curPos = reader.tell();

    for(uint32_t i = 0u; i < numEntriesA; ++i) {
        uint16_t keyCount = reader.read<uint16_t>();
        while(keyCount != 0) {
            const uint32_t fileSize = reader.readIntBE();
            FileKeyMd5 md5 = reader.read<FileKeyMd5>();
            FileKeyMd5 key = reader.read<FileKeyMd5>();
            mEncodingEntries.insert(std::make_pair(md5, EncodingEntry(fileSize, key)));
            if(keyCount > 0) {
                reader.seekMod((keyCount - 1) * 16);
            }

            keyCount = reader.read<uint16_t>();
        }

        curPos += 0x1000;
        reader.seek(curPos);
    }
}
