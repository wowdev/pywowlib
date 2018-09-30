from ..io_utils.types import *
from collections import namedtuple
from io import BytesIO
from .definitions import wotlk
from .definitions.types import DBCString, DBCLangString


class DBCHeader:

    def __init__(self):
        self.magic = 'WDBC'
        self.record_count = 0
        self.field_count = 0
        self.record_size = 0
        self.string_block_size = 0

    def read(self, f):
        self.magic = f.read(4).decode('utf-8')
        self.record_count = uint32.read(f)
        self.field_count = uint32.read(f)
        self.record_size = uint32.read(f)
        self.string_block_size = uint32.read(f)

        return self

    def write(self, f):
        f.write(self.magic.encode('utf-8'))
        string.write(f, self.magic)
        uint32.write(f, self.record_count)
        uint32.write(f, self.field_count)
        uint32.write(f, self.record_size)
        uint32.write(f, self.string_block_size)

        return self


class DBCFile:
    def __init__(self, name):
        definition = getattr(wotlk, name)
        if not definition:
            raise FileNotFoundError('No definition for DB <<{}>> found.'.format(name))

        self.header = DBCHeader()
        self.name = name
        self.field_names = namedtuple('RecordGen', [name for name in definition.keys()])
        self.field_types = tuple([type_ for type_ in definition.values()])
        self.records = []

        self.max_id = 0

    def read(self, f):
        self.header.read(f)
        str_block_ofs = 20 + self.header.record_count * self.header.record_size

        for _ in range(self.header.record_count):
            args = []
            for f_type in self.field_types:
                if f_type in (DBCString, DBCLangString):
                    args.append(f_type.read(f, str_block_ofs))
                else:
                    args.append(f_type.read(f))

            record = self.field_names(*args)
            self.records.append(record)

            # store max used id,
            if record.ID > self.max_id:
                self.max_id = record.ID

        '''
        for _ in range(self.header.record_count):
            record = self.field_names(*[f_type.read(f, str_block_ofs)
                                        if f_type in (DBCString, DBCLangString)
                                        else f_type.read(f) for f_type in self.field_types])

            self.records.append(record)
        
            # store max used id,
            if record.ID > self.max_id:
                self.max_id = record.ID
                
        '''

        return

    def write(self, f):
        f.seek(20)
        self.header.record_count = len(self.records)
        str_block_ofs = 20 + self.header.record_count * self.header.record_size

        for record in self.records:
            for i, field in enumerate(record):
                type_ = self.field_types[i]
                if type_ in (DBCString, DBCLangString):
                    field.write(f, field, str_block_ofs)
                else:
                    type_.write(f, field)

        f.seek(0, 2)
        self.header.string_block_size = f.tell() - str_block_ofs
        f.seek(0)
        self.header.write(f)

    def read_from_gamedata(self, game_data):
        f = BytesIO(game_data.read_file('DBFilesClient\\{}.dbc'.format(self.name)))
        self.read(f)

    def get_record(self, uid):
        for record in self.records:
            if record.ID == uid:
                return record

    def get_field(self, uid, name):
        record = self.get_record(uid)
        if record:
            return getattr(record, name)

    def add_record(self, *args):
        self.records.append(self.field_names(args))
        self.header.record_count += 1
        return len(self.records) - 1

    def __getitem__(self, uid):
        for record in self.records:
            if record.ID == uid:
                return record

