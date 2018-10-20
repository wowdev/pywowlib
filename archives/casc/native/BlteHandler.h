

#ifndef CYTHON_CASC_BLTEHANDLER_H
#define CYTHON_CASC_BLTEHANDLER_H

#include <stdint.h>
#include <vector>

#include "BinaryReader.h"

class BlteHandler {
    static const unsigned int MAGIC = 0x45544C42;

    std::vector<uint8_t> mDecompressedData;

    void handleCompressedBlock(uint32_t frameHeaderSize, uint64_t decompressedSize, std::vector<uint8_t>& compressedData);
    void handleBlock(uint32_t frameHeaderSize, uint32_t decompressedSize, uint32_t compressedSize, BinaryReader& reader);
    void parse(BinaryReader& reader);

    inline uint32_t swap(const uint32_t& value) {
        const uint32_t b0 = value & 0xFF;
        const uint32_t b1 = (value >> 8) & 0xFF;
        const uint32_t b2 = (value >> 16) & 0xFF;
        const uint32_t b3 = (value >> 24) & 0xFF;
        return b3 | (b2 << 8u) | (b1 << 16u) | (b0 << 24u);
    }

public:
    explicit BlteHandler(BinaryReader& reader);

    const std::vector<uint8_t>& getDecompressedData() const { return mDecompressedData; }
};


#endif //CYTHON_CASC_BLTEHANDLER_H
