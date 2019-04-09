from io import BytesIO
from .wow_common_types import ChunkHeader
from .m2_format import *
from .m2_chunks import AFID, BFID


class PHYS:

    def __init__(self, size=4):
        self.header = ChunkHeader(magic='SYHP')
        self.header.size = size
        self.version = 0

    def read(self, f):
        self.version = int16.read(f)

    def write(self, f):
        self.header.size = 4
        self.header.write(f)
        int16.write(f, self.version)


class PHYV:

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='VYHP')
        self.header.size = size

    def read(self, f):
        pass
    def write(self, f):
        pass

class PHYT:

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='TYHP')
        self.header.size = size

    def read(self, f):
        pass
    def write(self, f):
        pass

class BODY:

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='YDOB')
        self.header.size = size

    def read(self, f):
        pass
    def write(self, f):
        pass

class BDY2(BODY):
    pass

class BDY3(BODY):
    pass

class BDY4(BODY):
    pass


class SHAP:

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='PAHS')
        self.header.size = size

    def read(self, f):
        pass
    def write(self, f):
        pass

class SHP2(SHAP):
    pass


#TODO: create shape types enum


class PLYT:

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='TYLP')
        self.header.size = size

    def read(self, f):
        pass
    def write(self, f):
        pass

class JOIN:

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='NIOJ')
        self.header.size = size

    def read(self, f):
        pass
    def write(self, f):
        pass

#TODO: create joint types enum


class WELJ:

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='JLEW')
        self.header.size = size

    def read(self, f):
        pass
    def write(self, f):
        pass

class WLJ2(WELJ):
    pass

class SPHJ:

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='JHPS')
        self.header.size = size

    def read(self, f):
        pass
    def write(self, f):
        pass

class SHOJ:

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='JHOS')
        self.header.size = size

    def read(self, f):
        pass
    def write(self, f):
        pass

class PRSJ:

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='JSRP')
        self.header.size = size

    def read(self, f):
        pass
    def write(self, f):
        pass

class REVJ:

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='JVER')
        self.header.size = size

    def read(self, f):
        pass
    def write(self, f):
        pass

class DSTJ:

    def __init__(self, size=0):
        self.header = ChunkHeader(magic='JTSD')
        self.header.size = size

    def read(self, f):
        pass
    def write(self, f):
        pass