from typing import List, Tuple
from .wow_common_types import *


###########################
# WMO GROUP
###########################

class MOGPFlags:
    HasCollision = 0x1
    HasVertexColor = 0x4
    Outdoor = 0x8
    DoNotUseLocalLighting = 0x40
    HasLight = 0x200
    HasDoodads = 0x800
    HasWater = 0x1000
    Indoor = 0x2000
    AlwaysDraw = 0x10000
    HasSkybox = 0x40000
    IsNotOcean = 0x80000
    IsMountAllowed = 0x200000
    HasTwoMOCV = 0x1000000
    HasTwoMOTV = 0x2000000


# contain WMO group header
class MOGP(ContentChunk):
    def __init__(self):
        super().__init__()
        self.group_name_ofs = 0
        self.desc_group_name_ofs = 0
        self.flags = 0
        self.bounding_box_corner1 = (0, 0, 0)
        self.bounding_box_corner2 = (0, 0, 0)
        self.portal_start = 0
        self.portal_count = 0
        self.n_batches_a = 0
        self.n_batches_b = 0
        self.n_batches_c = 0
        self.n_batches_d = 0
        self.fog_indices = (0, 0, 0, 0)
        self.liquid_type = 0
        self.group_id = 0
        self.unknown1 = 0
        self.unknown2 = 0

    def read(self, f):
        super().read(f)
        self.group_name_ofs = uint32.read(f)
        self.desc_group_name_ofs = uint32.read(f)
        self.flags = uint32.read(f)
        self.bounding_box_corner1 = vec3D.read(f)
        self.bounding_box_corner2 = vec3D.read(f)
        self.portal_start = uint16.read(f)
        self.portal_count = uint16.read(f)
        self.n_batches_a = uint16.read(f)
        self.n_batches_b = uint16.read(f)
        self.n_batches_c = uint16.read(f)
        self.n_batches_d = uint16.read(f)
        self.fog_indices = uint8.read(f, 4)
        self.liquid_type = uint32.read(f)
        self.group_id = uint32.read(f)
        self.unknown1 = uint32.read(f)
        self.unknown2 = uint32.read(f)

        return self

    def write(self, f):
        super().write(f)

        uint32.write(f, self.group_name_ofs)
        uint32.write(f, self.desc_group_name_ofs)
        uint32.write(f, self.flags)
        vec3D.write(f, self.bounding_box_corner1)
        vec3D.write(f, self.bounding_box_corner2)
        uint16.write(f, self.portal_start)
        uint16.write(f, self.portal_count)
        uint16.write(f, self.n_batches_a)
        uint16.write(f, self.n_batches_b)
        uint16.write(f, self.n_batches_c)
        uint16.write(f, self.n_batches_d)
        uint8.write(f, self.fog_indices, 4)
        uint32.write(f, self.liquid_type)
        uint32.write(f, self.group_id)
        uint32.write(f, self.unknown1)
        uint32.write(f, self.unknown2)

        return self


class TriangleMaterial:
    """ Material information """

    def __init__(self):
        self.flags = 0
        self.material_id = 0

    def read(self, f):
        self.flags = uint8.read(f)
        self.material_id = uint8.read(f)

        return self

    def write(self, f):
        uint8.write(f, self.flags)
        uint8.write(f, self.material_id)

        return self

    @staticmethod
    def size():
        return 2


class MOPY(ArrayChunk):
    """ Contains list of triangle materials. One for each triangle """

    item = TriangleMaterial
    data = 'triangle_materials'
    triangle_materials: List[TriangleMaterial]


class MOVI(ArrayChunk):
    """ Triangle Indices """

    item = uint16
    data = 'indices'
    indices: List[int]


class MOVT(ArrayChunk):
    """ Vertices """

    item = vec3D
    data = 'vertices'
    vertices: List[Tuple[float, float, float]]


class MONR(ArrayChunk):
    """ Normals """

    item = vec3D
    data = 'normals'
    normals: List[Tuple[float, float, float]]


class MOTV(ArrayChunk):
    """ Texture coordinates """

    item = float32, float32
    data = 'tex_coords'
    tex_coords: List[Tuple[float, float]]


class Batch:
    def __init__(self):
        self.bounding_box = (0, 0, 0, 0, 0, 0)
        self.start_triangle = 0
        self.n_triangles = 0
        self.start_vertex = 0
        self.last_vertex = 0
        self.unknown = 0
        self.material_id = 0

    def read(self, f):
        self.bounding_box = int16.read(f, 6)
        self.start_triangle = uint32.read(f)
        self.n_triangles = uint16.read(f)
        self.start_vertex = uint16.read(f)
        self.last_vertex = uint16.read(f)
        self.unknown = uint8.read(f)
        self.material_id = uint8.read(f)

        return self

    def write(self, f):
        int16.write(f, self.bounding_box, 6)
        uint32.write(f, self.start_triangle)
        uint16.write(f, self.n_triangles)
        uint16.write(f, self.start_vertex)
        uint16.write(f, self.last_vertex)
        uint8.write(f, self.unknown)
        uint8.write(f, self.material_id)

        return self

    @staticmethod
    def size():
        return 24


