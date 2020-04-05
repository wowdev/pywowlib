from ..io_utils.types import *
from io import SEEK_CUR
from collections import Iterable

__reload_order_index__ = 1


###### M2 file versions ######

@singleton
class M2VersionsManager:

    def __init__(self):
        self.m2_version = M2Versions.WOTLK

    def set_m2_version(self, version: int):
        self.m2_version = version


class M2Versions:
    CLASSIC = 256
    TBC = 263
    WOTLK = 264
    CATA = 272
    MOP = 272
    WOD = 273  # ?
    LEGION = 274
    BFA = 274  # TODO: verify

    @classmethod
    def from_expansion_number(cls, exp_num: int):

        v_dict = {
            0: cls.CLASSIC,
            1: cls.TBC,
            2: cls.WOTLK,
            3: cls.CATA,
            4: cls.WOD,
            5: cls.LEGION,
            6: cls.BFA
        }

        return v_dict[exp_num]


#############################################################
######                WoW Common Types                 ######
#############################################################

class CArgb:
    """A color given in values of red, green, blue and alpha"""
    def __init__(self, color=(255, 255, 255, 255)):
        self.r, self.g, self.b, self.a = color

    def read(self, f):
        self.r, self.g, self.b, self.a = uint8.read(f, 4)

    def write(self, f):
        uint8.write(f, (self.r, self.g, self.b, self.a), 4)


class CImVector:
    """A color given in values of blue, green, red and alpha"""
    def __init__(self, color=(255, 255, 255, 255)):
        self.b, self.g, self.r, self.a = color

    def read(self, f):
        self.b, self.g, self.r, self.a = uint8.read(f, 4)

    def write(self, f):
        uint8.write(f, (self.b, self.g, self.r, self.a), 4)


class C3Vector:
    """A three component float vector"""
    def __init__(self, vector=None):
        if vector is None:
            vector = (0.0, 0.0, 0.0)
        self.x, self.y, self.z = vector

    def read(self, f):
        self.x = float32.read(f)
        self.y = float32.read(f)
        self.z = float32.read(f)

        return self

    def write(self, f):
        float32.write(f, self.x)
        float32.write(f, self.y)
        float32.write(f, self.z)

        return self


class C4Plane:
    """A 3D plane defined by four floats"""
    def __init__(self):
        self.normal = (0, 0, 0)
        self.distance = 0.0

    def read(self, f):
        self.normal = vec3D.read(f)
        self.distance = float32.read(f)

        return self

    def write(self, f):
        vec3D.write(f, self.normal)
        float32.write(f, self.distance)

        return self

    @staticmethod
    def size():
        return 16


class CRange:
    """A one dimensional float range defined by the bounds."""
    def __init__(self):
        self.min = 0.0
        self.max = 0.0

    def read(self, f):
        self.min = float32.read(f)
        self.max = float32.read(f)

        return self

    def write(self, f):
        float32.write(f, self.min)
        float32.write(f, self.max)

        return self


class CAaBox:
    """An axis aligned box described by the minimum and maximum point."""
    def __init__(self, min_=None, max_=None):
        if min_ is None:
            min_ = (0.0, 0.0, 0.0)
        if max_ is None:
            max_ = (0.0, 0.0, 0.0)
        self.min = min_
        self.max = max_

    def read(self, f):
        self.min = vec3D.read(f)
        self.max = vec3D.read(f)

        return self

    def write(self, f):
        vec3D.write(f, self.min)
        vec3D.write(f, self.max)

        return self


class fixed_point:
    """A fixed point real number, opposed to a floating point."""
    def __init__(self, type_, dec_bits, int_bits):
        self.type = type_
        self.dec_bits = dec_bits
        self.int_bits = int_bits
        self.value = 0

    def read(self, f):
        fixed_point_val = self.type.read(f)
        decimal_part = fixed_point_val & ((1 << self.dec_bits) - 1)
        integral_part = (fixed_point_val >> self.dec_bits) & (1 << self.int_bits) - 1
        sign = -1.0 if (fixed_point_val & (1 << (self.dec_bits + self.int_bits)) != 0) else 1.0

        self.value = sign * (integral_part + decimal_part / (((1 << self.dec_bits) - 1) + 1.0))

        return self

    def write(self, f):
        sign = 1 if self.value < 0 else 0
        integral_part = int(self.value) & ((1 << self.int_bits) - 1)
        decimal_part = int((self.value - int(self.value)) * (1 << self.dec_bits))
        fixed_point_val = (sign << (self.int_bits + self.dec_bits)) | (integral_part << self.int_bits) | decimal_part

        self.type.write(f, fixed_point_val)

        return self


fixed16 = uint16


class MemoryManager:
    @staticmethod
    def mem_reserve(f, n_bytes):
        if n_bytes:
            pos = f.tell()
            f.seek(pos + n_bytes)
            f.write(b'\0')
            f.seek(pos)

    @staticmethod
    def ofs_request(f):
        pos = f.tell()
        ofs = f.seek(0, 2)
        f.seek(pos)
        return ofs


