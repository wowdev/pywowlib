from collections import OrderedDict

from .wow_common_types import CAaBox, CRange, M2Array, M2Versions, fixed16, fixed_point, MemoryManager, \
    M2VersionsManager, M2ExternalSequenceCache
from ..io_utils.types import *
from .skin_format import M2SkinProfile
from ..enums.m2_enums import M2KeyBones, M2GlobalFlags, M2AttachmentTypes, M2EventTokens


__reload_order_index__ = 2


class M2Bounds:

    def __init__(self):
        self.extent = CAaBox()
        self.radius = 0.0

    def read(self, f):
        self.extent.read(f)
        self.radius = float32.read(f)
        return self

    def write(self, f):
        self.extent.write(f)
        float32.write(f, self.radius)

    def to_obj(self):
        return {
            "extent": self.extent.to_obj(),
            "radius": self.radius
        }


class M2String:
    __slots__ = ('value',)

    def __init__(self):
        self.value = ""

    def read(self, f):
        n_characters = uint32.read(f)
        ofs_characters = uint32.read(f)

        pos = f.tell()
        f.seek(ofs_characters)
        self.value = f.read(n_characters).decode('utf-8').rstrip('\0')
        f.seek(pos)

        return self

    def write(self, f):
        ofs = MemoryManager.ofs_request(f)

        uint32.write(f, len(self.value) + 1)
        uint32.write(f, ofs)

        pos = f.tell()
        f.seek(ofs)
        self.value = f.write((self.value + '\0').encode('utf-8'))
        f.seek(pos)
        
        return self

    def to_obj(self):
        return self.value


class M2SplineKey(metaclass=Template):
    
    def __init__(self, type_):
        self.value = type_()
        self.in_tan = type_()
        self.out_tan = type_()

        self.type = type_
   
    def read(self, f):
        if type(self.type) is GenericType:
            self.value = self.type.read(f)
            self.in_tan = self.type.read(f)
            self.out_tan = self.type.read(f)
        else:
            self.value.read(f)
            self.in_tan.read(f)
            self.out_tan.read(f)

        return self
        
    def write(self, f):
        if type(self.type) is GenericType:
            self.type.write(f, self.value)
            self.type.write(f, self.in_tan)
            self.type.write(f, self.out_tan)
        else:
            self.value.write(f)
            self.in_tan.write(f)
            self.out_tan.write(f)
            
        return self
    
    def to_obj(self):
        return {
            "value": self.value.to_obj(),
            "in_tan": self.in_tan.to_obj(),
            "out_tan": self.out_tan.to_obj()
        }

class M2Range:
    
    def __init__(self):
        self.minimum = 0
        self.maximum = 0
   
    def read(self, f):
        self.minimum = uint32.read(f)
        self.maximum = uint32.read(f)

        return self
        
    def write(self, f):
        uint32.write(f, self.minimum)
        uint32.write(f, self.maximum)

        return self

    def to_obj(self):
        return {
            "minimum": self.minimum,
            "maximum": self.maximum
        }

    
    
class M2TrackBase:
    
    def __init__(self):

        self.m2_version = M2VersionsManager().m2_version

        self.interpolation_type = 0
        self.global_sequence = -1

        if self.m2_version < M2Versions.WOTLK:
            self.interpolation_ranges = M2Array(M2Range)
            self.timestamps = M2Array(uint32)
        else:
            self.timestamps = M2Array(M2Array << uint32)

    def read(self, f):
        self.interpolation_type = uint16.read(f)
        self.global_sequence = int16.read(f)

        if self.m2_version < M2Versions.WOTLK:
            self.interpolation_ranges.read(f)
        self.timestamps.read(f, is_anim_data=True)

        return self

    def write(self, f):
        uint16.write(f, self.interpolation_type)
        int16.write(f, self.global_sequence)

        if self.m2_version < M2Versions.WOTLK:
            self.interpolation_ranges.write(f)

        self.timestamps.write(f)

        return self

    def new(self):
        if self.m2_version < M2Versions.WOTLK:
            return self.interpolation_ranges.new(), self.timestamps
        else:
            return self.timestamps.new()

    def to_obj(self):
        # TODO: pre-wotlk
        return {
            "interpolation_type": self.interpolation_type,
            "global_sequence": self.global_sequence,
            "timestamps": self.timestamps.to_obj()
        }

    @staticmethod
    def size():
        return 12 if M2VersionsManager().m2_version >= M2Versions.WOTLK else 20


class M2Track(M2TrackBase, metaclass=Template):

    def __init__(self, *args):

        type_, self.creator = args
        self.m2_version = M2VersionsManager().m2_version

        super(M2Track, self).__init__()
        self.values = M2Array(type_) if self.m2_version < M2Versions.WOTLK else M2Array(M2Array << type_)

    def read(self, f):

        super(M2Track, self).read(f)
        self.values.read(f, is_anim_data=True)

        M2TrackCache().add_track(self, self.creator)

        return self

    def write(self, f):
        super(M2Track, self).write(f)
        self.values.write(f)

        return self

    def to_obj(self):
        return self.values.to_obj()

    @staticmethod
    def size():
        return 20 if M2VersionsManager().m2_version >= M2Versions.WOTLK else 28


class M2PartTrack:
    def __init__(self, type_):
        self.times = M2Array(fixed16)
        self.values = M2Array(type_)

    def read(self, f):
        self.times.read(f)
        self.values.read(f)

        return self

    def write(self, f):
        self.times.write(f)
        self.values.write(f)

        return self

    def to_obj(self):
        return {
            "times": self.times.to_obj(),
            "values": self.values.to_obj()
        }

    @staticmethod
    def size():
        return M2Array.size() * 2


class FBlock:

    def __init__(self, type_):
        self.timestamps = M2Array(uint16)
        self.keys = M2Array(type_)

    def read(self, f):
        self.timestamps.read(f)
        self.keys.read(f)

        return self

    def write(self, f):
        self.timestamps.write(f)
        self.keys.write(f)

        return self

    def to_obj(self):
        return {
            "timestamps": self.timestamps.to_obj(),
            "keys": self.keys.to_obj()
        }

    @staticmethod
    def size():
        return 16


class Vector_2fp_6_9:

    def __init__(self):
        self.x = fixed_point(uint16, 6, 9)
        self.y = fixed_point(uint16, 6, 9)

    def read(self, f):
        self.x.read(f)
        self.y.read(f)

        return self

    def write(self, f):
        self.x.write(f)
        self.y.write(f)
        
        return self
    
    def to_obj(self):
        return {
            "x": self.x.value,
            "y": self.y.value,
        }

class M2Box:
    
    def __init__(self):
        self.model_rotation_speed_min = (0.0, 0.0, 0.0)
        self.model_rotation_speed_max = (0.0, 0.0, 0.0)
   
    def read(self, f):
        self.model_rotation_speed_min = vec3D.read(f)
        self.model_rotation_speed_max = vec3D.read(f)

        return self
        
    def write(self, f):
        vec3D.write(f, self.model_rotation_speed_min)
        vec3D.write(f, self.model_rotation_speed_max)

        return self

    def to_obj(self):
        return {
            "speed_min": list(self.model_rotation_speed_min),
            "speed_max": list(self.model_rotation_speed_max),
        }

