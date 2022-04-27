from .ctypes import *
from .array import StructArray
from .struct_protocol import StructIOProtocol, StructFormatType
from .var_type_protocol import VarTypeProtocol
from .exceptions import StructError
from .class_namespace_hook import NameSpaceHook

from io import IOBase
from typing import Set, Tuple, Type, Dict, Union, Optional


def recurse_format_chunks(format_chunks: StructFormatType) -> str:

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
            for _ in range(n_values):
                yield from recurse_format_chunks(format)


class StructMeta(type):
    _struct_format_chunks: Optional[StructFormatType]
    _struct_is_template: bool
    _struct_is_plain_old_data: bool
    _struct_is_resolved: bool
    _struct_is_specified: bool
    _struct_original: Optional[StructIOProtocol]

    _struct_template_definitions: Optional[Dict[Tuple[Tuple[str, Any]], StructIOProtocol]]

    def __new__(mcs, classname, bases, cls_dict, original: Optional[StructIOProtocol] = None):
        # first turning the cls_dict into a normal Python dict, as we no longer need hooked functionality here
        cls_dict = dict(cls_dict)

        annotations = cls_dict.get('__annotations__')
        if annotations is None:
            raise StructError(f"Struct <'{classname}'>: Empty structs are not supported. "
                              "A struct must contain data-type annotations.")

        is_plain_old_data = True
        is_template = False
        is_resolved = True

        for attr_name, annotation_type in annotations.items():
            # check if current Struct is a template (has at least one template parameter)
            if isinstance(annotation_type, VarTypeProtocol):
                is_template = True
                is_resolved = False

            elif isinstance(annotation_type, StructIOProtocol):
                if annotation_type._struct_is_template:
                    is_template = True

                    # if any nested struct is unresolved, we consider the parent struct unresolved too
                    if not annotation_type._struct_is_resolved:
                        is_resolved = False

                    if not annotation_type._struct_is_specified:
                        raise StructError(f"Struct <'{classname}'> contains unspecified struct at field '{attr_name}'."
                                          f" Struct signature: {annotation_type._struct_get_template_arg_sig_repr()}")

                if attr_name in cls_dict:
                    raise StructError(f"Struct <'{classname}'>: Default values are only supported for plain data "
                                      f"types. Field '{attr_name}' must not have a default value.")

            elif isinstance(annotation_type, GenericType):
                # check if provided default value is of correct type
                default_value = cls_dict.get(attr_name)
                if default_value is not None and not isinstance(default_value, annotation_type.py_type):
                    raise TypeError(f"Struct <'{classname}'>: Default value provided for field '{attr_name}' is "
                                    f"'{str(type(default_value))}', expected '{str(type(annotation_type.py_type))}'")

            else:
                _is_plain_old_data = False

        format_chunks: Optional[StructFormatType] = None

        if is_resolved:
            format_chunks = StructMeta._struct_generate_format_specification(annotations, cls_dict)

        if is_template and original is None:
            cls_dict['_struct_template_definitions'] = {}

        # pack format
        format_processed = "".join(recurse_format_chunks(format_chunks)) if format_chunks else None

        cls_dict['_struct_format_chunks'] = format_chunks
        cls_dict['_struct_token_string'] = None if not is_resolved else format_processed
        cls_dict['read'] = StructMeta.read
        cls_dict['write'] = StructMeta.write
        cls_dict['_struct_is_template'] = is_template
        cls_dict['_struct_is_plain_old_data'] = is_plain_old_data

        if is_template:
            if '_struct_is_specified' not in cls_dict:
                cls_dict['_struct_is_specified'] = is_resolved

            cls_dict['_struct_is_resolved'] = is_resolved
        else:
            cls_dict['_struct_is_resolved'] = True
            cls_dict['_struct_is_specified'] = True

        cls_dict['_struct_original'] = original

        new_type = type.__new__(mcs, classname, bases, cls_dict)

        return new_type

    @classmethod
    def __prepare__(mcs, name, bases):
        return NameSpaceHook()

    @staticmethod
    def _struct_generate_format_specification(annotations: Dict[str, Any], cls_dict: Dict) -> Optional[StructFormatType]:
        # generate struct specification for non-template structs right away
        format_chunks = []

        for attr_name, annotation_type in annotations.items():

            if isinstance(annotation_type, StructIOProtocol):
                # handle nested structures
                format_chunks.append((attr_name, annotation_type._struct_format_chunked(), None,
                                      annotation_type.length()))

            elif isinstance(annotation_type, GenericType):
                # handle plain types
                default_value = cls_dict.get(attr_name)
                format_chunks.append((attr_name, annotation_type.format, default_value, annotation_type.length()))

        return format_chunks

    def _struct_get_template_arg_sig(cls) -> Set[str]:
        sig = set([t.__name__ for _, t in cls.__annotations__.items() if isinstance(t, VarTypeProtocol)])

        for _, t in cls.__annotations__.items():
            if isinstance(t, StructIOProtocol):
                sig.update(t._struct_get_template_arg_sig())

        return sig

    def _struct_get_template_arg_sig_repr(cls) -> str:
        return f"{cls.__name__ if cls._struct_original is None else cls._struct_original.__name__}" \
               f"<{', '.join(cls._struct_get_template_arg_sig())}>"

    def write(self: StructIOProtocol, f: IOBase) -> StructIOProtocol:
        return self

    def read(self: StructIOProtocol, f: IOBase) -> StructIOProtocol:
        return self

    def _struct_format_chunked(cls) -> StructFormatType:
        if not cls._struct_is_resolved:
            raise StructError(f"Attempted to access struct format for template Struct <'{cls.__name__}'> "
                              "that does not have all its template parameters specified.")

        return cls._struct_format_chunks

    def length(cls) -> int:
        return 1

    @staticmethod
    def _struct_is_valid_template_type(arg_type: Any) -> bool:
        return isinstance(arg_type, (VarTypeProtocol, StructIOProtocol, GenericType))

    def _struct_substitute_template_params(cls, params: Dict[str, Any]) -> StructIOProtocol:

        if cls._struct_is_resolved:
            raise StructError(f"Attempted to specify an already resolved Struct <'{cls.__name__}'>")

        params_hashable = tuple([(name, type) for name, type in params.items()])

        orig_type = cls._struct_original if cls._struct_original is not None else cls
        definition = orig_type._struct_template_definitions.get(params_hashable)

        if definition is not None:
            return definition

        # create specialization here
        new_dict = cls.__dict__.copy()
        annotations = new_dict['__annotations__']
        new_dict['__annotations__'] = new_annotations = annotations.copy()

        # substitute struct's own template params first
        has_unresolved_args = False
        for attr_name, annotation_type in annotations.items():
            if isinstance(annotation_type, VarTypeProtocol):
                resolved_type = params.get(annotation_type.__name__)

                if resolved_type is None:
                    raise StructError(f"Failed to substitute template argument '{annotation_type.__name__}', "
                                      f"not found in provided parameters. Struct signature: "
                                      f"{cls._struct_get_template_arg_sig_repr()}")

                # do not declare this struct specified yet if parent template parameters is passed
                if isinstance(resolved_type, VarTypeProtocol):
                    has_unresolved_args = True

                if not StructMeta._struct_is_valid_template_type(resolved_type):
                    raise TypeError(f"Failed to substitute template argument '{annotation_type.__name__}'. "
                                    f"Template argument may be represented only by another Struct, "
                                    f"plain type or VarTypeProtocol")

                new_annotations[attr_name] = resolved_type

        new_dict['_struct_is_specified'] = True

        # substitute nested structs template params
        for attr_name, annotation_type in annotations.items():
            if isinstance(annotation_type, StructIOProtocol) \
                and annotation_type._struct_is_template \
                and not annotation_type._struct_is_resolved:

                new_annotations[attr_name] = annotation_type._struct_substitute_template_params(params)

        if not has_unresolved_args:
            new_dict['_struct_is_resolved'] = True

            if '_struct_template_definitions' in new_dict:
                del new_dict['_struct_template_definitions']

        args = ', '.join(name + '=' + (str(t) if isinstance(t, int) else (t.__name__ if isinstance(t, StructIOProtocol)
                                                  or isinstance(t, VarTypeProtocol) else t.name))
                                       for name, t in params.items())

        new_type = StructMeta.__new__(StructMeta,
                                      f"{cls.__name__ if cls._struct_original is None else cls._struct_original.__name__}"
                                      f"<{args}>",
           cls.__bases__, new_dict, cls)

        # store known specialization to avoid duplicating types
        orig_type._struct_template_definitions[params_hashable] = new_type

        return new_type

    def __getitem__(cls, item: Union[str, int, VarTypeProtocol]) -> StructArray:
        """ Defines [] syntax for declaring arrays. """

        if not isinstance(item, int):
            raise TypeError(f"Struct <'{cls.__name__}'>: [] syntax is used to indicate arrays. Argument type "
                            f"must be 'int' or 'str' for dynamic expressions, or 'VarTypeProtocol' for templates.")

        return StructArray(cls, item)

    def __mod__(cls, other: Union[Dict[str, Any], Any]) -> Type[StructIOProtocol]:
        """ Defines syntax for specifying template parameters """

        if isinstance(other, dict):
            return cls._struct_substitute_template_params(other)
        else:
            if len(cls._struct_get_template_arg_sig()) != 1:
                raise TypeError(f"Failed to substitute template arguments, "
                                f"Struct <'{cls.__name__}'>: defines {len(cls._struct_get_template_arg_sig())}, got 1.")

            n = next(iter(cls._struct_get_template_arg_sig()))

            return cls._struct_substitute_template_params({n: other})




