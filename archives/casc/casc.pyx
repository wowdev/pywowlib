from libcpp cimport bool
from libc.stdlib cimport free

cdef extern from "native/LocalCascHandler.h":
    cdef cppclass LocalCascHandler:
        LocalCascHandler() except +
        void initialize(const char* dataPath) except +
        bool fileExists(const char* fileName)
        bool fileDataIdExists(int fileDataId)
        void* openFile(const char* fileName, int& fileSize) except +
        void* openFileByFileId(int fileDataId, int& fileSize) except +

cdef class CascHandlerLocal:
    cdef LocalCascHandler c_casc;
    def __cinit__(self):
        self.c_casc = LocalCascHandler()

    def initialize(self, path):
        self.c_casc.initialize(path)

    def exists(self, file):
        if isinstance(file, str):
            return self.c_casc.fileExists(file)
        elif isinstance(file, int):
            return self.c_casc.fileDataIdExists(file)
        else:
            raise ValueError('file must be either string or int')

    def openFile(self, file):
        cdef int fileSize
        cdef void* dataPtr
        fileSize = 0
        if isinstance(file, str):
            dataPtr = self.c_casc.openFile(file, fileSize)
        elif isinstance(file, int):
            dataPtr = self.c_casc.openFileByFileId(file, fileSize)
        else:
            raise ValueError("File must be either string or int")

        cdef unsigned char[::1] mview = <unsigned char[:fileSize]>(dataPtr)
        ret = memoryview(mview).tobytes()
        free(dataPtr)
        return ret
