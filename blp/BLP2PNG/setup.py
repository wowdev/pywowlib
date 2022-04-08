#!/usr/bin/env python
import sys
import platform
import argparse
from setuptools import setup, Extension
from Cython.Build import cythonize


def print_error(*s: str):
    print("\033[91m {}\033[00m".format(' '.join(s)))


def print_succes(*s: str):
    print("\033[92m {}\033[00m".format(' '.join(s)))


def print_info(*s: str):
    print("\033[93m {}\033[00m".format(' '.join(s)))


def main(debug: bool):

    print_info("\nBuilding BLP2PNG extension...")
    print(f'Target mode: {"Debug" if debug else "Release"}')

    # compiler and linker settings
    if platform.system() == 'Darwin':
        if debug:
            extra_compile_args = ['-g3', '-O0', '-stdlib=libc++']
            extra_link_args = ['-stdlib=libc++']
        else:
            extra_compile_args = ['-O3', '-stdlib=libc++']
            extra_link_args = ['-stdlib=libc++']

    elif platform.system() == 'Windows':
        if debug:
            extra_compile_args = ['/std:c++17', '/Zi']
            extra_link_args = ['/DEBUG:FULL']
        else:
            extra_compile_args = ['/std:c++17']
            extra_link_args = []
    else:
        if debug:
            extra_compile_args = ['-std=c++17', '-O0', '-g']
            extra_link_args = []
        else:
            extra_compile_args = ['-std=c++17', '-O3']
            extra_link_args = []

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

    print_succes("\nSuccessfully built BLP2PNG extension.")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--wbs_debug', action='store_true', help='Compile CASC extension in debug mode.')
    args, unknown = parser.parse_known_args()

    if args.wbs_debug:
        sys.argv.remove('--wbs_debug')


    main(args.wbs_debug)
