from .wow_common_types import *
from ..enums.adt_enums import *
from .. import CLIENT_VERSION, WoWVersions

__reload_order_index__ = 2

TILE_SIZE = 5533.333333333
MAP_SIZE_MIN = -17066.66656
MAP_SIZE_MAX = 17066.66657


class MVER:
    def __init__(self):
        self.header = ChunkHeader('REVM', 4)
        self.version = 18

    def read(self, f):
        self.header.read(f)
        self.version = uint32.read(f)

        return self

    def write(self, f):
        self.header.write(f)
        uint32.write(self.header)

        return self


class MHDR:
    def __init__(self):
        self.header = ChunkHeader('RDHM', 54)
        self.flags = 0
        self.mcin = 0
        self.mtex = 0
        self.mmdx = 0
        self.mmid = 0
        self.mwmo = 0
        self.mwid = 0
        self.mddf = 0
        self.modf = 0
        self.mfbo = 0
        self.mh2o = 0
        self.mtxf = 0
        self.mamp_value = 0

    def read(self, f):
        self.header.read(f)
        pos = f.tell()
        self.flags = uint32.read(f)
        self.mcin = pos + uint32.read(f)
        self.mtex = pos + uint32.read(f)
        self.mmdx = pos + uint32.read(f)
        self.mmid = pos + uint32.read(f)
        self.mwmo = pos + uint32.read(f)
        self.mwid = pos + uint32.read(f)
        self.mddf = pos + uint32.read(f)
        self.modf = pos + uint32.read(f)
        self.mfbo = pos + uint32.read(f)
        self.mh2o = pos + uint32.read(f)
        self.mtxf = pos + uint32.read(f)
        self.mamp_value = uint8.read(f)
        f.skip(15)

        return self

    def write(self, f):
        self.header.write(f)
        pos = f.tell()
        uint32.write(f, self.flags)
        uint32.write(f, pos + self.mcin)
        uint32.write(f, pos + self.mtex)
        uint32.write(f, pos + self.mmdx)
        uint32.write(f, pos + self.mmid)
        uint32.write(f, pos + self.mwmo)
        uint32.write(f, pos + self.mwid)
        uint32.write(f, pos + self.mddf)
        uint32.write(f, pos + self.modf)
        uint32.write(f, pos + self.mfbo)
        uint32.write(f, pos + self.mh2o)
        uint32.write(f, pos + self.mtxf)
        uint8.write(f, self.mamp_value)
        f.skip(15)

        return self


class MCIN:
    def __init__(self):
        self.header = ChunkHeader('NICM', 16)
        self.offset = 0
        self.size = 0

    def read(self, f):
        self.header.read(f)
        self.offset = uint32.read(f)
        self.size = uint32.read(f)
        f.skip(8)

        return self

    def write(self, f):
        self.header.write(f)
        uint32.write(f, self.header)
        uint32.write(f, self.size)
        f.skip(8)

        return self


class MTEX(StringBlockChunk):
    magic = 'XTEM'


