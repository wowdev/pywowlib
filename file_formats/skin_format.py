from .wow_common_types import *

__reload_order_index__ = 2

#############################################################
######                   M2 Skin                       ######
#############################################################

# Note: Before Wotlk it was written inside the .m2 file


class M2SkinSubmesh:
    
    def __init__(self):
        self.skin_section_id = 0                                # Mesh part ID, see below.
        self.level = 0                                          # (level << 16) is added (|ed) to startTriangle and alike to avoid having to increase those fields to uint32s.
        self.vertex_start = 0                                   # Starting vertex number.
        self.vertex_count = 0                                   # Number of vertices.
        self.index_start = 0                                    # Starting triangle index (that's 3* the number of triangles drawn so far).
        self.index_count = 0                                    # Number of triangle indices.
        self.bone_count = 0                                     # Number of elements in the bone lookup table. Max seems to be 256 in Wrath
        self.bone_combo_index = 0                               # Starting index in the bone lookup table.
        self.bone_influences = 0                                # <= 4 from <=BC documentation: Highest number of bones needed at one time in this Submesh --Tinyn (wowdev.org)
        self.center_bone_index = 0
        self.center_position = (0.0, 0.0, 0.0)                  # Average position of all the vertices in the sub mesh.

        if VERSION >= M2Versions.TBC:
            self.sort_ceter_position = (0.0, 0.0, 0.0)          # The center of the box when an axis aligned box is built around the vertices in the submesh.
            self.sort_radius = 0.0                              # Distance of the vertex farthest from CenterBoundingBox.
   
    def read(self, f):
        self.skin_section_id = uint16.read(f)
        self.level = uint16.read(f)
        self.vertex_start = uint16.read(f) + (self.level << 16)
        self.vertex_count = uint16.read(f)
        self.index_start = uint16.read(f) + (self.level << 16)
        self.index_count = uint16.read(f)
        self.bone_count = uint16.read(f)
        self.bone_combo_index = uint16.read(f)
        self.bone_influences = uint16.read(f)
        self.center_bone_index = uint16.read(f)
        self.center_position = vec3D.read(f)

        if VERSION >= M2Versions.TBC:
            self.sort_ceter_position = vec3D.read(f)
            self.sort_radius = float32.read(f)
            
        return self
        
    def write(self, f):
        uint16.write(f, self.skin_section_id)
        uint16.write(f, self.level)
        uint16.write(f, self.vertex_start)
        uint16.write(f, self.vertex_count)
        uint16.write(f, self.index_start)
        uint16.write(f, self.index_count)
        uint16.write(f, self.bone_count)
        uint16.write(f, self.bone_combo_index)
        uint16.write(f, self.bone_influences)
        uint16.write(f, self.center_bone_index)
        vec3D.write(f, self.center_position)

        if VERSION >= M2Versions.TBC:
            vec3D.write(f, self.sort_ceter_position)
            float32.write(f, self.sort_radius)

        return self


class M2SkinTextureUnit:
    def __init__(self):
        self.flags = 0
        self.priority_plane = 0
        self.shader_id = 0
        self.skin_section_index = 0
        self.geoset_index = 0
        self.color_index = -1
        self.material_index = 0
        self.material_layer = 0
        self.texture_count = 0
        self.texture_combo_index = 0
        self.texture_coord_combo_index = 0
        self.texture_weight_combo_index = 0
        self.texture_transform_combo_index = 0

    def read(self, f):
        self.flags = uint8.read(f)
        self.priority_plane = int8.read(f)
        self.shader_id = uint16.read(f)
        self.skin_section_index = uint16.read(f)
        self.geoset_index = uint16.read(f)
        self.color_index = int16.read(f)
        self.material_index = uint16.read(f)
        self.material_layer = uint16.read(f)
        self.texture_count = uint16.read(f)
        self.texture_combo_index = uint16.read(f)
        self.texture_coord_combo_index = uint16.read(f)
        self.texture_weight_combo_index = uint16.read(f)
        self.texture_transform_combo_index = uint16.read(f)

        return self

    def write(self, f):
        uint8.write(f, self.flags)
        int8.write(f, self.priority_plane)
        uint16.write(f, self.shader_id)
        uint16.write(f, self.skin_section_index)
        uint16.write(f, self.geoset_index)
        int16.write(f, self.color_index)
        uint16.write(f, self.material_index)
        uint16.write(f, self.material_layer)
        uint16.write(f, self.texture_count)
        uint16.write(f, self.texture_combo_index)
        uint16.write(f, self.texture_coord_combo_index)
        uint16.write(f, self.texture_weight_combo_index)
        uint16.write(f, self.texture_transform_combo_index)

        return self


class M2ShadowBatch:

    def __init__(self):
        self.flags = 0                                          # if auto-generated: M2Batch.flags & 0xFF
        self.flags2 = 0                                         # if auto-generated: (renderFlag[i].flags & 0x04 ? 0x01 : 0x00)
                                                                # (!renderFlag[i].blendingmode ? 0x02: 0x00)
                                                                # | (renderFlag[i].flags & 0x80 ? 0x04: 0x00)
                                                                # | (renderFlag[i].flags & 0x400 ? 0x06: 0x00)
        self._unknown1 = 0
        self.submesh_id = 0
        self.texture_id = 0
        self.color_id = 0
        self.transparency_id = 0

    def read(self, f):
        self.flags = uint8.read(f)
        self.flags2 = uint8.read(f)
        self._unknown1 = uint16.read(f)
        self.submesh_id = uint16.read(f)
        self.texture_id = uint16.read(f)
        self.color_id = uint16.read(f)
        self.transparency_id = uint16.read(f)

        return self

    def write(self, f):
        uint8.write(f, self.flags)
        uint8.write(f, self.flags2)
        uint16.write(f, self._unknown1)
        uint16.write(f, self.submesh_id)
        uint16.write(f, self.texture_id)
        uint16.write(f, self.color_id)
        uint16.write(f, self.transparency_id)
        return self


class M2SkinProfile:

    def __init__(self):
        self._size = 48 if VERSION >= M2Versions.WOTLK else 44

        if VERSION >= M2Versions.WOTLK:
            self.magic = 'SKIN'

        self.vertex_indices = M2Array(uint16)
        self.triangle_indices = M2Array(uint16)
        self.bone_indices = M2Array(Array << (uint8, 4))
        self.submeshes = M2Array(M2SkinSubmesh)
        self.texture_units = M2Array(M2SkinTextureUnit)
        self.bone_count_max = 0

        if VERSION >= M2Versions.CATA:
            self.shadow_batches = M2Array(M2ShadowBatch)
            self._size += 8

    def read(self, f):
        self.magic = f.read(4).decode('utf-8')
        self.vertex_indices.read(f)
        self.triangle_indices.read(f)
        self.bone_indices.read(f)
        self.submeshes.read(f)
        self.texture_units.read(f)
        self.bone_count_max = uint32.read(f)

        if VERSION >= M2Versions.CATA:
            self.shadow_batches.read(f)

        return self

    def write(self, f):
        MemoryManager.mem_reserve(f, self._size)

        f.write(self.magic.encode('ascii'))
        self.vertex_indices.write(f)
        self.triangle_indices.write(f)
        self.bone_indices.write(f)
        self.submeshes.write(f)
        self.texture_units.write(f)
        uint32.write(f, self.bone_count_max)

        if VERSION >= M2Versions.CATA:
            self.shadow_batches.write(f)

        return self









