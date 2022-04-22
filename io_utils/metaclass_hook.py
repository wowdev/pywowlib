from .struct import StructMeta

import builtins


class StructsContextManagerMeta(type):
    _orig_build_class = builtins.__build_class__

    def __enter__(cls):
        cls._orig_build_class = builtins.__build_class__

        def my_build_class(func, name, *bases, **kwargs):
            if not any(isinstance(b, type) for b in bases):
                # a 'regular' class, not a metaclass
                if 'metaclass' in kwargs:
                    if not isinstance(kwargs['metaclass'], type):
                        # the metaclass is a callable, but not a class
                        orig_meta = kwargs.pop('metaclass')

                        class HookedMeta(StructMeta):
                            def __new__(meta, name, bases, attrs):
                                return orig_meta(name, bases, attrs)

                        kwargs['metaclass'] = HookedMeta
                    elif kwargs['metaclass'] is StructMeta:
                        return cls._orig_build_class(func, name, *bases, **kwargs)
                    else:
                        # There already is a metaclass, insert ours and hope for the best

                        class SubclassedMeta(StructMeta, kwargs['metaclass']):
                            pass

                        kwargs['metaclass'] = SubclassedMeta
                else:
                    kwargs['metaclass'] = StructMeta

            return cls._orig_build_class(func, name, *bases, **kwargs)

        builtins.__build_class__ = my_build_class

    def __exit__(cls, exc_type, exc_val, exc_tb):
        builtins.__build_class__ = cls._orig_build_class


class Structs(metaclass=StructsContextManagerMeta):
    pass



