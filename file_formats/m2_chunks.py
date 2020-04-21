from io import BytesIO
from .wow_common_types import MVER, M2Array, fixed16, M2ContentChunk, M2ArrayChunk
from ..io_utils.types import *
from .m2_format import M2Header, M2PartTrack, M2Track, M2Bounds, M2TrackBase


#############################################################
######                 Legion Chunks                   ######
#############################################################

class PFID(M2ContentChunk):

    def __init__(self):
        super().__init__()
        self.phys_file_id = 0

    def read(self, f):
        super().read(f)
        self.phys_file_id = uint32.read(f)

        return self

    def write(self, f):
        self.size = 4
        super().write(f)
        uint32.write(f, self.phys_file_id)

        return self


class SFID(M2ContentChunk):
    def __init__(self, n_views=0):
        super().__init__()
        self.skin_file_data_ids = []
        self.lod_skin_file_data_ids = []

        self.n_views = n_views

    def read(self, f):
        super().read(f)

        self.skin_file_data_ids = []
        self.lod_skin_file_data_ids = []

        for i in range(self.n_views):
            self.skin_file_data_ids.append(uint32.read(f))

        for i in range((self.size - self.n_views * 4) // 4):
            self.lod_skin_file_data_ids.append(uint32.read(f))

        return self

    def write(self, f):
        self.size = len(self.skin_file_data_ids) * 4 + len(self.lod_skin_file_data_ids) * 4
        super().write(f)

        for val in self.skin_file_data_ids:
            uint32.write(f, val)

        for val in self.lod_skin_file_data_ids:
            uint32.write(f, val)

        return self


class AnimFileID:
    def __init__(self):
        self.anim_id = 0
        self.sub_anim_id = 0
        self.file_id = 0

    def read(self, f):
        self.anim_id = uint16.read(f)
        self.sub_anim_id = uint16.read(f)
        self.file_id = uint32.read(f)

        return self

    def write(self, f):
        uint16.write(f, self.anim_id)
        uint16.write(f, self.sub_anim_id)
        uint32.write(f, self.file_id)

        return self

    @staticmethod
    def size():
        return 8


class AFID(M2ArrayChunk):
    """ Animation File ID """
    item = AnimFileID
    data = "anim_file_ids"


class BFID(M2ArrayChunk):
    """ Bone file data IDs """
    item = uint32
    data = "bone_file_data_ids"


class TextureAC:
    def __init__(self):
        self.unk1 = 0
        self.unk2 = 0

    def read(self, f):
        self.unk1 = int8.read(f)
        self.unk2 = int8.read(f)

    def write(self, f):
        int8.write(self.unk1, f)
        int8.write(self.unk2, f)

    @staticmethod
    def size():
        return 2


class TXAC(M2ArrayChunk):
    """ Texture AC """
    item = TextureAC
    data = "texture_ac"



class ExtendedParticle:

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

    @staticmethod
    def size():
        return 12


class EXPT(M2ArrayChunk):
    "Extended Particle "

    item = ExtendedParticle
    data = "extended_particles"


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


class EXP2(M2ContentChunk):
    def __init__(self):
        super().__init__()
        self.content = M2Array(ExtendedParticle2)

    def read(self, f):
        super().read(f)
        self.content.read(f)

        return self

    def write(self, f):
        self.size = M2Array.size()
        super().write(f)
        self.content.write(f)

        return self


class PABC(M2ContentChunk):
    def __init__(self):
        super().__init__()
        self.content = M2Array(uint16)

    def read(self, f):
        super().read(f)
        self.content.read(f)

        return self

    def write(self, f):
        self.size = M2Array.size()
        super().write(f)
        self.content.write(f)

        return self


class PADC(M2ContentChunk):
    def __init__(self):
        super().__init__()
        self.content = M2Array(M2Track << (fixed16, PADC))

    def read(self, f):
        super().read(f)
        self.content.read(f)

        return self

    def write(self, f):
        self.size = M2Array.size()
        super().write(f)
        self.content.write(f)

        return self


class PSBC(M2ContentChunk):
    def __init__(self):
        super().__init__()
        self.content = M2Array(M2Bounds)

    def read(self, f):
        super().read(f)
        self.content.read(f)

        return self

    def write(self, f):
        self.size = M2Array.size()
        super().write(f)
        self.content.write(f)

        return self


class PEDC(M2ContentChunk):
    def __init__(self):
        super().__init__()
        self.content = M2Array(M2TrackBase)

    def read(self, f):
        super().read(f)
        self.content.read(f)

        return self

    def write(self, f):
        self.size = M2Array.size()
        super().write(f)
        self.content.write(f)

        return self


class SKID(M2ContentChunk):
    def __init__(self):
        super().__init__()
        self.skeleton_file_id = 0

    def read(self, f):
        super().read(f)
        self.skeleton_file_id = uint32.read(f)

        return self

    def write(self, f):
        self.size = uint32.size()
        super().write(f)
        uint32.write(f, self.skeleton_file_id)

        return self


#############################################################
######                 BfA Chunks                      ######
#############################################################


class TXID(M2ArrayChunk):
    """ Texture File Data ID """
    item = uint32
    data = "texture_ids"


class RPID(M2ArrayChunk):
    """ Recursive Particle File Data ID """
    item = uint32
    data = "recursive_particle_models"


class GPID(M2ArrayChunk):
    """ Geometry Particle Data ID """
    item = uint32
    data = "geometry_particle_models"


class LDV1(M2ContentChunk):

    def __init__(self):
        super().__init__()
        self.unk0 = 0
        self.lod_count = 0
        self.unk2_f = 0.0
        self.particle_bone_lod = [0, 0, 0, 0]
        self.unk4 = 0

    def read(self, f):
        super().read(f)
        self.unk0 = uint16.read(f)
        self.lod_count = uint16.read(f)
        self.unk2_f = float32.read(f)
        self.particle_bone_lod = list(uint8.read(f, 4))
        self.unk4 = uint32.read(f)

        return self

    def write(self, f):
        self.size = 16
        super().write(f)
        uint16.write(f, self.unk0)
        uint16.write(f, self.lod_count)
        float32.write(f, self.unk2_f)
        uint32.write(f, self.unk4)

        return self



class PGD1Entry:

    def __init__(self):
        self.unk = [0, 0]

    def read(self, f):
        self.unk = list(uint8.read(f, 2))

    def write(self, f):
        uint8.write(f, self.unk, 2)

    @staticmethod
    def size():
        return 2


class PGD1(M2ContentChunk):

    def __init__(self):
        super().__init__()
        self.p_g_d_v1 = M2Array(PGD1Entry)

    def read(self, f):
        super().read(f)
        self.p_g_d_v1.read(f)

        return self

    def write(self, f):
        self.size = self.p_g_d_v1.n_elements * PGD1Entry.size()
        super().write(f)
        self.p_g_d_v1.write(f)

        return self


#############################################################
######                 Main Chunks                     ######
#############################################################

class MD20(M2Header):
    pass


class MD21(M2Header, M2ContentChunk):
    def __init__(self):
        super().__init__()

    def read(self, f):
        M2ContentChunk.read(self, f)
        md20_raw = f.read(self.size)

        with BytesIO(md20_raw) as f2:
            magic = f2.read(4)
            assert magic != 'MD20'

            M2Header.read(self, f2)

        return self

    def write(self, f):

        with BytesIO() as f2:
            M2Header.write(self, f2)
            md20_raw = f2.read()
            self.size = len(md20_raw)
            M2ContentChunk.write(self, f)
            f.write(md20_raw)

        return self

