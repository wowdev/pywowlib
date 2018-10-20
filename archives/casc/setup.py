from distutils.core import setup, Extension
from Cython.Build import cythonize

setup(
    name='Python CASC Handler',
    ext_modules=cythonize(Extension(
        "CASC",
        sources=[
            "casc.pyx",

            "native/BinaryReader.cpp",
            "native/BlteHandler.cpp",
            "native/DataStream.cpp",
            "native/EncodingFileParser.cpp",
            "native/Jenkins96.cpp",
            "native/KeyValueConfig.cpp",
            "native/LocalCascHandler.cpp",
            "native/RootFileParser.cpp",
            "native/String.cpp",
            "native/Structures.cpp",
            "native/TokenConfig.cpp",

            # ZLIB
            "native/zlib/adler32.c",
            "native/zlib/compress.c",
            "native/zlib/crc32.c",
            "native/zlib/deflate.c",
            "native/zlib/infback.c",
            "native/zlib/inffast.c",
            "native/zlib/inflate.c",
            "native/zlib/inftrees.c",
            "native/zlib/trees.c",
            "native/zlib/uncompr.c",
            "native/zlib/zutil.c"
        ],

        include_dirs=["native/zlib"],
        language="c++",
        extra_compile_args=['-O3']
    )),
    requires=['Cython']
)