class M2CompQuaternion:
    
    def __init__(self, quaternion=(-1, 0, 0, 0)):
        self.x = quaternion[1]
        self.y = quaternion[2]
        self.z = quaternion[3]
        self.w = quaternion[0]

    def read(self, f):
        self.y = int16.read(f)
        self.x = -int16.read(f)
        self.z = int16.read(f)
        self.w = int16.read(f)

        return self

    def write(self, f):
        int16.write(f, self.x)
        int16.write(f, self.y)
        int16.write(f, self.z)
        int16.write(f, self.w)

        return self

    def to_quaternion(self, quat_type=None):
        type_ = quat_type if quat_type else tuple
        return type_(
            (
                (self.w + 32768 if self.w < 0 else self.w - 32767) / 32767,
                (self.x + 32768 if self.x < 0 else self.x - 32767) / 32767,
                (self.y + 32768 if self.y < 0 else self.y - 32767) / 32767,
                (self.z + 32768 if self.z < 0 else self.z - 32767) / 32767
            )
        )

    def from_quaternion(self):
        pass
        # TODO: implement

    def to_obj(self):
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
            "w": self.w,
        }

#############################################################
######              Animation sequences                ######
#############################################################


class M2SequenceFlags:
    blended_animation_auto = 0x1                                # Sets 0x80 when loaded. (M2Init)
    load_low_priority_sequence = 0x10                           # apparently set during runtime in CM2Shared::LoadLowPrioritySequence for all entries of a loaded sequence (including aliases)
    looped_animation = 0x20                                     # primary bone sequence -- If set, the animation data is in the .m2 file. If not set, the animation data is in an .anim file.
    is_alias = 0x40                                             # has next / is alias (To find the animation data, the client skips these by following aliasNext until an animation without 0x40 is found.)
    blended_animation = 0x80                                    # Blended animation (if either side of a transition has 0x80, lerp between end->start states, unless end==start by comparing bone values)
    sequence_stored_in_model = 0x100                            # sequence stored in model ?
    some_legion_flag = 0x800                                    # seen in Legion 24500


class M2Sequence:

    def __init__(self):
        self.m2_version = M2VersionsManager().m2_version

        self.id = 0                                             # Animation id in AnimationData.dbc
        self.variation_index = 0                                # Sub-animation id: Which number in a row of animations this one is.

        if self.m2_version <= M2Versions.TBC:
            self.start_timestamp = 0
            self.end_timestamp = 0
        else:
            self.duration = 0                                   # The length of this animation sequence in milliseconds.

        self.movespeed = 0                                      # This is the speed the character moves with in this animation.
        self.flags = 0                                          # See below.
        self.frequency = 0                                      # This is used to determine how often the animation is played. For all animations of the same type, this adds up to 0x7FFF (32767).
        self.padding = 0
        self.replay = M2Range()                                 # May both be 0 to not repeat. Client will pick a random number of repetitions within bounds if given.

        if self.m2_version < M2Versions.WOD:
            self.blend_time = 0
        else:
            self.blend_time_in = 0                              # The client blends (lerp) animation states between animations where the end and start values differ. This specifies how long that blending takes. Values: 0, 50, 100, 150, 200, 250, 300, 350, 500.
            self.blend_time_out = 0                             # The client blends between this sequence and the next sequence for blendTimeOut milliseconds.
                                                                # For both blendTimeIn and blendTimeOut, the client plays both sequences simultaneously while interpolating between their animation transforms.
        self.bounds = M2Bounds()
        self.variation_next = 0                                 # id of the following animation of this animation_id, points to an Index or is -1 if none.
        self.alias_next = 0                                     # id in the list of animations. Used to find actual animation if this sequence is an alias (flags & 0x40)

    def read(self, f):
        self.id = uint16.read(f) #2
        self.variation_index = uint16.read(f) #2

        if self.m2_version <= M2Versions.TBC:
            self.start_timestamp = uint32.read(f) #4
            self.end_timestamp = uint32.read(f) #4
        else:
            self.duration = uint32.read(f)  #4
        
        self.movespeed = float32.read(f) #4
        self.flags = uint32.read(f) #4
        self.frequency = int16.read(f) #2
        self.padding = uint16.read(f) #2
        self.replay.read(f)

        if self.m2_version < M2Versions.WOD:
            self.blend_time = uint32.read(f) #4
        else:
            self.blend_time_in = uint16.read(f) #2
            self.blend_time_out = uint16.read(f) #2

        self.bounds.read(f)
        self.variation_next = int16.read(f) #2
        self.alias_next = uint16.read(f) #2

        return self

    def write(self, f):
        uint16.write(f, self.id)
        uint16.write(f, self.variation_index)
        if self.m2_version <= M2Versions.TBC:
            uint32.write(f, self.start_timestamp)
            uint32.write(f, self.end_timestamp)
        else:
            uint32.write(f, self.duration)

        float32.write(f, self.movespeed)
        uint32.write(f, self.flags)
        int16.write(f, self.frequency)
        uint16.write(f, self.padding)
        self.replay.write(f)

        if self.m2_version < M2Versions.WOD:
            uint32.write(f, self.blend_time)
        else:
            uint16.write(f, self.blend_time_in)
            uint16.write(f, self.blend_time_out)

        self.bounds.write(f)
        int16.write(f, self.variation_next)
        uint16.write(f, self.alias_next)

        return self

    def to_obj(self):
        # TODO: non-wotlk
        return {
            "id": self.id,
            "variation_index": self.variation_index,
            "duration": self.duration,
            "movespeed": self.movespeed,
            "flags": self.flags,
            "frequency": self.frequency,
            "padding": self.padding,
            "replay": self.replay.to_obj(),
            "blend_time": self.blend_time,
            "bounds": self.bounds.to_obj(),
            "variation_next": self.variation_next,
            "alias_next": self.alias_next
        }

    @staticmethod
    def size():
        return 32 if M2VersionsManager().m2_version <= M2Versions.TBC else 28


#############################################################
######                     Bones                       ######
#############################################################

