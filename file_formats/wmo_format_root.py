from struct import pack, unpack
from .wow_common_types import ChunkHeader, MVER


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
        self.n_materials = unpack("I", f.read(4))[0]
        self.n_groups = unpack("I", f.read(4))[0]
        self.n_portals = unpack("I", f.read(4))[0]
        self.n_lights = unpack("I", f.read(4))[0]
        self.n_models = unpack("I", f.read(4))[0]
        self.n_doodads = unpack("I", f.read(4))[0]
        self.n_sets = unpack("I", f.read(4))[0]
        self.ambient_color = unpack("BBBB", f.read(4))
        self.id = unpack("I", f.read(4))[0]
        self.bounding_box_corner1 = unpack("fff", f.read(12))
        self.bounding_box_corner2 = unpack("fff", f.read(12))
        self.flags = unpack("I", f.read(4))[0]

    def write(self, f):
        self.header.write(f)
        f.write(pack('I', self.n_materials))
        f.write(pack('I', self.n_groups))
        f.write(pack('I', self.n_portals))
        f.write(pack('I', self.n_lights))
        f.write(pack('I', self.n_models))
        f.write(pack('I', self.n_doodads))
        f.write(pack('I', self.n_sets))
        f.write(pack('BBBB', *self.ambient_color))
        f.write(pack('I', self.id))
        f.write(pack('fff', *self.bounding_box_corner1))
        f.write(pack('fff', *self.bounding_box_corner2))
        f.write(pack('I', self.flags))


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
        self.flags = unpack("I", f.read(4))[0]
        self.shader = unpack("I", f.read(4))[0]
        self.blend_mode = unpack("I", f.read(4))[0]
        self.texture1_ofs = unpack("I", f.read(4))[0]
        self.emissive_color = unpack("BBBB", f.read(4))
        self.sidn_emissive_color = unpack("BBBB", f.read(4))
        self.texture2_ofs = unpack("I", f.read(4))[0]
        self.diff_color = unpack("BBBB", f.read(4))
        self.terrain_type = unpack("I", f.read(4))[0]
        self.texture3_ofs = unpack("I", f.read(4))[0]
        self.color3 = unpack("BBBB", f.read(4))
        self.tex3_flags = unpack("I", f.read(4))[0]
        self.runtime_data = unpack("IIII", f.read(16))[0]

    def write(self, f):
        f.write(pack('I', self.flags))
        f.write(pack('I', self.shader))
        f.write(pack('I', self.blend_mode))
        f.write(pack('I', self.texture1_ofs))
        f.write(pack('BBBB', *self.emissive_color))
        f.write(pack('BBBB', *self.sidn_emissive_color))
        f.write(pack('I', self.texture2_ofs))
        f.write(pack('BBBB', *self.diff_color))
        f.write(pack('I', self.terrain_type))
        f.write(pack('I', self.texture3_ofs))
        f.write(pack('BBBB', *self.color3))
        f.write(pack('I', self.tex3_flags))
        f.write(pack('IIII', *self.runtime_data))


class MOMT:
    """ Materials """

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

        # padd 4 bytes after
        padding = len(self.string_table) % 4
        if padding > 0:
            for i_pad in range(4 - padding):
                self.string_table.append(0)

        self.header.size = len(self.string_table)
        self.header.write(f)

        f.write(self.string_table)

    def add_string(self, s):
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


class GroupInfo:
    def __init__(self):
        self.flags = 0
        self.bounding_box_corner1 = (0, 0, 0)
        self.bounding_box_corner2 = (0, 0, 0)
        self.name_ofs = 0

    def read(self, f):
        self.flags = unpack("I", f.read(4))[0]
        self.bounding_box_corner1 = unpack("fff", f.read(12))
        self.bounding_box_corner2 = unpack("fff", f.read(12))
        self.name_ofs = unpack("I", f.read(4))[0]

    def write(self, f):
        f.write(pack('I', self.flags))
        f.write(pack('fff', *self.bounding_box_corner1))
        f.write(pack('fff', *self.bounding_box_corner2))
        f.write(pack('I', self.name_ofs))


class MOGI:
    """ Group informations """

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

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='VPOM')
        self.header.size = size
        self.portal_vertices = []

    def read(self, f):
        count = self.header.size // 12
        self.portal_vertices = []

        # 12 = sizeof(float) * 3
        for i in range(count):
            self.portal_vertices.append(unpack("fff", f.read(12)))

    def write(self, f):
        self.header.size = len(self.portal_vertices) * 12
        self.header.write(f)

        for v in self.portal_vertices:
            f.write(pack('fff', *v))


class PortalInfo:
    def __init__(self):
        self.start_vertex = 0
        self.n_vertices = 0
        self.normal = (0, 0, 0)
        self.unknown = 0

    def read(self, f):
        self.start_vertex = unpack("H", f.read(2))[0]
        self.n_vertices = unpack("H", f.read(2))[0]
        self.normal = unpack("fff", f.read(12))
        self.unknown = unpack("f", f.read(4))[0]

    def write(self, f):
        f.write(pack('H', self.start_vertex))
        f.write(pack('H', self.n_vertices))
        f.write(pack('fff', *self.normal))
        f.write(pack('f', self.unknown))


