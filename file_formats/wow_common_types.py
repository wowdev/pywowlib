import struct

from ..io_utils.types import *
from io import SEEK_CUR, BytesIO
from collections.abc import Iterable
from typing import Optional, Protocol, Self

__reload_order_index__ = 1


###### M2 file versions ######

@singleton
class M2VersionsManager:

    def __init__(self):
        self.m2_version = M2Versions.WOTLK

    def set_m2_version(self, version: int):
        self.m2_version = version


@singleton
class M2ExternalSequenceCache:
    def __init__(self, m2_header):
        self.external_sequences = {i: sequence for i, sequence in enumerate(m2_header.sequences)
                                   if not sequence.flags & 0x130}


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
            4: cls.MOP,
            5: cls.WOD,
            6: cls.LEGION,
            7: cls.BFA
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

        self.is_read = False

    def read(self, f, ignore_header=False, ignore_data=False, is_anim_data=False):

        if not ignore_header:
            self.n_elements = uint32.read(f)
            self.ofs_elements = uint32.read(f)

        if ignore_data:
            return self

        pos = f.tell()

        f.seek(self.ofs_elements)

        if not is_anim_data:

            type_t = type(self.type)

            if type_t is GenericType:
                self.values = [self.type.read(f) for _ in range(self.n_elements)]
            else:
                self.values = [self.type().read(f) for _ in range(self.n_elements)]

        else:
            self.values = [self.type().read(f, ignore_data=bool(M2ExternalSequenceCache().external_sequences.get(i)))
                           for i in range(self.n_elements)]

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


class IOProtocol(Protocol):
    def read(self, f) -> Self: ...
    def write(self, f) -> Self: ...


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


class ContentChunkBuffered:  # for inheriting only
    raw_data = None

    def __init__(self):
        self.magic = self.__class__.__name__
        self.size = 0
        self.raw_data = None

    def from_bytes(self, data: bytes):
        self.raw_data = data

    def read(self, f):
        self.size = uint32.read(f)
        return self

    def write(self, f):
        f.write(self.magic[::-1].encode('ascii'))
        uint32.write(f, self.size)
        return self

    def _write_buffered(self, f):
        raw_data = super().__getattribute__('raw_data')
        magic = super().__getattribute__('magic')

        f.write(magic[::-1].encode('ascii'))
        size = len(raw_data)
        self.size = size
        uint32.write(f, size)
        f.write(raw_data)

        return self

    def __getattribute__(self, item):
        raw_data = super().__getattribute__('raw_data')

        if raw_data is not None:
            if item == 'write':
                return super().__getattribute__('_write_buffered')
            elif item == 'read':
                self.raw_data = None
            elif item == 'size':
                return len(raw_data)
            else:
                size = struct.pack('I', len(raw_data))
                super().__getattribute__('read')(BytesIO(size + raw_data))
                self.raw_data = None
                return super().__getattribute__(item)

        return super().__getattribute__(item)


class M2ContentChunk(ContentChunk):  # for inheriting only, M2 files do not have reversed headers

    def write(self, f):
        f.write(self.magic.encode('ascii'))
        uint32.write(f, self.size)
        return self


class M2RawChunk(M2ContentChunk):

    def __init__(self):
        super().__init__()
        self.raw_data = BytesIO()

    def read(self, f):
        super().read(f)

        self.raw_data.write(f.read(self.size))
        self.raw_data.seek(0)

        return self

    def write(self, f):

        self.raw_data.seek(0, 2)
        self.size = self.raw_data.tell()
        self.raw_data.seek(0)
        super().write(f)

        f.write(self.raw_data.read())

        return self


class ArrayChunkBase:  # for internal use only
    item: IOProtocol = None
    data: str = "content"
    raw_data: Optional[bytes] = None
    lazy_read: bool = False

    def __init__(self):
        super().__init__()
        setattr(self, self.data, [])

    def from_bytes(self, data: bytes):
        self.raw_data = data

    def as_bytes(self) -> Optional[bytes]:
        return self.raw_data

    def read(self, f) -> Self:
        super().read(f)

        if self.lazy_read:
            self._read_content_raw(f)
        else:
            self._read_content(f)

        return self

    def _read_content(self, f):
        size = 0

        if isinstance(self.item, Iterable):
            for var in self.item:
                size += var.size()

            setattr(self, self.data, [tuple([var().read(f) for var in self.item]) for _ in range(self.size // size)])

        else:
            setattr(self, self.data, [self.item().read(f) for _ in range(self.size // self.item.size())])

    def _read_content_raw(self, f):
        self.raw_data = f.read(self.size)

    def write(self, f) -> Self:
        self.size = 0

        if isinstance(self.item, Iterable):

            is_generic_type_map = [False] * len(self.item)

            for i, var in enumerate(self.item):
                self.size += var.size()
                is_generic_type_map[i] = isinstance(var, GenericType)

            if self.raw_data is None:
                content = getattr(self, self.data)
                self.size *= len(content)
            else:
                self.size = len(self.raw_data)

            super().write(f)

            if self.raw_data:
                f.write(self.raw_data)
                return self

            for struct in content:
                for i, var in enumerate(struct):

                    if is_generic_type_map[i]:
                        self.item[i].write(f, var)

                    else:
                        var.write(f)

        else:
            content = None
            if self.raw_data is None:
                content = getattr(self, self.data)
                self.size = (len(content) * self.item.size())
            else:
                self.size = len(self.raw_data)

            super().write(f)

            if self.raw_data:
                f.write(self.raw_data)
                return self

            for var in content:

                if isinstance(self.item, GenericType):

                    self.item.write(f, var)

                else:
                    var.write(f)

        return self

    def __getattribute__(self, item):
        raw_data = super().__getattribute__('raw_data')
        if item == super().__getattribute__('data') and raw_data is not None:
            f = BytesIO(raw_data)
            self.size = len(raw_data)
            self._read_content(f)
            self.raw_data = None

        return super().__getattribute__(item)


class ArrayChunk(ArrayChunkBase, ContentChunk):  # for inheriting only
    pass


class M2ArrayChunk(ArrayChunkBase, M2ContentChunk):  # for inheriting only
    pass


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
        uint32.write(f, self.version)

        return self