class MOBA(ArrayChunk):
    """ Batches """

    item = Batch
    data = 'batches'
    batches: List[Batch]


class MOLR(ArrayChunk):
    """ Lights """

    item = int16
    data = 'light_refs'
    light_refs: List[int]


class MODR(ArrayChunk):
    """ Doodads """

    item = int16
    data = 'doodad_refs'
    doodad_refs: List[int]


class BSPPlaneType:
    YZ_plane = 0
    XZ_plane = 1
    XY_plane = 2
    Leaf = 4  # end node, contains polygons


class BSPNode:
    def __init__(self):
        self.plane_type = 0
        self.children = (0, 0)
        self.num_faces = 0
        self.first_face = 0
        self.dist = 0

    def read(self, f):
        self.plane_type = int16.read(f)
        self.children = int16.read(f, 2)
        self.num_faces = uint16.read(f)
        self.first_face = uint32.read(f)
        self.dist = float32.read(f)

        return self

    def write(self, f):
        int16.write(f, self.plane_type)
        int16.write(f, self.children, 2)
        uint16.write(f, self.num_faces)
        uint32.write(f, self.first_face)
        float32.write(f, self.dist)

        return self


    @staticmethod
    def size():
        return 16


class MOBN(ArrayChunk):
    """ Collision geometry """

    item = BSPNode
    data = 'nodes'
    nodes: List[BSPNode]


class MOBR(ArrayChunk):

    item = uint16
    data = 'faces'
    faces: List[uint16]


class MOCV(ArrayChunk):
    """ Vertex colors """

    item = uint8, uint8, uint8, uint8
    data = 'vert_colors'
    vert_colors: List[Tuple[int, int, int, int]]


class LiquidVertex:
    def __init__(self):
        self.is_water = True
        self.height = 0

        # water
        self.flow1 = 0
        self.flow2 = 0
        self.flow1_pct = 0
        self.filler = 0

        # magma
        self.u = 0
        self.v = 0

    def read(self, f):
        pos = f.tell()

        self.flow1 = uint8.read(f)
        self.flow2 = uint8.read(f)
        self.flow1_pct = uint8.read(f)
        self.filler = uint8.read(f)

        f.seek(pos)

        self.u = int16.read(f)
        self.v = int16.read(f)

        self.height = float32.read(f)

        return self

    def write(self, f):
        if self.is_water:
            uint8.write(f, self.flow1)
            uint8.write(f, self.flow2)
            uint8.write(f, self.flow1_pct)
            uint8.write(f, self.filler)
        else:
            int16.write(f, self.u)
            int16.write(f, self.v)

        float32.write(f, self.height)

        return self


class MLIQ(ContentChunkBuffered):
    """ Liquid """

    def __init__(self):
        super().__init__()
        self.x_verts = 0
        self.y_verts = 0
        self.x_tiles = 0
        self.y_tiles = 0
        self.position = (0, 0, 0)
        self.material_id = 0
        self.vertex_map = []
        self.tile_flags = []
        self.is_water = True

    def read(self, f):
        super().read(f)
        self.x_verts = uint32.read(f)
        self.y_verts = uint32.read(f)
        self.x_tiles = uint32.read(f)
        self.y_tiles = uint32.read(f)
        self.position = vec3D.read(f)
        self.material_id = uint16.read(f)

        self.vertex_map = []

        for i in range(self.x_verts * self.y_verts):
            vtx = LiquidVertex()
            vtx.read(f)
            self.vertex_map.append(vtx)

        self.tile_flags = []

        # 0x40 = visible
        # 0x0C = invisible
        # well some other strange things (e.g 0x7F = visible, etc...)

        for i in range(self.x_tiles * self.y_tiles):
            self.tile_flags.append(uint8.read(f))

        return self

    def write(self, f):
        self.size = 30 + self.x_verts * self.y_verts * 8 + self.x_tiles * self.y_tiles
        super().write(f)

        uint32.write(f, self.x_verts)
        uint32.write(f, self.y_verts)
        uint32.write(f, self.x_tiles)
        uint32.write(f, self.y_tiles)
        vec3D.write(f, self.position)
        uint16.write(f, self.material_id)

        for vtx in self.vertex_map:
            vtx.is_water = self.is_water
            vtx.write(f)

        for tile_flag in self.tile_flags:
            uint8.write(f, tile_flag)

        return self


