from ..io_utils.types import *
from collections import OrderedDict
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

    __slots__ = ('size', 'offset')

    def __init__(self):
        self.size = 0
        self.offset = 0

    def read(self, f):
        self.size = uint16.read(f)
        self.offset = uint16.read(f)

        return self

    def write(self, f):
        uint16.write(f, self.size)
        uint16.write(f, self.offset)

        return self


class OffsetMapEntry:

    __slots__ = ('offset', 'size')

    def __init__(self):
        self.offset = 0
        self.size = 0

    def read(self, f):
        self.offset = uint32.read(f)
        self.size = uint16.read(f)

    def write(self, f):
        uint32.write(f, self.offset)
        uint16.write(f, self.offset)


class FieldStorageInfo:
    def __init__(self):
        self.field_offset_bits = 0
        self.field_size_bits = 0
        self.additional_data_size = 0
        self.storage_type = FieldCompression.NONE

    def read(self, f):
        self.field_offset_bits = uint16.read(f)
        self.field_size_bits = uint16.read(f)
        self.additional_data_size = uint32.read(f)
        self.storage_type = uint32.read(f)

        if self.storage_type == FieldCompression.BITPACKED:
            self.bitpacking_offset_bits = uint32.read(f)
            self.bitpacking_size_bits = uint32.read(f)
            self.flags = uint32.read(f)  # known values - 0x01: sign-extend (signed)

        elif self.storage_type == FieldCompression.COMMON_DATA:
            self.default_value = uint32.read(f)
            self.unk_or_unused2 = uint32.read(f)
            self.unk_or_unused3 = uint32.read(f)

        elif self.storage_type == FieldCompression.BITPACKED_INDEXED:
            self.bitpacking_offset_bits = uint32.read(f)
            self.bitpacking_size_bits = uint32.read(f)
            self.unk_or_unused3 = uint32.read(f)

        elif self.storage_type == FieldCompression.BITPACKED_INDEXED_ARRAY:
            self.bitpacking_offset_bits = uint32.read(f)
            self.bitpacking_size_bits = uint32.read(f)
            self.array_count = uint32.read(f)

        else:
            self.unk_or_unused1 = uint32.read(f)
            self.unk_or_unused2 = uint32.read(f)
            self.unk_or_unused3 = uint32.read(f)

        return self

    def write(self, f):
        uint32.write(f, self.field_offset_bits)
        uint32.write(f, self.field_size_bits)
        uint32.write(f, self.additional_data_size)
        uint32.write(f, self.storage_type)

        if self.storage_type == FieldCompression.BITPACKED:
            uint32.write(f, self.bitpacking_offset_bits)
            uint32.write(f, self.bitpacking_size_bits)
            uint32.write(f, self.flags)

        elif self.storage_type == FieldCompression.COMMON_DATA:
            uint32.write(f, self.default_value)
            uint32.write(f, self.unk_or_unused2)
            uint32.write(f, self.unk_or_unused3)

        elif self.storage_type == FieldCompression.BITPACKED_INDEXED:
            uint32.write(f, self.bitpacking_offset_bits)
            uint32.write(f, self.bitpacking_size_bits)
            uint32.write(f, self.unk_or_unused3)

        elif self.storage_type == FieldCompression.BITPACKED_INDEXED_ARRAY:
            uint32.write(f, self.bitpacking_offset_bits)
            uint32.write(f, self.bitpacking_size_bits)
            uint32.write(f, self.array_count)

        else:
            uint32.write(f, self.unk_or_unused1)
            uint32.write(f, self.unk_or_unused2)
            uint32.write(f, self.unk_or_unused3)

        return self


class RelationshipEntry:
    def __init__(self):
        self.foreign_id = 0
        self.record_index = 0

    def read(self, f):
        self.foreign_id = uint32.read(f)
        self.record_index = uint32.read(f)

        return self

    def write(self, f):
        uint32.write(f, self.foreign_id)
        uint32.write(f, self.record_index)

        return self


class RelationshipMapping:
    def __init__(self):
        self.num_entries = 0
        self.min_id = 0
        self.max_id = 0
        self.entries = []

    def read(self, f):
        self.num_entries = uint32.read(f)
        self.min_id = uint32.read(f)
        self.max_id = uint32.read(f)
        self.entries = [RelationshipEntry().read(f) for _ in range(self.num_entries)]

        return self

    def write(self, f):
        uint32.write(f, len(self.entries))
        uint32.write(f, self.min_id)
        uint32.write(f, self.max_id)

        for entry in self.entries:
            entry.write(f)

        return self


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
    def __init__(self):
        self.header = WDC1Header()
        self.fields = []
        self.id_list = []

        self.record_data = []
        self.string_data = None

        self.variable_record_data = None
        self.offset_map = []

        self.copy_table = {}
        self.field_info = []
        self.pallet_data = None
        self.common_data = None

        self.relationship_map = RelationshipMapping()

    def read(self, f):
        self.header.read(f)
        self.fields = [FieldStructure().read(f) for _ in range(self.header.total_field_count)]

        # normal records
        if not (self.header.flags & WDBFlags.HasOffsetMap):
            self.record_data = [f.read(self.header.record_size) for _ in range(self.header.record_count)]
            self.string_data = f.read(self.header.string_table_size)

        # offset map records
        # since they are variable length, they are pointed to by an array of 6-byte offset + size pairs.
        else:
            self.variable_record_data = f.read(self.header.offset_map_offset - self.header.size
                                               - (4 * self.header.total_field_count))

            self.offset_map = [OffsetMapEntry().read(f) for _ in range(self.header.max_id - self.header.min_id + 1)]

        self.id_list = [uint32.read(f) for _ in range(self.header.id_list_size // 4)]

        if self.header.copy_table_size > 0:
            self.copy_table = {uint32.read(f): uint32.read(f) for _ in range(self.header.copy_table_size // 8)}

        self.field_info = [FieldStorageInfo().read(f) for _ in range(self.header.field_storage_info_size // 24)]
        self.pallet_data = f.read(self.header.pallet_data_size)
        self.common_data = f.read(self.header.common_data_size)

        if self.header.relationship_data_size > 0:
            self.relationship_map = RelationshipMapping().read(f)

    def parse_field_data(self):

        has_non_inline_ids = self.header.flags & WDBFlags.HasNonInlineIDs

        records = OrderedDict()

        # normal records
        if not (self.header.flags & WDBFlags.HasOffsetMap):
            if has_non_inline_ids:

                for field_struct, field_info in zip(self.fields, self.field_info):
                    is_array = False

                    if field_struct.size != 0:
                        length = field_info.field_size_bits // (32 - field_struct.size)
                        is_array = length > 1

            else:
                pass

        # offset map records
        else:
            pass












