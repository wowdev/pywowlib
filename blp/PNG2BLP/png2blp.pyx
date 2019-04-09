from libcpp cimport bool
from libc.stdlib cimport free

cdef extern from "native/Png2Blp.h":
    cdef cppclass Png2Blp:
        Png2Blp()
        void load(const char* pngData, unsigned int fileSize) except +
        void* createBlpPalettedInMemory(bool generateMipMaps, int alphaDepth, int minQuality, int maxQuality, int& fileSize)
        void* createBlpUncompressedInMemory(bool generateMipMaps, int& fileSize)
        void* createBlpDxtInMemory(bool generateMipMaps, int dxtFormat, int& fileSize)

cdef class BlpFromPng:
    cdef Png2Blp c_converter;

    def __cinit__(self, png_data, png_size):
        self.c_converter = Png2Blp()
        self.c_converter.load(png_data, png_size)

    def create_blp_paletted_in_memory(self, mip_maps, alpha_depth, min_quality, max_quality):
        cdef void* dataPtr
        cdef unsigned int fileSize
        fileSize = 0
        dataPtr = self.c_converter.createBlpPalettedInMemory(mip_maps, alpha_depth, min_quality, max_quality, fileSize)
        cdef unsigned char[::1] mview = <unsigned char[:fileSize]>(dataPtr)
        ret = memoryview(mview).tobytes()
        free(dataPtr)
        return ret

    def create_blp_uncompressed_in_memory(self, mip_maps):
        cdef void* dataPtr
        cdef unsigned int fileSize
        fileSize = 0
        dataPtr = self.c_converter.createBlpUncompressedInMemory(mip_maps, fileSize)
        cdef unsigned char[::1] mview = <unsigned char[:fileSize]>(dataPtr)
        ret = memoryview(mview).tobytes()
        free(dataPtr)
        return ret

    def create_blp_paletted_in_memory(self, mip_maps, dxtFormat):
        cdef void* dataPtr
        cdef unsigned int fileSize
        fileSize = 0
        dataPtr = self.c_converter.createBlpDxtInMemory(mip_maps, dxtFormat, fileSize)
        cdef unsigned char[::1] mview = <unsigned char[:fileSize]>(dataPtr)
        ret = memoryview(mview).tobytes()
        free(dataPtr)
        return ret