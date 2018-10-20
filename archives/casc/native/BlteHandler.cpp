
#include <cstring>
#include "BlteHandler.h"
#include "zlib/zlib.h"

#pragma pack(push, 1)

struct DataBlock {
    uint32_t compressedSize;
    uint32_t decompressedSize;
    uint8_t hash[16];
};

#pragma pack(pop)

BlteHandler::BlteHandler(BinaryReader &reader) {
    parse(reader);
}

void BlteHandler::handleCompressedBlock(uint32_t frameHeaderSize, uint64_t decompressedSize,
                                        std::vector<uint8_t> &compressedData) {
    z_stream stream;
    memset(&stream, 0, sizeof stream);
    inflateInit(&stream);
    if(frameHeaderSize != 0) {
        std::vector<uint8_t> decompressedData(decompressedSize);

        stream.next_in = compressedData.data() + 1;
        stream.avail_in = static_cast<uInt>(compressedData.size() - 1);
        stream.next_out = decompressedData.data();
        stream.avail_out = static_cast<uInt>(decompressedSize);

        while(stream.avail_in > 0) {
            int result = inflate(&stream, Z_FULL_FLUSH);
            if(result < 0) {
                throw std::runtime_error("error decompressing zStream");
            }

            if(result == Z_STREAM_END) {
                break;
            }
        }

        mDecompressedData.insert(mDecompressedData.end(), decompressedData.begin(), decompressedData.end());
    } else {
        std::vector<uint8_t> chunk(compressedData.size());
        stream.next_in = compressedData.data() + 1;
        stream.avail_in = static_cast<uInt>(compressedData.size() - 1);
        while(stream.avail_in > 0) {
            stream.next_out = chunk.data();
            stream.avail_out = static_cast<uInt>(chunk.size());
            int result = inflate(&stream, Z_FULL_FLUSH);
            if(result < 0) {
                throw std::runtime_error("error decompressing zStream");
            }

            uint32_t numRead = static_cast<uint32_t>(chunk.size() - stream.avail_out);
            mDecompressedData.insert(mDecompressedData.end(), chunk.begin(), chunk.begin() + numRead);
            if(result == Z_STREAM_END) {
                break;
            }
        }
    }

    inflateEnd(&stream);
}

void BlteHandler::handleBlock(uint32_t frameHeaderSize, uint32_t decompressedSize, uint32_t compressedSize,
                              BinaryReader &reader) {
    std::vector<uint8_t> blockData(compressedSize);
    reader.read(blockData);
    const uint8_t indicator = blockData[0];
    switch(indicator) {
        case 0x45:
            throw std::runtime_error("Encrypted files not supported");

        case 0x46:
            throw std::runtime_error("Recursive frames not supported");

        case 0x4E: {
            mDecompressedData.insert(mDecompressedData.end(), blockData.begin() + 1, blockData.end());
            break;
        }

        case 0x5A: {
            handleCompressedBlock(frameHeaderSize, decompressedSize, blockData);
            break;
        }

        default:
            throw std::runtime_error("Unrecognized frame indicator");
    }
}

void BlteHandler::parse(BinaryReader &reader) {
    if(reader.getData().size() < 8) {
        throw std::runtime_error("Cannot parse BLTE stream: Not enough data");
    }

    uint32_t magic = reader.read<uint32_t>();
    if(magic != MAGIC) {
        throw std::runtime_error("Cannot parse BLTE stream: Invalid magic");
    }

    uint32_t headerSize = reader.readIntBE();
    uint32_t blockCount = 1;
    if(headerSize > 0) {
        if(reader.read<uint8_t>() != 0x0F) {
            throw std::runtime_error("Cannot parse BLTE stream: Invalid header");
        }
        blockCount = (reader.read<uint8_t>() << 16) | (reader.read<uint8_t>() << 8) | reader.read<uint8_t>();
        if(blockCount == 0) {
            throw std::runtime_error("Cannot parse BLTE stream: Invalid header");
        }

        uint32_t frameHeaderSize = 24u * blockCount + 12u;
        if(frameHeaderSize != headerSize) {
            throw std::runtime_error("Cannot parse BLTE stream: Invalid header size");
        }
    }

    std::vector<DataBlock> dataBlocks(blockCount);
    if(headerSize != 0) {
        reader.read(dataBlocks);
        for(uint32_t i = 0; i < blockCount; ++i) {
            DataBlock& block = dataBlocks[i];
            block.compressedSize = swap(block.compressedSize);
            block.decompressedSize = swap(block.decompressedSize);
        }
    } else {
        for(uint32_t i = 0; i < blockCount; ++i) {
            DataBlock& block = dataBlocks[i];
            block.compressedSize = static_cast<uint32_t>(reader.getData().size() - 8);
            block.decompressedSize = block.compressedSize - 1;
        }
    }

    for(uint32_t i = 0; i < blockCount; ++i) {
        handleBlock(headerSize, dataBlocks[i].decompressedSize, dataBlocks[i].compressedSize, reader);
    }
}
