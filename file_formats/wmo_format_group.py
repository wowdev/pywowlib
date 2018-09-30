from struct import pack, unpack
from .wow_common_types import ChunkHeader, MVER


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
        self.group_name_ofs = unpack("I", f.read(4))[0]
        self.desc_group_name_ofs = unpack("I", f.read(4))[0]
        self.flags = unpack("I", f.read(4))[0]
        self.bounding_box_corner1 = unpack("fff", f.read(12))
        self.bounding_box_corner2 = unpack("fff", f.read(12))
        self.portal_start = unpack("H", f.read(2))[0]
        self.portal_count = unpack("H", f.read(2))[0]
        self.n_batches_a = unpack("H", f.read(2))[0]
        self.n_batches_b = unpack("H", f.read(2))[0]
        self.n_batches_c = unpack("H", f.read(2))[0]
        self.n_batches_d = unpack("H", f.read(2))[0]
        self.fog_indices = unpack("BBBB", f.read(4))
        self.liquid_type = unpack("I", f.read(4))[0]
        self.group_id = unpack("I", f.read(4))[0]
        self.unknown1 = unpack("I", f.read(4))[0]
        self.unknown2 = unpack("I", f.read(4))[0]

    def write(self, f):
        self.header.write(f)

        f.write(pack('I', self.group_name_ofs))
        f.write(pack('I', self.desc_group_name_ofs))
        f.write(pack('I', self.flags))
        f.write(pack('fff', *self.bounding_box_corner1))
        f.write(pack('fff', *self.bounding_box_corner2))
        f.write(pack('H', self.portal_start))
        f.write(pack('H', self.portal_count))
        f.write(pack('H', self.n_batches_a))
        f.write(pack('H', self.n_batches_b))
        f.write(pack('H', self.n_batches_c))
        f.write(pack('H', self.n_batches_d))
        f.write(pack('BBBB', *self.fog_indices))
        f.write(pack('I', self.liquid_type))
        f.write(pack('I', self.group_id))
        f.write(pack('I', self.unknown1))
        f.write(pack('I', self.unknown2))


class TriangleMaterial:
    """ Material information """

    def __init__(self):
        self.flags = 0
        self.material_id = 0

    def read(self, f):
        self.flags = unpack("B", f.read(1))[0]
        self.material_id = unpack("B", f.read(1))[0]

    def write(self, f):
        f.write(pack('B', self.flags))
        f.write(pack('B', self.material_id))


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
            self.indices.append(unpack("H", f.read(2))[0])

    def write(self, f):
        self.header.size = len(self.indices) * 2
        self.header.write(f)

        for i in self.indices:
            f.write(pack('H', i))


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
            self.vertices.append(unpack("fff", f.read(12)))

    def write(self, f):
        self.header.size = len(self.vertices) * 12
        self.header.write(f)

        for v in self.vertices:
            f.write(pack('fff', *v))


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
            self.normals.append(unpack("fff", f.read(12)))

    def write(self, f):
        self.header.size = len(self.normals) * 12
        self.header.write(f)

        for n in self.normals:
            f.write(pack('fff', *n))


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
            self.tex_coords.append(unpack("ff", f.read(8)))

    def write(self, f):
        self.header.size = len(self.tex_coords) * 8
        self.header.write(f)

        for tc in self.tex_coords:
            f.write(pack('ff', *tc))


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
        self.bounding_box = unpack("hhhhhh", f.read(12))
        self.start_triangle = unpack("I", f.read(4))[0]
        self.n_triangles = unpack("H", f.read(2))[0]
        self.start_vertex = unpack("H", f.read(2))[0]
        self.last_vertex = unpack("H", f.read(2))[0]
        self.unknown = unpack("B", f.read(1))[0]
        self.material_id = unpack("B", f.read(1))[0]

    def write(self, f):
        f.write(pack('hhhhhh', *self.bounding_box))
        f.write(pack('I', self.start_triangle))
        f.write(pack('H', self.n_triangles))
        f.write(pack('H', self.start_vertex))
        f.write(pack('H', self.last_vertex))
        f.write(pack('B', self.unknown))
        f.write(pack('B', self.material_id))


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
            self.light_refs.append(unpack("h", f.read(2))[0])

    def write(self, f):
        self.header.size = len(self.light_refs) * 2

        self.header.write(f)
        for lr in self.light_refs:
            f.write(pack('h', lr))


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
            self.doodad_refs.append(unpack("h", f.read(2))[0])

    def write(self, f):
        self.header.size = len(self.doodad_refs) * 2
        self.header.write(f)

        for dr in self.doodad_refs:
            f.write(pack('h', dr))


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
        self.plane_type = unpack("h", f.read(2))[0]
        self.children = unpack("hh", f.read(4))
        self.num_faces = unpack("H", f.read(2))[0]
        self.first_face = unpack("I", f.read(4))[0]
        self.dist = unpack("f", f.read(4))[0]

    def write(self, f):
        f.write(pack('h', self.plane_type))
        f.write(pack('hh', *self.children))
        f.write(pack('H', self.num_faces))
        f.write(pack('I', self.first_face))
        f.write(pack('f', self.dist))


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
            self.faces.append(unpack("H", f.read(2))[0])

    def write(self, f):
        self.header.size = len(self.faces) * 2
        self.header.write(f)

        for face in self.faces:
            f.write(pack('H', face))


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
            self.vert_colors.append(unpack("BBBB", f.read(4)))

    def write(self, f):
        self.header.size = len(self.vert_colors) * 4
        self.header.write(f)

        for vc in self.vert_colors:
            f.write(pack('BBBB', *vc))


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

        self.flow1 = unpack("B", f.read(1))[0]
        self.flow2 = unpack("B", f.read(1))[0]
        self.flow1_pct = unpack("B", f.read(1))[0]
        self.filler = unpack("B", f.read(1))[0]

        f.seek(pos)

        self.u = unpack("h", f.read(2))[0]
        self.v = unpack("h", f.read(2))[0]

        self.height = unpack("f", f.read(4))

    def write(self, f):
        if self.is_water:
            f.write(pack('B', self.flow1))
            f.write(pack('B', self.flow2))
            f.write(pack('B', self.flow1_pct))
            f.write(pack('B', self.filler))
        else:
            f.write(pack('h', self.u))
            f.write(pack('h', self.v))

        f.write(pack('f', self.height))


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
        self.x_verts = unpack("I", f.read(4))[0]
        self.y_verts = unpack("I", f.read(4))[0]
        self.x_tiles = unpack("I", f.read(4))[0]
        self.y_tiles = unpack("I", f.read(4))[0]
        self.position = unpack("fff", f.read(12))
        self.material_id = unpack("H", f.read(2))[0]

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
            self.tile_flags.append(unpack("B", f.read(1))[0])

    def write(self, f):
        self.header.size = 30 + self.x_verts * self.y_verts * 8 + self.x_tiles * self.y_tiles
        self.header.write(f)

        f.write(pack('I', self.x_verts))
        f.write(pack('I', self.y_verts))
        f.write(pack('I', self.x_tiles))
        f.write(pack('I', self.y_tiles))
        f.write(pack('fff', *self.position))
        f.write(pack('H', self.material_id))

        for vtx in self.vertex_map:
            vtx.is_water = self.is_water
            vtx.write(f)

        for tile_flag in self.tile_flags:
            f.write(pack('B', tile_flag))


