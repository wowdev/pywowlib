#ifndef CYTHON_BLP_BLPCONVERT_H
#define CYTHON_BLP_BLPCONVERT_H

#include <string>
#include <stdint.h>
#include <cstdlib>
#include <vector>
#include "ByteStream.h"
#include "BlpStructure.h"
#include <image.hpp>

namespace python_blp {
    namespace _detail {
        struct RgbDataArray {
            RgbDataArray() {
                data.color = 0;
            }

            union data {
                uint32_t color;
                uint8_t buffer[4];
            } data;
        };
    }

    enum Format {
        RGB,
        RGB_PALETTE,
        DXT1,
        DXT2,
        DXT3,
        UNKNOWN
    };

    struct Image
    {
        std::vector<std::uint32_t> buffer;
        std::size_t width;
        std::size_t height;
    };

    class BlpConvert
    {
        typedef void (BlpConvert::*tConvertFunction)(ByteStream&, std::vector<uint32_t>&, const std::size_t&) const;

    public:
        Image get_raw_pixels(unsigned char* inputFile, std::size_t fileSize) const;

    private:

        void loadFirstLayer(const BlpHeader &header, ByteStream &data, Image &image) const;

        Format getFormat(const BlpHeader &header) const;

        void parseUncompressed(ByteStream &data, Image &image) const;

        void parseUncompressedPalette(const uint8_t &alphaDepth, ByteStream &data, std::size_t size,
                                      Image &image) const;

        void parseCompressed(const Format &format, ByteStream &data, Image &image) const;

        void decompressPaletteFastPath(const uint32_t* palette, const std::vector<uint8_t> &indices,
                                       Image &image) const;

        void decompressPaletteARGB8(const uint8_t &alphaDepth, uint32_t *const palette, const std::vector<uint8_t> &indices,
                                    Image &image) const;

        void dxt1GetBlock(ByteStream& stream, std::vector<uint32_t>& blockData, const size_t& blockOffset) const;
        void dxt2GetBlock(ByteStream& stream, std::vector<uint32_t>& blockData, const size_t& blockOffset) const;
        void dxt3GetBlock(ByteStream& stream, std::vector<uint32_t>& blockData, const size_t& blockOffset) const;

        void readDXTColors(ByteStream& stream, _detail::RgbDataArray* colors, bool preMultipliedAlpha, bool use4Colors = false) const;

        tConvertFunction getDxtConvertFunction(const Format& format) const;

    };
}

#endif //CYTHON_BLP_BLPCONVERT_H
