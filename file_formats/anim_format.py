import struct

from io import BytesIO

from .wow_common_types import M2RawChunk


class AFM2(M2RawChunk):
    pass


class AFSA(M2RawChunk):
    pass


class AFSB(M2RawChunk):
    pass


class AnimFile:

    def __init__(self, split=False, old=True):

        self.old = old
        self.split = split

        if old:
            self.raw_data = BytesIO()
        else:
            self.afm2 = AFM2()
            self.afsa, self.afsb = (AFSA(), AFSB()) if split else (None, None)

    def read(self, f):

        if self.old:
            self.raw_data.write(f.read())
            self.raw_data.seek(0)

        else:

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

                magic_lower = magic.lower()

                local_chunk = getattr(self, magic_lower)

                if not local_chunk:
                    setattr(self, magic_lower, chunk().read(f))
                else:
                    local_chunk.read(f)

        return self

    def write(self, f):

        if self.old:
            f.write(bytes(self.raw_data.getbuffer()))

        else:

            self.afm2.write(f)

            if self.afsa:
                self.afsa.write(f)

            if self.afsb:
                self.afsb.write(f)

        return self





