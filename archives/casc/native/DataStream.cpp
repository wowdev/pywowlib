
#include <sstream>
#include <iomanip>
#include <cstring>
#include "DataStream.h"

#ifndef _WIN32
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/mman.h>
#endif

DataStream::DataStream(const std::string &path, uint32_t index) :
#ifdef _WIN32
    mFileMapping(NULL), mFileHandle(NULL)
#else
    mFd(-1)
#endif
{
    std::stringstream stream;
    stream << path << "/data/data/data." << std::setw(3) << std::setfill('0') << index;

#ifdef _WIN32
    mFileHandle = CreateFile(stream.str().c_str(), GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, NULL,
                             OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);

    if(mFileHandle == NULL) {
        throw std::runtime_error("Error opening file for data stream");
    }

    mFileMapping = CreateFileMapping(mFileHandle, NULL, PAGE_READONLY, 0, 0, NULL);
    if(mFileMapping == NULL) {
        CloseHandle(mFileHandle);
        mFileHandle = NULL;
        throw std::runtime_error("Error creating file mapping for data stream");
    }

    SYSTEM_INFO systemInfo;
    GetSystemInfo(&systemInfo);
    mOffsetMask = systemInfo.dwAllocationGranularity - 1;
    mAllocationMask = ~mOffsetMask;
#else
    mFd = open(stream.str().c_str(), O_RDONLY);
    if(mFd < 0) {
        throw std::runtime_error("Error opening file for data stream");
    }

    mOffsetMask = static_cast<uint32_t>(getpagesize()) - 1;
    mAllocationMask = ~mOffsetMask;
#endif
}

DataStream::~DataStream() {
#ifdef _WIN32
    if(mFileMapping != NULL) {
        CloseHandle(mFileMapping);
    }

    if(mFileHandle != NULL) {
        CloseHandle(mFileHandle);
    }
#else
    if(mFd >= 0) {
        close(mFd);
    }
#endif
}

BinaryReader DataStream::read(uint32_t offset, uint32_t size) {
    std::vector<uint8_t> fileData(size);

    const uint32_t actualAddress = offset & mAllocationMask;
    const uint32_t allocationOffset = offset & mOffsetMask;
    size += allocationOffset;

#ifdef _WIN32
    uint8_t* address = reinterpret_cast<uint8_t*>(MapViewOfFile(mFileMapping, FILE_MAP_READ, 0, actualAddress, size));
#else
    uint8_t* address = reinterpret_cast<uint8_t*>(mmap(NULL, size, PROT_READ, MAP_PRIVATE, mFd, actualAddress));
#endif

    if(address == NULL) {
        throw std::runtime_error("Error mapping view of file");
    }

    memcpy(fileData.data(), address + allocationOffset, fileData.size());

#ifdef _WIN32
    UnmapViewOfFile(address);
#else
    munmap(address, size);
#endif

    return BinaryReader(fileData);
}
