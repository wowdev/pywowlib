from typing import List, Tuple
from .wow_common_types import *


###########################
# WMO ROOT
###########################

class MOHD(ContentChunk):
    """ WMO Root header """

    def __init__(self):
        super().__init__()
        self.n_materials = 0
        self.n_groups = 0
        self.n_portals = 0
        self.n_lights = 0
        self.n_models = 0
        self.n_doodads = 0
        self.n_sets = 0
        self.ambient_color = (0, 0, 0, 0)
        self.id = 0
        self.bounding_box_corner1 = (0.0, 0.0, 0.0)
        self.bounding_box_corner2 = (0.0, 0.0, 0.0)
        self.flags = 0

    def read(self, f):
        super().read(f)
        self.n_materials = uint32.read(f)
        self.n_groups = uint32.read(f)
        self.n_portals = uint32.read(f)
        self.n_lights = uint32.read(f)
        self.n_models = uint32.read(f)
        self.n_doodads = uint32.read(f)
        self.n_sets = uint32.read(f)
        self.ambient_color = uint8.read(f, 4)
        self.id = uint32.read(f)
        self.bounding_box_corner1 = vec3D.read(f)
        self.bounding_box_corner2 = vec3D.read(f)
        self.flags = uint32.read(f)

        return self

    def write(self, f):
        self.size = 64
        super().write(f)
        uint32.write(f, self.n_materials)
        uint32.write(f, self.n_groups)
        uint32.write(f, self.n_portals)
        uint32.write(f, self.n_lights)
        uint32.write(f, self.n_models)
        uint32.write(f, self.n_doodads)
        uint32.write(f, self.n_sets)
        uint8.write(f, self.ambient_color, 4)
        uint32.write(f, self.id)
        vec3D.write(f, self.bounding_box_corner1)
        vec3D.write(f, self.bounding_box_corner2)
        uint32.write(f, self.flags)

        return self


class MOTX(ContentChunk):
    """ Texture names """

    def __init__(self):
        super().__init__()
        self.string_table = bytearray()
        self.string_table.append(0)

    def read(self, f):
        super().read(f)
        self.string_table = f.read(self.size)

        return self

    def write(self, f):
        self.size = len(self.string_table)
        super().write(f)

        f.write(self.string_table)

        return self

    def add_string(self, s : str):
        padding = len(self.string_table) % 4
        if padding > 0:
            for iPad in range(4 - padding):
                self.string_table.append(0)

        ofs = len(self.string_table)
        self.string_table.extend(s.encode('ascii'))
        self.string_table.append(0)
        return ofs

    def get_string(self, ofs : int):
        if ofs >= len(self.string_table):
            return ''
        start = ofs
        i = ofs
        while self.string_table[i] != 0:
            i += 1
        return self.string_table[start:i].decode('ascii')

    def get_all_strings(self):
        strings = []
        cur_str = ""

        for byte in self.string_table:
            if byte:
                cur_str += chr(byte)
            elif cur_str:
                strings.append(cur_str)
                cur_str = ""

        return strings


class WMOMaterial:

    def __init__(self):
        self.flags = 0
        self.shader = 0
        self.blend_mode = 0
        self.texture1_ofs = 0
        self.emissive_color = (0, 0, 0, 0)
        self.sidn_emissive_color = (0, 0, 0, 0)
        self.texture2_ofs = 0
        self.diff_color = (0, 0, 0, 0)
        self.terrain_type = 0
        self.texture3_ofs = 0
        self.color3 = (0, 0, 0, 0)
        self.tex3_flags = 0
        self.runtime_data = (0, 0, 0, 0)

    def read(self, f):
        self.flags = uint32.read(f)
        self.shader = uint32.read(f)
        self.blend_mode = uint32.read(f)
        self.texture1_ofs = uint32.read(f)
        self.emissive_color = uint8.read(f, 4)
        self.sidn_emissive_color = uint8.read(f, 4)
        self.texture2_ofs = uint32.read(f)
        self.diff_color = uint8.read(f, 4)
        self.terrain_type = uint32.read(f)
        self.texture3_ofs = uint32.read(f)
        self.color3 = uint8.read(f, 4)
        self.tex3_flags = uint32.read(f)
        self.runtime_data = uint32.read(f, 4)

        return self

    def write(self, f):
        uint32.write(f, self.flags)
        uint32.write(f, self.shader)
        uint32.write(f, self.blend_mode)
        uint32.write(f, self.texture1_ofs)
        uint8.write(f, self.emissive_color, 4)
        uint8.write(f, self.sidn_emissive_color, 4)
        uint32.write(f, self.texture2_ofs)
        uint8.write(f, self.diff_color, 4)
        uint32.write(f, self.terrain_type)
        uint32.write(f, self.texture3_ofs)
        uint8.write(f, self.color3, 4)
        uint32.write(f, self.tex3_flags)
        uint32.write(f, self.runtime_data, 4)

        return self

    @staticmethod
    def size():
        return 64