class M2CompBone:

    def __init__(self):
        self.m2_version = M2VersionsManager().m2_version

        self.key_bone_id = 0                                                                                      # Back-reference to the key bone lookup table. -1 if this is no key bone.
        self.flags = 0
        self.parent_bone = 0                                                                                      # Parent bone ID or -1 if there is none.
        self.submesh_id = 0

        # union
        self.u_dist_to_furth_desc = 0
        self.u_zratio_of_chain = 0
        self.bone_name_crc = 0                                                                                 # these are for debugging only. their bone names match those in key bone lookup.
        # unionend

        self.translation = M2Track(vec3D, M2CompBone)
        self.rotation = M2Track(quat if self.m2_version <= M2Versions.CLASSIC else M2CompQuaternion, M2CompBone)  # compressed values, default is (32767,32767,32767,65535) == (0,0,0,1) == identity

        self.scale = M2Track(vec3D, M2CompBone)
        self.pivot = (0.0, 0.0, 0.0)                                                                              # The pivot point of that bone.

        # Helpers
        self.parent = None
        self.children = []
        self.name = 'Bone'
        self.index = 0

    def read(self, f):
        self.key_bone_id = int32.read(f)
        self.flags = uint32.read(f)
        self.parent_bone = int16.read(f)
        self.submesh_id = uint16.read(f)
        self.bone_name_crc = uint32.read(f)

        self.translation.read(f)
        self.rotation.read(f)
        self.scale.read(f)
        self.pivot = vec3D.read(f)

        if self.key_bone_id >= 35:

            print(self.key_bone_id, ":", hex(self.bone_name_crc), ",")

        return self

    def write(self, f):
        int32.write(f, self.key_bone_id)
        uint32.write(f, self.flags)
        int16.write(f, self.parent_bone)
        uint16.write(f, self.submesh_id)
        uint32.write(f, self.bone_name_crc)
        self.translation.write(f)
        self.rotation.write(f)
        self.scale.write(f)
        vec3D.write(f, self.pivot)

        return self

    def build_relations(self, bones):
        if self.parent_bone >= 0:
            parent = bones[self.parent_bone]
            self.parent = parent
            parent.children.append(self)

    def load_bone_name(self, bone_type_dict):

        self.name = M2KeyBones.get_bone_name(self.key_bone_id, self.index)

        b_type = bone_type_dict.get(self.index)

        if b_type and self.key_bone_id < 0:
            prefix, i, item = b_type

            if prefix in ('AT', 'ET'):
                self.name = "{}_{}_{}".format(prefix, item, i)

            elif prefix in ('LT', 'RB', 'PT'):
                self.name = "{}_{}".format(prefix, i)

    def get_depth(self):
        if not self.children:
            return 0
        return sum(map(lambda x: x.get_depth(), self.children)) + len(self.children)

    def to_obj(self):
        return {
            "key_bone_id": self.key_bone_id,
            "flags": self.flags,
            "parent_bone": self.parent_bone,
            "submesh_id": self.submesh_id,
            "u_dist_to_furth_desc": self.u_dist_to_furth_desc,
            "u_zratio_of_chain": self.u_zratio_of_chain,
            "bone_name_crc": self.bone_name_crc,
            "translation": self.translation.to_obj(),
            "rotation": self.rotation.to_obj(),
            "scale": self.scale.to_obj(),
            "pivot": list(self.pivot),
        }

    @staticmethod
    def size():
        return 88 if M2VersionsManager().m2_version >= M2Versions.WOTLK else 110


#############################################################
######              Geometry and rendering             ######
#############################################################

###### Vertices ######

class M2Vertex:
    __slots__ = ('pos', 'bone_weights', 'bone_indices',
                 'normal', 'tex_coords', 'tex_coords2')

    def __init__(self):
        self.pos = (0.0, 0.0, 0.0)
        self.bone_weights = (0, 0, 0, 0)
        self.bone_indices = (0, 0, 0, 0)
        self.normal = (0.0, 0.0, 0.0)
        self.tex_coords = (0.0, 0.0)
        self.tex_coords2 = (0.0, 0.0)

    def read(self, f):
        self.pos = vec3D.read(f)
        self.bone_weights = uint8.read(f, 4)
        self.bone_indices = uint8.read(f, 4)
        self.normal = vec3D.read(f)
        self.tex_coords = vec2D.read(f)
        self.tex_coords2 = vec2D.read(f)

        return self

    def write(self, f):
        vec3D.write(f, self.pos)
        uint8.write(f, self.bone_weights, 4)
        uint8.write(f, self.bone_indices, 4)
        vec3D.write(f, self.normal)
        vec2D.write(f, self.tex_coords)
        vec2D.write(f, self.tex_coords2)

        return self

    def to_obj(self):
        return {
            "pos": list(self.pos),
            "bone_weights": list(self.bone_weights),
            "bone_indices": list(self.bone_indices),
            "normal": list(self.normal),
            "tex_coords": list(self.tex_coords),
            "tex_coords2": list(self.tex_coords2)
        }

###### Render flags ######

class M2Material:

    def __init__(self):
        self.flags = 0
        self.blending_mode = 0  # apparently a bitfield

    def read(self, f):
        self.flags = uint16.read(f)
        self.blending_mode = uint16.read(f)

        return self

    def write(self, f):
        uint16.write(f, self.flags)
        uint16.write(f, self.blending_mode)

        return self

    def to_obj(self):
        return {
            "flags": self.flags,
            "blending_mode": self.blending_mode
        }


###### Colors and transparency ######

class M2Color:

    def __init__(self):
        self.color = M2Track(vec3D, M2Color)
        self.alpha = M2Track(fixed16, M2Color)

    def read(self, f):
        self.color.read(f)
        self.alpha.read(f)

        return self

    def write(self, f):
        self.color.write(f)
        self.alpha.write(f)

        return self

    @staticmethod
    def size():
        return 40 if M2VersionsManager().m2_version >= M2Versions.WOTLK else 56

    def to_obj(self):
        return {
            "color": self.color.to_obj(),
            "alpha": self.alpha.to_obj()
        }


class M2Texture:

    def __init__(self):
        self.type = 0
        self.flags = 0
        self.filename = M2String()

        # BFA+ (internal use only)
        self.fdid = 0

    def read(self, f):
        self.type = uint32.read(f)
        self.flags = uint32.read(f)
        self.filename.read(f)

        return self

    def write(self, f):
        uint32.write(f, self.type)
        uint32.write(f, self.flags)
        self.filename.write(f)

        return self

    @staticmethod
    def size():
        return 16

    def to_obj(self):
        return {
            "type": self.type,
            "flags": self.flags,
            "filename": self.filename.to_obj()
        }

#############################################################
######                    Effects                      ######
#############################################################

class M2TextureTransform:

    def __init__(self):
        self.translation = M2Track(vec3D, M2TextureTransform)
        self.rotation = M2Track(quat, M2TextureTransform)      # rotation center is texture center (0.5, 0.5, 0.5)
        self.scaling = M2Track(vec3D, M2TextureTransform)

    def read(self, f):
        self.translation.read(f)
        self.rotation.read(f)
        self.scaling.read(f)

        return self

    def write(self, f):
        self.translation.write(f)
        self.rotation.write(f)
        self.scaling.write(f)

        return self

    def to_obj(self):
        return {
            "translation": self.translation.to_obj(),
            "rotation": self.rotation.to_obj(),
            "scaling": self.scaling.to_obj()
        }

    @staticmethod
    def size():
        return 60 if M2VersionsManager().m2_version >= M2Versions.WOTLK else 84


class M2Ribbon:

    def __init__(self):
        self.m2_version = M2VersionsManager().m2_version

        self.ribbon_id = -1                                     # Always (as I have seen): -1.
        self.bone_index = 0                                     # A bone to attach to.
        self.position = (0.0, 0.0, 0.0)                         # And a position, relative to that bone.
        self.texture_indices = M2Array(uint16)                  # into textures
        self.material_indices = M2Array(uint16)                 # into materials
        self.color_track = M2Track(vec3D, M2Ribbon)
        self.alpha_track = M2Track(fixed16, M2Ribbon)           # And an alpha value in a short, where: 0 - transparent, 0x7FFF - opaque.
        self.height_above_track = M2Track(float32, M2Ribbon)
        self.height_below_track = M2Track(float32, M2Ribbon)    # do not set to same!
        self.edges_per_second = 0.0                             # this defines how smooth the ribbon is. A low value may produce a lot of edges.
        self.edge_lifetime = 0.0                                # the length aka Lifespan. in seconds
        self.gravity = 0.0                                      # use arcsin(val) to get the emission angle in degree
        self.texture_rows = 0                                   # tiles in texture
        self.texture_cols = 0
        self.tex_slot_track = M2Track(uint16, M2Ribbon)
        self.visibility_track = M2Track(uint8, M2Ribbon)

        if self.m2_version >= M2Versions.WOTLK:                         # TODO: verify version
            self.priority_plane = 0
            self.padding = 0

    def read(self, f):
        self.ribbon_id = int32.read(f)
        self.bone_index = uint32.read(f)
        self.position = vec3D.read(f)
        self.texture_indices.read(f)
        self.material_indices.read(f)
        self.color_track.read(f)
        self.alpha_track.read(f)
        self.height_above_track.read(f)
        self.height_below_track.read(f)
        self.edges_per_second = float32.read(f)
        self.edge_lifetime = float32.read(f)
        self.gravity = float32.read(f)
        self.texture_rows = uint16.read(f)
        self.texture_cols = uint16.read(f)
        self.tex_slot_track.read(f)
        self.visibility_track.read(f)

        if self.m2_version >= M2Versions.WOTLK:
            self.priority_plane = int16.read(f)
            self.padding = uint16.read(f)

        return self

    def write(self, f):
        int32.write(f, self.ribbon_id)
        uint32.write(f, self.bone_index)
        vec3D.write(f, self.position)
        self.texture_indices.write(f)
        self.material_indices.write(f)
        self.color_track.write(f)
        self.alpha_track.write(f)
        self.height_above_track.write(f)
        self.height_below_track.write(f)
        float32.write(f, self.edges_per_second)
        float32.write(f, self.edge_lifetime)
        float32.write(f, self.gravity)
        uint16.write(f, self.texture_rows)
        uint16.write(f, self.texture_cols)
        self.tex_slot_track.write(f)
        self.visibility_track.write(f)

        if self.m2_version >= M2Versions.WOTLK:
            int16.write(f, self.priority_plane)
            uint16.write(f, self.padding)

        return self

    def to_obj(self):
        return {
            "ribbon_id": self.ribbon_id,
            "bone_index": self.bone_index,
            "position": list(self.position),
            "texture_indices": self.texture_indices.to_obj(),
            "material_indices": self.material_indices.to_obj(),
            "color_track": self.color_track.to_obj(),
            "alpha_track": self.alpha_track.to_obj(),
            "height_above_track": self.height_above_track.to_obj(),
            "height_below_track": self.height_below_track.to_obj(),
            "edges_per_second": self.edges_per_second,
            "edge_lifetime": self.edge_lifetime,
            "gravity": self.gravity,
            "texture_rows": self.texture_rows,
            "texture_colrs": self.texture_cols,
            "tex_slot_track": self.tex_slot_track.to_obj(),
            "visibility_track": self.visibility_track.to_obj(),
            "padding_plane": self.padding_plane,
            "padding": self.padding
        }

    @staticmethod
    def size():
        return 176 if M2VersionsManager().m2_version >= M2Versions.WOTLK else 220


class M2Particle:

    def __init__(self):
        self.m2_version = M2VersionsManager().m2_version

        self.particle_id = 0                                    # Always (as I have seen): -1.
        self.flags = 0                                          # See Below
        self.position = (0.0, 0.0, 0.0)                         # The position. Relative to the following bone.
        self.bone = 0                                           # The bone its attached to.
        self.texture = 0                                        # And the textures that are used. For multi-textured particles actually three ids
        self.geometry_model_filename = M2Array(int8)            # if given, this emitter spawns models
        self.recursion_model_filename = M2Array(int8)           # if given, this emitter is an alias for the (maximum 4) emitters of the given model

        if self.m2_version >= M2Versions.TBC:
            self.blending_type = 0                              # A blending type for the particle. See Below
            self.emitter_type = 0                               # 1 - Plane (rectangle), 2 - Sphere, 3 - Spline, 4 - Bone
            self.particle_color_index = 0                       # This one is used for ParticleColor.dbc. See below.
        else:
            self.blending_type = 0                              # A blending type for the particle. See Below
            self.emitter_type = 0                               # 1 - Plane (rectangle), 2 - Sphere, 3 - Spline, 4 - Bone

        if self.m2_version >= M2Versions.CATA:
            self.multi_tex_param_x = fixed_point(uint8, 2, 5)
            self.multi_tex_param_y = fixed_point(uint8, 2, 5)
        else:
            self.particle_type = 0                                # Found below.
            self.head_or_tail = 0                                 # 0 - Head, 1 - Tail, 2 - Both

        self.texture_tile_rotation = 0                            # Rotation for the texture tile. (Values: -1,0,1) -- priorityPlane
        self.texture_dimensions_rows = 0                          # for tiled textures
        self.texture_dimension_columns = 0
        self.emission_speed = M2Track(float32, M2Particle)        # Base velocity at which particles are emitted.
        self.speed_variation = M2Track(float32, M2Particle)       # Random variation in particle emission speed. (range: 0 to 1)
        self.vertical_range = M2Track(float32, M2Particle)        # Drifting away vertically. (range: 0 to pi) For plane generators, this is the maximum polar angle of the initial velocity;
        self.horizontal_range = M2Track(float32, M2Particle)      # They can do it horizontally too! (range: 0 to 2*pi) For plane generators, this is the maximum azimuth angle of the initial velocity;
                                                                  # 0 makes the velocity have no sideways (y-axis) component.  For sphere generators, this is the maximum azimuth angle of the initial position.
        self.gravity = M2Track(float32, M2Particle)               # Not necessarily a float; see below.
        self.lifespan = M2Track(float32, M2Particle)              # 0 makes the velocity have no sideways (y-axis) component.  For sphere generators, this is the maximum azimuth angle of the initial position.

        if self.m2_version >= M2Versions.WOTLK:
            self.life_span_vary = 0.0                             # An individual particle's lifespan is added to by lifespanVary * random(-1, 1)
            self.emission_rate_vary = 0.0                         # This adds to the base emissionRate value the same way as lifespanVary. The random value is different every update.

        self.emission_rate = M2Track(float32, M2Particle)
        self.emission_area_length = M2Track(float32, M2Particle)  # For plane generators, this is the width of the plane in the x-axis. For sphere generators, this is the minimum radius.
        self.emission_area_width = M2Track(float32, M2Particle)   # For plane generators, this is the width of the plane in the y-axis. For sphere generators, this is the maximum radius.
        self.z_source = M2Track(float32, M2Particle)              # When greater than 0, the initial velocity of the particle is (particle.position - C3Vector(0, 0, zSource)).Normalize()
        
        if self.m2_version >= M2Versions.WOTLK:
            self.color_track = FBlock(vec3D)                      # Most likely they all have 3 timestamps for {start, middle, end}.
            self.alpha_track = FBlock(fixed16)
            self.scale_track = FBlock(vec2D)
            self.scale_vary = (0.0, 0.0)                          # A percentage amount to randomly vary the scale of each particle
            self.head_cell_track = FBlock(uint16)                 # Some kind of intensity values seen: 0,16,17,32 (if set to different it will have high intensity)
            self.tail_cell_track = FBlock(uint16)
        else:
            self.mid_point = 0.0                                  # Middle point in lifespan (0 to 1).
            self.color_values = Array((Array << uint8, 4), 3)
            self.scale_values = Array(float32, 4)
            self.head_cell_begin = Array(uint16, 2)
            self.head_cell_end = Array(uint16, 2)
            self.tiles = Array(int16, 4)                          # Indices into the tiles on the texture? Or tailCell maybe?

        self.tail_length = 0.0                                    # TailCellTime?
        self.twinkle_speed = 0.0                                  # has something to do with the spread
        self.twinkle_percent = 0.0                                # has something to do with the spread
        self.twinkle_scale = CRange()
        self.burst_multiplier = 0.0                               # ivelScale
        self.drag = 0.0                                           # For a non-zero values, instead of travelling linearly the particles seem to slow down sooner. Speed is multiplied by exp( -drag * t ).
        
        if self.m2_version >= M2Versions.WOTLK:
            self.basespin = 0.0                                   # Initial rotation of the particle quad
            self.base_spin_vary = 0.0
            self.spin = 0.0                                       # Rotation of the particle quad per second
            self.spin_vary = 0.0
        else:
            self.spin = 0.0                                       # 0.0 for none, 1.0 to rotate the particle 360 degrees throughout its lifetime.

        self.tumble = M2Box()
        self.wind_vector = (0.0, 0.0, 0.0)
        self.wind_time = 0.0
        self.follow_speed1 = 0.0
        self.follow_scale1 = 0.0
        self.follow_speed2 = 0.0
        self.follow_scale2 = 0.0
        self.spline_points = M2Array(vec3D)                     # Set only for spline praticle emitter. Contains array of points for spline
        self.enabled_in = M2Track(uint8, M2Particle)            # (boolean) Appears to be used sparely now, probably there's a flag that links particles to animation sets where they are enabled.

        if self.m2_version >= M2Versions.CATA:
            self.multi_texture_param0 = Array(Vector_2fp_6_9, 2)
            self.multi_texture_param1 = Array(Vector_2fp_6_9, 2)

    def read(self, f):
        self.particle_id = uint32.read(f)
        self.flags = uint32.read(f)
        self.position = vec3D.read(f)
        self.bone = uint16.read(f)
        self.texture = uint16.read(f)
        self.geometry_model_filename.read(f)
        self.recursion_model_filename.read(f)

        if self.m2_version >= M2Versions.TBC:
            self.blending_type = uint8.read(f)
            self.emitter_type = uint8.read(f)
            self.particle_color_index = uint16.read(f)
        else:
            self.blending_type = uint16.read(f)
            self.emitter_type = uint16.read(f)

        if self.m2_version >= M2Versions.CATA:
            self.multi_tex_param_x.read(f)
            self.multi_tex_param_y.read(f)
        else:
            self.particle_type = uint8.read(f)
            self.head_or_tail = uint8.read(f)

        self.texture_tile_rotation = uint16.read(f)
        self.texture_dimensions_rows = uint16.read(f)
        self.texture_dimension_columns = uint16.read(f)
        self.emission_speed.read(f)
        self.speed_variation.read(f)
        self.vertical_range.read(f)
        self.horizontal_range.read(f)
        self.gravity.read(f)
        self.lifespan.read(f)

        if self.m2_version >= M2Versions.WOTLK:
            self.life_span_vary = float32.read(f)

        self.emission_rate.read(f)

        if self.m2_version >= M2Versions.WOTLK:
            self.emission_rate_vary = float32.read(f)

        self.emission_area_length.read(f)
        self.emission_area_width.read(f)
        self.z_source.read(f)

        if self.m2_version >= M2Versions.WOTLK:
            self.color_track.read(f)
            self.alpha_track.read(f)
            self.scale_track.read(f)
            self.scale_vary = vec2D.read(f)
            self.head_cell_track.read(f)
            self.tail_cell_track.read(f)
        else:
            self.mid_point = float32.read(f)
            self.color_values.read(f)
            self.scale_values.read(f)
            self.head_cell_begin.read(f)
            f.skip(2)
            self.head_cell_end.read(f)
            f.skip(2)
            self.tiles.read(f)

        self.tail_length = float32.read(f)
        self.twinkle_speed = float32.read(f)
        self.twinkle_percent = float32.read(f)
        self.twinkle_scale.read(f)
        self.burst_multiplier = float32.read(f)
        self.drag = float32.read(f)

        if self.m2_version >= M2Versions.WOTLK:
            self.basespin = float32.read(f)
            self.base_spin_vary = float32.read(f)
            self.spin = float32.read(f)
            self.spin_vary = float32.read(f)
        else:
            self.spin = float32.read(f)

        self.tumble.read(f)
        self.wind_vector = vec3D.read(f)
        self.wind_time = float32.read(f)
        self.follow_speed1 = float32.read(f)
        self.follow_scale1 = float32.read(f)
        self.follow_speed2 = float32.read(f)
        self.follow_scale1 = float32.read(f)
        self.spline_points.read(f)
        self.enabled_in.read(f)

        if self.m2_version >= M2Versions.CATA:
            self.multi_texture_param0.read(f)
            self.multi_texture_param1.read(f)

        return self

    def write(self, f):
        uint32.write(f, self.particle_id)
        uint32.write(f, self.flags)
        vec3D.write(f, self.position)
        uint16.write(f, self.bone)
        uint16.write(f, self.texture)
        self.geometry_model_filename.write(f)
        self.recursion_model_filename.write(f)

        if self.m2_version >= M2Versions.TBC:
            uint8.write(f, self.blending_type)
            uint8.write(f, self.emitter_type)
            uint16.write(f, self.particle_color_index)
        else:
            uint16.write(f, self.blending_type)
            uint16.write(f, self.emitter_type)
            
        if self.m2_version >= M2Versions.CATA:
            self.multi_tex_param_x.write(f)
            self.multi_tex_param_y.write(f)
        else:
            uint8.write(f, self.particle_type)
            uint8.write(f, self.head_or_tail)
            
        uint16.write(f, self.texture_tile_rotation)
        uint16.write(f, self.texture_dimensions_rows)
        uint16.write(f, self.texture_dimension_columns)
        self.emission_speed.write(f)
        self.speed_variation.write(f)
        self.vertical_range.write(f)
        self.horizontal_range.write(f)
        self.gravity.write(f)
        self.lifespan.write(f)

        if self.m2_version >= M2Versions.WOTLK:
            float32.write(f, self.life_span_vary)

        self.emission_rate.write(f)

        if self.m2_version >= M2Versions.WOTLK:
            float32.write(f, self.emission_rate_vary)
            
        self.emission_area_length.write(f)
        self.emission_area_width.write(f)
        self.z_source.write(f)

        if self.m2_version >= M2Versions.WOTLK:
            self.color_track.write(f)
            self.alpha_track.write(f)
            self.scale_track.write(f)
            vec2D.write(f, self.scale_vary)
            self.head_cell_track.write(f)
            self.tail_cell_track.write(f)
        else:
            float32.write(f, self.mid_point)
            self.color_values.write(f)
            self.scale_values.write(f)
            self.head_cell_begin.write(f)
            uint16.write(f, 1)
            self.head_cell_end.write(f)
            uint16.write(f, 1)
            self.tiles.write(f)

        float32.write(f, self.tail_length)
        float32.write(f, self.twinkle_speed)
        float32.write(f, self.twinkle_percent)
        self.twinkle_scale.write(f)
        float32.write(f, self.burst_multiplier)
        float32.write(f, self.drag)

        if self.m2_version >= M2Versions.WOTLK:
            float32.write(f, self.basespin)
            float32.write(f, self.base_spin_vary)
            float32.write(f, self.spin)
            float32.write(f, self.spin_vary)
        else:
            float32.write(f, self.spin)

        self.tumble.write(f)
        vec3D.write(f, self.wind_vector)
        float32.write(f, self.wind_time)

        float32.write(f, self.follow_speed1)
        float32.write(f, self.follow_scale1)
        float32.write(f, self.follow_speed2)
        float32.write(f, self.follow_scale2)
        self.spline_points.write(f)
        self.enabled_in.write(f)

        if self.m2_version >= M2Versions.CATA:
            self.multi_texture_param0.write(f)
            self.multi_texture_param1.write(f)

        return self

    def to_obj(self):
        return {
            "particle_id": self.particle_id,
            "flags": self.flags,
            "position": list(self.position),
            "bone": self.bone,
            "texture": self.texture,
            "geometry_model_filename": self.geometry_model_filename.to_obj(),
            "recursion_model_filename": self.recursion_model_filename.to_obj(),
            "blending_type": self.blending_type,
            "emitter_type": self.emitter_type,
            "particle_color_index": self.particle_color_index,
            "particle_type": self.particle_type,
            "head_or_tail": self.head_or_tail,
            "texture_tile_rotation": self.texture_tile_rotation,
            "texture_dimensions_rows": self.texture_dimensions_rows,
            "texture_dimensions_columns": self.texture_dimension_columns,
            "emission_speed": self.emission_speed.to_obj(),
            "speed_variation": self.speed_variation.to_obj(),
            "vertical_range": self.vertical_range.to_obj(),
            "horizontal_range": self.horizontal_range.to_obj(),
            "gravity": self.gravity.to_obj(),
            "lifespan": self.lifespan.to_obj(),
            "life_span_vary": self.life_span_vary.to_obj(),
            "emission_rate_vary": self.emission_rate_vary.to_obj(),
            "emission_rate": self.emission_rate.to_obj(),
            "emission_area_length": self.emission_area_length.to_obj(),
            "emission_area_width": self.emission_area_width.to_obj(),
            "z_source": self.z_source.to_obj(),
            "color_track": self.color_track.to_obj(),
            "alpha_track": self.alpha_track.to_obj(),
            "scale_track": self.scale_track.to_obj(),
            "scale_vary": list(self.scale_vary),
            "head_cell_track": self.head_cell_track.to_obj(),
            "tail_cell_track": self.tail_cell_track.to_obj(),
            "tail_length": self.tail_length,
            "twinkle_speed": self.twinkle_speed,
            "twinkle_scale": self.twinkle_scale.to_obj(),
            "burst_multiplier": self.burst_multiplier,
            "drag": self.drag,
            "basespin": self.basespin,
            "base_spin_vary": self.base_spin_vary,
            "spin": self.spin,
            "tumble": self.tumble.to_obj(),
            "wind_vector": list(self.wind_vector),
            "wind_time": self.wind_time,
            "follow_speed1": self.follow_speed1,
            "follow_scale1": self.follow_scale1,
            "follow_speed2": self.follow_speed2,
            "follow_scale2": self.follow_scale2,
            "spline_points": self.spline_points.to_obj(),
            "enabled_in": self.enabled_in.to_obj(),
        }

#############################################################
######                  Miscellaneous                  ######
#############################################################

###### Lights ######

class M2Light:

    def __init__(self):
        self.type = 1                                                    # Types are listed below.
        self.bone = -1                                                   # -1 if not attached to a bone
        self.position = (0.0, 0.0, 0.0)                                  # relative to bone, if given
        self.ambient_color = M2Track(vec3D, M2Light)
        self.ambient_intensity = M2Track(float32, M2Light)               # defaults to 1.0
        self.diffuse_color = M2Track(vec3D, M2Light)
        self.diffuse_intensity = M2Track(float32, M2Light)
        self.attenuation_start = M2Track(float32, M2Light)
        self.attenuation_end = M2Track(float32, M2Light)
        self.visibility = M2Track(uint8, M2Light)                        # enabled?

    def read(self, f):
        self.type = uint16.read(f)
        self.bone = int16.read(f)
        self.position = vec3D.read(f)
        self.ambient_color.read(f)
        self.ambient_intensity.read(f)
        self.diffuse_color.read(f)
        self.diffuse_intensity.read(f)
        self.attenuation_start.read(f)
        self.attenuation_end.read(f)
        self.visibility.read(f)

        return self

    def write(self, f):
        uint16.write(f, self.type)
        int16.write(f, self.bone)
        vec3D.write(f, self.position)
        self.ambient_color.write(f)
        self.ambient_intensity.write(f)
        self.diffuse_color.write(f)
        self.diffuse_intensity.write(f)
        self.attenuation_start.write(f)
        self.attenuation_end.write(f)
        self.visibility.write(f)

        return self

    def to_obj(self):
        return {
            "type": self.type,
            "bone": self.bone,
            "position": list(self.position),
            "ambient_color": self.ambient_color.to_obj(),
            "ambient_intensity": self.ambient_intensity.to_obj(),
            "diffuse_color": self.diffuse_color.to_obj(),
            "diffuse_intensity": self.diffuse_intensity.to_obj(),
            "attenuation_start": self.attenuation_start.to_obj(),
            "attenuation_end": self.attenuation_end.to_obj(),
            "visibility": self.visibility.to_obj(),
        }

    @staticmethod
    def size():
        return 156 if M2VersionsManager().m2_version >= M2Versions.WOTLK else 212


###### Cameras ######

