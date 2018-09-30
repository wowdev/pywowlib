from .file_formats.adt_chunks import *
from .file_formats.wow_common_types import ChunkHeader
from io import BufferedReader

__reload_order_index__ = 3


class ADTFile:
    def __init__(self, file=None):

        self.header = MHDR()
        self.textures = MTEX()
        self.model_filenames = []
        self.map_object_filenames = []
        self.model_instances = MDDF()
        self.map_object_instances = MODF()
        self.chunks = [[MCNK() for _ in range(16)] for _ in range(16)]

        if file:
            if type(file) is BufferedReader:
                self.read(file)

            elif type(file) is str:
                with open(file, 'rb') as f:
                    self.read(f)

            else:
                raise NotImplementedError('\nFile argument must be either a filepath string or io.BufferedReader')

    def read(self, f):

        mver = MVER().read(f)

        if mver.version != 18:  # Blizzard has never cared to change it so far
            raise NotImplementedError('Unknown ADT version: ({})'.format(mver.version))

        mhdr = MHDR().read(f)

        # read header chunks

        f.seek(mhdr.mcin)
        mcnk_pointers = MCIN().read(f)

        f.seek(mhdr.mtex)
        self.textures.read(f)

        f.seek(mhdr.mmid)
        mmid = MMID().read(f)

        f.seek(mhdr.mmdx)
        mmdx_header = ChunkHeader().read(f)
        mmdx_data_pos = f.tell()

        assert mmdx_header == 'XDMM'














