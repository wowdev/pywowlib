import sys

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

            magic = f.read(4).decode('utf-8')

            chunk = getattr(sys.modules[self.__class__.__module__], magic)

            if not chunk:
                raise Exception('\n\nEncountered unknown chunk \"{}\"'.format(magic))

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





