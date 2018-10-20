cmake_minimum_required(VERSION 3.5)
project(cython_casc)

set(CMAKE_CXX_STANDARD 98)

add_library(cython_casc
        native/zlib/adler32.c native/zlib/compress.c
        native/zlib/crc32.c native/zlib/crc32.h
        native/zlib/deflate.c native/zlib/deflate.h
        native/zlib/infback.c
        native/zlib/inffast.c native/zlib/inffast.h
        native/zlib/inffixed.h native/zlib/inflate.c
        native/zlib/inflate.h native/zlib/inftrees.c
        native/zlib/inftrees.h native/zlib/trees.c
        native/zlib/trees.h native/zlib/uncompr.c
        native/zlib/zconf.h native/zlib/zlib.h
        native/zlib/zutil.c native/zlib/zutil.h
        native/EncodingFileParser.cpp native/EncodingFileParser.h
        native/BinaryReader.cpp native/BinaryReader.h
        native/Structures.cpp native/Structures.h
        native/RootFileParser.cpp native/RootFileParser.h
        native/LocalCascHandler.cpp native/LocalCascHandler.h
        native/TokenConfig.cpp native/TokenConfig.h
        native/String.cpp native/String.h
        native/KeyValueConfig.cpp native/KeyValueConfig.h
        native/DataStream.cpp native/DataStream.h
        native/BlteHandler.cpp native/BlteHandler.h
        native/Jenkins96.cpp native/Jenkins96.h)