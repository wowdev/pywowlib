from typing import Any


class GenericType:
    __slots__ = (
        "format",
        "py_type",
        "size"
    )

    def __init__(self, format: str, py_type: Any, size: int):
        self.format = format
        self.py_type = py_type
        self.size = size


byte = GenericType('s', bytes, 1)
int8 = GenericType('b', int, 1)
uint8 = GenericType('B', int, 1)
int16 = GenericType('h', int, 2)
uint16 = GenericType('H', int, 2)
int32 = GenericType('i', int, 4)
uint32 = GenericType('I', int, 4)
int64 = GenericType('q', int, 8)
uint64 = GenericType('Q', int, 8)
float16 = GenericType('e', float, 2)
float32 = GenericType('f', float, 4)
float64 = GenericType('d', float, 8)

# aliases
double = float64
char = byte