class M2Camera:

    def __init__(self):
        self.m2_version = M2VersionsManager().m2_version

        self.type = 0                                                     # 0: portrait, 1: characterinfo; -1: else (flyby etc.); referenced backwards in the lookup table.
        if self.m2_version < M2Versions.CATA:
            self.fov = 0.0                                                # Diagonal FOV in radians. See below for conversion.

        self.far_clip = 0.0
        self.near_clip = 0.0
        self.positions = M2Track(M2SplineKey << vec3D, M2Camera)          # positions; // How the camera's position moves. Should be 3*3 floats.
        self.position_base = (0.0, 0.0, 0.0)
        self.target_position = M2Track(M2SplineKey << vec3D, M2Camera)    # How the target moves. Should be 3*3 floats.
        self.target_position_base = (0.0, 0.0, 0.0)
        self.roll = M2Track(M2SplineKey << float32, M2Camera)             # The camera can have some roll-effect. Its 0 to 2*Pi.
        if self.m2_version >= M2Versions.CATA:
            self.fov = M2Track(M2SplineKey << float32, M2Camera)          # Diagonal FOV in radians. float vfov = dfov / sqrt(1.0 + pow(aspect, 2.0));

    def read(self, f):
        self.type = int32.read(f)
        if self.m2_version < M2Versions.CATA:
            self.fov = float32.read(f)
        self.far_clip = float32.read(f)
        self.near_clip = float32.read(f)
        self.positions.read(f)
        self.position_base = vec3D.read(f)
        self.target_position.read(f)
        self.target_position_base = vec3D.read(f)
        self.roll.read(f)
        if self.m2_version >= M2Versions.CATA:
            self.fov.read(f)
            
        return self

    def write(self, f):
        int32.write(f, self.type)
        if self.m2_version < M2Versions.CATA:
            float32.write(f, self.fov)
        float32.write(f, self.far_clip)
        float32.write(f, self.near_clip)
        self.positions.write(f)
        vec3D.write(f, self.position_base)
        self.target_position.write(f)
        vec3D.write(f, self.target_position_base)
        self.roll.write(f)
        if self.m2_version >= M2Versions.CATA:
            self.fov.write(f)

        return self

    def to_obj(self):
        return {
            "type": self.type,
            "fov": self.fov,
            "far_clip": self.far_clip,
            "near_clip": self.near_clip,
            "positions": self.positions.to_obj(),
            "position_base": list(self.position_base),
            "target_position": self.target_position.to_obj(),
            "target_position_base": list(self.target_position_base),
            "roll": self.roll.to_obj()
        }

    @staticmethod
    def size():
        tracks = 60 if M2VersionsManager().m2_version >= M2Versions.WOTLK else 84
        return tracks + 40 if M2VersionsManager().m2_version < M2Versions.CATA else tracks + 64


###### Attachments ######

class M2Attachment:

    def __init__(self):
        self.id = 0                                             # Referenced in the lookup-block below.
        self.bone = 0                                           # attachment base
        self.unknown = 0                                        # see BogBeast.m2 in vanilla for a model having values here
        self.position = (0.0, 0.0, 0.0)                         # relative to bone; Often this value is the same as bone's pivot point
        self.animate_attached = M2Track(boolean, M2Attachment)  # whether or not the attached model is animated when this model is. only a bool is used. default is true.

    def read(self, f):
        self.id = uint32.read(f)
        self.bone = uint16.read(f)
        self.unknown = uint16.read(f)
        self.position = vec3D.read(f)
        self.animate_attached.read(f)

        return self

    def write(self, f):
        uint32.write(f, self.id)
        uint16.write(f, self.bone)
        uint16.write(f, self.unknown)
        vec3D.write(f, self.position)
        self.animate_attached.write(f)

        return self

    def to_obj(self):
        return {
            "id": self.id,
            "bone": self.bone,
            "unknown": self.unknown,
            "position": list(self.position),
            "animate_attached": self.animate_attached.to_obj()
        }

    @staticmethod
    def size():
        return 40 if M2VersionsManager().m2_version >= M2Versions.WOTLK else 48


###### Events ######

class M2Event:

    def __init__(self):
        self.identifier = ""
        self.data = 0
        self.bone = 0
        self.position = (0.0, 0.0, 0.0)
        self.enabled = M2TrackBase()

    def read(self, f):
        self.identifier = string.read(f, 4).decode('utf-8')
        self.data = uint32.read(f)
        self.bone = uint32.read(f)
        self.position = vec3D.read(f)   
        self.enabled.read(f)
        
        return self

    def write(self, f):
        string.write(f, self.identifier.encode('utf-8'), 4)
        uint32.write(f, self.data)
        uint32.write(f, self.bone)  
        vec3D.write(f, self.position)
        self.enabled.write(f)

        return self

    def to_obj(self):
        return {
            "identifier": self.identifier,
            "data": self.data,
            "bone": self.bone,
            "position": list(self.position),
            "enabled": self.enabled.to_obj()
        }

    @staticmethod
    def size():
        return 36 if M2VersionsManager().m2_version >= M2Versions.WOTLK else 44


#############################################################
######                  M2 Header                      ######
#############################################################

