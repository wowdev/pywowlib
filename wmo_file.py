import os
import struct

from .file_formats import wmo_format_root
from .file_formats.wmo_format_root import *
from .file_formats import wmo_format_group
from .file_formats.wmo_format_group import *


class WMOFile:

    def __init__(self, version, filepath=None):
        self.version = version
        self.filepath = filepath
        self.display_name = os.path.basename(os.path.splitext(filepath)[0])
        self.groups : List[WMOGroupFile] = []
        self.export = True

        self._texture_lookup = {}
        self._doodad_lookup = {}

        # initialize chunks
        self.mver = MVER()
        self.mohd = MOHD()
        self.motx = MOTX()
        self.momt = MOMT()
        self.mogn = MOGN()
        self.mogi = MOGI()
        self.mosb = MOSB()
        self.mopv = MOPV()
        self.mopt = MOPT()
        self.mopr = MOPR()
        self.movv = MOVV()
        self.movb = MOVB()
        self.molt = MOLT()
        self.mods = MODS()
        self.modn = MODN()
        self.modd = MODD()
        self.mfog = MFOG()
        self.mcvp = MCVP()

    def read(self):

        if self.filepath:
            n_groups = self.read_chunks()
            root_name = os.path.splitext(self.filepath)[0]

            for i in range(n_groups):
                group_path = root_name + "_" + str(i).zfill(3) + ".wmo"

                if not os.path.isfile(group_path):
                    raise FileNotFoundError("\nNot all referenced WMO groups are present in the directory.\a")

                group = WMOGroupFile(self.version, self, filepath=group_path)
                group.read()
                self.groups.append(group)

    def read_chunks(self):
        with open(self.filepath, 'rb') as f:

            is_root = False

            while True:
                try:
                    magic = f.read(4).decode('utf-8')[::-1]

                except EOFError:
                    break

                except struct.error:
                    break

                except UnicodeDecodeError:
                    print('\nAttempted reading non-chunked data.')
                    break

                if not magic:
                    break

                if not is_root and magic == 'MOHD':
                    is_root = True

                # getting the correct chunk parsing class
                chunk = getattr(wmo_format_root, magic, None)

                # skipping unknown chunks
                if chunk is None:
                    print("\nEncountered unknown chunk \"{}\"".format(magic))
                    f.seek(ContentChunk().read(f).size, 1)
                    continue

                magic_lower = magic.lower()
                local_chunk = getattr(self, magic_lower, None)

                if local_chunk:
                    local_chunk.read(f)

                else:
                    setattr(self, magic_lower, chunk().read(f)) \
                        if magic != 'GFID' else setattr(self, magic_lower,
                                                        chunk(use_lods=self.mohd.flags & MOHDFlags.UseLod,
                                                              n_groups=self.mohd.n_groups,
                                                              n_lods=self.mohd.n_lods).read(f))

            # attempt automatically finding a root file if user tries to import the group
            if is_root:
                return self.mohd.n_groups
            else:
                self.filepath = self.filepath[:-8]  # cutting away the group prefix

                if os.path.isfile(self.filepath):
                    return self.read_chunks()
                else:
                    raise FileNotFoundError('\nError: Unable to find WMO root file or it is corrupted.')

    def write(self):

        if self.export:

            # write root chunks
            with open(self.filepath, 'wb') as f:

                self.mver.write(f)
                self.mohd.write(f)
                self.motx.write(f)
                self.momt.write(f)
                self.mogn.write(f)
                self.mogi.write(f)
                self.mosb.write(f)
                self.mopv.write(f)
                self.mopt.write(f)
                self.mopr.write(f)
                self.movv.write(f)
                self.movb.write(f)
                self.molt.write(f)
                self.mods.write(f)
                self.modn.write(f)
                self.modd.write(f)
                self.mfog.write(f)

                # TODO: MCVP and WotLK+

        # write group files
        for group in self.groups:
            group.write()

    def add_group(self):
        filepath = os.path.splitext(self.filepath)[0]
        group = WMOGroupFile(self.version, self, "{}_{}.wmo".format(filepath, str(len(self.groups)).zfill(3)))
        self.groups.append(group)

        return group

    def add_material(  self
                     , diff_texture_1: str
                     , diff_texture_2: str = ""
                     , shader: int = 0
                     , blendmode: int = 0
                     , terrain_type: int = 0
                     , flags: int = 0
                     , emissive_color: Tuple[int, int, int, int] = (0, 0, 0, 0)
                     , diff_color: Tuple[int, int, int, int] = (0, 0, 0, 0)
                    ):

        """ Add new material. Note that colors are BGRA """

        wow_mat = WMOMaterial()

        wow_mat.shader = shader
        wow_mat.blend_mode = blendmode
        wow_mat.terrain_type = terrain_type

        if diff_texture_1:

            if diff_texture_1 not in self._texture_lookup:
                self._texture_lookup[diff_texture_1] = self.motx.add_string(diff_texture_1)

            wow_mat.texture1_ofs = self._texture_lookup[diff_texture_1]

        else:
            raise ReferenceError('\nError. Material must have a diffuse texture.')

        if diff_texture_2:

            if diff_texture_2 not in self._texture_lookup:
                self._texture_lookup[diff_texture_2] = self.motx.add_string(diff_texture_2)

            wow_mat.texture2_ofs = self._texture_lookup[diff_texture_2]

        wow_mat.emissive_color = emissive_color

        wow_mat.diff_color = diff_color

        wow_mat.flags = flags

        mat_index = len(self.momt.materials)

        self.momt.materials.append(wow_mat)

        return mat_index

    def add_doodad_set(self, name: str, n_doodads: int = 0):
        """ Allocate a new doodad set """

        doodad_set = DoodadSet()
        doodad_set.name = name
        doodad_set.start_doodad = len(self.modd.definitions)
        doodad_set.n_doodads = n_doodads

        if name == "Set_$DefaultGlobal":
            self.mods.sets.insert(0, doodad_set)
        else:
            self.mods.sets.append(doodad_set)

    def add_doodad(  self
                   , path: str
                   , position: Tuple[float, float, float]
                   , rotation_quat: Tuple[float, float, float, float]
                   , scale: float
                   , color: Tuple[float, float, float, float]
                   , flags: int

                  ):
        """ Add doodad to last added doodad sets. This method should be called after add_doodad_set.
            Note that colors are BGRA.
        """

        doodad_def = DoodadDefinition()

        path = os.path.splitext(path)[0] + ".MDX"

        doodad_def.name_ofs = self._doodad_lookup.get(path)
        if not doodad_def.name_ofs:
            doodad_def.name_ofs = self.modn.add_string(path)
            self._doodad_lookup[path] = doodad_def.name_ofs

        doodad_def.position = position
        doodad_def.rotation = rotation_quat
        doodad_def.scale = scale
        doodad_def.color = color
        doodad_def.flags = flags

        self.modd.definitions.append(doodad_def)

    def add_light(  self
                  , type: int
                  , unk1: float
                  , unk2: bool
                  , use_attenuation: bool
                  , padding: bool
                  , color: Tuple[int, int, int, int]
                  , position: Tuple[float, float, float]
                  , intensity: float
                  , attenuation_start: float
                  , attenuation_end: float
                 ):
        """ Add light. Not actually a light, rather than a shadow caster. """

        light = Light()
        light.light_type = type

        if light.light_type in {0, 1}:
            light.unknown4 = unk1

        light.type = unk2
        light.use_attenuation = use_attenuation
        light.padding = padding
        light.color = color
        light.position = position
        light.intensity = intensity
        light.attenuation_start = attenuation_start
        light.attenuation_end = attenuation_end

        self.molt.lights.append(light)

    def add_fog(  self
                , big_radius: float
                , small_radius: float
                , color1: Tuple[int, int, int, int]
                , color2: Tuple[int, int, int, int]
                , end_dist: float
                , end_dist2: float
                , position: Tuple[float, float, float]
                , start_factor: float
                , start_factor2: float
                , flags: int
               ):

        """ Add fog sphere. Note that colors are BGRA"""

        fog = Fog()

        fog.big_radius = big_radius
        fog.small_radius = fog.big_radius * (small_radius / 100)

        fog.color1 = color1

        fog.color2 = color2
        fog.end_dist = end_dist
        fog.end_dist2 = end_dist2
        fog.position = position
        fog.start_factor = start_factor
        fog.start_factor2 = start_factor2
        fog.flags = flags

        self.mfog.fogs.append(fog)

    def get_global_bounding_box(self):
        """ Calculate bounding box of an entire scene """
        corner1 = self.mogi.infos[0].bounding_box_corner1
        corner2 = self.mogi.infos[0].bounding_box_corner2

        for gi in self.mogi.infos:
            v = gi.bounding_box_corner1
            if v[0] < corner1[0]:
                corner1[0] = v[0]
            if v[1] < corner1[1]:
                corner1[1] = v[1]
            if v[2] < corner1[2]:
                corner1[2] = v[2]

            v = gi.bounding_box_corner2
            if v[0] > corner2[0]:
                corner2[0] = v[0]
            if v[1] > corner2[1]:
                corner2[1] = v[1]
            if v[2] > corner2[2]:
                corner2[2] = v[2]

        return corner1, corner2


