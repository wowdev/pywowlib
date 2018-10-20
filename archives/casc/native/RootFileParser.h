

#ifndef CYTHON_CASC_ROOTFILEPARSER_H
#define CYTHON_CASC_ROOTFILEPARSER_H

#include <map>
#include <stdint.h>

#include "Structures.h"
#include "BinaryReader.h"

class RootFileParser {
    std::multimap<uint64_t, FileKeyMd5>& mRootDataMap;
    std::multimap<uint32_t, FileKeyMd5>& mFileDataIds;

public:
    explicit RootFileParser(std::multimap<uint64_t, FileKeyMd5>& rootDataMap,
            std::multimap<uint32_t, FileKeyMd5>& fileDataIdMap);

    void parse(BinaryReader& reader, const LocaleFlags::Values& localeFlags);
};


#endif //CYTHON_CASC_ROOTFILEPARSER_H
