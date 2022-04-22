from .struct_protocol import StructFormatType
from .array import StructArray

from typing import Any



class GenericType:
    __slots__ = (
        "format",
        "py_type",
        "size",
        "name"
    )

    def __init__(self, format: str, py_type: Any, size: int, name: str):
        self.format = format
        self.py_type = py_type
        self.size = size
        self.name = name

    def __getitem__(self, item) -> 'StructArray':
        return StructArray(self, item)

    def length(self) -> int:
        return 1


byte = GenericType('s', bytes, 1, 'byte')
int8 = GenericType('b', int, 1, 'int8')
uint8 = GenericType('B', int, 1, 'uint8')
int16 = GenericType('h', int, 2, 'int16')
uint16 = GenericType('H', int, 2, 'uint16')
int32 = GenericType('i', int, 4, 'int32')
uint32 = GenericType('I', int, 4, 'uint32')
int64 = GenericType('q', int, 8, 'int64')
uint64 = GenericType('Q', int, 8, 'uint64')
float16 = GenericType('e', float, 2, 'float16')
float32 = GenericType('f', float, 4, 'float32')
float64 = GenericType('d', float, 8, 'float64')

# aliases
double = GenericType('d', float, 8, 'double')
char = GenericType('s', bytes, 1, 'char')
