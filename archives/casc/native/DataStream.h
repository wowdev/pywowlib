

#ifndef CYTHON_CASC_DATASTREAM_H
#define CYTHON_CASC_DATASTREAM_H

#include <stdint.h>
#include <string>
#include "BinaryReader.h"

#ifdef _WIN32
#include <windows.h>
#else
#endif

class DataStream {
    uint32_t mOffsetMask;
    uint32_t mAllocationMask;
#ifdef _WIN32
    HANDLE mFileHandle;
    HANDLE mFileMapping;
#else
    int mFd;
#endif

public:
    explicit DataStream(const std::string& path, uint32_t index);
    ~DataStream();

    BinaryReader read(uint32_t offset, uint32_t size);
};


#endif //CYTHON_CASC_DATASTREAM_H