class M2Header:

    def __init__(self):
        self.m2_version = M2VersionsManager().m2_version

        self._size = 324 if self.m2_version <= M2Versions.TBC else 304

        self.magic = 'MD20'
        self.version = self.m2_version
        self.name = M2String()
        self.global_flags = 0
        self.global_sequences = M2Array(uint32)
        self.sequences = M2Array(M2Sequence)
        self.sequence_lookup = M2Array(uint16)

        if self.m2_version <= M2Versions.TBC:
            self.playable_animation_lookup = M2Array(uint32)

        self.bones = M2Array(M2CompBone)

        self.key_bone_lookup = M2Array(int16)
        self.vertices = M2Array(M2Vertex)

        if self.m2_version <= M2Versions.TBC:
            self.skin_profiles = M2Array(M2SkinProfile)
        else:
            self.num_skin_profiles = 1

        self.colors = M2Array(M2Color)
        self.textures = M2Array(M2Texture)
        self.texture_weights = M2Array(M2Track << (fixed16, M2Header))

        if self.m2_version <= M2Versions.TBC:
            self.unknown = M2Array(uint16)

        self.texture_transforms = M2Array(M2TextureTransform)
        self.replacable_texture_lookup = M2Array(int16)
        self.materials = M2Array(M2Material)
        self.bone_lookup_table = M2Array(uint16)
        self.texture_lookup_table = M2Array(uint16)
        self.tex_unit_lookup_table = M2Array(int16)
        self.transparency_lookup_table = M2Array(uint16)

        self.texture_transforms_lookup_table = M2Array(int16)
        
        self.bounding_box = CAaBox()
        self.bounding_sphere_radius = 0.0

        self.collision_box = CAaBox()
        self.collision_sphere_radius = 0.0
        
        self.collision_triangles = M2Array(uint16)
        self.collision_vertices = M2Array(vec3D)
        self.collision_normals = M2Array(vec3D)
        self.attachments = M2Array(M2Attachment)
        self.attachment_lookup_table = M2Array(uint16)
        self.events = M2Array(M2Event)
        self.lights = M2Array(M2Light)
        self.cameras = M2Array(M2Camera)
        self.camera_lookup_table = M2Array(uint16)
        self.ribbon_emitters = M2Array(M2Ribbon)
        self.particle_emitters = M2Array(M2Particle)

        if self.m2_version >= M2Versions.WOTLK:
            self.texture_combiner_combos = M2Array(uint16)
            self._size += 8

    def read(self, f):
        self.version = uint32.read(f)

        M2VersionsManager().set_m2_version(self.version)

        self.name.read(f)
        self.global_flags = uint32.read(f)
        self.global_sequences.read(f)
        self.sequences.read(f)
        self.sequence_lookup.read(f)

        if self.m2_version <= M2Versions.TBC:
            self.playable_animation_lookup.read(f)

        M2ExternalSequenceCache(self)

        self.bones.read(f)

        self.key_bone_lookup.read(f)
        self.vertices.read(f)

        if self.m2_version <= M2Versions.TBC:
            self.skin_profiles.read(f)
        else:
            self.num_skin_profiles = uint32.read(f)

        self.colors.read(f)
        self.textures.read(f)
        self.texture_weights.read(f)
        
        if self.m2_version <= M2Versions.TBC:
            self.unknown.read(f)

        self.texture_transforms.read(f)
        self.replacable_texture_lookup.read(f)
        self.materials.read(f)
        self.bone_lookup_table.read(f)
        self.texture_lookup_table.read(f)
        self.tex_unit_lookup_table.read(f)
        self.transparency_lookup_table.read(f)
        self.texture_transforms_lookup_table.read(f)

        self.bounding_box.read(f)
        self.bounding_sphere_radius = float32.read(f)
        self.collision_box.read(f)
        self.collision_sphere_radius = float32.read(f)

        self.collision_triangles.read(f)
        self.collision_vertices.read(f)
        self.collision_normals.read(f)
        self.attachments.read(f)

        self.attachment_lookup_table.read(f)
        self.events.read(f)
        self.lights.read(f)
        self.cameras.read(f)

        self.camera_lookup_table.read(f)
        self.ribbon_emitters.read(f)
        self.particle_emitters.read(f)

        if self.m2_version >= M2Versions.WOTLK and self.global_flags & M2GlobalFlags.UseTextureCombinerCombos:
            self.texture_combiner_combos.read(f)

        return self

    def write(self, f):
        MemoryManager.mem_reserve(f, self._size)

        f.write(self.magic.encode('utf-8'))
        uint32.write(f, self.version)
        self.name.write(f)
        uint32.write(f, self.global_flags)
        self.global_sequences.write(f)
        self.sequences.write(f)
        self.sequence_lookup.write(f)

        if self.m2_version <= M2Versions.TBC:
            self.playable_animation_lookup.write(f)

        self.bones.write(f)

        self.key_bone_lookup.write(f)
        self.vertices.write(f)

        if self.m2_version <= M2Versions.TBC:
            self.skin_profiles.write(f)
        else:
            uint32.write(f, self.num_skin_profiles)

        self.colors.write(f)
        self.textures.write(f)

        self.texture_weights.write(f)

        if self.m2_version <= M2Versions.TBC:
            self.unknown.write(f)

        self.texture_transforms.write(f)
        self.replacable_texture_lookup.write(f)
        self.materials.write(f)
        self.bone_lookup_table.write(f)
        self.texture_lookup_table.write(f)
        self.tex_unit_lookup_table.write(f)
        self.transparency_lookup_table.write(f)
        self.texture_transforms_lookup_table.write(f)

        self.bounding_box.write(f)
        float32.write(f, self.bounding_sphere_radius)
        self.collision_box.write(f)
        float32.write(f, self.collision_sphere_radius)

        self.collision_triangles.write(f)
        self.collision_vertices.write(f)
        self.collision_normals.write(f)
        self.attachments.write(f)

        self.attachment_lookup_table.write(f)
        self.events.write(f)
        self.lights.write(f)
        self.cameras.write(f)

        self.camera_lookup_table.write(f)
        self.ribbon_emitters.write(f)
        self.particle_emitters.write(f)

        if self.m2_version >= M2Versions.WOTLK and self.global_flags & M2GlobalFlags.UseTextureCombinerCombos:
            self.texture_combiner_combos.write(f)

        return self

    def to_obj(self):
        return {
            "name": self.name.to_obj(),
            "global_flags": self.global_flags,
            "global_sequences": self.global_sequences.to_obj(),
            "sequence_lookup": self.sequence_lookup.to_obj(),
            "bones": self.bones.to_obj(),
            "key_bone_lookup": self.key_bone_lookup.to_obj(),
            "vertices": self.vertices.to_obj(),
            "num_skin_profiles": self.num_skin_profiles,
            "colors": self.colors.to_obj(),
            "textures": self.textures.to_obj(),
            "texture_weights": self.texture_weights.to_obj(),
            "texture_transofmrs": self.texture_transforms.to_obj(),
            "replacable_texture_lookup": self.replacable_texture_lookup.to_obj(),
            "materials": self.materials.to_obj(),
            "bone_lookup_table": self.bone_lookup_table.to_obj(),
            "texture_lookup_table": self.texture_lookup_table.to_obj(),
            "tex_unit_lookup_table": self.tex_unit_lookup_table.to_obj(),
            "transparency_lookup_table": self.transparency_lookup_table.to_obj(),
            "texture_transforms_lookup_table": self.texture_transforms_lookup_table.to_obj(),
            "bounding_box": self.bounding_box.to_obj(),
            "collision_box": self.collision_box.to_obj(),
            "collision_sphere_radius": self.collision_sphere_radius,
            "collision_triangles": self.collision_triangles.to_obj(),
            "collision_normals": self.collision_normals.to_obj(),
            "attachments": self.attachments.to_obj(),
            "attachment_lookup_table": self.attachment_lookup_table.to_obj(),
            "events": self.events.to_obj(),
            "lights": self.lights.to_obj(),
            "cameras": self.cameras.to_obj(),
            "camera_lookup_table": self.camera_lookup_table.to_obj(),
            "ribbon_emitters": self.ribbon_emitters.to_obj(),
            "particle_emitters": self.particle_emitters.to_obj(),
            "texture_combiner_combos": self.texture_combiner_combos.to_obj(),
        }

    def assign_bone_names(self):
        # assign bone names # TODO: rewrite this crap
        bone_type_dict = {}

        for i, attachment in enumerate(self.attachments):
            if attachment.bone > 0:
                bone_type_dict[attachment.bone] = ('AT', i, M2AttachmentTypes.get_attachment_name(
                    self.attachment_lookup_table[attachment.id], i))

        for i, event in enumerate(self.events):
            if event.bone > 0:
                bone_type_dict[event.bone] = ('ET', i, M2EventTokens.get_event_name(event.identifier))

        for i, light in enumerate(self.lights):
            if light.bone > 0:
                bone_type_dict[light.bone] = ('LT', i, light)

        for i, ribbon_emitter in enumerate(self.ribbon_emitters):
            if ribbon_emitter.bone_index > 0:
                bone_type_dict[ribbon_emitter.bone_index] = ('RB', i, ribbon_emitter)

        for i, particle_emitter in enumerate(self.particle_emitters):
            if particle_emitter.bone > 0:
                bone_type_dict[particle_emitter.bone] = ('PT', i, particle_emitter)

        for i, bone in enumerate(self.bones):
            bone.index = i
            bone.build_relations(self.bones)
            bone.load_bone_name(bone_type_dict)


#############################################################
######               M2 Parsing Helpers                ######
#############################################################

@singleton
class M2TrackCache:
    def __init__(self):
        self.m2_tracks = OrderedDict()

    def add_track(self, track, creator):
        self.m2_tracks.setdefault(creator, []).append(track)

    def purge(self):
        self.m2_tracks.clear()





        
        

        


