

#ifndef CYTHON_CASC_INDEXPARSER_H
#define CYTHON_CASC_INDEXPARSER_H

#include "BinaryReader.h"
#include <map>
#include "Structures.h"

class EncodingFileParser {
    typedef std::map<FileKeyMd5, EncodingEntry, FileKeyMd5::Less> tEncodingMap;

    tEncodingMap& mEncodingEntries;

public:
    explicit EncodingFileParser(tEncodingMap& encodingMap);

    void parse(BinaryReader& reader);
};


#endif //CYTHON_CASC_INDEXPARSER_H
