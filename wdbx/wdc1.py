from ..io_utils.types import *
from enum import IntEnum


class WDC1Header:
    size = 80

    def __init__(self):
        self.magic = 'WDC1'
        self.record_count = 0
        self.field_count = 0
        self.record_size = 0
        self.string_table_size = 0
        self.table_hash = 0                 # hash of the table name
        self.layout_hash = 0                # this is a hash field that changes only when the structure of the data changes
        self.min_id = 0
        self.max_id = 0
        self.locale = 0                     # as seen in TextWowEnum
        self.copy_table_size = 0
        self.flags = 0                      # possible values are listed in Known Flag Meanings
        self.id_index = 0                   # this is the index of the field containing ID values = 0 this is ignored if flags & 0x04 != 0
        self.total_field_count = 0          # from WDC1 onwards, this value seems to always be the same as the 'field_count' value
        self.bitpacked_data_offset = 0      # relative position in record where bitpacked data begins = 0 not important for parsing the file
        self.lookup_column_count = 0
        self.offset_map_offset = 0          # Offset to array of struct {self.offset = 0 uint16_t size = 0}[max_id - min_id + 1] = 0
        self.id_list_size = 0               # List of ids present in the DB file
        self.field_storage_info_size = 0
        self.common_data_size = 0
        self.pallet_data_size = 0
        self.relationship_data_size = 0

    def read(self, f):
        self.magic = f.read(4).decode('utf-8')
        self.record_count = uint32.read(f)
        self.field_count = uint32.read(f)
        self.record_size = uint32.read(f)
        self.string_table_size = uint32.read(f)
        self.table_hash = uint32.read(f)
        self.layout_hash = uint32.read(f)
        self.min_id = uint32.read(f)
        self.max_id = uint32.read(f)
        self.locale = uint32.read(f)
        self.copy_table_size = uint32.read(f)
        self.flags = uint16.read(f)
        self.id_index = uint16.read(f)
        self.total_field_count = uint32.read(f)
        self.bitpacked_data_offset = uint32.read(f)
        self.lookup_column_count = uint32.read(f)
        self.offset_map_offset = uint32.read(f)
        self.id_list_size = uint32.read(f)
        self.field_storage_info_size = uint32.read(f)
        self.common_data_size = uint32.read(f)
        self.pallet_data_size = uint32.read(f)
        self.relationship_data_size = uint32.read(f)

    def write(self, f):
        f.write(self.magic.encode('utf-8'))
        uint32.write(f, self.record_count)
        uint32.write(f, self.field_count)
        uint32.write(f, self.record_size)
        uint32.write(f, self.string_table_size)
        uint32.write(f, self.table_hash)
        uint32.write(f, self.layout_hash)
        uint32.write(f, self.min_id)
        uint32.write(f, self.max_id)
        uint32.write(f, self.locale)
        uint32.write(f, self.copy_table_size)
        uint16.write(f, self.flags)
        uint16.write(f, self.id_index)
        uint32.write(f, self.total_field_count)
        uint32.write(f, self.bitpacked_data_offset)
        uint32.write(f, self.lookup_column_count)
        uint32.write(f, self.offset_map_offset)
        uint32.write(f, self.id_list_size)
        uint32.write(f, self.field_storage_info_size)
        uint32.write(f, self.common_data_size)
        uint32.write(f, self.pallet_data_size)
        uint32.write(f, self.relationship_data_size)

    class FieldStructure:
        def __init__(self):
            self.size = 0
            self.offset = 0

        def read(self, f):
            self.size = uint16.read(f)
            self.offset = uint16.read(f)

        def write(self, f):
            uint16.write(f, self.size)
            uint16.write(f, self.offset)


    class WDBFlags(IntEnum):
        HasOffsetMap = 0x1
        HasRelationshipData = 0x2
        HasNonInlineIDs = 0x4
        IsBitpacked = 0x10


    class FieldCompression(IntEnum):
        NONE = 0
        BITPACKED = 1
        COMMON_DATA = 2
        BITPACKED_INDEXED = 3
        BITPACKED_INDEXED_ARRAY = 4


    class WDC1:
