from io import IOBase
from typing import Protocol, List, Union, Tuple, Any, Optional, Dict, Type, Set, TypeVar, runtime_checkable


StructFormatType = List[Union[Tuple[str, str, Any, Optional[Any], int], 'StructFormatType']]


@runtime_checkable
class StructIOProtocol(Protocol):
    _struct_is_template: bool
    _struct_is_resolved: bool

    def write(self, f: IOBase) -> 'StructIOProtocol': ...
    def read(self, f: IOBase) -> 'StructIOProtocol': ...

    @classmethod
    def _struct_format_chunked(cls) -> StructFormatType: ...

    @classmethod
    def _struct_get_template_arg_sig(cls) -> Set[str]: ...

    @classmethod
    def length(cls) -> int: ...
