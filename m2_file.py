import os
import struct

from typing import List
from itertools import chain
from collections import deque

from .enums.m2_enums import M2TextureTypes
from .file_formats import m2_chunks
from .file_formats.m2_format import *
from .file_formats.m2_chunks import *
from .file_formats.skin_format import M2SkinProfile, M2SkinSubmesh, M2SkinTextureUnit
from .file_formats.skel_format import SkelFile
from .file_formats.anim_format import AnimFile
from .file_formats.wow_common_types import M2Versions


class M2Dependencies:

    def __init__(self):
        self.textures = []
        self.skins = []
        self.anims = []
        self.bones = []
        self.lod_skins = []


class M2File:
    def __init__(self, version, filepath=None):
        self.version = M2Versions.from_expansion_number(version)
        self.root = None
        self.filepath = filepath
        self.raw_path = os.path.splitext(filepath)[0]
        self.dependencies = M2Dependencies()
        self.skins = [M2SkinProfile()]
        self.skels = deque()
        self.texture_path_map = {}

        if self.version >= M2Versions.LEGION:
            self.root = MD21()
            self.pfid = None
            self.sfid = None
            self.afid = None
            self.bfid = None
            self.txac = None
            self.expt = None
            self.exp2 = None
            self.pabc = None
            self.padc = None
            self.psbc = None
            self.pedc = None
            self.skid = None

            if self.version >= M2Versions.BFA:
                self.txid = None
                self.ldv1 = None
                self.rpid = None
                self.gpid = None

            # everything gets handled as of 03.04.20

        else:
            self.root = MD20()

        if filepath:
            self.read()

    def read(self):
        self.skins = []

        with open(self.filepath, 'rb') as f:
            magic = f.read(4).decode('utf-8')

            if magic == 'MD20':
                self.root = MD20().read(f)
            else:
                self.root = MD21().read(f)

                while True:
                    try:
                        magic = f.read(4).decode('utf-8')

                    except EOFError:
                        break

                    except struct.error:
                        break

                    except UnicodeDecodeError:
                        print('\nAttempted reading non-chunked data.')
                        break

                    if not magic:
                        break

                    # getting the correct chunk parsing class
                    chunk = getattr(m2_chunks, magic, None)

                    # skipping unknown chunks
                    if chunk is None:
                        print("\nEncountered unknown chunk \"{}\"".format(magic))
                        f.seek(M2ContentChunk().read(f).size, 1)
                        continue

                    if magic != 'SFID':
                        setattr(self, magic.lower(), chunk().read(f))

                    else:
                        self.sfid = SFID(n_views=self.root.num_skin_profiles).read(f)

    def find_main_skel(self) -> int:

        if self.skid:
            return self.skid.skeleton_file_id

        return 0

    def read_skel(self, path: str) -> int:

        skel = SkelFile(path)

        with open(path, 'rb') as f:
            skel.read(f)

        self.skels.appendleft(skel)

        if skel.skpd:
            return skel.skpd.parent_skel_file_id

        return 0

    def process_skels(self):

        for skel in self.skels:

            if skel.skl1:
                self.root.name = skel.skl1.name

            if skel.ska1:
                self.root.attachments = skel.ska1.attachments
                self.root.attachment_lookup_table = skel.ska1.attachment_lookup_table

            if skel.skb1:
                self.root.bones = skel.skb1.bones
                self.root.key_bone_lookup = skel.skb1.key_bone_lookup

            if skel.sks1:
                self.root.global_sequences = skel.sks1.global_loops
                self.root.sequences = skel.sks1.sequences
                self.root.sequence_lookup = skel.sks1.sequence_lookups

            if skel.afid:
                self.afid.anim_file_ids = skel.afid.anim_file_ids

    def find_model_dependencies(self) -> M2Dependencies:

        # find skins
        if self.sfid:
            self.dependencies.skins = [fdid for fdid in self.sfid.skin_file_data_ids]
            self.dependencies.lod_skins = [fdid for fdid in self.sfid.lod_skin_file_data_ids]

        elif self.version >= M2Versions.WOTLK:

            if self.version >= M2Versions.WOD:
                self.dependencies.lod_skins = ["{}{}.skin".format(
                    self.raw_path, str(i + 1).zfill(2))  for i in range(2)]
                self.dependencies.skins = ["{}{}.skin".format(
                    self.raw_path, str(i).zfill(2)) for i in range(self.root.num_skin_profiles)]

        # find textures
        for i, texture in enumerate(self.root.textures):

            if texture.type != M2TextureTypes.NONE:
                continue

            if texture.filename.value:
                self.dependencies.textures.append(texture.filename.value)

            elif i < len(self.txid.texture_ids) and self.txid.texture_ids[i] > 0:

                texture.txid = self.txid.texture_ids[i]
                self.dependencies.textures.append(texture.txid)

        # find bones
        if self.bfid:
            self.dependencies.bones = [fdid for fdid in self.bfid.bone_file_data_ids]

        elif self.version >= M2Versions.WOD:

            for sequence in self.root.sequences:

                if sequence.id == 808:
                    self.dependencies.bones.append("{}_{}.bone".format(
                        self.raw_path, str(sequence.variation_index).zfill(2)))

        # TODO: find phys

        # find anims
        anim_paths_map = {}
        for i, sequence in enumerate(self.root.sequences):
            # handle alias animations
            real_anim = sequence
            a_idx = i

            while real_anim.flags & 0x40 and real_anim.alias_next != a_idx:
                a_idx = real_anim.alias_next
                real_anim = self.root.sequences[real_anim.alias_next]

            if not sequence.flags & 0x130:
                anim_paths_map[real_anim.id, sequence.variation_index] \
                    = "{}{}-{}.anim".format(self.raw_path if not self.skels else self.skels[0].root_basepath
                                            , str(real_anim.id).zfill(4)
                                            , str(sequence.variation_index).zfill(2))

        if self.afid:

            for record in self.afid.anim_file_ids:

                if not record.file_id:
                    continue

                anim_paths_map[record.anim_id, record.sub_anim_id] = record.file_id

        self.dependencies.anims = list(anim_paths_map.values())

        return self.dependencies

    @staticmethod
    def process_anim_file(raw_data : BytesIO, tracks: List[M2Track], real_seq_index: int):

        for track in tracks:

            if track.global_sequence < 0 and track.timestamps.n_elements > real_seq_index:

                timestamps = track.timestamps[real_seq_index]
                timestamps.read(raw_data, ignore_header=True)

                frame_values = track.values[real_seq_index]
                frame_values.read(raw_data, ignore_header=True)

    def read_additional_files(self):

        if self.version >= M2Versions.WOTLK:
            # load skins

            for i in range(self.root.num_skin_profiles):
                with open("{}{}.skin".format(self.raw_path, str(i).zfill(2)), 'rb') as skin_file:
                    self.skins.append(M2SkinProfile().read(skin_file))

            # load anim files
            track_cache = M2TrackCache()
            for i, sequence in enumerate(self.root.sequences):
                # handle alias animations
                real_anim = sequence
                a_idx = i

                while real_anim.flags & 0x40 and real_anim.alias_next != a_idx:
                    a_idx = real_anim.alias_next
                    real_anim = self.root.sequences[real_anim.alias_next]

                if not sequence.flags & 0x130:

                    anim_path = "{}{}-{}.anim".format(self.raw_path if not self.skels else self.skels[0].root_basepath,
                                                      str(real_anim.id).zfill(4),
                                                      str(sequence.variation_index).zfill(2))

                    anim_file = AnimFile(split=bool(self.skels)
                                         , old=not bool(self.skels)
                                               and not self.root.global_flags & M2GlobalFlags.ChunkedAnimFiles)

                    with open(anim_path, 'rb') as f:
                        anim_file.read(f)

                    if anim_file.old or not anim_file.split:

                        if anim_file.old:
                            raw_data = anim_file.raw_data
                            print('old')
                        else:
                            raw_data = anim_file.afm2.raw_data
                            print('chunked')

                        for creator, tracks in track_cache.m2_tracks.items():

                            M2File.process_anim_file(raw_data, tracks, a_idx)

                    else:

                        print('chunked split')

                        for creator, tracks in track_cache.m2_tracks.items():

                            if creator is M2CompBone:
                                M2File.process_anim_file(anim_file.afsb.raw_data, tracks, a_idx)
                            elif creator is M2Attachment:
                                M2File.process_anim_file(anim_file.afsa.raw_data, tracks, a_idx)
                            else:
                                M2File.process_anim_file(anim_file.afm2.raw_data, tracks, a_idx)

        else:
            self.skins = self.root.skin_profiles

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