# portal infos
class MOPT:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='REVM')
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
        self.portal_index = unpack("H", f.read(2))[0]
        self.group_index = unpack("H", f.read(2))[0]
        self.side = unpack("h", f.read(2))[0]
        self.padding = unpack("H", f.read(2))[0]

    def write(self, f):
        f.write(pack('H', self.portal_index))
        f.write(pack('H', self.group_index))
        f.write(pack('h', self.side))
        f.write(pack('H', self.padding))


class MOPR:
    """ Portal relations """

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

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='VVOM')
        self.header.size = size
        self.visible_vertices = []

    def read(self, f):
        self.visible_vertices = []

        for i in range(self.header.size // 12):
            self.visible_vertices.append(unpack("fff", f.read(12)))

    def write(self, f):
        self.header.size = len(self.visible_vertices) * 12
        self.header.write(f)

        for v in self.visible_vertices:
            f.write(pack('fff', *v))


class VisibleBatch:
    def __init__(self):
        self.start_vertex = 0
        self.n_vertices = 0

    def read(self, f):
        self.start_vertex = unpack("H", f.read(2))[0]
        self.n_vertices = unpack("H", f.read(2))[0]

    def write(self, f):
        f.write(pack('H', self.start_vertex))
        f.write(pack('H', self.n_vertices))


class MOVB:
    """ Visible batches """

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
        self.light_type = unpack("B", f.read(1))[0]
        self.type = unpack("B", f.read(1))[0]
        self.use_attenuation = unpack("B", f.read(1))[0]
        self.padding = unpack("B", f.read(1))[0]
        self.color = unpack("BBBB", f.read(4))
        self.position = unpack("fff", f.read(12))
        self.intensity = unpack("f", f.read(4))[0]
        self.attenuation_start = unpack("f", f.read(4))[0]
        self.attenuation_end = unpack("f", f.read(4))[0]
        self.unknown1 = unpack("f", f.read(4))[0]
        self.unknown2 = unpack("f", f.read(4))[0]
        self.unknown3 = unpack("f", f.read(4))[0]
        self.unknown4 = unpack("f", f.read(4))[0]

    def write(self, f):
        f.write(pack('B', self.light_type))
        f.write(pack('B', self.type))
        f.write(pack('B', self.use_attenuation))
        f.write(pack('B', self.padding))
        f.write(pack('BBBB', *self.color))
        f.write(pack('fff', *self.position))
        f.write(pack('f', self.intensity))
        f.write(pack('f', self.attenuation_start))
        f.write(pack('f', self.attenuation_end))
        f.write(pack('f', self.unknown1))
        f.write(pack('f', self.unknown2))
        f.write(pack('f', self.unknown3))
        f.write(pack('f', self.unknown4))


class MOLT:
    """ Lights """

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
        self.start_doodad = unpack("I", f.read(4))[0]
        self.n_doodads = unpack("I", f.read(4))[0]
        self.padding = unpack("I", f.read(4))[0]

    def write(self, f):
        f.write(self.name.ljust(20, '\0').encode('ascii'))
        f.write(pack('I', self.start_doodad))
        f.write(pack('I', self.n_doodads))
        f.write(pack('I', self.padding))


class MODS:
    """ Doodad sets """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='SDOM')
        self.header.size = size
        self.sets = []

    def read(self, f):
        count = self.header.size // 32

        self.sets = []

        for i in range(count):
            set = DoodadSet()
            set.read(f)
            self.sets.append(set)

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
        weird_thing = unpack("I", f.read(4))[0]
        self.name_ofs = weird_thing & 0xFFFFFF
        self.flags = (weird_thing >> 24) & 0xFF
        self.position = unpack("fff", f.read(12))
        self.rotation = unpack("ffff", f.read(16))
        self.scale = unpack("f", f.read(4))[0]
        self.color = unpack("BBBB", f.read(4))

    def write(self, f):
        weird_thing = ((self.flags & 0xFF) << 24) | (self.name_ofs & 0xFFFFFF)
        f.write(pack('I', weird_thing))
        f.write(pack('fff', *self.position))
        f.write(pack('ffff', *self.rotation))
        f.write(pack('f', self.scale))
        f.write(pack('BBBB', *self.color))


class MODD:
    """ Doodad definition """

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
        self.flags = unpack("I", f.read(4))[0]
        self.position = unpack("fff", f.read(12))
        self.small_radius = unpack("f", f.read(4))[0]
        self.big_radius = unpack("f", f.read(4))[0]
        self.end_dist = unpack("f", f.read(4))[0]
        self.start_factor = unpack("f", f.read(4))[0]
        self.color1 = unpack("BBBB", f.read(4))
        self.end_dist2 = unpack("f", f.read(4))[0]
        self.start_factor2 = unpack("f", f.read(4))[0]
        self.color2 = unpack("BBBB", f.read(4))

    def write(self, f):
        f.write(pack('I', self.flags))
        f.write(pack('fff', *self.position))
        f.write(pack('f', self.small_radius))
        f.write(pack('f', self.big_radius))
        f.write(pack('f', self.end_dist))
        f.write(pack('f', self.start_factor))
        f.write(pack('BBBB', *self.color1))
        f.write(pack('f', self.end_dist2))
        f.write(pack('f', self.start_factor2))
        f.write(pack('BBBB', *self.color2))


class MFOG:
    """ Fogs """

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
            f.write(pack('ffff', self.convex_volume_planes[i]))


