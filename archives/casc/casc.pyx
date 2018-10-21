from libcpp cimport bool
from libc.stdlib cimport free
from typing import Any

cdef extern from "native/LocalCascHandler.h":
    cdef cppclass LocalCascHandler:
        LocalCascHandler() except +
        void initialize(const char* dataPath) except +
        void initializeWithBuildKey(const char* dataPath, const char* buildKey) except +
        void initializeWithBuildInfo(const char* dataPath, const char* buildInfo) except +
        void initializeWithBuildInfoPath(const char* dataPath, const char* buildInfoPath) except +
        bool fileExists(const char* fileName)
        bool fileDataIdExists(int fileDataId)
        void* openFile(const char* fileName, int& fileSize) except +
        void* openFileByFileId(int fileDataId, int& fileSize) except +

cdef class CascHandlerLocal:
    cdef LocalCascHandler c_casc;

    def __cinit__(self):
        self.c_casc = LocalCascHandler()

    def initialize(self, path: str):
        self.c_casc.initialize(path.encode('utf-8'))

    def initialize_with_build_key(self, path: str, build_key: str):
        self.c_casc.initializeWithBuildKey(path.encode('utf-8'), build_key.encode('utf-8'))

    def initialize_with_build_info(self, path: str, build_info: str):
        self.c_casc.initializeWithBuildInfo(path.encode('utf-8'), build_info.encode('utf-8'))

    def initialize_with_build_info_path(self, path: str, build_info_path: str):
        self.c_casc.initializeWithBuildInfoPath(path.encode('utf-8'), build_info_path.encode('utf-8'))

    def exists(self, file: Any):
        if isinstance(file, str):
            return self.c_casc.fileExists(file.encode('utf-8'))
        elif isinstance(file, int):
            return self.c_casc.fileDataIdExists(file)
        else:
            raise ValueError('file must be either string or int')

    def open_file(self, file: Any):
        cdef int file_size
        cdef void* dataPtr
        file_size = 0

        if isinstance(file, str):
            data_ptr = self.c_casc.openFile(file, file_size.encode('utf-8'))
        elif isinstance(file, int):
            data_ptr = self.c_casc.openFileByFileId(file, file_size)
        else:
            raise ValueError("File must be either string or int")

        cdef unsigned char[::1] mview = <unsigned char[:file_size]>(data_ptr)
        ret = memoryview(mview).tobytes()
        free(data_ptr)
        return ret

    def __contains__(self, item: Any):
        return self.exists(item)
