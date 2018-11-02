import os
from .dbd.code.Python3.dbd import parse_dbd_file
from .types import DBCString, DBCLangString
from ..io_utils import types


class DBDefinition:
    def __init__(self, name, build):
        self._dbd_raw = parse_dbd_file('{}/dbd/definitions/{}.dbd'.format(os.path.dirname(os.path.abspath(__file__)),
                                                                          name))

        self.name = name
        self.build = build

        for _def in self._dbd_raw.definitions:
            for _build in _def.builds:
                if str(_build) == build:
                    definition = _def
                    break
            else:
                continue
            break
        else:
            raise NotImplementedError('\nNo definition found for table \"{}\" for build \"{}\"'.format(name, build))

        columns = {column.name: column.type for column in self._dbd_raw.columns}

        self.definition = {}
        for entry in definition.entries:
            type_name = columns[entry.column]

            if type_name == 'int':
                real_type = getattr(types, "{}{}{}".format('u' if entry.is_unsigned else '',
                                                           type_name, entry.int_width))

            elif type_name == 'float':
                real_type = types.float32

            elif type_name == 'string':
                real_type = DBCString

            elif type_name == 'locstring':
                real_type = DBCLangString

            else:
                raise TypeError('\nUnknown DBD type \"{}\"'.format(type_name))

            self.definition[entry.column] = real_type

    def __getitem__(self, item):
        return self.definition[item]








