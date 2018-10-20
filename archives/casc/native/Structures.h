

#ifndef CYTHON_CASC_STRUCTURES_H
#define CYTHON_CASC_STRUCTURES_H

#include <cstdlib>
#include <stdint.h>
#include <cstring>

#pragma pack(push, 1)

class FileKeyMd5 {
    friend struct Less;
public:
    struct Less {
        bool operator ()(const FileKeyMd5& value, const FileKeyMd5& other) const {
            const std::size_t* vals = reinterpret_cast<const std::size_t*>(value.mKey);
            const std::size_t* otherVals = reinterpret_cast<const std::size_t*>(other.mKey);

            for (std::size_t i = sizeof(FileKeyMd5) / sizeof(std::size_t); i > 0; --i) {
                if(vals[i - 1] > otherVals[i - 1]) {
                    return false;
                } else if(vals[i - 1] < otherVals[i - 1]) {
                    return true;
                }
            }

            // equal is not less
            return false;
        }
    };

private:
    static const FileKeyMd5 ZERO_KEY;
    uint8_t mKey[16];

public:
    FileKeyMd5() {
        memset(mKey, 0, sizeof mKey);
    };
    explicit FileKeyMd5(const uint8_t* data) { memcpy(mKey, data, sizeof mKey); }

    bool operator <(const FileKeyMd5& other) const {
        return memcmp(mKey, other.mKey, sizeof mKey) < 0;
    }

    bool operator ==(const FileKeyMd5& other) const {
        return memcmp(mKey, other.mKey, sizeof mKey) == 0;
    }

    bool isNotZero() const {
        return memcmp(mKey, ZERO_KEY.mKey, sizeof mKey) != 0;
    }

    uint8_t* begin() { return mKey; }
    uint8_t* end() { return mKey + sizeof mKey; }

    const uint8_t* cbegin() const { return mKey; }
    const uint8_t* cend() const { return mKey + sizeof mKey; }
};

struct EncodingEntry {
    uint32_t size;
    FileKeyMd5 key;

    EncodingEntry() : size(0) { }
    EncodingEntry(uint32_t size, const FileKeyMd5& key) : size(size), key(key) {}
};

struct IndexEntry {
    uint32_t index;
    uint32_t offset;
    uint32_t size;

    IndexEntry() : index(0), offset(0), size(0) {}
    IndexEntry(const uint32_t index, const uint32_t offset, const uint32_t size) : index(index), offset(offset), size(size) {

    }
};

struct LocaleFlags {
    enum Values {
        ALL = 0xFFFFFFFF,
        NONE = 0,

        EN_US = 0x00000002,
        KO_KR = 0x00000004,
        FR_FR = 0x00000010,
        DE_DE = 0x00000020,
        ZH_CN = 0x00000040,
        ES_ES = 0x00000080,
        ZH_TW = 0x00000100,
        EN_GB = 0x00000200,
        EN_CN = 0x00000400,
        EN_TW = 0x00000800,
        ES_MX = 0x00001000,
        RU_RU = 0x00002000,
        PT_BR = 0x00004000,
        IT_IT = 0x00008000,
        PT_PT = 0x00010000,
        EN_SG = 0x20000000,
        PL_PL = 0x40000000
    };
};

struct RootElement {
    FileKeyMd5 key;
    uint64_t hash;
};

#pragma pack(pop)

#endif //CYTHON_CASC_STRUCTURES_H
