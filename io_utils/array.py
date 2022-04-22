from .struct_protocol import StructIOProtocol, StructFormatType
from .exceptions import StructError

from io import IOBase
from typing import Union, Any, Dict, TypeVar, Optional, Tuple, Set


class StructArray:
    _struct_array_is_generic: bool
    _struct_array_qualifier: Union[int, str, TypeVar]
    _struct_array_type: Union[StructIOProtocol, 'GenericType', TypeVar]

    # compling with StructIOProtocol interface
    _struct_is_template: bool
    _struct_is_resolved: bool
    _struct_is_specified: bool = True

    def __init__(self, u_type: Union[StructIOProtocol, 'GenericType', TypeVar], qualifier: Union[int, TypeVar]):
        # check if any template arguments are passed
        self._struct_is_template = isinstance(u_type, TypeVar) \
                                   or isinstance(qualifier, TypeVar) \
                                   or (isinstance(u_type, StructIOProtocol) and u_type._struct_is_template)
        self.__name__ = 'StructArray'

        if not self._struct_is_template:
            self._struct_is_resolved = True
        else:
            self._struct_is_resolved = False

        # check if underlying type is generic type
        self._struct_array_is_generic = u_type.__class__.__name__ == 'GenericType'

        if not (isinstance(qualifier, int) or isinstance(qualifier, TypeVar)):
            raise TypeError("Arrays can only be specified with integers or template non-type integer variables.")

        self._struct_array_qualifier = qualifier
        self._struct_array_type = u_type

    def write(self: StructIOProtocol, f: IOBase) -> StructIOProtocol: ...

    def read(self: StructIOProtocol, f: IOBase) -> StructIOProtocol: ...

    def _struct_format_chunked(self) -> Union[StructFormatType, str, None]:
        if not self._struct_is_resolved:
            return None

        if self._struct_array_is_generic:
            return self._struct_array_type.format
        else:
            return self._struct_array_type._struct_format_chunked()

    def length(self) -> int:
        if not self._struct_is_resolved:
            raise StructError("Accessing length of unresolved array is undefined.")

        if isinstance(self._struct_array_type, StructArray):
            return self._struct_array_qualifier * self._struct_array_type._struct_array_qualifier

        return self._struct_array_qualifier

    def _struct_get_template_arg_sig(self) -> Set[str]:
        if not self._struct_is_template:
            return set()

        ret = set()
        if isinstance(self._struct_array_type, TypeVar):
            ret.add(self._struct_array_type.__name__)
        elif isinstance(self._struct_array_type, StructIOProtocol):
            ret.update(self._struct_array_type._struct_get_template_arg_sig())

        if isinstance(self._struct_array_qualifier, TypeVar):
            ret.add((self._struct_array_qualifier.__name__))

        return ret

    def _struct_substitute_template_params(self, params: Dict[str, Any]) -> 'StructArray':
        if self._struct_is_resolved:
            raise StructError("Attempted substituting template parameters for an already resolved array.")

        struct_array_type = self._struct_array_type
        struct_array_qualifier = self._struct_array_qualifier

        counter = 0
        # first substitute arrays's own template entries
        if isinstance(self._struct_array_type, TypeVar):
            if new_type := params.get(self._struct_array_type.__name__):
                counter += 1

                # check if substituted type is of allowed type
                if not (isinstance(new_type, StructIOProtocol)
                        or isinstance(new_type, TypeVar)
                        or new_type.__class__.__name__ == 'GenericType'):
                    raise TypeError(f"Failed to substitute array type parameter"
                                    f" '{self._struct_array_type.__name__}'. "
                                    f"Specified type is not a Struct, plain type or TypeVar.")

                struct_array_type = new_type
            else:
                raise StructError(f"Failed to substitute array type parameter. Required parameter"
                                  f"'{self._struct_array_type.__name__}' not specified.")

        # substitute template type if nested into this array
        elif isinstance(self._struct_array_type, StructIOProtocol) \
                and self._struct_array_type._struct_is_template \
                and not self._struct_array_type._struct_is_resolved:

                # check if type was specified at all
                if not self._struct_array_type._struct_is_specified:
                    raise StructError(f"Failed to subsititute array type parameter. Contains unspecified type "
                                      f"<'{self._struct_array_type.__name__}'>")

                new_type = self._struct_array_type._struct_substitute_template_params(params)

                struct_array_type = new_type

        if isinstance(self._struct_array_qualifier, TypeVar):
            if new_type := params.get(self._struct_array_qualifier.__name__):
                counter += 1

                # check if substituted type is of allowed type
                if not (isinstance(new_type, TypeVar) or isinstance(new_type, int)):
                    raise TypeError(f"Failed to substitute array length parameter"
                                    f" '{self._struct_array_qualifier.__name__}'. "
                                    f"Specified type is not an int or TypeVar.")

                struct_array_qualifier = new_type
            else:
                raise StructError(f"Failed to substitute array type parameter. Required parameter"
                                  f"'{self._struct_array_type.__name__}' not specified.")


        #if counter != len(params):
        #    raise StructError(f"Failed to substitute array template parameters. Expected {counter}, "
         #                     f"{len(params)} given.")

        return StructArray(struct_array_type, struct_array_qualifier)


    def __mod__(self, other: Union[Dict[str, Any], Any]) -> 'StructIOProtocol': ...

    def __getitem__(self, item: Union[str, int, TypeVar]) -> 'StructArray':
        return StructArray(self, item)