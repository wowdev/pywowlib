from .ctypes import *

from io import IOBase
from types import FunctionType
from typing import Protocol, Self, runtime_checkable


@runtime_checkable
class StructIOProtocol(Protocol):
    def write(self, f: IOBase) -> Self: ...
    def read(self, f: IOBase) -> Self: ...
    def size(self) -> int: ...


class StructMeta(type):

    def __new__(mcs, classname, bases, cls_dict):
        annotations = cls_dict.get('__annotations__')
        if annotations is None:
            raise RuntimeError("Empty structs are not supported. A struct must contain data-type annotations.")

        is_plain_old_data = False

        data_fields = {}
        logic_fields = {}

        for attr_name, annotation_type in annotations.items():

            # skip fields that do not represent the data layout
            if not isinstance(annotation_type, StructIOProtocol) or not isinstance(annotation_type, GenericType):
                continue



        for attr_name, attribute in cls_dict.items():
            if isinstance(attribute, FunctionType) or (annotation_type := annotations.get(attr_name) is None):
                continue




            annotations.get(attr_name)

        return type.__new__(mcs, classname, bases, cls_dict)