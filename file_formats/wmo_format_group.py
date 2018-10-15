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
class MOGP:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='PGOM')
        self.header.size = size
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

    def write(self, f):
        self.header.write(f)

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


class TriangleMaterial:
    """ Material information """

    def __init__(self):
        self.flags = 0
        self.material_id = 0

    def read(self, f):
        self.flags = uint8.read(f)
        self.material_id = uint8.read(f)

    def write(self, f):
        uint8.write(f, self.flags)
        uint8.write(f, self.material_id)


class MOPY:
    """ Contains list of triangle materials. One for each triangle """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='YPOM')
        self.header.size = size
        self.triangle_materials = []

    def read(self, f):
        count = self.header.size // 2

        self.triangle_materials = []

        for i in range(count):
            tri = TriangleMaterial()
            tri.read(f)
            self.triangle_materials.append(tri)

    def write(self, f):
        self.header.size = len(self.triangle_materials) * 2
        self.header.write(f)

        for tri in self.triangle_materials:
            tri.write(f)


class MOVI:
    """ Triangle Indices """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='IVOM')
        self.header.size = size
        self.indices = []

    def read(self, f):
        # 2 = sizeof(unsigned short)
        count = self.header.size // 2

        self.indices = []

        for i in range(count):
            self.indices.append(uint16.read(f))

    def write(self, f):
        self.header.size = len(self.indices) * 2
        self.header.write(f)

        for i in self.indices:
            uint16.write(f, i)


class MOVT:
    """ Vertices """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='TVOM')
        self.header.size = size
        self.vertices = []

    def read(self, f):

        # 4 * 3 = sizeof(float) * 3
        count = self.header.size // (4 * 3)

        self.vertices = []

        for i in range(count):
            self.vertices.append(vec3D.read(f))

    def write(self, f):
        self.header.size = len(self.vertices) * 12
        self.header.write(f)

        for v in self.vertices:
            vec3D.write(f, v)


class MONR:
    """ Normals """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='RNOM')
        self.header.size = size
        self.normals = []

    def read(self, f):
        # 4 * 3 = sizeof(float) * 3
        count = self.header.size // (4 * 3)

        self.normals = []

        for i in range(count):
            self.normals.append(vec3D.read(f))

    def write(self, f):
        self.header.size = len(self.normals) * 12
        self.header.write(f)

        for n in self.normals:
            vec3D.write(f, n)


class MOTV:
    """ Texture coordinates """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='VTOM')
        self.header.size = size
        self.tex_coords = []

    def read(self, f):
        # 4 * 2 = sizeof(float) * 2
        count = self.header.size // (4 * 2)

        self.tex_coords = []

        for i in range(count):
            self.tex_coords.append(float32.read(f, 2))

    def write(self, f):
        self.header.size = len(self.tex_coords) * 8
        self.header.write(f)

        for tc in self.tex_coords:
            float32.write(f, tc, 2)


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

    def write(self, f):
        int16.write(f, self.bounding_box, 6)
        uint32.write(f, self.start_triangle)
        uint16.write(f, self.n_triangles)
        uint16.write(f, self.start_vertex)
        uint16.write(f, self.last_vertex)
        uint8.write(f, self.unknown)
        uint8.write(f, self.material_id)


class MOBA:
    """ Batches """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='ABOM')
        self.header.size = size
        self.batches = []

    def read(self, f):
        count = self.header.size // 24

        self.batches = []

        for i in range(count):
            batch = Batch()
            batch.read(f)
            self.batches.append(batch)

    def write(self, f):
        self.header.size = len(self.batches) * 24
        self.header.write(f)

        for b in self.batches:
            b.write(f)


class MOLR:
    """ Lights """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='RLOM')
        self.header.size = size
        self.light_refs = []

    def read(self, f):
        # 2 = sizeof(short)
        count = self.header.size // 2

        self.light_refs = []

        for i in range(count):
            self.light_refs.append(int16.read(f))

    def write(self, f):
        self.header.size = len(self.light_refs) * 2

        self.header.write(f)
        for lr in self.light_refs:
            int16.write(f, lr)


class MODR:
    """ Doodads """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='RDOM')
        self.header.size = size
        self.doodad_refs = []

    def read(self, f):
        # 2 = sizeof(short)
        count = self.header.size // 2

        self.doodad_refs = []

        for i in range(count):
            self.doodad_refs.append(int16.read(f))

    def write(self, f):
        self.header.size = len(self.doodad_refs) * 2
        self.header.write(f)

        for dr in self.doodad_refs:
            int16.write(f, dr)


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

    def write(self, f):
        int16.write(f, self.plane_type)
        int16.write(f, self.children, 2)
        uint16.write(f, self.num_faces)
        uint32.write(f, self.first_face)
        float32.write(f, self.dist)


class MOBN:
    """ Collision geometry """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='NBOM')
        self.header.size = size
        self.nodes = []

    def read(self, f):
        count = self.header.size // 0x10

        self.nodes = []

        for i in range(count):
            node = BSPNode()
            node.read(f)
            self.nodes.append(node)

    def write(self, f):
        self.header.size = len(self.nodes) * 0x10

        self.header.write(f)
        for node in self.nodes:
            node.write(f)