#############################################################
######                 Legion Chunks                   ######
#############################################################

'''
class MOPB:
    def __init__(self, size):
        self.header = ChunkHeader(magic='BPOM')
        self.size = size
        self.map_objects_prepass_batches = []

    def read(self, f):
        self.map_objects_prepass_batches = []
        for i in range(self.size // 24):
            self.map_objects_prepass_batches.append(char.read(f))

    def write(self, f):
        self.size = len(self.map_objects_prepass_batches) * 24
        super().write(f)

        for val in self.map_objects_prepass_batches:
            char.write(f, val)


class MOLS:
    def __init__(self, size):
        self.header = ChunkHeader(magic='SLOM')
        self.size = size
        self.map_object_spot_lights = []

    def read(self, f):
        self.map_object_spot_lights = []
        for i in range(self.size // 56):
            self.map_object_spot_lights.append(char.read(f))

    def write(self, f):
        self.size = len(self.map_object_spot_lights) * 56
        super().write(f)

        for val in self.map_object_spot_lights:
            char.write(f, val)
'''


class MapObjectPointLight:
    def __init__(self):
        self.unk = 0
        self.color = CImVector()
        self.pos = (0, 0, 0)
        self.intensity = 0.0
        self.attenuation_start = 0.0
        self.attenuation_end = 0.0
        self.unk4 = 0.0
        self.unk5 = 0
        self.unk6 = 0

    def read(self, f):
        self.unk = uint32.read(f)
        self.color.read(f)
        self.pos = vec3D.read(f)
        self.intensity = float32.read(f)
        self.attenuation_start = float32.read(f)
        self.attenuation_end = float32.read(f)
        self.unk4 = float32.read(f)
        self.unk5 = uint32.read(f)
        self.unk6 = uint32.read(f)

        return self

    def write(self, f):
        uint32.write(f, self.unk)
        self.color.write(f)
        vec3D.write(f, self.pos)
        float32.write(f, self.intensity)
        float32.write(f, self.attenuation_start)
        float32.write(f, self.attenuation_end)
        float32.write(f, self.unk4)
        uint32.write(f, self.unk5)
        uint32.write(f, self.unk6)

        return self

    @staticmethod
    def size():
        return 44


class MOLP(ArrayChunk):

    item = MapObjectPointLight
    data = 'map_object_point_lights'
    vert_map_object_point_lightscolors: List[MapObjectPointLight]


#############################################################
######                 Cata Chunks                     ######
#############################################################

class MORB(ContentChunk):
    def __init__(self, size=8):
        super().__init__()
        self.start_index = 0
        self.index_count = 0

    def read(self, f):
        super().read(f)
        self.start_index = uint32.read(f)
        self.index_count = uint16.read(f)
        f.skip(2)

        return self


    def write(self, f):
        self.size = 8
        super().write(f)
        uint32.write(f, self.start_index)
        uint16.write(f, self.index_count)
        uint16.write(f, 0)

        return self


'''
class MOTA:
    """ Map Object Tangent Array """

    def __init__(self, size, moba_count=0, accumulated_num_indices=0):  # TODO: check wiki
        self.header = ChunkHeader(magic='ATOM')
        self.size = size
        self.first_index = []

        self.moba_count = moba_count
        self.accumulated_num_indices = accumulated_num_indices

    def read(self, f):
        self.first_index = []

        for i in range(self.moba_count):
            self.first_index.append(uint16.read(f))

        for i in range(self.accumulated_num_indices):
            self.first_index.append(uint16.read(f))

    def write(self, f):
        self.size = len(self.first_index) * 2
        super().write(f)

        for val in self.first_index:
            uint16.write(f, val)


class MOBS:
    def __init__(self, size):
        self.header = ChunkHeader(magic='SBOM')
        self.size = size
        self.map_object_shadow_batches = []

    def read(self, f):
        self.map_object_shadow_batches = []
        for i in range(self.size // 24):
            self.map_object_shadow_batches.append(int8.read(f))

    def write(self, f):
        self.size = len(self.map_object_shadow_batches) * 24
        super().write(f)

        for val in self.map_object_shadow_batches:
            int8.write(f, val)

'''


#############################################################
######                 WoD Chunks                     ######
#############################################################

class MDAL(ContentChunk):
    def __init__(self):
        super().__init__()
        self.mdal = (0, 0, 0, 0)

    def read(self, f):
        super().read(f)
        self.mdal = uint8.read(f, 4)

        return self

    def write(self, f):
        self.size = 4
        super().write(f)

        uint8.write(f, self.mdal, 4)

        return self


class MOPL(ArrayChunk):

    item = C4Plane
    data = 'terrain_cutting_planes'
    terrain_cutting_planes: List[C4Plane]
