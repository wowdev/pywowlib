from distutils.core import setup, Extension
from Cython.Build import cythonize

setup(
    name='BLP To PNG Converter',
    ext_modules=cythonize(Extension(
        "BLP2PNG",
        sources=[
            "blp.pyx",
            "native/BlpConvert.cpp",
            "native/ByteStream.cpp",

            # LIBPNG
            "native/libpng/png.c",
            "native/libpng/pngerror.c",
            "native/libpng/pngget.c",
            "native/libpng/pngmem.c",
            "native/libpng/pngpread.c",
            "native/libpng/pngread.c",
            "native/libpng/pngrio.c",
            "native/libpng/pngrtran.c",
            "native/libpng/pngrutil.c",
            "native/libpng/pngset.c",
            "native/libpng/pngtrans.c",
            "native/libpng/pngwio.c",
            "native/libpng/pngwrite.c",
            "native/libpng/pngwtran.c",
            "native/libpng/pngwutil.c",

            # ZLIB
            "native/zlib/adler32.c",
            "native/zlib/compress.c",
            "native/zlib/crc32.c",
            "native/zlib/deflate.c",
            "native/zlib/gzclose.c",
            "native/zlib/gzlib.c",
            "native/zlib/gzread.c",
            "native/zlib/gzwrite.c",
            "native/zlib/infback.c",
            "native/zlib/inffast.c",
            "native/zlib/inflate.c",
            "native/zlib/inftrees.c",
            "native/zlib/trees.c",
            "native/zlib/uncompr.c",
            "native/zlib/zutil.c"
        ],

        include_dirs=["native/pngpp", "native/libpng", "native/zlib"],
        language="c++"
    )),
    requires=['Cython']
)