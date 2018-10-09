from .wow_common_types import ChunkHeader, MVER
from ..io_utils.types import *

#############################################################
######                 Legion Chunks                   ######
#############################################################


class PFID:
    def __init__(self, size=8):
        self.header = ChunkHeader(magic='PFID')
        self.header.size = size
        self.phys_file_id = 0

    def read(self, f):
        self.phys_file_id = uint32.read(f)

    def write(self, f):
        self.header.size = 4
        self.header.write(f)
        uint32.write(f, self.phys_file_id)


class SFID:
    def __init__(self, size=0, n_views=0, lod_bands=0):
        self.header = ChunkHeader(magic='SFID')
        self.header.size = size
        self.skin_file_data_ids = []
        self.lod_skin_file_data_ids = []

        self.n_views = n_views
        self.lod_bands = lod_bands

    def read(self, f):
        self.skin_file_data_ids = []
        self.lod_skin_file_data_ids = []

        for i in range(self.n_views):
            self.skin_file_data_ids.append(uint32.read(f))

        for i in range(self.lod_bands):
            self.lod_skin_file_data_ids.append(uint32.read(f))

    def write(self, f):
        self.header.size = len(self.skin_file_data_ids) * 4 + len(self.lod_skin_file_data_ids) * 4
        self.header.write(f)

        for val in self.skin_file_data_ids:
            uint32.write(f, val)

        for val in self.lod_skin_file_data_ids:
            uint32.write(f, val)


class AnimFileID:
    def __init__(self):
        self.anim_id = 0
        self.sub_anim_id = 0
        self.file_id = 0

    def read(self, f):
        self.anim_id = uint16.read(f)
        self.sub_anim_id = uint16.read(f)
        self.file_id = uint32.read(f)

    def write(self, f):
        uint16.write(f, self.anim_id)
        uint16.write(f, self.sub_anim_id)
        uint32.write(f, self.file_id)


class AFID:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='AFID')
        self.header.size = size
        self.anim_file_ids = []

    def read(self, f):
        for _ in range(self.header.size // 8):
            anim_id = AnimFileID()
            anim_id.read(f)
            self.anim_file_ids.append(anim_id)

    def write(self, f):
        self.header.size = len(self.anim_file_ids) * 8
        self.header.write(f)

        for val in self.anim_file_ids:
            val.write(f)


class BFID:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='BFID')
        self.header.size = size
        self.bone_file_data_ids = []

    def read(self, f):
        self.bone_file_data_ids = []
        for i in range(self.header.size // 4):
            self.bone_file_data_ids.append(uint32.read(f))

    def write(self, f):
        self.header.size = len(self.bone_file_data_ids) * 4
        self.header.write(f)

        for val in self.bone_file_data_ids:
            uint32.write(f, val)


class TXAC:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='TXAC')
        self.header.size = size

        self.texture_ac = []

    def read(self, f):
        self.texture_ac = []
        for i in range(self.header.size // 2):
            self.texture_ac.append((int8.read(f), int8.read(f)))

    def write(self, f):
        self.header.size = len(self.texture_ac) * 2
        for pair in self.texture_ac:
            for val in pair:
                int8.write(f, val)


class SKID:
    def __init__(self, size=8):
        self.header = ChunkHeader(magic='SKID')
        self.header.size = size
        self.skeleton_file_id = 0

    def read(self, f):
        self.skeleton_file_id = uint32.read(f)

    def write(self, f):
        self.header.size = 4
        self.header.write(f)
        uint32.write(f, self.skeleton_file_id)


#############################################################
######                 BfA Chunks                      ######
#############################################################


class TXID:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='TXID')
        self.header.size = size
        self.texture_id = []

    def read(self, f):
        self.texture_id = []
        for i in range(self.header.size // 4):
            self.texture_id.append(uint32.read(f))

    def write(self, f):
        self.header.size = len(self.texture_id) * 4
        self.header.write(f)

        for fileDataID in self.texture_id:
            uint32.write(f, fileDataID)


class RPID:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='RPID')
        self.header.size = size
        self.recursive_particle_models = []

    def read(self, f):
        self.recursive_particle_models = []
        for i in range(self.header.size // 4):
            self.recursive_particle_models.append(uint32.read(f))

    def write(self, f):
        self.header.size = len(self.recursive_particle_models) * 4
        self.header.write(f)

        for file_data_id in self.recursive_particle_models:
            uint32.write(f, file_data_id)


class GPID:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='GPID')
        self.header.size = size
        self.geometry_particle_models = []

    def read(self, f):
        self.geometry_particle_models = []
        for i in range(self.header.size // 4):
            self.geometry_particle_models.append(uint32.read(f))

    def write(self, f):
        self.header.size = len(self.geometry_particle_models) * 4
        self.header.write(f)

        for file_data_id in self.geometry_particle_models:
            uint32.write(f, file_data_id)