class MOMT(ArrayChunk):
    """ Materials """

    item = WMOMaterial
    data = "materials"
    materials: List[WMOMaterial]


class MOGN(ContentChunk):
    """ Group names """

    def __init__(self):
        super().__init__()
        self.string_table = bytearray(b'\x00\x00')

    def read(self, f):
        super().read(f)
        self.string_table = f.read(self.size)

        return self

    def write(self, f):

        self.size = len(self.string_table)
        super().write(f)

        f.write(self.string_table)

        return self

    def add_string(self, s):
        ofs = len(self.string_table)
        self.string_table.extend(s.encode('ascii'))
        self.string_table.extend(b'\x00')
        return ofs

    def get_string(self, ofs):
        if ofs >= len(self.string_table):
            return ''
        start = ofs
        i = ofs
        while self.string_table[i] != 0:
            i += 1
        return self.string_table[start:i].decode('ascii')


class GroupInfo:
    def __init__(self):
        self.flags = 0
        self.bounding_box_corner1 = (0, 0, 0)
        self.bounding_box_corner2 = (0, 0, 0)
        self.name_ofs = 0

    def read(self, f):
        self.flags = uint32.read(f)
        self.bounding_box_corner1 = vec3D.read(f)
        self.bounding_box_corner2 = vec3D.read(f)
        self.name_ofs = uint32.read(f)

        return self

    def write(self, f):
        uint32.write(f, self.flags)
        vec3D.write(f, self.bounding_box_corner1)
        vec3D.write(f, self.bounding_box_corner2)
        uint32.write(f, self.name_ofs)

        return self

    @staticmethod
    def size():
        return 32


class MOGI(ArrayChunk):
    """ Group informations """

    item = GroupInfo
    data = "infos"
    infos: List[GroupInfo]


class MOSB(ContentChunk):
    """ Skybox """
    def __init__(self, size=0):
        super().__init__()
        self.size = size
        self.skybox = ''

    def read(self, f):
        super().read(f)
        self.skybox = f.read(self.size).decode('ascii')

        return self

    def write(self, f):

        if not self.skybox:
            self.skybox = '\x00\x00\x00'

        self.size = len(self.skybox) + 1
        super().write(f)

        f.write(self.skybox.encode('ascii') + b'\x00')

        return self


class MOPV(ArrayChunk):
    """ Portal vertices """

    item = vec3D
    data = 'portal_vertices'
    portal_vertices: List[Tuple[float, float, float]]


class PortalInfo:
    def __init__(self):
        self.start_vertex = 0
        self.n_vertices = 0
        self.normal = (0, 0, 0)
        self.unknown = 0

    def read(self, f):
        self.start_vertex = uint16.read(f)
        self.n_vertices = uint16.read(f)
        self.normal = vec3D.read(f)
        self.unknown = float32.read(f)

        return self

    def write(self, f):
        uint16.write(f, self.start_vertex)
        uint16.write(f, self.n_vertices)
        vec3D.write(f, self.normal)
        float32.write(f, self.unknown)

        return self

    @staticmethod
    def size():
        return 20


# portal infos
class MOPT(ArrayChunk):

    item = PortalInfo
    data = 'infos'
    infos: List[PortalInfo]


class PortalRelation:
    def __init__(self):
        self.portal_index = 0
        self.group_index = 0
        self.side = 0
        self.padding = 0

    def read(self, f):
        self.portal_index = uint16.read(f)
        self.group_index = uint16.read(f)
        self.side = int16.read(f)
        self.padding = uint16.read(f)

        return self

    def write(self, f):
        uint16.write(f, self.portal_index)
        uint16.write(f, self.group_index)
        int16.write(f, self.side)
        uint16.write(f, self.padding)

        return self

    @staticmethod
    def size():
        return 8


class MOPR(ArrayChunk):
    """ Portal relations """

    item = PortalRelation
    data = 'relations'
    relations: List[PortalRelation]


