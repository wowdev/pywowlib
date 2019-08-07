from typing import List, Tuple
from .wow_common_types import *


###########################
# WMO ROOT
###########################

class MOHD:
    """ WMO Root header """

    def __init__(self, size=64):
        self.header = ChunkHeader(magic='DHOM')
        self.header.size = size
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

    def write(self, f):
        self.header.write(f)
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


class MOTX:
    """ Texture names """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='XTOM')
        self.header.size = size
        self.string_table = bytearray()

    def read(self, f):
        self.string_table = f.read(self.header.size)

    def write(self, f):
        self.header.size = len(self.string_table)
        self.header.write(f)

        f.write(self.string_table)

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


class MOMT:
    """ Materials """

    materials: List[WMOMaterial]

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='TMOM')
        self.header.size = size
        self.materials = []

    def read(self, f):
        self.materials = []
        for i in range(self.header.size // 64):
            mat = WMOMaterial()
            mat.read(f)
            self.materials.append(mat)

    def write(self, f):
        self.header.size = len(self.materials) * 64
        self.header.write(f)

        for mat in self.materials:
            mat.write(f)


class MOGN:
    """ Group names """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='NGOM')
        self.header.size = size
        self.string_table = bytearray(b'\x00\x00')

    def read(self, f):
        self.string_table = f.read(self.header.size)

    def write(self, f):

        self.header.size = len(self.string_table)
        self.header.write(f)

        f.write(self.string_table)

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

    def write(self, f):
        uint32.write(f, self.flags)
        vec3D.write(f, self.bounding_box_corner1)
        vec3D.write(f, self.bounding_box_corner2)
        uint32.write(f, self.name_ofs)


class MOGI:
    """ Group informations """

    infos: List[GroupInfo]

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='IGOM')
        self.header.size = size
        self.infos = []

    def read(self, f):
        count = self.header.size // 32

        self.infos = []
        for i in range(count):
            info = GroupInfo()
            info.read(f)
            self.infos.append(info)

    def write(self, f):
        self.header.size = len(self.infos) * 32
        self.header.write(f)

        for info in self.infos:
            info.write(f)


class MOSB:
    """ Skybox """
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='BSOM')
        self.header.size = size
        self.skybox = ''

    def read(self, f):
        self.skybox = f.read(self.header.size).decode('ascii')

    def write(self, f):

        if not self.skybox:
            self.skybox = '\x00\x00\x00'

        self.header.size = len(self.skybox) + 1
        self.header.write(f)

        f.write(self.skybox.encode('ascii') + b'\x00')


class MOPV:
    """ Portal vertices """

    portal_vertices: List[Tuple[float, float, float]]

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='VPOM')
        self.header.size = size
        self.portal_vertices = []

    def read(self, f):
        count = self.header.size // 12
        self.portal_vertices = []

        # 12 = sizeof(float) * 3
        for i in range(count):
            self.portal_vertices.append(vec3D.read(f))

    def write(self, f):
        self.header.size = len(self.portal_vertices) * 12
        self.header.write(f)

        for v in self.portal_vertices:
            vec3D.write(f, v)


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

    def write(self, f):
        uint16.write(f, self.start_vertex)
        uint16.write(f, self.n_vertices)
        vec3D.write(f, self.normal)
        float32.write(f, self.unknown)


# portal infos
class MOPT:

    infos: List[PortalInfo]

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='TPOM')
        self.header.size = size
        self.infos = []

    def read(self, f):
        self.infos = []

        # 20 = sizeof(PortalInfo)
        for i in range(self.header.size // 20):
            info = PortalInfo()
            info.read(f)
            self.infos.append(info)

    def write(self, f):
        self.header.size = len(self.infos) * 20
        self.header.write(f)

        for info in self.infos:
            info.write(f)


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

    def write(self, f):
        uint16.write(f, self.portal_index)
        uint16.write(f, self.group_index)
        int16.write(f, self.side)
        uint16.write(f, self.padding)


class MOPR:
    """ Portal relations """

    relations: List[PortalRelation]

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='RPOM')
        self.header.size = size
        self.relations = []

    def read(self, f):
        self.relations = []

        for i in range(self.header.size // 8):
            relation = PortalRelation()
            relation.read(f)
            self.relations.append(relation)

    def write(self, f):
        self.header.size = len(self.relations) * 8
        self.header.write(f)

        for relation in self.relations:
            relation.write(f)


class MOVV:
    """ Visible vertices """

    visible_vertices: List[Tuple[float, float, float]]

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='VVOM')
        self.header.size = size
        self.visible_vertices = []

    def read(self, f):
        self.visible_vertices = []

        for i in range(self.header.size // 12):
            self.visible_vertices.append(vec3D.read(f))

    def write(self, f):
        self.header.size = len(self.visible_vertices) * 12
        self.header.write(f)

        for v in self.visible_vertices:
            vec3D.write(f, v)


class VisibleBatch:
    def __init__(self):
        self.start_vertex = 0
        self.n_vertices = 0

    def read(self, f):
        self.start_vertex = uint16.read(f)
        self.n_vertices = uint16.read(f)

    def write(self, f):
        uint16.write(f, self.start_vertex)
        uint16.write(f, self.n_vertices)


class MOVB:
    """ Visible batches """

    batches: List[VisibleBatch]

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='BVOM')
        self.header.size = size
        self.batches = []

    def read(self, f):
        count = self.header.size // 4

        self.batches = []

        for i in range(count):
            batch = VisibleBatch()
            batch.read(f)
            self.batches.append(batch)

    def write(self, f):
        self.header.size = len(self.batches) * 4
        self.header.write(f)

        for batch in self.batches:
            batch.write(f)


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


