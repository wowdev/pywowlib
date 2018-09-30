from ...io_utils.types import uint32
from ... import CLIENT_VERSION, WoWVersions


class DBCString:
    @staticmethod
    def read(f, str_block_ofs):
        ofs = uint32.read(f)
        pos = f.tell()
        f.seek(ofs + str_block_ofs)

        strng = b''
        while True:
            char = f.read(1)
            if char != b'\0':
                strng += char
            else:
                break
        f.seek(pos)

        return strng.decode('utf-8')

    @staticmethod
    def write(f, string, str_block_ofs):
        pos = f.tell()
        f.seek(0, 2)
        str_pos = f.tell()
        f.write((string + '\0').encode('utf-8'))
        f.seek(pos)
        uint32.write(str_pos - str_block_ofs)


class DBCLangString:
    def __init__(self):
        if CLIENT_VERSION < WoWVersions.CATA:
            self.enUS = ''
            self.koKR = ''
            self.frFR = ''
            self.deDE = ''
            self.enCN = ''  # also zhCN
            self.enTW = ''  # also zhTW
            self.esES = ''
            self.esMX = ''

            if CLIENT_VERSION >= WoWVersions.TBC:
                self.ruRU = ''
                self.jaJP = ''
                self.ptPT = ''  # also ptBR
                self.itIT = ''
                self.unknown_12 = ''
                self.unknown_13 = ''
                self.unknown_14 = ''
                self.unknown_15 = ''

        else:
            self.client_locale = ''

        self.flags = 0

    @classmethod
    def read(cls, f, str_block_ofs):
        instance = cls()

        if CLIENT_VERSION < WoWVersions.CATA:
            instance.enUS = DBCString.read(f, str_block_ofs)
            instance.koKR = DBCString.read(f, str_block_ofs)
            instance.frFR = DBCString.read(f, str_block_ofs)
            instance.deDE = DBCString.read(f, str_block_ofs)
            instance.enCN = DBCString.read(f, str_block_ofs)
            instance.enTW = DBCString.read(f, str_block_ofs)
            instance.esES = DBCString.read(f, str_block_ofs)
            instance.esMX = DBCString.read(f, str_block_ofs)

            if CLIENT_VERSION >= WoWVersions.TBC:
                instance.ruRU = DBCString.read(f, str_block_ofs)
                instance.jaJP = DBCString.read(f, str_block_ofs)
                instance.ptPT = DBCString.read(f, str_block_ofs)
                instance.itIT = DBCString.read(f, str_block_ofs)
                instance.unknown_12 = DBCString.read(f, str_block_ofs)
                instance.unknown_13 = DBCString.read(f, str_block_ofs)
                instance.unknown_14 = DBCString.read(f, str_block_ofs)
                instance.unknown_15 = DBCString.read(f, str_block_ofs)

        else:
            instance.client_locale = DBCString.read(f, str_block_ofs)

        instance.flags = uint32.read(f)

        return instance

    @staticmethod
    def write(instance, f, str_block_ofs):

        if CLIENT_VERSION < WoWVersions.CATA:
            DBCString.write(f, instance.enUS, str_block_ofs)
            DBCString.write(f, instance.koKR, str_block_ofs)
            DBCString.write(f, instance.frFR, str_block_ofs)
            DBCString.write(f, instance.deDE, str_block_ofs)
            DBCString.write(f, instance.enCN, str_block_ofs)
            DBCString.write(f, instance.enTW, str_block_ofs)
            DBCString.write(f, instance.esES, str_block_ofs)
            DBCString.write(f, instance.esMX, str_block_ofs)

            if CLIENT_VERSION >= WoWVersions.TBC:
                DBCString.write(f, instance.ruRU, str_block_ofs)
                DBCString.write(f, instance.jaJP, str_block_ofs)
                DBCString.write(f, instance.ptPT, str_block_ofs)
                DBCString.write(f, instance.itIT, str_block_ofs)
                DBCString.write(f, instance.unknown_12, str_block_ofs)
                DBCString.write(f, instance.unknown_13, str_block_ofs)
                DBCString.write(f, instance.unknown_14, str_block_ofs)
                DBCString.write(f, instance.unknown_15, str_block_ofs)

        else:
            DBCString.write(f, instance.client_locale, str_block_ofs)

        uint32.write(f, instance.flags)

        return instance

