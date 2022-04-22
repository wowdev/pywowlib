#!/usr/bin/env python
import sys
import argparse
import platform
from setuptools import setup, Extension
from Cython.Build import cythonize


def print_error(*s: str):
    print("\033[91m {}\033[00m".format(' '.join(s)))


def print_succes(*s: str):
    print("\033[92m {}\033[00m".format(' '.join(s)))


def print_info(*s: str):
    print("\033[93m {}\033[00m".format(' '.join(s)))


def main(debug: bool):
    print_info("\nBuilding PNG2BLP extension...")
    print(f'Target mode: {"Debug" if debug else "Release"}')

    # compiler and linker settings
    if platform.system() == 'Darwin':
        if debug:
            extra_compile_args = ['-std=c++17', '-g3', '-O0']
            extra_link_args = []
        else:
            extra_compile_args = ['-std=c++17', '-O3']
            extra_link_args = []

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

    setup(
        name='BLP To PNG Converter',
        ext_modules=cythonize([Extension(
            "PNG2BLP",
            sources=[
                "png2blp.pyx",

                "native/BinaryWriter.cpp",
                "native/GaussFiltering.cpp",
                "native/MipMapGenerator.cpp",
                "native/Png2Blp.cpp",
                "native/PngReader.cpp",
                "native/Quantizer.cpp",

                # ZLIB
                "../include/zlib/adler32.c",
                "../include/zlib/compress.c",
                "../include/zlib/crc32.c",
                "../include/zlib/deflate.c",
                "../include/zlib/infback.c",
                "../include/zlib/inffast.c",
                "../include/zlib/inflate.c",
                "../include/zlib/inftrees.c",
                "../include/zlib/trees.c",
                "../include/zlib/uncompr.c",
                "../include/zlib/zutil.c",

                # PNGPP
                # header only

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

                # LIBIMAGEQUANT
                "../include/libimagequant/blur.c",
                "../include/libimagequant/kmeans.c",
                "../include/libimagequant/libimagequant.c",
                "../include/libimagequant/mediancut.c",
                "../include/libimagequant/mempool.c",
                "../include/libimagequant/nearest.c",
                "../include/libimagequant/pam.c",

                # LIBTXC_DXTN
                "../include/libtxc_dxtn/txc_compress_dxtn.c",
                "../include/libtxc_dxtn/txc_fetch_dxtn.c"
            ],

            include_dirs=["../include/zlib", "../include/libimagequant", "../include/libpng", "../include/libtxc_dxtn", "../include/pngpp"],
            language="c++",
            extra_compile_args=extra_compile_args,
            extra_link_args=extra_link_args
        )]),
        requires=['Cython']
    )

    print_succes("\nSuccesfully built PNG2BLP extension.")


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--wbs_debug', action='store_true', help='Compile CASC extension in debug mode.')
    args, unknown = parser.parse_known_args()

    if args.wbs_debug:
        sys.argv.remove('--wbs_debug')

    main(args.wbs_debug)
