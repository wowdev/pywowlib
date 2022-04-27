from typing import Protocol, runtime_checkable


@runtime_checkable
class VarTypeProtocol(Protocol):
    _struct_implements_var_type_protocol: bool
    __name__: str

    def __init__(self, name: str, /): ...

    def __repr__(self) -> str: ...

    def __getitem__(self, item) -> 'StructArray': ...

