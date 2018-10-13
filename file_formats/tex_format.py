from .wow_common_types import ChunkHeader
from ..io_utils.types import *


class TXVR:
    def __init__(self, size=4):
        self.header = ChunkHeader(magic='RVXT')
        self.header.size = size
        self.version = 0

    def read(self, f):
        self.version = uint32.read(f)

    def write(self, f):
        self.header.size = 4
        self.header.write(f)
        uint32.write(f, self.version)


class SBlobTexture:
    def __init__(self):
        self.filename_offset = 0
        self.txmd_offset = 0
        self.size_x = 0
        self.size_y = 0
        self.m_num_levels = 0
        self.loaded = 0
        self.dxt_type = 0
        self.flags = 0

    def read(self, f):
        self.filename_offset = uint32.read(f)
        self.txmd_offset = uint32.read(f)
        self.size_x = uint8.read(f)
        self.size_y = uint8.read(f)
        self.m_num_levels = uint7.read(f)  # TODO: int7 custom type
        self.loaded = uint1.read(f)  # TODO: int1 custom type
        self.dxt_type = uint4.read(f)   # TODO: int4 custom type
        self.flags = uint4.read(f)


    def write(self, f):
        uint32.write(f, self.filename_offset)
        uint32.write(f, self.txmd_offset)
        uint8.write(f, self.size_x)
        uint8.write(f, self.size_y)
        uint7.write(f, self.m_num_levels)
        uint1.write(f, self.loaded)
        uint4.write(f, self.dxt_type)
        uint4.write(f, self.flags)


class TXBT:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='TBXT')
        self.header.size = size
        self.entries = []

    def read(self, f):
        for _ in range(self.header.size // 12):
            s_blob_texture = SBlobTexture()
            s_blob_texture.read(f)
            self.entries.append(s_blob_texture)

    def write(self, f):
        self.header.size = len(self.entries) * 12
        self.header.write(f)

        for val in self.entries:
            val.write(f)


class TXFN:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='NFXT')
        self.header.size = size
        self.filenames = []

    def read(self, f):
        self.filenames = []
        for i in range(self.header.size):
            self.filenames.append(int8.read(f))

    def write(self, f):
        self.header.size = len(self.filenames)
        self.header.write(f)

        for val in self.filenames:
            int8.write(f, val)


class TXMD:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='DMXT')
        self.header.size = size
        self.texture_data = []

    def read(self, f):
        self.texture_data = []
        for i in range(self.header.size):
            self.texture_data.append(int8.read(f))

    def write(self, f):
        self.header.size = len(self.texture_data)
        self.header.write(f)

        for val in self.texture_data:
            int8.write(f, val)