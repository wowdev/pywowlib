from .ctypes import *

from io import IOBase
from types import FunctionType
from typing import Protocol, List, Union, Tuple, Any, Optional, runtime_checkable


class StructError(Exception):
    pass

T = List[Union[Tuple[str, str, Any, Optional[Any], int], 'T_f']]
@runtime_checkable
class StructIOProtocol(Protocol):
    def write(self, f: IOBase) -> 'StructIOProtocol': ...
    def read(self, f: IOBase) -> 'StructIOProtocol': ...

    '''
    @classmethod
    def size(self) -> int: ...

    @classmethod
    def is_pod(cls) -> bool: ...

    @classmethod
    def type_of(cls, name: str) -> Union[GenericType, 'StructIOProtocol']: ...
    '''

    @classmethod
    def _struct_format_chunked(cls) -> T: ...


def recurse_format_chunks(format_chunks: T) -> str:

    for i, (attr_name, format, default_value, n_values) in enumerate(format_chunks):
        if n_values == 0:
            continue

        is_trivial = not isinstance(format, list)

        # handle basic data types
        if is_trivial:
            if n_values == 1:
                yield format
            else:
                yield f"{n_values}{format}"
        else:
            for i in range(n_values):
                yield from recurse_format_chunks(format)



class StructMeta(type):

    def __new__(mcs, classname, bases, cls_dict):
        annotations = cls_dict.get('__annotations__')
        if annotations is None:
            raise StructError(f"Struct <'{classname}'>: Empty structs are not supported. "
             "A struct must contain data-type annotations.")

        is_plain_old_data = False

        format_chunks: T = []

        for attr_name, annotation_type in annotations.items():

            # skip fields that do not represent the data layout
            is_sub_struct = isinstance(annotation_type, StructIOProtocol)
            if not is_sub_struct and not isinstance(annotation_type, GenericType):
                continue

            if is_sub_struct:
                # handle nested structures
                format_chunks.append((attr_name, annotation_type._struct_format_chunked(), None, 1))

                if attr_name in cls_dict:
                    raise StructError(f"Struct <'{classname}'>: Default values are only supported for basic data types. "
                                      f"Field '{attr_name}' must not have a default value.")


            else:
                # handle plain types
                default_value = cls_dict.get(attr_name)

                # check if provided default value is of correct type
                if default_value is not None and not isinstance(default_value, annotation_type.py_type):
                    raise TypeError(f"Struct <'{classname}'>: Default value provided for field '{attr_name}' is "
                        f"'{str(type(default_value))}', expected '{str(type(annotation_type.py_type))}'")

                format_chunks.append((attr_name, annotation_type.format, default_value, 1))

        # pack format
        format_processed = "".join(recurse_format_chunks(format_chunks))

        cls_dict['format_chunks'] = format_chunks
        cls_dict['write'] = StructMeta._struct_format_chunked
        cls_dict['read'] = StructMeta.read
        cls_dict['write'] = StructMeta.write

        print(format_processed)


        return type.__new__(mcs, classname, bases, cls_dict)

    def write(self, f: IOBase) -> StructIOProtocol:
        return self

    def read(self, f: IOBase) -> StructIOProtocol:
        return self

    def _struct_format_chunked(cls) -> T:
        return cls.format_chunks
