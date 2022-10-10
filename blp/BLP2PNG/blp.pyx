from libcpp.vector cimport vector
from libc.stdint cimport uint32_t
from cython.parallel cimport prange
cimport cython

cimport numpy as np
import numpy as np

import bpy


cdef extern from "native/BlpConvert.h" namespace "python_blp" nogil:

    cdef struct Image:
       vector[uint32_t] buffer
       size_t width
       size_t height

    cdef cppclass BlpConvert:
        BlpConvert()
        Image get_raw_pixels(unsigned char* inputFile, size_t fileSize) const

cdef struct BufDesc:
    unsigned char* data
    size_t length

cdef class BlpConverter:
    cdef BlpConvert c_convert
    def __cinit__(self):
        self.c_convert = BlpConvert()

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.nonecheck(False)
    cpdef create_image(self, data):
        cdef Image c_img = self.c_convert.get_raw_pixels(data, len(data))
        cdef vector[float] float_buf
        float_buf.resize(c_img.width * c_img.height * 4)
        cdef unsigned char* data_as_bytes = <unsigned char*>(c_img.buffer.data())

        cdef size_t i = 0
        for i in range(c_img.width * c_img.height * 4):
            float_buf[i] = data_as_bytes[i] / 255.0

        cdef float[::1] arr = <float [:float_buf.size()]>(float_buf.data())

        img = bpy.data.images.new('test', c_img.width, c_img.height
                                  , alpha=True
                                  , float_buffer=False
                                  , stereo3d=False
                                  , is_data=False
                                  , tiled=False)


        img.pixels.foreach_set(np.asarray(arr))
        img.update()

        return img

    @cython.cdivision(True)
    @cython.boundscheck(False)
    @cython.nonecheck(False)
    cpdef create_images(self, image_buffers):
        cdef size_t i = 0
        cdef size_t j = 0

        cdef vector[BufDesc] py_bytes
        cdef vector[vector[float]] c_images_float
        cdef vector[Image] c_images
        cdef size_t n_images = len(image_buffers)
        py_bytes.resize(n_images)
        c_images_float.resize(n_images)
        c_images.resize(n_images)

        for i in range(n_images):
            py_bytes[i].data = image_buffers[i]
            py_bytes[i].length = len(image_buffers[i])



        cdef unsigned char* data_as_bytes
        cdef size_t num_pixels
        
        i = 0
        for i in prange(n_images, nogil=True):
            c_images[i] = self.c_convert.get_raw_pixels(py_bytes[i].data, py_bytes[i].length)
            num_pixels = c_images[i].width * c_images[i].height * 4
            c_images_float[i].resize(num_pixels)

            data_as_bytes = <unsigned char*>(c_images[i].buffer.data())

            j = 0
            for j in range(num_pixels):
                c_images_float[i][j] = data_as_bytes[j] / 255.0

        cdef float[::1] mem_view
        i = 0
        for i in range(n_images):
            mem_view = <float [:c_images_float[i].size()]>(c_images_float[i].data())
            img = bpy.data.images.new('test', c_images[i].width, c_images[i].height
                                      , alpha=True
                                      , float_buffer=False
                                      , stereo3d=False
                                      , is_data=False
                                      , tiled=False)

            img.pixels.foreach_set(np.asarray(mem_view))
            img.update()





