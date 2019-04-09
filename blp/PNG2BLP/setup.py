import platform
from distutils.core import setup, Extension
from Cython.Build import cythonize

if platform.system() != 'Darwin':
    extra_compile_args = ['-O3'] 
    extra_link_args = []
else:
    extra_compile_args = ['-O3', '-mmacosx-version-min=10.9', '-stdlib=libc++', '-Wdeprecated']
    extra_link_args = ['-stdlib=libc++', '-mmacosx-version-min=10.9']

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