class MMID:
    def __init__(self):
        self.header = ChunkHeader('DIMM')
        self.offsets = []

    def read(self, f):
        self.header.read(f)

        for _ in range(self.header.size // 4):
            self.offsets.append(uint32.read(f))

        return self

    def write(self, f):
        self.header.size = len(self.offsets) * 4
        self.header.write(f)

        for offset in self.offsets:
            uint32.write(offset)

        return self


class MWID:
    def __init__(self):
        self.header = ChunkHeader('DIWM')
        self.offsets = []

    def read(self, f):
        self.header.read(f)

        for _ in range(self.header.size // 4):
            self.offsets.append(uint32.read(f))

    def write(self, f):
        self.header.size = len(self.offsets) * 4
        self.header.write(f)

        for offset in self.offsets:
            uint32.write(offset)


class ADTDoodadDefinition:
    def __init__(self):
        self.name_id = 0
        self.unique_id = 0
        self.position = (0, 0, 0)
        self.rotation = (0, 0, 0)
        self.scale = 0
        self.flags = 0

    def read(self, f):
        self.name_id = uint32.read(f)
        self.unique_id = uint32.read(f)
        self.position = vec3D.read(f)
        self.rotation = vec3D.read(f)
        self.scale = uint16.read(f)
        self.flags = uint16.read(f)

        return self

    def write(self, f):
        uint32.write(f, self.name_id)
        uint32.write(f, self.unique_id)
        vec3D.write(f, self.position)
        vec3D.write(f, self.rotation)
        uint16.write(f, self.scale)
        uint16.write(f, self.flags)

        return self


class MDDF:
    def __init__(self):
        self.header = ChunkHeader('FDDM')
        self.doodad_instances = []

    def read(self, f):
        self.header.read(f)
        for _ in range(self.header.size // 36):
            self.doodad_instances.append(ADTDoodadDefinition().read(f))

    def write(self, f):
        self.header.size = len(self.doodad_instances) * 36
        self.header.write(f)

        for doodad in self.doodad_instances:
            doodad.write(f)


class ADTWMODefinition:
    def __init__(self):
        self.name_id = 0
        self.unique_id = 0
        self.position = (0.0, 0.0, 0.0)
        self.rotation = (0.0, 0.0, 0.0)
        self.extents = CAaBox()
        self.flags = 0
        self.doodad_set = 0
        self.name_set = 0
        self.scale = 0

    def read(self, f):
        self.name_id = uint32.read(f)
        self.unique_id = uint32.read(f)
        self.position = vec3D.read(f)
        self.rotation = vec3D.read(f)
        self.extents.read(f)
        self.flags = uint16.read(f)
        self.doodad_set = uint16.read(f)
        self.name_set = uint16.read(f)
        self.scale = uint16.read(f)

    def write(self, f):
        uint32.write(f, self.name_id)
        uint32.write(f, self.unique_id)
        vec3D.write(f, self.position)
        vec3D.write(f, self.rotation)
        self.extents.write(f)
        uint16.write(f, self.flags)
        uint16.write(f, self.doodad_set)
        uint16.write(f, self.name_set)
        uint16.write(f, self.scale)


class MODF:
    def __init__(self):
        self.header = ChunkHeader('FDOM')
        self.wmo_instances = []

    def read(self, f):
        self.header.read(f)
        for _ in range(self.header.size // 64):
            wmo_instance = ADTWMODefinition()
            wmo_instance.read(f)
            self.wmo_instances.append(wmo_instance)

    def write(self, f):
        self.header.size = len(self.wmo_instances) * 64
        self.header.write(f)

        for wmo_instance in self.wmo_instances:
            wmo_instance.write(f)


class MCNK:
    def __init__(self):
        self.header = ChunkHeader('KNCM')
        self.index_x = 0
        self.index_y = 0
        self.n_layers = 0
        self.n_doodad_refs = 0

        if CLIENT_VERSION >= WoWVersions.MOP:
            self.hole_high_res = 0
        else:
            self.ofs_height = 0
            self.ofs_normal = 0

        self.ofs_layer = 0
        self.ofs_refs = 0
        self.ofs_alpha = 0
        self.size_alpha = 0
        self.ofs_shadow = 0
        self.size_shadow = 0
        self.area_id = 0
        self.n_map_obj_refs = 0
        self.holes_low_res = 0
        self.unknown_but_used = 0
        self.low_quality_texture_map = []


class MCVT:
    def __init__(self):
        self.header = ChunkHeader('TVCM', 580)
        self.height = [0.0] * 145

    def read(self, f):
        self.header.read(f)
        self.height = [float32.read(f) for _ in range(145)]

    def write(self, f):
        self.header.write(f)
        for value in self.height: float32.write(value)


class MCLV:
    def __init__(self):
        self.header = ChunkHeader('VLCM', 580)
        self.colors = [(255, 255, 255, 255)] * 145

    def read(self, f):
        self.header.read(f)
        self.colors = [uint8.read(f, 4) for _ in range(145)]

    def write(self, f):
        self.header.write(f)
        for value in self.colors: uint8.write(f, value, 4)


class MCCV:
    def __init__(self):
        self.header = ChunkHeader('VCCM', 580)
        self.colors = [(255, 255, 255, 255)] * 145

    def read(self, f):
        self.header.read(f)
        self.colors = [uint8.read(f, 4) for _ in range(145)]

    def write(self, f):
        self.header.write(f)
        for value in self.colors: uint8.write(f, value, 4)


class MCNR:
    def __init__(self):
        self.header = ChunkHeader('RNCM', 435 if CLIENT_VERSION <= WoWVersions.WOTLK else 448)
        self.normals = [(0, 0, 0)] * 145

    def read(self, f):
        self.header.read(f)
        self.normals = [int8.read(f, 3) for _ in range(145)]
        f.skip(13)

    def write(self, f):
        self.header.write(f)
        for normal in self.normals: int8.write(f, normal, 3)
        f.skip(13)  # TODO: write original data here


class MCLYLayer:
    def __init__(self):
        self.texture_id = 0
        self.flags = 0
        self.offset_in_mcal = 0
        self.effect_id = 0

    def read(self, f):
        self.texture_id = uint32.read(f)
        self.flags = uint32.read(f)
        self.offset_in_mcal = uint32.read(f)
        self.effect_id = uint32.read(f)

    def write(self, f):
        uint32.write(f, self.texture_id)
        uint32.write(f, self.flags)
        uint32.write(f, self.offset_in_mcal)
        uint32.write(f, self.effect_id)


class MCLY:
    def __init__(self):
        self.header = ChunkHeader('YLCM')
        self.layers = []

    def read(self, f):
        self.header.read(f)

        for _ in range(self.header.size // 16):
            layer = MCLYLayer()
            layer.read(f)
            self.layers.append(layer)

    def write(self, f):
        self.header.size = len(self.layers * 16)
        self.header.write(f)

        for layer in self.layers:
            layer.write(f)


class MCRF:
    def __init__(self):
        self.header = ChunkHeader('MCRF')
        self.doodad_refs = []
        self.object_refs = []

    def read(self, f, n_doodad_refs, n_object_refs):
        self.header.read(f)
        self.doodad_refs = [uint32.read(f) for _ in range(n_doodad_refs)]
        self.object_refs = [uint32.read(f) for _ in range(n_object_refs)]

    def write(self, f):
        n_doodad_refs = len(self.doodad_refs)
        n_object_refs = len(self.object_refs)
        self.header.size = n_doodad_refs * 4 + n_object_refs * 4
        self.header.write(f)

        uint32.write(f, self.doodad_refs, n_doodad_refs)
        uint32.write(f, self.object_refs, n_object_refs)


class MCSH:
    def __init__(self):
        self.header = ChunkHeader('HSCM', 512)
        self.shadow_map = [[0 for _ in range(64)] for _ in range(64)]

    def read(self, f):
        self.header.read(f)
        f.skip(512)  # TODO: implement

    def write(self, f):
        self.header.write(f)
        f.skip(512)


class MCAL:
    def __init__(self, type):
        self.header = ChunkHeader('LACM')
        self.type = type
        self.alpha_map = [[0 for _ in range(64)] for _ in range(64)]

    def read(self, f):
        if self.type in (ADTAlphaTypes.LOWRES, ADTAlphaTypes.BROKEN):
            cur_pos = 0
            alpha_map_flat = [0] * 4096

            for i in range(2048):
                cur_byte = uint8.read(f)
                nibble1 = cur_byte & 0x0F
                nibble2 = (cur_byte & 0xF0) >> 4

                first = nibble1 * 255 // 15
                second = nibble2 * 255 // 15

                alpha_map_flat[i + cur_pos + 0] = first
                alpha_map_flat[i + cur_pos + 1] = second
                cur_pos += 1

            self.alpha_map = [[alpha_map_flat[i * j] for i in range(64)] for j in range(64)]

            if self.type == ADTAlphaTypes.BROKEN:
                for row in self.alpha_map:
                    row[63] = row[62]

                for i, column in enumerate(self.alpha_map[62]):
                    self.alpha_map[63][i] = column

        elif self.type == ADTAlphaTypes.HIGHRES:
            self.alpha_map = [[uint8.read(f) for _ in range(64)] for _ in range(64)]

        elif self.type == ADTAlphaTypes.HIGHRES_COMPRESSED:
            alpha_map_flat = [0] * 4096
            alpha_offset = 0

            while alpha_offset < 4096:
                cur_byte = uint8.read(f)
                mode = bool(cur_byte >> 7)
                count = cur_byte & 0b1111111

                if mode:  # fill
                    alpha = uint8.read(f)
                    for i in range(count):
                        alpha_map_flat[alpha_offset] = alpha
                        alpha_offset += 1
                else:  # copy
                    for i in range(count):
                        alpha_map_flat[alpha_offset] = uint8.read(f)
                        alpha_offset += 1

    def write(self, f):
        if self.type in (ADTAlphaTypes.LOWRES, ADTAlphaTypes.BROKEN):
            self.header.size = 2048
            self.header.write(f)

            alpha_map_flat = []
            for row in self.alpha_map:
                for value in row:
                    alpha_map_flat.append(value)

            for i in range(0, 4096, 2):
                nibble1 = alpha_map_flat[i] // (255 // 15)
                nibble2 = alpha_map_flat[i + 1] // (255 // 15)
                uint8.write(f, nibble1 + (nibble2 << 4))

        elif self.type == ADTAlphaTypes.HIGHRES:
            self.header.size = 4096
            self.header.write(f)

            for row in self.alpha_map:
                for value in row:
                    uint8.write(f, value)

        elif self.type == ADTAlphaTypes.HIGHRES_COMPRESSED:

            alpha_map_flat = []
            for row in self.alpha_map:
                for value in row:
                    alpha_map_flat.append(value)

            class Cache:
                def __init__(self, pos=0, val=256):
                    self.reset_pos(pos)
                    self.reset_val(val)

                def reset_pos(self, pos):
                    self.pos = pos
                    self.stride = 1

                def reset_val(self, val):
                    self.val = val
                    self.count = 1

                def dump(self, file, mode=None, container=None):
                    mode = mode if mode is not None else self.count > 1

                    if not (mode or container):
                        return False

                    count = (self.count if mode else self.stride - 1) & 0x7F
                    uint8.write(file, mode * 0x80 | count)

                    if mode:
                        uint8.write(file, self.val)
                    else:
                        for j in range(self.pos, self.pos + count):
                            uint8.write(file, container[j])

                    return True

            cache = Cache(0, alpha_map_flat[0])

            for pos, val in enumerate(alpha_map_flat, 1):
                if not (pos % 64):
                    cache.dump(f, container=alpha_map_flat)
                    cache.reset_pos(pos)
                    cache.reset_val(val)
                    continue

                if cache.val != val:
                    if cache.count > 1:
                        cache.dump(f, True)
                        cache.reset_pos(pos)
                    else:
                        cache.stride += 1

                    cache.reset_val(val)
                else:
                    if cache.count == 1 and cache.stride > 1:
                        cache.dump(f, False, alpha_map_flat)

                    cache.count += 1

            cache.dump(f, container=alpha_map_flat)















































