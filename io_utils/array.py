from .struct_protocol import StructIOProtocol, StructFormatType
from .exceptions import StructError
from .var_type_protocol import VarTypeProtocol

from io import IOBase
from typing import Union, Any, Dict, Set


class StructArray:
    _struct_array_is_generic: bool
    _struct_array_qualifier: Union[int, str, VarTypeProtocol]
    _struct_array_type: Union[StructIOProtocol, 'GenericType', VarTypeProtocol]

    # compling with StructIOProtocol interface
    _struct_is_template: bool
    _struct_is_resolved: bool
    _struct_is_specified: bool = True

    def __init__(self, u_type: Union[StructIOProtocol, 'GenericType', VarTypeProtocol], qualifier: Union[int, VarTypeProtocol]):
        # check if any template arguments are passed
        self._struct_is_template = isinstance(u_type, VarTypeProtocol) \
                                   or isinstance(qualifier, VarTypeProtocol) \
                                   or (isinstance(u_type, StructIOProtocol) and u_type._struct_is_template)
        self.__name__ = 'StructArray'

        if not self._struct_is_template:
            self._struct_is_resolved = True
        else:
            self._struct_is_resolved = False

        # check if underlying type is generic type
        self._struct_array_is_generic = u_type.__class__.__name__ == 'GenericType'

        if not isinstance(qualifier, (int, VarTypeProtocol)):
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
        if isinstance(self._struct_array_type, VarTypeProtocol):
            ret.add(self._struct_array_type.__name__)
        elif isinstance(self._struct_array_type, StructIOProtocol):
            ret.update(self._struct_array_type._struct_get_template_arg_sig())

        if isinstance(self._struct_array_qualifier, VarTypeProtocol):
            ret.add((self._struct_array_qualifier.__name__))

        return ret

    @staticmethod
    def _struct_is_valid_template_type(arg_type: Any) -> bool:
        return isinstance(arg_type, (VarTypeProtocol, StructIOProtocol)) \
               or (hasattr(arg_type.__class__, '__name__') and arg_type.__class__.__name__ == 'GenericType')

    def _struct_substitute_template_params(self, params: Dict[str, Any]) -> 'StructArray':
        if self._struct_is_resolved:
            raise StructError("Attempted substituting template parameters for an already resolved array.")

        struct_array_type = self._struct_array_type
        struct_array_qualifier = self._struct_array_qualifier

        counter = 0
        # first substitute arrays's own template entries
        if isinstance(self._struct_array_type, VarTypeProtocol):
            if new_type := params.get(self._struct_array_type.__name__):
                counter += 1

                # check if substituted type is of allowed type
                if not StructArray._struct_is_valid_template_type(new_type):
                    raise TypeError(f"Failed to substitute array type parameter"
                                    f" '{self._struct_array_type.__name__}'. "
                                    f"Specified type is not a Struct, plain type or VarTypeProtocol.")

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

        if isinstance(self._struct_array_qualifier, VarTypeProtocol):
            if new_type := params.get(self._struct_array_qualifier.__name__):
                counter += 1

                # check if substituted type is of allowed type
                if not (isinstance(new_type, VarTypeProtocol) or isinstance(new_type, int)):
                    raise TypeError(f"Failed to substitute array length parameter"
                                    f" '{self._struct_array_qualifier.__name__}'. "
                                    f"Specified type is not an int or VarTypeProtocol.")

                struct_array_qualifier = new_type
            else:
                raise StructError(f"Failed to substitute array length parameter. Required parameter"
                                  f" '{self._struct_array_qualifier.__name__}' not specified.")


        #if counter != len(params):
        #    raise StructError(f"Failed to substitute array template parameters. Expected {counter}, "
         #                     f"{len(params)} given.")

        return StructArray(struct_array_type, struct_array_qualifier)


    def __mod__(self, other: Union[Dict[str, Any], Any]) -> 'StructIOProtocol': ...

    def __getitem__(self, item: Union[str, int, VarTypeProtocol]) -> 'StructArray':
        return StructArray(self, item)