class MOBR:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='RBOM')
        self.header.size = size
        self.faces = []

    def read(self, f):
        count = self.header.size // 2

        self.faces = []

        for i in range(count):
            self.faces.append(uint16.read(f))

    def write(self, f):
        self.header.size = len(self.faces) * 2
        self.header.write(f)

        for face in self.faces:
            uint16.write(f, face)


class MOCV:
    """ Vertex colors """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='VCOM')
        self.header.size = size
        self.vert_colors = []

    def read(self, f):
        # 4 = sizeof(unsigned char) * 4
        count = self.header.size // 4

        self.vert_colors = []

        for i in range(count):
            self.vert_colors.append(uint8.read(f, 4))

    def write(self, f):
        self.header.size = len(self.vert_colors) * 4
        self.header.write(f)

        for vc in self.vert_colors:
            uint8.write(f, vc, 4)


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


class MLIQ:
    """ Liquid """

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='QILM')
        self.header.size = size
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

    def write(self, f):
        self.header.size = 30 + self.x_verts * self.y_verts * 8 + self.x_tiles * self.y_tiles
        self.header.write(f)

        uint32.write(f, self.x_verts)
        uint32.write(f, self.y_verts)
        uint32.write(f, self.x_tiles)
        uint32.write(f, self.y_tiles)
        vec3D.write(f, *self.position)
        uint16.write(f, self.material_id)

        for vtx in self.vertex_map:
            vtx.is_water = self.is_water
            vtx.write(f)

        for tile_flag in self.tile_flags:
            uint8.write(f, tile_flag)


#############################################################
######                 Legion Chunks                   ######
#############################################################

'''
class MOPB:
    def __init__(self, size):
        self.header = ChunkHeader(magic='BPOM')
        self.header.size = size
        self.map_objects_prepass_batches = []

    def read(self, f):
        self.map_objects_prepass_batches = []
        for i in range(self.header.size // 24):
            self.map_objects_prepass_batches.append(char.read(f))

    def write(self, f):
        self.header.size = len(self.map_objects_prepass_batches) * 24
        self.header.write(f)

        for val in self.map_objects_prepass_batches:
            char.write(f, val)


class MOLS:
    def __init__(self, size):
        self.header = ChunkHeader(magic='SLOM')
        self.header.size = size
        self.map_object_spot_lights = []

    def read(self, f):
        self.map_object_spot_lights = []
        for i in range(self.header.size // 56):
            self.map_object_spot_lights.append(char.read(f))

    def write(self, f):
        self.header.size = len(self.map_object_spot_lights) * 56
        self.header.write(f)

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


class MOLP:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='PLOM')
        self.header.size = size
        self.map_object_point_lights = []

    def read(self, f):
        for _ in range(self.header.size // 44):
            mopl = MapObjectPointLight()
            mopl.read(f)
            self.map_object_point_lights.append(mopl)

    def write(self, f):
        self.header.size = len(self.map_object_point_lights) * 44
        self.header.write(f)

        for val in self.map_object_point_lights:
            val.write(f)


#############################################################
######                 Cata Chunks                     ######
#############################################################

class MORB:
    def __init__(self, size=8):
        self.header = ChunkHeader(magic='BROM')
        self.header.size = size
        self.start_index = 0
        self.index_count = 0

    def read(self, f):
        self.start_index = uint32.read(f)
        self.index_count = uint16.read(f)
        f.skip(2)

    def write(self, f):
        self.header.size = 8
        self.header.write(f)
        uint32.write(f, self.start_index)
        uint16.write(f, self.index_count)
        uint16.write(f, 0)


'''
class MOTA:
    """ Map Object Tangent Array """

    def __init__(self, size, moba_count=0, accumulated_num_indices=0):  # TODO: check wiki
        self.header = ChunkHeader(magic='ATOM')
        self.header.size = size
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
        self.header.size = len(self.first_index) * 2
        self.header.write(f)

        for val in self.first_index:
            uint16.write(f, val)


class MOBS:
    def __init__(self, size):
        self.header = ChunkHeader(magic='SBOM')
        self.header.size = size
        self.map_object_shadow_batches = []

    def read(self, f):
        self.map_object_shadow_batches = []
        for i in range(self.header.size // 24):
            self.map_object_shadow_batches.append(int8.read(f))

    def write(self, f):
        self.header.size = len(self.map_object_shadow_batches) * 24
        self.header.write(f)

        for val in self.map_object_shadow_batches:
            int8.write(f, val)

'''

#############################################################
######                 WoD Chunks                     ######
#############################################################

class MDAL:
    def __init__(self, size=4):
        self.header = ChunkHeader(magic='LADM')
        self.header.size = size
        self.mdal = (0, 0, 0, 0)

    def read(self, f):
        self.mdal = uint8.read(f, 4)

    def write(self, f):
        self.header.size = 4
        self.header.write(f)

        uint8.write(f, self.mdal, 4)


class MOPL:
    def __init__(self, size=0):
        self.header = ChunkHeader(magic='LPOM')
        self.header.size = size
        self.terrain_cutting_planes = []

    def read(self, f):
        for _ in range(self.header.size // 16):
            self.terrain_cutting_planes.append(C4Plane().read(f))

    def write(self, f):
        n_planes = len(self.terrain_cutting_planes)

        if n_planes > 32:
            raise OverflowError("\nMax. number of cutting planes is 32.")

        self.header.size = len(self.terrain_cutting_planes) * 16
        self.header.write(f)

        for val in self.terrain_cutting_planes:
            val.write(f)
