from .struct_protocol import StructIOProtocol
from .ctypes import GenericType

from typing import Callable, Dict, List
from collections.abc import Iterable


class StructContext:
    pass


class LogicExpr:
    __slots__ = ()


class If(LogicExpr):
    __slots__ = ('expr',)
    expr: Callable[[StructContext], bool]

    def __init__(self, expr: Callable[[StructContext], bool]):
        self.expr = expr


class Elif(If):
    pass


class Else(LogicExpr):
    __slots__ = ()


class Endif(LogicExpr):
    __slots__ = ()


ConditionalScope = Dict[str, GenericType | StructIOProtocol] | LogicExpr


class Conditional:
    _logic_tree: List[ConditionalScope | List[ConditionalScope]]

    def __init__(self, *args: Iterable[Dict[str, GenericType | StructIOProtocol] | LogicExpr]):
        self._parse_logic_scope(args)
        self._logic_tree = []

    def _parse_logic_scope(self,
                           args: Iterable[Dict[str, GenericType | StructIOProtocol] | LogicExpr]
                           ) -> List[ConditionalScope | List[ConditionalScope]]:

        if not len(args):
            raise SyntaxError("Empty conditionals are not allowed.")

        if not isinstance(args[0], If):
            raise SyntaxError("Conditional statements must begin with an If token.")

        
        for arg in args:
            if isinstance(arg, If):

        


