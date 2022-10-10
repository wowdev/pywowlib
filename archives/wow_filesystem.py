import re
import os
import time
import csv
import hashlib

from typing import Union, List, Dict, Tuple

from .. import WoWVersionManager, WoWVersions
from .mpq import MPQFile
from .casc.CASC import CASCHandler, FileOpenFlags, LocaleFlags
from ..wdbx.wdbc import DBCFile
from ..blp import BLP2PNG


class WoWFileData:
    def __init__(self, wow_path, project_path):
        self.wow_path = wow_path
        self.files = self.init_mpq_storage(self.wow_path, project_path) \
            if WoWVersionManager().client_version < WoWVersions.WOD else self.init_casc_storage(self.wow_path,
                                                                                                project_path)

        #self.db_files_client = DBFilesClient(self)
        #self.db_files_client.init_tables()

        with open(os.path.join(os.path.dirname(__file__), 'listfile.csv'), newline='') as f:
            self.listfile = {int(row[0]): row[1] for row in csv.reader(f, delimiter=';')}

    def __del__(self):
        print("\nUnloaded game data.")

    def has_file(self, identifier: Union[str, int]):
        """ Check if the file is available in WoW filesystem """
        for storage, storage_type in reversed(self.files):
            if storage_type:
                if WoWVersionManager().client_version < WoWVersions.WOD:
                    identifier = identifier.replace('/', '\\')
                    file = identifier in storage
                else:

                    if isinstance(identifier, int):
                        file = (identifier, FileOpenFlags.CASC_OPEN_BY_FILEID) in storage

                    elif isinstance(identifier, str):
                        file = (identifier, FileOpenFlags.CASC_OPEN_BY_NAME) in storage

            else:

                if isinstance(identifier, int):
                    continue

                abs_path = os.path.join(storage, identifier)
                file = os.path.exists(abs_path) and os.path.isfile(abs_path)

            if file:
                return storage, storage_type

        return None, None

    def read_file(  self
                  , identifier: Union[str, int]
                  , local_dir: str = ""
                  , file_format: str = "unk"
                  , no_exc: bool = False) -> Tuple[bytes, str]:
        """ Read the latest version of the file from loaded archives and directories. """

        if WoWVersionManager().client_version < WoWVersions.WOD:

            if local_dir:
                local_path = os.path.join(local_dir, os.path.basename(identifier))

                if os.path.isfile(local_path):
                    return open(local_path, 'rb').read(), local_path

                local_path = os.path.join(local_dir, identifier)
                if os.path.isfile(local_path):
                    return open(local_path, 'rb').read(), local_path

            storage, is_archive = self.has_file(identifier)

            if storage:

                if is_archive:
                    return storage.open(identifier.replace('/', '\\')).read(), ""

                else:
                    filepath = os.path.join(storage, identifier)
                    return open(filepath, "rb").read(), filepath

        else:

            if local_dir:

                filepath = self.guess_filepath(identifier, file_format) if isinstance(identifier, int) else identifier

                if filepath:
                    local_path = os.path.join(local_dir, os.path.basename(filepath))

                    if os.path.isfile(local_path):
                        return open(local_path, 'rb').read(), local_path

                    local_path = os.path.join(local_dir, filepath)

                    if os.path.isfile(local_path):
                        return open(local_path, 'rb').read(), local_path

            storage, is_archive = self.has_file(identifier)

            if storage:

                if is_archive:
                    open_flag = FileOpenFlags.CASC_OPEN_BY_FILEID \
                        if isinstance(identifier, int) else FileOpenFlags.CASC_OPEN_BY_NAME

                    with storage.read_file(identifier, open_flag) as casc_file:
                        file = casc_file.data

                    return file, ""

                else:
                    filepath = os.path.join(storage, identifier)
                    return open(filepath, "rb").read(), filepath

        error_msg = "Requested file \"{}\" was not found in WoW filesystem.".format(identifier)

        if no_exc:
            print(error_msg)
        else:
            raise KeyError(error_msg)

    def extract_file(  self
                     , dir_path: str
                     , identifier: Union[str, int]
                     , file_format: str = ""
                     , no_exc: bool = False) -> str:
        """ Extract the latest version of the file from loaded archives to provided working directory. """

        file, filepath = self.read_file(identifier, dir_path, file_format, no_exc)

        if filepath:
            return filepath

        filepath = os.path.join(dir_path, identifier) \
            if isinstance(identifier, str) else os.path.join(dir_path, self.guess_filepath(identifier, file_format))

        file_dir = os.path.dirname(filepath)
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)

        f = open(filepath, 'wb')
        f.write(file or b'')
        f.close()

        return filepath

    def extract_files(  self
                      , dir_path: str
                      , identifiers: List[Union[str, int]]
                      , file_format: str = ""
                      , no_exc: bool = False) -> List[str]:

        """ Extract the latest version of the files from loaded archives to provided working directory. """

        return [self.extract_file(dir_path, identifier, file_format, no_exc) for identifier in identifiers]

    def extract_textures_as_png(self, dir_path: str, identifiers) -> Dict[Union[int, str], str]:
        """ Read the latest version of the texture files from loaded archives and directories and
        extract them to current working directory as PNG images. """

        pairs = []
        hash_writes = []
        filepaths = {}

        for identifier in identifiers:

            result = self.read_file(identifier, dir_path, 'blp', True)

            if result is None:
                continue

            file = result[0]

            filepath = (identifier.replace('/', '\\') if os.name == 'nt' else identifier) \
                if isinstance(identifier, str) else self.guess_filepath(identifier, 'blp')

            filepath_png_base = os.path.splitext(filepath)[0] + '.png'
            filepath_png = os.path.join(dir_path, filepath_png_base)
            filepath_hash = filepath_png+'.md5'
            filepaths[identifier] = filepath_png

            new_hash = hashlib.md5(file).hexdigest()
            if os.path.exists(filepath_png):
                if os.path.exists(filepath_hash):
                    with open(filepath_hash, 'r') as old_hash_file:
                        old_hash = old_hash_file.read()
                        if new_hash == old_hash:
                            continue
            # don't write now: wait until we know blp has been converted
            hash_writes.append((filepath_hash,new_hash))
            pairs.append((file, filepath_png_base.replace('\\', '/').encode('utf-8')))

        if pairs:
            BLP2PNG().convert(pairs, dir_path.encode('utf-8'))

        # note: assumes previous operation throws if it was not successful
        for (path,hash_value) in hash_writes:
            with open(path,'w') as file:
                file.write(hash_value)

        return filepaths

    def guess_filepath(self, identifier: int, file_format: str = ".unk") -> str:
        """ Tries to get the filepath from listfile or makes a new one"""

        filepath = self.listfile.get(identifier)

        if not filepath:
            filepath = "{}.{}".format(identifier, file_format)

        if os.name == 'nt':
            return filepath.replace('/', '\\')

        return filepath

    def traverse_file_path(self, path: str) -> Union[None, str]:
        """ Traverses WoW file system in order to identify internal file path. """

        path = (os.path.splitext(path)[0] + ".blp", "")
        rest_path = ""

        matches = []
        while True:
            path = os.path.split(path[0])

            if not path[1]:
                break

            rest_path = os.path.join(path[1], rest_path)
            rest_path = rest_path[:-1] if rest_path.endswith('\\') else rest_path

            if os.name != 'nt':
                rest_path_n = rest_path.replace('/', '\\')
            else:
                rest_path_n = rest_path

            rest_path_n = rest_path_n[:-1] if rest_path_n.endswith('\\') else rest_path_n

            if self.has_file(rest_path_n)[0]:
                matches.append(rest_path_n)

        max_len = 0
        ret_path = None
        for match in matches:
            length = len(match)

            if length > max_len:
                max_len = length
                ret_path = match

        return ret_path

    @staticmethod
    def list_game_data_paths(path) -> List[Tuple[str, str]]:
        """List files and directories in a directory that correspond to WoW patch naming rules."""
        """Returns list of tuples (normalized_path, real_path)"""

        dir_files: List[Tuple[str, str]] = []
        for f in os.listdir(path):
            cur_path = os.path.join(path, f)

            if os.path.isfile(cur_path) \
            and os.path.splitext(f)[1].lower() == '.mpq' \
            or not os.path.isfile(cur_path) \
            and re.match(r'patch-\w.mpq', f.lower()):
                dir_files.append((cur_path.lower().strip(), cur_path))

        map(lambda x: (x[0].lower(), x[1]), dir_files)

        dir_files.sort(key=lambda s: os.path.splitext(s[0])[0])

        locales = (
            'frFR', 'deDE', 'enGB',
            'enUS', 'itIT', 'koKR',
            'zhCN', 'zhTW', 'ruRU',
            'esES', 'esMX', 'ptBR'
        )

        for locale in locales:
            locale_path = os.path.join(path, locale)
            token = locale
            if os.path.exists(locale_path):
                break
        else:
            raise NotADirectoryError('\nFailed to load game data. WoW client appears to be missing a locale folder.')

        locale_dir_files: List[Tuple[str, str]] = []
        for f in os.listdir(locale_path):
            cur_path = os.path.join(locale_path, f)

            if os.path.isfile(cur_path) \
            and os.path.splitext(f)[1].lower() == '.mpq' \
            or not os.path.isfile(cur_path) \
            and re.match(r'patch-{}-\w.mpq'.format(token), f.lower()):
                locale_dir_files.append((cur_path.lower().strip(), cur_path))

        map(lambda x: (x[0].lower(), x[1]), locale_dir_files)
        locale_dir_files.sort(key=lambda s: os.path.splitext(s[0])[0])

        return dir_files + locale_dir_files

    @staticmethod
    def is_wow_path_valid(wow_path):
        """Check if a given path is a path to WoW client."""
        if wow_path:
            if os.path.exists(os.path.join(wow_path, "Wow.exe")):
                return True

            if os.path.exists(os.path.join(os.path.join(wow_path, "_retail_"), "WoW.exe")):
                return True

            if os.path.exists(os.path.join(os.path.join(wow_path, "_retail_"), "World of Warcraft.app")):
                return True

        return False

    @staticmethod
    def init_casc_storage(wow_path, project_path=None):

        if not WoWFileData.is_wow_path_valid(wow_path):
            print("\nPath to World of Warcraft is empty or invalid. Failed to load game data.")
            return None

        print("\nProcessing available game resources of client: " + wow_path)
        start_time = time.time()

        #wow_path = os.path.join(wow_path, '')  # ensure the path has trailing slash

        casc = CASCHandler(wow_path, LocaleFlags.CASC_LOCALE_ALL, False)

        print("\nDone initializing data packages.")
        print("Total loading time: ", time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))
        return [(casc, True), (project_path.lower().strip(os.sep), False)] if project_path else [(casc, True)]

    @staticmethod
    def init_mpq_storage(wow_path, project_path=None) -> List[Tuple[Union[MPQFile, str], bool]]:
        """Open game resources and store links to them in memory"""

        print("\nProcessing available game resources of client: " + wow_path)
        start_time = time.time()

        if not WoWFileData.is_wow_path_valid(wow_path):
            print("\nPath to World of Warcraft is empty or invalid. Failed to load game data.")
            return None

        data_packages = WoWFileData.list_game_data_paths(os.path.join(wow_path, "Data"))

        # project path takes top priority if it is not loaded already

        if project_path:
            p_path = project_path.lower().strip(os.sep)
            if p_path not in data_packages:
                data_packages.append((p_path, p_path))

        resource_map: List[Tuple[Union[MPQFile, str], bool]] = []

        for package, package_path in data_packages:
            if os.path.isfile(package_path):
                resource_map.append((MPQFile(package_path, 0x00000100), True))
                print("\nLoaded MPQ: " + os.path.basename(package))
            else:
                resource_map.append((package_path, False))
                print("\nLoaded folder patch: {}".format(os.path.basename(package)))

        print("\nDone initializing data packages.")
        print("Total loading time: ", time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))
        return resource_map


class DBFilesClient:
    def __init__(self, game_data):
        self.game_data = game_data
        self.tables = {}
        self.tables_to_save = []

    def __getattr__(self, name):
        if name in self.tables:
            return self.tables[name]

        wdb = DBCFile(name)
        wdb.read_from_gamedata(self.game_data)
        self.tables[name] = wdb

        return wdb

    def add(self, name):
        wdb = DBCFile(name)
        wdb.read_from_gamedata(self.game_data)
        self.tables[name] = wdb

        return wdb

    def save_table(self, wdb):
        self.tables_to_save.append(wdb)

    def save_changes(self):
        pass

    def __contains__(self, item):
        check = self.tables.get(item)
        return True if check else False

    def init_tables(self):
        self.add('AnimationData')



