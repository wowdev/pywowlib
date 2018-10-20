

#include "RootFileParser.h"

RootFileParser::RootFileParser(std::multimap<uint64_t, FileKeyMd5> &rootDataMap,
                               std::multimap<uint32_t, FileKeyMd5> &fileDataIdMap) :
        mRootDataMap(rootDataMap),
        mFileDataIds(fileDataIdMap) {

}

void RootFileParser::parse(BinaryReader &reader, const LocaleFlags::Values& localeFlags) {
    while(reader.hasAvailable()) {
        uint32_t count = reader.read<uint32_t>();
        reader.seekMod(4); // content flags
        LocaleFlags::Values locales = static_cast<LocaleFlags::Values>(reader.read<uint32_t>());
        if((locales & localeFlags) == 0) {
            reader.seekMod(count * 28);
            continue;
        }

        std::vector<uint32_t> fileDataIdValues(count);
        for(uint32_t i = 0; i < count; ++i) {
            uint32_t value = reader.read<uint32_t>();
            if(i == 0) {
                fileDataIdValues[i] = value;
            } else {
                fileDataIdValues[i] = fileDataIdValues[i - 1] + 1 + value;
            }
        }

        std::vector<RootElement> rootElements(count);
        reader.read(rootElements);
        for(uint32_t i = 0; i < count; ++i) {
            const RootElement& element = rootElements[i];
            mRootDataMap.insert(std::make_pair(element.hash, element.key));
            mFileDataIds.insert(std::make_pair(fileDataIdValues[i], element.key));
        }
    }

}
