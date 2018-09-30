import os

from itertools import chain
from .file_formats.m2_format import *
from .file_formats.skin_format import M2SkinProfile, M2SkinSubmesh, M2SkinTextureUnit

__reload_order_index__ = 3


class M2File:
    def __init__(self, version, filepath=None):
        self.version = version

        if filepath:
            self.filepath = filepath
            with open(filepath, 'rb') as f:
                self.root = M2Header()
                self.root.read(f)
                self.skins = []

                if version >= M2Versions.WOTLK:
                    # load skins

                    raw_path = os.path.splitext(filepath)[0]
                    for i in range(self.root.num_skin_profiles):
                        with open("{}{}.skin".format(raw_path, str(i).zfill(2)), 'rb') as skin_file:
                            self.skins.append(M2SkinProfile().read(skin_file))

                    track_cache = M2TrackCache()
                    # load anim files
                    for i, sequence in enumerate(self.root.sequences):

                        # handle alias animations
                        real_anim = sequence
                        a_idx = i
                        while real_anim.flags & 0x40 and real_anim.alias_next != a_idx:
                            a_idx = real_anim.alias_next
                            real_anim = self.root.sequences[real_anim.alias_next]

                        if not sequence.flags & 0x130:
                            anim_path = "{}{}-{}.anim".format(os.path.splitext(filepath)[0],
                                                              str(real_anim.id).zfill(4),
                                                              str(sequence.variation_index).zfill(2))

                            # TODO: implement game-data loading
                            anim_file = open(anim_path, 'rb')

                            for track in track_cache.m2_tracks:
                                if track.global_sequence < 0 and track.timestamps.n_elements > a_idx:
                                    frames = track.timestamps[a_idx]
                                    values = track.values[a_idx]

                                    timestamps = track.timestamps[i]
                                    timestamps.ofs_elements = frames.ofs_elements
                                    timestamps.n_elements = frames.n_elements
                                    timestamps.read(anim_file, ignore_header=True)

                                    frame_values = track.values[i]
                                    frame_values.ofs_elements = values.ofs_elements
                                    frame_values.n_elements = values.n_elements
                                    frame_values.read(anim_file, ignore_header=True)
                else:
                    self.skins = self.root.skin_profiles

        else:
            self.filepath = None
            self.root = M2Header()
            self.skins = [M2SkinProfile()]

    def write(self, filepath):
        with open(filepath, 'wb') as f:
            if self.version < M2Versions.WOTLK:
                self.root.skin_profiles = self.skins
            else:
                raw_path = os.path.splitext(filepath)[0]
                for i, skin in enumerate(self.skins):
                    with open("{}{}.skin".format(raw_path, str(i).zfill(2)), 'wb') as skin_file:
                        skin.write(skin_file)

            self.root.write(f)

            # TODO: anim, skel and phys

    def add_skin(self):
        skin = M2SkinProfile()
        self.skins.append(skin)
        return skin

    def add_vertex(self, pos, normal, tex_coords, bone_weights, bone_indices, tex_coords2=None):
        vertex = M2Vertex()
        vertex.pos = tuple(pos)
        vertex.normal = tuple(normal)
        vertex.tex_coords = tuple(tex_coords)

        # rigging information
        vertex.bone_weights = bone_weights
        vertex.bone_indices = bone_indices

        skin = self.skins[0]

        # handle optional properties
        if tex_coords2:
            vertex.tex_coords2 = tex_coords2

        vertex_index = self.root.vertices.add(vertex)
        skin.vertex_indices.append(vertex_index)
        return vertex_index

    def add_geoset(self, vertices, normals, uv, uv2, tris, b_indices, b_weights, origin, sort_pos, sort_radius, mesh_part_id):

        submesh = M2SkinSubmesh()
        texture_unit = M2SkinTextureUnit()
        skin = self.skins[0]

        # get max bone influences per vertex
        max_influences = 0
        for b_index_set, b_weight_set in zip(b_indices, b_weights):
            v_max_influences = 0
            for b_index, b_weight in zip(b_index_set, b_weight_set):
                if b_index != 0 or (b_index == 0 and b_weight != 0):
                    v_max_influences += 1

                if max_influences < v_max_influences:
                    max_influences = v_max_influences

        # localize bone indices
        unique_bone_ids = set(chain(*b_indices))

        bone_lookup = {}
        for bone_id in unique_bone_ids:
            bone_lookup[bone_id] = self.root.bone_lookup_table.add(bone_id)

        # add vertices
        start_index = len(self.root.vertices)
        for i, vertex_pos in enumerate(vertices):
            local_b_indices = tuple([bone_lookup[idx] for idx in b_indices[i]])
            args = [vertex_pos, normals[i], uv[i], b_weights[i], b_indices[i]]

            if uv2:
                args.append(uv2[i])

            self.add_vertex(*args)

            indices = skin.bone_indices.new()
            indices.values = b_indices[i]

        # found min bone index
        bone_min = None
        for index_set in b_indices:
            for index in index_set:
                if bone_min is None:
                    bone_min = index
                elif index < bone_min:
                    bone_min = index

        # found  max bone index
        bone_max = None
        for index_set in b_indices:
            for index in index_set:
                if bone_max is None:
                    bone_max = index
                elif index > bone_max:
                    bone_max = index

        submesh.bone_combo_index = bone_min
        submesh.bone_count = bone_max + 1
        submesh.bone_influences = max_influences

        submesh.vertex_start = start_index
        submesh.vertex_count = len(vertices)
        submesh.center_position = tuple(origin)

        if self.version >= M2Versions.TBC:
            submesh.sort_ceter_position = tuple(sort_pos)
            submesh.sort_radius = sort_radius

        submesh.skin_section_id = mesh_part_id
        submesh.index_start = len(skin.triangle_indices)
        submesh.index_count = len(tris) * 3

        # add triangles
        for i, tri in enumerate(tris):
            for idx in tri:
                skin.triangle_indices.append(start_index + idx)

        geoset_index = skin.submeshes.add(submesh)
        texture_unit.skin_section_index = geoset_index
        self.root.tex_unit_lookup_table.append(skin.texture_units.add(texture_unit))

        return geoset_index

    def add_material_to_geoset(self, geoset_id, render_flags, blending, flags, shader_id, tex_id):  # TODO: Add extra params & cata +
        skin = self.skins[0]
        tex_unit = skin.texture_units[geoset_id]
        tex_unit.flags = flags
        tex_unit.shader_id = shader_id
        tex_unit.texture_count = 1 # TODO: multitexturing
        tex_unit.texture_combo_index = tex_id
        # tex_unit.color_index = color_id

        # check if we already have that render flag else create it
        for i, material in enumerate(self.root.materials):
            if material.flags == render_flags and material.blending_mode == blending:
                tex_unit.material_index = i
                break
        else:
            m2_mat = M2Material()
            m2_mat.flags = render_flags
            m2_mat.blending_mode = blending
            tex_unit.material_index = self.root.materials.add(m2_mat)

    def add_texture(self, path, flags, tex_type):

        # check if this texture was already added
        for i, tex in enumerate(self.root.textures):
            if tex.filename.value == path and tex.flags == flags and tex.type == tex_type:
                return i

        texture = M2Texture()
        texture.filename.value = path
        texture.flags = flags
        texture.type = tex_type

        tex_id = self.root.textures.add(texture)
        self.root.texture_lookup_table.append(tex_id)
        self.root.texture_transforms_lookup_table.append(-1)
        self.root.replacable_texture_lookup.append(0)   # TODO: get back here

        return tex_id

    def add_bone(self, pivot, key_bone_id, flags, parent_bone):
        m2_bone = M2CompBone()
        m2_bone.key_bone_id = key_bone_id
        m2_bone.flags = flags
        m2_bone.parent_bone = parent_bone
        m2_bone.pivot = tuple(pivot)

        bone_id = self.root.bones.add(m2_bone)
        self.root.key_bone_lookup.append(key_bone_id)

        return bone_id

    def add_dummy_anim_set(self, origin):
        self.add_bone(tuple(origin), -1, 0, -1)
        self.add_anim(0, 0, (0, 888.77778), 0, 32, 32767, (0, 0), 150,
                      ((self.root.bounding_box.min, self.root.bounding_box.max), self.root.bounding_sphere_radius),
                      None, None
                      )
        self.root.bone_lookup_table.append(0)
        self.root.transparency_lookup_table.add(len(self.root.texture_weights))
        texture_weight = self.root.texture_weights.new()
        if self.version >= M2Versions.WOTLK:
            texture_weight.timestamps.new().add(0)
            texture_weight.values.new().add(32767)
        else:
            pass
            # TODO: pre-wotlk

    def add_anim(self, a_id, var_id, frame_bounds, movespeed, flags, frequency, replay, bl_time, bounds, var_next=None, alias_next=None):
        seq = M2Sequence()
        seq_id = self.root.sequences.add(seq)
        self.root.sequence_lookup.append(seq_id)

        # It is presumed that framerate is always 24 fps.
        if self.version <= M2Versions.TBC:
            seq.start_timestamp, seq.end_timestamp = int(frame_bounds[0] // 0.0266666), int(frame_bounds[1] // 0.0266666)
        else:
            seq.duration = int((frame_bounds[1] - frame_bounds[0]) // 0.0266666)

        seq.id = a_id
        seq.variation_index = var_id
        seq.variation_next = var_next if var_next else -1
        seq.alias_next = alias_next if alias_next else seq_id
        seq.flags = flags
        seq.frequency = frequency
        seq.movespeed = movespeed
        seq.replay.minimum, seq.replay.maximum = replay
        seq.bounds.extent.min, seq.bounds.extent.max = bounds[0]
        seq.bounds.radius = bounds[1]

        if self.version <= M2Versions.WOD:
            seq.blend_time = bl_time
        else:
            seq.blend_time_in, seq.blend_time_out = bl_time

        return seq_id

    def add_bone_track(self, bone_id, trans, rot, scale):
        bone = self.root.bones[bone_id]

        rot_ts = [int(frame // 0.0266666) for frame in rot[0]]
        trans_ts = [int(frame // 0.0266666) for frame in trans[0]]
        scale_ts = [int(frame // 0.0266666) for frame in scale[0]]

        if self.version < M2Versions.WOTLK:
            rot_quats = rot[1]

            if self.version <= M2Versions.CLASSIC:
                rot_quats = [(qtrn[1], qtrn[2], qtrn[3], qtrn[0]) for qtrn in rot[1]]

            bone.rotation.interpolation_ranges.append(len(bone.rotation.timestamps), len(rot[0]) - 1)
            bone.rotation.timestamps.extend(rot_ts)
            bone.rotation.values.extend(rot_quats)

            bone.translation.interpolation_ranges.append(len(bone.translation.timestamps), len(trans[0]) - 1)
            bone.translation.timestamps.extend(trans_ts)
            bone.translation.values.extend(trans[1])

            bone.scale.interpolation_ranges.append(len(bone.scale.timestamps), len(rot[0]) - 1)
            bone.scale.timestamps.extend(scale_ts)
            bone.scale.values.extend(scale[1])

        else:
            bone.rotation.timestamps.new().from_iterable(rot_ts)
            bone.rotation.values.new().from_iterable(rot[1])

            bone.translation.timestamps.new().from_iterable(trans_ts)
            bone.translation.values.new().from_iterable(trans[1])

            bone.scale.timestamps.new().from_iterable(scale_ts)
            bone.scale.values.new().from_iterable(scale[1])

    def add_collision_mesh(self, vertices, faces, normals):

        # add collision geometry
        self.root.collision_vertices.extend(vertices)
        for face in faces: self.root.collision_triangles.extend(face)
        self.root.collision_normals.extend(normals)