class MOLT:
    """ Lights """

    lights: List[Light]

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='TLOM')
        self.header.size = size
        self.lights = []

    def read(self, f):
        # 48 = sizeof(Light)
        count = self.header.size // 48

        self.lights = []
        for i in range(count):
            light = Light()
            light.read(f)
            self.lights.append(light)

    def write(self, f):
        self.header.size = len(self.lights) * 48
        self.header.write(f)

        for light in self.lights:
            light.write(f)


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

    def write(self, f):
        f.write(self.name.ljust(20, '\0').encode('ascii'))
        uint32.write(f, self.start_doodad)
        uint32.write(f, self.n_doodads)
        uint32.write(f, self.padding)



class MODS:
    """ Doodad sets """

    sets: List[DoodadSet]

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='SDOM')
        self.header.size = size
        self.sets = []

    def read(self, f):
        count = self.header.size // 32

        self.sets = []

        for i in range(count):
            d_set = DoodadSet()
            d_set.read(f)
            self.sets.append(d_set)

    def write(self, f):
        self.header.size = len(self.sets) * 32

        self.header.write(f)
        for set in self.sets:
            set.write(f)


class MODN:
    """ Doodad names """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='NDOM')
        self.header.size = size
        self.string_table = bytearray()

    def read(self, f):
        self.string_table = f.read(self.header.size)

    def write(self, f):
        self.header.size = len(self.string_table)

        self.header.write(f)
        f.write(self.string_table)

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

    def write(self, f):
        weird_thing = ((self.flags & 0xFF) << 24) | (self.name_ofs & 0xFFFFFF)
        uint32.write(f, weird_thing)
        vec3D.write(f, self.position)
        float32.write(f, self.rotation, 4)
        float32.write(f, self.scale)
        uint8.write(f, self.color, 4)


class MODD:
    """ Doodad definition """

    definitions: List[DoodadDefinition]

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='DDOM')
        self.header.size = size
        self.definitions = []

    def read(self, f):
        count = self.header.size // 40

        self.definitions = []
        for i in range(count):
            defi = DoodadDefinition()
            defi.read(f)
            self.definitions.append(defi)

    def write(self, f):
        self.header.size = len(self.definitions) * 40
        self.header.write(f)

        for defi in self.definitions:
            defi.write(f)


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


class MFOG:
    """ Fogs """

    fogs: List[Fog]

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='GOFM')
        self.header.size = size
        self.fogs = []

    def read(self, f):
        count = self.header.size // 48

        self.fogs = []
        for i in range(count):
            fog = Fog()
            fog.read(f)
            self.fogs.append(fog)

    def write(self, f):
        self.header.size = len(self.fogs) * 48
        self.header.write(f)

        for fog in self.fogs:
            fog.write(f)


class MCVP:
    """ Convex volume plane, used only for transport objects """

    convex_volume_planes: List[Tuple[float, float, float, float]]

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='PVCM')
        self.header.size = size
        self.convex_volume_planes = []

    def read(self, f):
        count = self.header.size // 16

        for i in range(0, count):
            self.convex_volume_planes.append(unpack('ffff', f.read(16)))

    def write(self, f):
        self.header.size = len(self.convex_volume_planes) * 16
        self.header.write(f)

        for i in self.convex_volume_planes:
            float32.write(f, self.convex_volume_planes[i], 4)


#############################################################
######                 Legion Chunks                   ######
#############################################################


class GFID:

    group_file_data_ids: List[List[int]]

    def __init__(self, size=0, use_lods=False, n_groups=0, n_lods=0):
        self.header = ChunkHeader(magic='DIFG')
        self.header.size = size
        self.group_file_data_ids = [[]] if not use_lods else [[] for _ in range(n_lods)]

        self.n_groups = n_groups
        self.n_lods = n_lods
        self.use_lods = use_lods

    def read(self, f):
        self.group_file_data_ids = [[]] if not self.use_lods else [[] for _ in range(self.n_lods)]

        for i in range(self.n_groups):
            for _ in range(self.n_groups):
                self.group_file_data_ids[i].append(uint32.read(f))

    def write(self, f):
        self.header.size = len(self.group_file_data_ids) * self.n_groups * 4
        self.header.write(f)

        for lod_level in self.group_file_data_ids:
            for val in lod_level:
                uint32.write(f, val)


class MOUV:

    map_object_uv: List[Tuple[float, float]]

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='VUOM')
        self.header.size = size
        self.map_object_uv = []

    def read(self, f):
        self.map_object_uv = []

        for _ in range(self.header.size // 8):
            self.map_object_uv.append(vec2D.read(f, 2))

    def write(self, f):
        self.header.size = len(self.map_object_uv) * 8
        self.header.write(f)

        for val in self.map_object_uv:
            vec2D.write(f, val, 2)


#############################################################
######                 BfA Chunks                      ######
#############################################################

######                >= 8.1 only!                     ######


class MOSI:
    def __init__(self, size=4):
        self.header = ChunkHeader(magic='ISOM')
        self.header.size = size
        self.skybox_file_id = 0

    def read(self, f):
        self.skybox_file_id = uint32.read(f)

    def write(self, f):
        self.header.size = 4
        self.header.write(f)
        uint32.write(f, self.skybox_file_id)


class MODI:

    doodad_file_ids: List[int]

    def __init__(self, size):
        self.header = ChunkHeader(magic='IDOM')
        self.header.size = size
        self.doodad_file_ids = []

    def read(self, f):
        self.doodad_file_ids = []

        for i in range(len(self.doodad_file_ids)):
            self.doodad_file_ids.append(uint32.read(f))

    def write(self, f):
        self.header.size = len(self.doodad_file_ids) * 4
        self.header.write(f)

        for val in self.doodad_file_ids:
            uint32.write(f, val)

