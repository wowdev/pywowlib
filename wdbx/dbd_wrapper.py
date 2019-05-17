import os
from collections import OrderedDict
from .dbd_parser import parse_dbd_file, build_version_raw
from .types import DBCString, DBCLangString
from ..io_utils import types


type_map = {
    'int': lambda entry: getattr(types, "{}{}{}".format(
        'u' if entry.is_unsigned else '', 'int', entry.int_width)),
    'float': lambda x: types.float32,
    'string': lambda x: DBCString,
    'locstring': lambda x: DBCLangString

}


class DBDefinition:
    def __init__(self, name, build):
        dbd_raw = parse_dbd_file('{}/dbd/definitions/{}.dbd'.format(os.path.dirname(os.path.abspath(__file__)),
                                                                          name))

        self.name = name
        self.build = build

        for _def in dbd_raw.definitions:
            for _build in _def.builds:
                if not isinstance(_build, tuple):
                    if str(_build) == build:
                        definition = _def
                        break
                elif _build[0] <= build_version_raw(*(int(s) for s in build.split('.'))) <= _build[1]:
                    definition = _def
                    break
            else:
                continue
            break
        else:
            raise NotImplementedError('\nNo definition found for table \"{}\" for build \"{}\"'.format(name, build))

        columns = {column.name: column.type for column in dbd_raw.columns}

        self.definition = OrderedDict()
        for entry in definition.entries:

            type_name = columns[entry.column]
            real_type = type_map.get(type_name)(entry)

            if not real_type:
                raise TypeError('\nUnknown DBD type \"{}\"'.format(type_name))

            self.definition[entry.column] = real_type

    def __getitem__(self, item):
        return self.definition[item]

    def keys(self):
        return self.definition.keys()

    def items(self):
        return self.definition.items()

    def values(self):
        return self.definition.values()