class WMOGroupFile:

    def __init__(self, version, root, filepath=None):
        self.version = version
        self.filepath = filepath
        self.root = root
        self.export = True

        # initialize chunks
        self.mver = MVER()
        self.mogp = MOGP()
        self.mopy = MOPY()
        self.movi = MOVI()
        self.movt = MOVT()
        self.monr = MONR()
        self.motv = MOTV()
        self.moba = MOBA()
        self.molr = MOLR()
        self.modr = MODR()
        self.mobn = MOBN()
        self.mobr = MOBR()
        self.mocv = MOCV()
        self.mliq = MLIQ()
        self.motv2 = None
        self.mocv2 = None

    def read(self):
        with open(self.filepath, 'rb') as f:

            is_mocv_processed = False
            is_motv_processed = False

            while True:
                try:
                    magic = f.read(4).decode('utf-8')[::-1]

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
                chunk = getattr(wmo_format_group, magic, None)

                # skipping unknown chunks
                if chunk is None:
                    print("\nEncountered unknown chunk \"{}\"".format(magic))
                    f.seek(ContentChunk().read(f).size, 1)
                    continue

                low_magic = magic.lower()
                local_chunk = getattr(self, low_magic, None)

                is_mocv = magic == 'MOCV'
                is_motv = magic == 'MOTV'

                if local_chunk and not ((is_mocv and is_mocv_processed) or (is_motv and is_motv_processed)):

                    if is_motv:
                        is_motv_processed = True

                    elif is_mocv:
                        is_mocv_processed = True

                    local_chunk.read(f)

                else:
                    local_chunk = chunk().read(f)

                    # handle duplicate chunk reading
                    if (is_mocv and is_mocv_processed) or (is_motv and is_motv_processed):
                        low_magic += '2'

                    setattr(self, low_magic, local_chunk)

    def write(self):

        if not self.export:
            return

        with open(self.filepath, 'wb') as f:

            self.mver.write(f)

            f.seek(0x58)
            self.mopy.write(f)
            self.movi.write(f)
            self.movt.write(f)
            self.monr.write(f)
            self.motv.write(f)
            self.moba.write(f)

            if self.molr:
                self.molr.write(f)

            if self.modr:
                self.modr.write(f)

            self.mobn.write(f)
            self.mobr.write(f)

            if self.mocv:
                self.mocv.write(f)

            if self.mliq:
                self.mliq.write(f)

            if self.motv2:
                self.motv2.write(f)

            if self.mocv2:
                self.mocv2.write(f)

            # get file size
            f.seek(0, 2)
            self.mogp.size = f.tell() - 20

            # write header
            f.seek(0xC)
            self.mogp.write(f)

    def add_blendmap_chunks(self):
        self.motv2 = MOTV()
        self.mocv2 = MOCV()