class MOVV(ArrayChunk):
    """ Visible vertices """

    item = vec3D
    data = 'visible_vertices'
    visible_vertices: List[Tuple[float, float, float]]


class VisibleBatch:
    def __init__(self):
        self.start_vertex = 0
        self.n_vertices = 0

    def read(self, f):
        self.start_vertex = uint16.read(f)
        self.n_vertices = uint16.read(f)

        return self

    def write(self, f):
        uint16.write(f, self.start_vertex)
        uint16.write(f, self.n_vertices)

        return self

    @staticmethod
    def size():
        return 4


class MOVB(ArrayChunk):
    """ Visible batches """

    item = VisibleBatch
    data = 'batches'
    batches: List[VisibleBatch]


class Light:
    def __init__(self):
        self.light_type = 0
        self.type = 1
        self.use_attenuation = 1
        self.padding = 1
        self.color = (0, 0, 0, 0)
        self.position = (0, 0, 0)
        self.intensity = 0
        self.attenuation_start = 0
        self.attenuation_end = 0
        self.unknown1 = 0
        self.unknown2 = 0
        self.unknown3 = 0
        self.unknown4 = 0

    def read(self, f):
        self.light_type = uint8.read(f)
        self.type = uint8.read(f)
        self.use_attenuation = uint8.read(f)
        self.padding = uint8.read(f)
        self.color = uint8.read(f, 4)
        self.position = vec3D.read(f)
        self.intensity = float32.read(f)
        self.attenuation_start = float32.read(f)
        self.attenuation_end = float32.read(f)
        self.unknown1 = float32.read(f)
        self.unknown2 = float32.read(f)
        self.unknown3 = float32.read(f)
        self.unknown4 = float32.read(f)

        return self

    def write(self, f):
        uint8.write(f, self.light_type)
        uint8.write(f, self.type)
        uint8.write(f, self.use_attenuation)
        uint8.write(f, self.padding)
        uint8.write(f, self.color, 4)
        vec3D.write(f, self.position)
        float32.write(f, self.intensity)
        float32.write(f, self.attenuation_start)
        float32.write(f, self.attenuation_end)
        float32.write(f, self.unknown1)
        float32.write(f, self.unknown2)
        float32.write(f, self.unknown3)
        float32.write(f, self.unknown4)

        return self

    @staticmethod
    def size():
        return 48


class MOLT(ArrayChunk):
    """ Lights """

    item = Light
    data = 'lights'
    lights: List[Light]


class DoodadSet:
    def __init__(self):
        self.name = ''
        self.start_doodad = 0
        self.n_doodads = 0
        self.padding = 0

    def read(self, f):
        self.name = f.read(20).decode("ascii")
        self.start_doodad = uint32.read(f)
        self.n_doodads = uint32.read(f)
        self.padding = uint32.read(f)

        return self

    def write(self, f):
        f.write(self.name.ljust(20, '\0').encode('ascii'))
        uint32.write(f, self.start_doodad)
        uint32.write(f, self.n_doodads)
        uint32.write(f, self.padding)

        return self

    @staticmethod
    def size():
        return 32


class MODS(ArrayChunk):
    """ Doodad sets """

    item = DoodadSet
    data = 'sets'
    sets: List[DoodadSet]


class MODN(ContentChunk):
    """ Doodad names """

    def __init__(self):
        super().__init__()
        self.string_table = bytearray()

    def read(self, f):
        super().read(f)
        self.string_table = f.read(self.size)

        return self

    def write(self, f):
        self.size = len(self.string_table)

        super().write(f)
        f.write(self.string_table)

        return self

    def add_string(self, s):
        padding = len(self.string_table) % 4
        if padding > 0:
            for iPad in range(4 - padding):
                self.string_table.append(0)

        ofs = len(self.string_table)
        self.string_table.extend(s.encode('ascii'))
        self.string_table.append(0)
        return ofs

    def get_string(self, ofs):
        if ofs >= len(self.string_table):
            return ''
        start = ofs
        i = ofs
        while self.string_table[i] != 0:
            i += 1
        return self.string_table[start:i].decode('ascii')

    def get_all_strings(self):
        strings = []
        cur_str = ""

        for byte in self.string_table:
            if byte:
                cur_str += chr(byte)
            elif cur_str:
                strings.append(cur_str)
                cur_str = ""

        return strings