class M2Array(metaclass=Template):
    def __init__(self, type_):
        self.n_elements = 0
        self.ofs_elements = 0
        self.type = type_
        self.values = []

    def read(self, f, ignore_header=False):
        if not ignore_header:
            self.n_elements = uint32.read(f)
            self.ofs_elements = uint32.read(f)

        pos = f.tell()

        try:
            f.seek(self.ofs_elements)

            type_t = type(self.type)

            if type_t is GenericType:
                self.values = [self.type.read(f) for _ in range(self.n_elements)]
            else:
                self.values = [self.type().read(f) for _ in range(self.n_elements)]
        except EOFError:
            self.values = [self.type()]

        f.seek(pos)

        return self

    def write(self, f):
        ofs = MemoryManager.ofs_request(f)
        uint32.write(f, len(self.values))
        uint32.write(f, ofs if len(self.values) else 0)

        pos = f.tell()
        f.seek(ofs)

        type_t = type(self.type)

        if type_t is not partial:
            if hasattr(self.type, 'size'):
                MemoryManager.mem_reserve(f, len(self.values) * self.type.size())
        elif hasattr(self.type.func, 'size'):
            MemoryManager.mem_reserve(f, len(self.values) * self.type.func.size())

        if type_t is GenericType:
            for value in self.values:
                self.type.write(f, value)
        else:
            for value in self.values:
                value.write(f)
        f.seek(pos)

        return self

    def __getitem__(self, item):
        return self.values[item]

    def append(self, value):
        self.values.append(value)

    def add(self, value):
        self.values.append(value)
        return len(self.values) - 1

    def extend(self, itrbl):
        self.values.extend(itrbl)

    def prepend(self, itrbl):
        self.values = itrbl[:].extend(self.values)

    def new(self):
        self.values.append(self.type())
        return self.values[-1]

    def from_iterable(self, itrbl):
        self.values = [self.type(item) for item in itrbl]

    def set(self, itrbl):
        self.values = itrbl

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return self.values.__iter__()

    @staticmethod
    def size():
        return uint32.size() * 2


class ContentChunk:  # for inheriting only

    def __init__(self):
        self.magic = self.__class__.__name__
        self.size = 0

    def read(self, f):
        self.size = uint32.read(f)
        return self

    def write(self, f):
        f.write(self.magic[::-1].encode('ascii'))
        uint32.write(f, self.size)
        return self


class ArrayChunk(ContentChunk):
    item = None
    data = "content"

    def __init__(self):
        super().__init__()
        setattr(self, self.data, [])

    def read(self, f):
        super().read(f)

        size = 0

        if isinstance(self.item, Iterable):
            for var in self.item:
                size += var.size()

            setattr(self, self.data, [tuple([var().read(f) for var in self.item]) for _ in range(self.size // size)])

        else:
            setattr(self, self.data, [self.item().read(f) for _ in range(self.size // self.item.size())])

        return self

    def write(self, f):
        content = getattr(self, self.data)

        if isinstance(self.item, Iterable):
            for var in self.item:
                self.size += var.size()

            super().write(f)

            for struct in content:
                for var in struct:
                    var.write(f)

        else:
            self.size = len(content) * self.item.size()

            super().write(f)

            for var in content:
                var.write(f)

        return self


class StringBlock:
    """A block of zero terminated strings."""

    def __init__(self, size=0, padding=0):
        self.strings = []
        self.size = size
        self.padding = padding

    def read(self, f):
        cur_str = ""

        for _ in range(self.size):
            # byte = f.read(1)
            # if byte != b'\x00':
            #     cur_str += byte.decode('ascii')
            charcode = uint8.read(f)
            if charcode:
                cur_str += chr(charcode)
            elif cur_str:
                self.strings.append(cur_str)
                cur_str = ""
                f.seek(self.padding, SEEK_CUR)

        return self

    def write(self, f):
        for str_ in self.strings:
            f.write((str_ + '\x00').encode())
            f.seek(self.padding, SEEK_CUR)

    def _add(self, str_):
        self.size += len(str_) + 1
        self.strings.append(str_)
        
    def _replace(self, index, str_):
        size_change = len(str_) - len(self.strings[index])
        self.strings[index] = str_
        self.size += size_change

    def _remove(self, index):
        self.size -= len(self.strings[index]) + 1
        del self.strings[index]

    def __getitem__(self, index):
        return self.strings[index]

    def __len__(self):
        return len(self.strings)


'''
class StringBlockChunk:
    magic = ""

    def __init__(self):
        self.header = ChunkHeader(self.magic)
        self.filenames = StringBlock()

    def read(self, f):
        self.header.read(f)
        self.filenames.size = self.header.size
        self.filenames.read(f)

        return self

    def write(self, f):
        self.header.size = self.filenames.size
        self.header.write(f)
        self.filenames.write(f)

        return self
        
'''


class MVER(ContentChunk):
    """ Version of the file. Actually meaningless. """

    def __init__(self, version=0):
        super().__init__()
        self.size = 4
        self.version = version

    def read(self, f):
        super().read(f)
        self.version = uint32.read(f)

        return self

    def write(self, f):
        super().write(f)
        uint32.write(self.version)

        return self


