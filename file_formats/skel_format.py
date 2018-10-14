from .wow_common_types import ChunkHeader
from .m2_format import *
from .m2_chunks import AFID, BFID


class SKL1:
    _size = 16

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='SKL1')
        self.header.size = size
        self.unk1 = 0
        self.name = M2Array(char)
        self.unk2 = []

    def read(self, f):
        self.unk1 = uint32.read(f)
        self.name.read(f)
        self.unk2 = [uint8.read(f) for _ in range(4)]

    def write(self, f):
        self.header.size = len(self.unk2) + self.unk1 * 4 + self.name.n_elements * char.size_()
        MemoryManager.mem_reserve(f, self._size)
        self.header.write(f)
        self.name.write(f)
        uint32.write(f, self.unk1)

        for val in self.unk2:
            uint8.write(f, val)


class SKA1:
    _size = 16

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='SKA1')
        self.header.size = size
        self.attachments = M2Array(M2Attachment)
        self.attachment_lookup_table = M2Array(uint16)

    def read(self, f):
        self.attachments.read(f)
        self.attachment_lookup_table = uint16.read(f)

    def write(self, f):
        self.header.size = self.attachments.n_elements * M2Attachment.size() \
                           + self.attachment_lookup_table.n_elements * 2
        MemoryManager.mem_reserve(f, self._size)
        self.header.write(f)
        self.attachments.write(f)
        uint16.write(f, self.attachment_lookup_table)


class SKB1:
    _size = 16

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='SKB1')
        self.header.size = size
        self.bones = M2Array(M2CompBone)
        self.key_bone_lookup = M2Array(uint16)

    def read(self, f):
        self.bones.read(f)
        self.key_bone_lookup = uint16.read(f)

    def write(self, f):
        self.header.size = self.bones.n_elements * M2Attachment.size() + self.key_bone_lookup.n_elements * 2
        MemoryManager.mem_reserve(f, self._size)
        self.header.write(f)
        self.bones.write(f)
        uint16.write(f, self.key_bone_lookup)


class SKS1:
    _size = 32

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='SKS1')
        self.header.size = size
        self.global_loops = M2Array(uint32)
        self.sequences = M2Array(M2Sequence)
        self.sequence_lookups = M2Array(uint16)
        self.unk = []

    def read(self, f):
        self.global_loops = uint32.read(f)
        self.sequences.read(f)
        self.sequence_lookups = uint16.read(f)

        self.unk = [uint8.read(f) for _ in range(8)]

    def write(self, f):
        self.header.size = len(self.unk) + self.global_loops.n_elements * 4 + self.sequences.n_elements * M2Sequence.size()\
        + self.sequence_lookups.n_elements * 2

        for val in self.unk:
            uint8.write(f, val)


class SKPD:
    _size = 32

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='SKPD')
        self.header.size = size
        self.parent_skel_file_id = 0

        self.unk1 = []
        self.unk2 = []

    def read(self, f):
        self.parent_skel_file_id = uint32.read(f)

        self.unk1 = [uint8.read(f) for _ in range(8)]
        self.unk2 = [uint8.read(f) for _ in range(4)]

    def write(self, f):
        self.header.size = len(self.unk1) + len(self.unk2) + self.parent_skel_file_id * 4

        for val in self.unk1:
            uint8.write(f, val)

        for val in self.unk2:
            uint8.write(f, val)

