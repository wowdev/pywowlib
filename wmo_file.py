import os
import struct

from .file_formats import wmo_format_root
from .file_formats.wmo_format_root import *
from .file_formats import wmo_format_group
from .file_formats.wmo_format_group import *
from .io_utils.types import uint32


class WMOFile:

    def __init__(self, version, filepath=None):
        self.version = version
        self.filepath = filepath
        self.display_name = os.path.basename(os.path.splitext(filepath)[0])
        self.groups = []

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
                    magic = f.read(4).decode('utf-8')
                    size = uint32.read(f)
                except EOFError:
                    break

                except struct.error:
                    break

                except UnicodeDecodeError:
                    print('\nAttempted reading non-chunked data.')
                    break

                magic_reversed = magic[::-1].upper()

                if magic_reversed == 'MOHD':
                    is_root = True

                # getting the correct chunk parsing class
                chunk = getattr(wmo_format_root, magic_reversed, None)

                # skipping unknown chunks
                if chunk is None:
                    print("\nEncountered unknown chunk \"{}\"".format(magic_reversed))
                    f.seek(size, 1)
                    continue

                read_chunk = chunk(size=size)
                read_chunk.read(f)
                setattr(self, magic_reversed.lower(), read_chunk)

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


class WMOGroupFile:

    def __init__(self, version, root, filepath=None):
        self.version = version
        self.filepath = filepath
        self.root = root

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
        self.motv2 = MOTV()
        self.mocv2 = MOCV()

    def read(self):
        with open(self.filepath, 'rb') as f:

            is_mocv_processed = False
            is_motv_processed = False

            while True:
                try:
                    magic = f.read(4).decode('utf-8')
                    size = uint32.read(f)
                except EOFError:
                    break

                except struct.error:
                    break

                except UnicodeDecodeError:
                    print('\nAttempted reading non-chunked data.')
                    break

                magic_reversed = magic[::-1]
                magic_reversed_upper = magic_reversed.upper()

                # getting the correct chunk parsing class
                chunk = getattr(wmo_format_group, magic_reversed_upper, None)

                # skipping unknown chunks
                if chunk is None:
                    print("\nEncountered unknown chunk \"{}\"".format(magic_reversed_upper))
                    f.seek(size, 1)
                    continue

                read_chunk = chunk(size=size)
                read_chunk.read(f)

                # handle duplicate chunk reading
                field_name = magic_reversed.lower()
                if isinstance(read_chunk, MOTV):
                    if is_motv_processed:
                        field_name += '2'
                    else:
                        is_motv_processed = True

                if isinstance(read_chunk, MOCV):
                    if is_mocv_processed:
                        field_name += '2'
                    else:
                        is_mocv_processed = True

                setattr(self, field_name, read_chunk)

    def write(self):

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
            self.mogp.header.Size = f.tell() - 20

            # write header
            f.seek(0xC)
            self.mogp.write(f)


