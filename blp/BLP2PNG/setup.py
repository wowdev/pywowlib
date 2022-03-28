#!/usr/bin/env python
import platform
from setuptools import setup, Extension
from Cython.Build import cythonize

def main():

    print("\nBuilding BLP2PNG extension.")

    if platform.system() != 'Darwin':
        extra_compile_args = ['-O3']
        extra_link_args = []
    else:
        extra_compile_args = ['-O3', '-mmacosx-version-min=10.9', '-stdlib=libc++', '-Wdeprecated']
        extra_link_args = ['-stdlib=libc++', '-mmacosx-version-min=10.9']

    extensions = [Extension(
        "BLP2PNG",
        sources=[
            "blp.pyx",
            "native/BlpConvert.cpp",
            "native/ByteStream.cpp",

            # LIBPNG
            "../include/libpng/png.c",
            "../include/libpng/pngerror.c",
            "../include/libpng/pngget.c",
            "../include/libpng/pngmem.c",
            "../include/libpng/pngpread.c",
            "../include/libpng/pngread.c",
            "../include/libpng/pngrio.c",
            "../include/libpng/pngrtran.c",
            "../include/libpng/pngrutil.c",
            "../include/libpng/pngset.c",
            "../include/libpng/pngtrans.c",
            "../include/libpng/pngwio.c",
            "../include/libpng/pngwrite.c",
            "../include/libpng/pngwtran.c",
            "../include/libpng/pngwutil.c",

            # ZLIB
            "../include/zlib/adler32.c",
            "../include/zlib/compress.c",
            "../include/zlib/crc32.c",
            "../include/zlib/deflate.c",
            "../include/zlib/gzclose.c",
            "../include/zlib/gzlib.c",
            "../include/zlib/gzread.c",
            "../include/zlib/gzwrite.c",
            "../include/zlib/infback.c",
            "../include/zlib/inffast.c",
            "../include/zlib/inflate.c",
            "../include/zlib/inftrees.c",
            "../include/zlib/trees.c",
            "../include/zlib/uncompr.c",
            "../include/zlib/zutil.c"
        ],

        include_dirs=["../include/pngpp", "../include/libpng", "../include/zlib"],
        language="c++",
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args
    )]

    for e in extensions:
        e.cython_directives = {'language_level': "3"}

    setup(
        name='BLP To PNG Converter',
        ext_modules=cythonize(extensions),
        requires=['Cython']
    )

    print("\nSuccesfully built BLP2PNG extension.")

if __name__ == '__main__':
    main()
