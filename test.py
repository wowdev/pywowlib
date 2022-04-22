from io_utils.ctypes import *
from io_utils.struct import *
from io_utils.metaclass_hook import Structs

from typing import TypeVar


# Struct module allows you to create data structs declaratively.
# Unlike Python's native struct module (which is still used under the hood),
# Struct features simplified and familiar syntax close to C++ as well as type templates.
# In order to create a struct use a metaclass hook:
with Structs: # -> you can also pass alignment and endianness parameters here
    class SimplePODStruct: # -> now a struct!
        field_name: int32 # -> declare a field
        some_araay: float32[10] # -> declare an array-field with static size

    T = TypeVar('T') # TODO: custom subclass of TypeVar to support array syntax
    Tx = TypeVar('Tx')
    class TemplatedStruct:
        variable_type_field: T
        variable_array_length: float32[Tx]

    # Now we can use this template.
    # Specify template parameters and use as final struct.
    # % operator is used to specify template arguments
    SpecifiedStruct = TemplatedStruct % {'T': int32, 'Tx': 10}

    s = SpecifiedStruct()
    # s.read(f)

    #print(len(s.variable_array_length))
    # >>> 10
    #print(type(s.variable_array_length))
    # >>> list # initialized Python equivalent type, bounds check is performed on writing

    s.variable_array_length = [x for x in range(0, 10)]
    # s.write(f)

    # It is also possible to nest templated structs and propagate template arguments further.

    class OneArgumentTemplate:
        a: T

    Ty = TypeVar('Ty')
    class NestedTemplatedStruct:
        a: TemplatedStruct % {'T': Ty, 'Tx': 100}
        b: OneArgumentTemplate % Ty # if a template only has one argument, you can omit the argument name

    s = (NestedTemplatedStruct % (OneArgumentTemplate % float32))() # nested template specialization
    # and let's finally print the internal structure of this type Frankenstein

    #print(s._struct_token_string)
    # >>> f100ff

    # These token strings are evaluated for every Struct with complete template specialization
    # or non-template Struct. Internally a cached Python struct object will be created.

    # The Python type representation of the Struct.
    # If you instantiate a Struct, the resulted instance will contain a tree structure of objects,
    # which corresponds to the specified layout.
    # In case the Struct is plain old data (POD), NamedTuple will be used for hosting substructs.
    # In case the Struct is not POD, meaning it also defines supplementary non-layout members or methods
    # they will remain in the created object.
    # This behavior in the future as well as performing or not performing bounds and typechecks on use
    # will be parameterizable.

NestedTemplatedStruct
# Some tests
T = TypeVar('T')
Ty = TypeVar('Ty')



with Structs:

    # simple non templated POD struct
    class StructD:
        a: int32
        b: float32
        c: char[10]

    # since StructD is simple, we can evaluate its struct token right away
    print("StructD:", StructD._struct_token_string)
    assert(StructD._struct_token_string == 'if10s')

    class StructB:
        a: int32
        b: T

    # StructB defines one template parameter
    # thus, its token string and size cannot be evaluated until template parameters are specifieds
    print("StructB:", StructB._struct_token_string)
    assert(StructB._struct_token_string is None)

    class StructA:
        a: StructB % {'T': char[10]}


    # nested array test
    class NestedArrayTest:
        a: float32[10][10]

    print("NestedArrayTest:", NestedArrayTest._struct_token_string)
    assert(NestedArrayTest._struct_token_string == '100f')

    # array of structs
    class ArrayOfStructs:
        a: NestedArrayTest[2][2]


    print("ArrayOfStructs:", ArrayOfStructs._struct_token_string)
    assert (ArrayOfStructs._struct_token_string == '100f100f100f100f')

    # array templated type

    class ArrayTemplatedType:
        a: StructArray(T, 10)[10] # TODO: custom TypeVar to support T[x][x]... syntax

    array_templated_type_spec = ArrayTemplatedType % int32

    print(array_templated_type_spec.__name__, array_templated_type_spec._struct_token_string)
    assert (array_templated_type_spec._struct_token_string == '100i')

    # forwarding templated types through another nested structure

    class ArrayTypeArgumentForwardTest:
        a: ArrayTemplatedType % {'T': Ty}


    ArrayTypeArgumentForwardTest_spec = ArrayTypeArgumentForwardTest % {'Ty': float32}
    print(ArrayTypeArgumentForwardTest_spec.__name__, ArrayTypeArgumentForwardTest_spec._struct_token_string)
    assert(ArrayTypeArgumentForwardTest_spec._struct_token_string == '100f')

    # nesting this spec into another struct
    class NestedSpec:
        a: ArrayTypeArgumentForwardTest_spec
        b: ArrayTypeArgumentForwardTest_spec

    print(NestedSpec.__name__, NestedSpec._struct_token_string)






