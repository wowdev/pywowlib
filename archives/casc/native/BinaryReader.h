

#ifndef CYTHON_CASC_BINARYREADER_H
#define CYTHON_CASC_BINARYREADER_H

#include <vector>
#include <stdint.h>
#include <stdexcept>

class BinaryReader {
    std::vector<uint8_t> mData;
    std::size_t mPosition;

public:
    explicit BinaryReader(const std::vector<uint8_t>& data);

    const std::vector<uint8_t>& getData() const {
        return mData;
    }

    void seek(const std::size_t position) {
        mPosition = position;
    }

    void seekMod(const int32_t mod) {
        mPosition += mod;
        if(mPosition < 0) {
            throw std::runtime_error("Attempted to seek behind the stream");
        }
    }

    const std::size_t tell() const {
        return mPosition;
    }

    bool hasAvailable() const {
        return mPosition < mData.size();
    }

    void read(void* buffer, std::size_t numBytes);

    template<typename T>
    void read(T& value) {
        read(&value, sizeof(T));
    }

    template<typename T>
    T read() {
        T ret;
        read(&ret, sizeof(T));
        return ret;
    }

    template<typename T>
    void read(std::vector<T>& buffer) {
        read(buffer.data(), buffer.size() * sizeof(T));
    }

    uint32_t readIntBE() {
        const uint32_t valueLE = read<uint32_t>();
        const uint32_t b0 = valueLE & 0xFF;
        const uint32_t b1 = (valueLE >> 8) & 0xFF;
        const uint32_t b2 = (valueLE >> 16) & 0xFF;
        const uint32_t b3 = (valueLE >> 24) & 0xFF;
        return b3 | (b2 << 8) | (b1 << 16) | (b0 << 24);
    }
};


#endif //CYTHON_CASC_BINARYREADER_H
