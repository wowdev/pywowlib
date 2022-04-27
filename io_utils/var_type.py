from .array import StructArray


class VarType:
    def __init__(self, name: str, /):
        self._struct_implements_var_type_protocol: bool = True
        if not isinstance(name, str):
            raise TypeError("VarType only accepts string tokens. Common usage is T = VarType['T'].")

        self.__name__ = name

    def __repr__(self) -> str:
        return f"~{self.__name__}"

    def __getitem__(self, item) -> StructArray:
        return StructArray(self, item)