class DoodadDefinition:
    def __init__(self):
        self.name_ofs = 0
        self.flags = 0
        self.position = (0, 0, 0)
        self.rotation = [0, 0, 0, 0]
        self.scale = 0
        self.color = [0, 0, 0, 0]

    def read(self, f):
        weird_thing = uint32.read(f)
        self.name_ofs = weird_thing & 0xFFFFFF
        self.flags = (weird_thing >> 24) & 0xFF
        self.position = vec3D.read(f)
        self.rotation = float32.read(f, 4)
        self.scale = float32.read(f)
        self.color = uint8.read(f, 4)

        return self

    def write(self, f):
        weird_thing = ((self.flags & 0xFF) << 24) | (self.name_ofs & 0xFFFFFF)
        uint32.write(f, weird_thing)
        vec3D.write(f, self.position)
        float32.write(f, self.rotation, 4)
        float32.write(f, self.scale)
        uint8.write(f, self.color, 4)

        return self


    @staticmethod
    def size():
        return 40


class MODD(ArrayChunk):
    """ Doodad definition """

    item = DoodadDefinition
    data = 'definitions'
    definitions: List[DoodadDefinition]


class Fog:
    def __init__(self):
        self.flags = 0
        self.position = (0, 0, 0)
        self.small_radius = 0
        self.big_radius = 0
        self.end_dist = 0
        self.start_factor = 0
        self.color1 = (0, 0, 0, 0)
        self.end_dist2 = 0
        self.start_factor2 = 0
        self.color2 = (0, 0, 0, 0)

    def read(self, f):
        self.flags = uint32.read(f)
        self.position = vec3D.read(f)
        self.small_radius = float32.read(f)
        self.big_radius = float32.read(f)
        self.end_dist = float32.read(f)
        self.start_factor = float32.read(f)
        self.color1 = uint8.read(f, 4)
        self.end_dist2 = float32.read(f)
        self.start_factor2 = float32.read(f)
        self.color2 = uint8.read(f, 4)

        return self

    def write(self, f):
        uint32.write(f, self.flags)
        vec3D.write(f, self.position)
        float32.write(f, self.small_radius)
        float32.write(f, self.big_radius)
        float32.write(f, self.end_dist)
        float32.write(f, self.start_factor)
        uint8.write(f, self.color1, 4)
        float32.write(f, self.end_dist2)
        float32.write(f, self.start_factor2)
        uint8.write(f, self.color2, 4)

        return self

    @staticmethod
    def size():
        return 48


class MFOG(ArrayChunk):
    """ Fogs """

    item = Fog
    data = 'fogs'
    fogs: List[Fog]


class MCVP(ArrayChunk):
    """ Convex volume plane, used only for transport objects """

    item = quat
    data = 'convex_volume_planes'
    convex_volume_planes: List[Tuple[float, float, float, float]]


#############################################################
######                 Legion Chunks                   ######
#############################################################


class GFID(ContentChunk):

    group_file_data_ids: List[List[int]]

    def __init__(self, use_lods=False, n_groups=0, n_lods=0):
        super().__init__()
        self.group_file_data_ids = [[]] if not use_lods else [[] for _ in range(n_lods)]

        self.n_groups = n_groups
        self.n_lods = n_lods
        self.use_lods = use_lods

    def read(self, f):
        super().read(f)
        self.group_file_data_ids = [[]] if not self.use_lods else [[] for _ in range(self.n_lods)]

        for i in range(self.n_groups):
            for _ in range(self.n_groups):
                self.group_file_data_ids[i].append(uint32.read(f))

        return self

    def write(self, f):
        self.size = len(self.group_file_data_ids) * self.n_groups * 4
        super().write(f)

        for lod_level in self.group_file_data_ids:
            for val in lod_level:
                uint32.write(f, val)

        return self


class MOUV(ArrayChunk):

    item = vec2D
    data = 'map_object_uv'
    map_object_uv: List[Tuple[float, float]]


#############################################################
######                 BfA Chunks                      ######
#############################################################

######                >= 8.1 only!                     ######


class MOSI(ContentChunk):

    def __init__(self):
        super().__init__()
        self.skybox_file_id = 0

    def read(self, f):
        super().read(f)
        self.skybox_file_id = uint32.read(f)

        return self

    def write(self, f):
        self.size = 4
        super().write(f)
        uint32.write(f, self.skybox_file_id)

        return self


class MODI(ArrayChunk):

    item = uint32
    data = 'doodad_file_ids'
    doodad_file_ids: List[int]
