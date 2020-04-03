from io import BytesIO
from .wow_common_types import ChunkHeader, MVER, M2Array, fixed16, ArrayChunk
from ..io_utils.types import *
from .m2_format import M2Header, M2PartTrack, M2Track, M2Bounds, M2TrackBase

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
    def __init__(self, size=0, n_views=0):
        self.header = ChunkHeader(magic='SFID')
        self.header.size = size
        self.skin_file_data_ids = []
        self.lod_skin_file_data_ids = []

        self.n_views = n_views

    def read(self, f):
        self.skin_file_data_ids = []
        self.lod_skin_file_data_ids = []

        for i in range(self.n_views):
            self.skin_file_data_ids.append(uint32.read(f))

        for i in range((self.header.size - self.n_views * 4) // 4):
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


class ExtendedParticle:
    size = 12

    def __init__(self):
        self.z_source = 0
        self.unk1 = 0
        self.unk2 = 0

    def read(self, f):
        self.z_source = uint32.read(f)
        self.unk1 = uint32.read(f)
        self.unk2 = uint32.read(f)

    def write(self, f):
        uint32.write(f, self.z_source)
        uint32.write(f, self.unk1)
        uint32.write(f, self.unk2)


class EXPT:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='EXPT')
        self.header.size = size
        self.extended_particles = []

    def read(self, f, n_particles):
        self.header.read(f)
        self.extended_particles = [ExtendedParticle() for _ in range(self.header.size // ExtendedParticle.size)]

        for rec in self.extended_particles:
            rec.read(f)

    def write(self, f):
        self.header.size = len(self.extended_particles) * ExtendedParticle.size

        for rec in self.extended_particles:
            rec.write(f)


class ExtendedParticle2:
    def __init__(self):
        self.z_source = 0
        self.unk1 = 0
        self.unk2 = 0
        self.unk3 = M2PartTrack(fixed16)

    def read(self, f):
        self.z_source = uint32.read(f)
        self.unk1 = uint32.read(f)
        self.unk2 = uint32.read(f)
        self.unk3.read(f)

    def write(self, f):
        uint32.write(f, self.z_source)
        uint32.write(f, self.unk1)
        uint32.write(f, self.unk2)
        self.unk3.write(f)

    @staticmethod
    def size():
        return uint32.size() * 3 + M2PartTrack.size()


class EXP2:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='EXP2')
        self.header.size = size
        self.content = M2Array(ExtendedParticle2)

    def read(self, f):
        self.content.read(f)

    def write(self, f):
        self.header.size = M2Array.size()
        self.header.write(f)
        self.content.write(f)


class PABC:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='PABC')
        self.header.size = size
        self.content = M2Array(uint16)

    def read(self, f):
        self.content.read(f)

    def write(self, f):
        self.header.size = M2Array.size()
        self.header.write(f)
        self.content.write(f)


class PADC:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='PADC')
        self.header.size = size
        self.content = M2Array(M2Track << fixed16)

    def read(self, f):
        self.content.read(f)

    def write(self, f):
        self.header.size = M2Array.size()
        self.header.write(f)
        self.content.write(f)


class PSBC:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='PSBC')
        self.header.size = size
        self.content = M2Array(M2Bounds)

    def read(self, f):
        self.content.read(f)

    def write(self, f):
        self.header.size = M2Array.size()
        self.header.write(f)
        self.content.write(f)


class PEDC:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='PEDC')
        self.header.size = size
        self.content = M2Array(M2TrackBase)

    def read(self, f):
        self.content.read(f)

    def write(self, f):
        self.header.size = M2Array.size()
        self.header.write(f)
        self.content.write(f)

class SKID:
    def __init__(self, size=8):
        self.header = ChunkHeader(magic='SKID')
        self.header.size = size
        self.skeleton_file_id = 0

    def read(self, f):
        self.skeleton_file_id = uint32.read(f)

    def write(self, f):
        self.header.size = uint32.size()
        self.header.write(f)
        uint32.write(f, self.skeleton_file_id)


class TXID(ArrayChunk):
    item = uint32

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


#############################################################
######                 Main Chunks                     ######
#############################################################

class MD20(M2Header):
    pass


class MD21(M2Header):
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='MD21')
        self.header.size = size
        super().__init__()

    def read(self, f):
        md20_raw = f.read(self.header.size)

        with BytesIO(md20_raw) as f2:
            magic = f2.read(4)
            assert magic != 'MD20'

            super().read(f2)

    def write(self, f):

        with BytesIO() as f2:
            super().write(f2)
            md20_raw = f2.read()
            self.header.size = len(md20_raw)
            self.header.write(f)
            f.write(md20_raw)

