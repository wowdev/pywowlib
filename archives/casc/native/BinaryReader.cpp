
#include "BinaryReader.h"
#include <cstring>

BinaryReader::BinaryReader(const std::vector<uint8_t> &data) : mData(data), mPosition(0) {

}

void BinaryReader::read(void *buffer, std::size_t numBytes) {
    if(mPosition + numBytes > mData.size() || mPosition < 0) {
        throw std::runtime_error("Attempted to read past the end or from behind the beginning of the stream");
    }

    memcpy(buffer, &mData[mPosition], numBytes);
    mPosition += numBytes;
}
