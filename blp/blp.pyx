
cdef extern from "native/BlpConvert.h" namespace "python_blp":
    cdef cppclass BlpConvert:
        BlpConvert() except +
        void convert(unsigned char* inputFile, unsigned int fileSize, const char* inputFileName,
                     const char* outputPath)


cdef class BlpConverter:
    cdef BlpConvert c_convert
    def __cinit__(self):
        self.c_convert = BlpConvert()

    cpdef convert(self, input_files, output_path):
        for data, name in input_files:
            self.c_convert.convert(data, len(data), bytes(name), bytes(output_path))