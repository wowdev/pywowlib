import re
import os
import time
import csv

from typing import Union, List, Dict

from .. import WoWVersionManager, WoWVersions
from .mpq import MPQFile
from .casc.CASC import CASCHandler, FileOpenFlags, LocaleFlags
from ..wdbx.wdbc import DBCFile
from ..blp import BLP2PNG


class WoWFileData:
    def __init__(self, wow_path, project_path):
        self.wow_path = wow_path
        self.files = self.init_mpq_storage(self.wow_path, project_path) if WoWVersionManager().client_version < WoWVersions.WOD \
                     else self.init_casc_storage(self.wow_path, project_path)

        #self.db_files_client = DBFilesClient(self)
        #self.db_files_client.init_tables()

        with open(os.path.join(os.path.dirname(__file__), 'listfile.csv'), newline='') as f:
            self.listfile = {int(row[0]): row[1] for row in csv.reader(f, delimiter=';')}

    def __del__(self):
        print("\nUnloaded game data.")

    def has_file(self, identifier: Union[str, int]):
        """ Check if the file is available in WoW filesystem """
        for storage, type in reversed(self.files):
            if type:
                if WoWVersionManager().client_version < WoWVersions.WOD:
                    file = identifier in storage
                else:

                    if isinstance(identifier, int):
                        file = (identifier, FileOpenFlags.CASC_OPEN_BY_FILEID) in storage

                    elif isinstance(identifier, str):
                        file = (identifier, FileOpenFlags.CASC_OPEN_BY_NAME) in storage

            else:
                abs_path = os.path.join(storage, identifier)
                file = os.path.exists(abs_path) and os.path.isfile(abs_path)

            if file:
                return storage, type

        return None, None

    def read_file(self, identifier: Union[str, int], local_dir: str = "", no_exc: bool = False) -> bytes:
        """ Read the latest version of the file from loaded archives and directories. """

        if WoWVersionManager().client_version < WoWVersions.WOD:

            if local_dir:
                local_path = os.path.join(local_dir, os.path.basename(identifier))

                if os.path.isfile(local_path):
                    return open(local_path, 'rb').read()

                local_path = os.path.join(local_dir, identifier)
                if os.path.isfile(local_path):
                    return open(local_path, 'rb').read()

            storage, is_archive = self.has_file(identifier)

            if storage:

                if is_archive:
                    return storage.open(identifier).read()

                else:
                    return open(os.path.join(storage, identifier), "rb").read()

        else:

            if local_dir:

                filepath = self.guess_filepath(identifier) if isinstance(identifier, int) else identifier

                if filepath:
                    local_path = os.path.join(local_dir, os.path.basename(filepath))

                    if os.path.isfile(local_path):
                        return open(local_path, 'rb').read()

                    local_path = os.path.join(local_dir, filepath)

                    if os.path.isfile(local_path):
                        return open(local_path, 'rb').read()

            storage, is_archive = self.has_file(identifier)

            if storage:

                if is_archive:
                    open_flag = FileOpenFlags.CASC_OPEN_BY_FILEID \
                        if isinstance(identifier, int) else FileOpenFlags.CASC_OPEN_BY_NAME

                    with storage.read_file(identifier, open_flag) as casc_file:
                        file = casc_file.data

                    return file

                else:

                    return open(os.path.join(storage, identifier), "rb").read()

        error_msg = "Requested file \"{}\" was not found in WoW filesystem.".format(identifier)

        if no_exc:
            print(error_msg)
        else:
            raise KeyError(error_msg)

    def extract_file(  self
                     , dir_path: str
                     , identifier: Union[str, int]
                     , host_file: str = ""
                     , file_format: str = ""
                     , local_dir: str = ""
                     , no_exc: bool = False) -> str:
        """ Extract the latest version of the file from loaded archives to provided working directory. """

        file = self.read_file(identifier, local_dir, no_exc)

        if isinstance(identifier, str):
            filepath = identifier

            if os.name != 'nt':
                filepath = filepath.replace('\\', '/')

        else:
            filepath = self.guess_filepath(identifier, file_format, host_file)

        if not file:
            return filepath

        wow_file_dir = os.path.dirname(filepath)

        if wow_file_dir in dir_path:
            abs_path = os.path.join(dir_path, os.path.basename(filepath))

        else:
            abs_path = os.path.join(dir_path, filepath)

        local_dir = os.path.dirname(abs_path)

        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        f = open(abs_path, 'wb')
        f.write(file or b'')
        f.close()

        return filepath

    def extract_files(  self
                      , dir_path: str
                      , identifiers: List[Union[str, int]]
                      , host_file: str = ""
                      , file_format: str = ""
                      , local_dir: str = ""
                      , no_exc: bool = False) -> List[str]:

        """ Extract the latest version of the files from loaded archives to provided working directory. """

        return [self.extract_file(dir_path, identifier, host_file, file_format, local_dir, no_exc)
                for identifier in identifiers]

    def extract_textures_as_png(  self
                                , dir_path: str
                                , identifiers
                                , host_file: str = ""
                                , local_dir: str = "") -> Dict[Union[int, str], str]:
        """ Read the latest version of the texture files from loaded archives and directories and
        extract them to current working directory as PNG images. """

        pairs = []
        filepaths = {}

        for identifier in identifiers:

            filepath = identifier

            if isinstance(identifier, int):

                filepath = self.guess_filepath(identifier, 'blp', host_file)

            filepaths[identifier] = filepath

            if os.name != 'nt':
                filename_ = filepath.replace('\\', '/')

                wow_file_dir = os.path.dirname(filename_)

                if wow_file_dir in dir_path:
                    abs_path = os.path.join(dir_path, os.path.basename(filename_))

                else:
                    abs_path = os.path.join(dir_path, filename_)

            else:

                wow_file_dir = os.path.dirname(filepath)

                if wow_file_dir in dir_path:
                    abs_path = os.path.join(dir_path, os.path.basename(filepath))

                else:
                    abs_path = os.path.join(dir_path, filepath)

            if not os.path.exists(os.path.splitext(abs_path)[0] + ".png"):
                try:
                    pairs.append((self.read_file(identifier, local_dir), filepath.replace('\\', '/').encode('utf-8')))
                except KeyError as e:
                    print(e)
        if pairs:
            BLP2PNG().convert(pairs, dir_path.encode('utf-8'))

        return filepaths

    def guess_filepath(self, identifier: int, file_format: str = "", host_file: str = "") -> str:
        """ Tries to get the filepath from listfile or makes a new one"""

        filepath = self.listfile.get(identifier)

        if not filepath:

            if host_file:
                host_dir = os.path.dirname(host_file)
                host_basename = os.path.splitext(os.path.basename(host_file))[0]

                filepath = os.path.join(host_dir, "{}_{}.{}".format(host_basename, identifier, file_format))

            else:
                filepath = "{}.{}".format(identifier, file_format)

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
    def list_game_data_paths(path):
        """List files and directories in a directory that correspond to WoW patch naming rules."""
        dir_files = []
        for f in os.listdir(path):
            cur_path = os.path.join(path, f)

            if os.path.isfile(cur_path) \
            and os.path.splitext(f)[1].lower() == '.mpq' \
            or not os.path.isfile(cur_path) \
            and re.match(r'patch-\w.mpq', f.lower()):
                dir_files.append(cur_path.lower().strip())

        map(lambda x: x.lower(), dir_files)

        dir_files.sort(key=lambda s: os.path.splitext(s)[0])

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

        locale_dir_files = []
        for f in os.listdir(locale_path):
            cur_path = os.path.join(locale_path, f)

            if os.path.isfile(cur_path) \
            and os.path.splitext(f)[1].lower() == '.mpq' \
            or not os.path.isfile(cur_path) \
            and re.match(r'patch-{}-\w.mpq'.format(token), f.lower()):
                locale_dir_files.append(cur_path.lower().strip())

        map(lambda x: x.lower(), locale_dir_files)
        locale_dir_files.sort(key=lambda s: os.path.splitext(s)[0])

        return dir_files + locale_dir_files


    @staticmethod
    def is_wow_path_valid(wow_path):
        """Check if a given path is a path to WoW client."""
        if wow_path:
            if os.path.exists(os.path.join(wow_path, "Wow.exe")):
                return True

            wow_path_raw = wow_path.split(':')[0]
            if os.path.exists(os.path.join(os.path.join(wow_path_raw, "_retail_"), "wow.exe")):
                return True

        return False

    @staticmethod
    def init_casc_storage(wow_path, project_path=None):

        if not WoWFileData.is_wow_path_valid(wow_path):
            print("\nPath to World of Warcraft is empty or invalid. Failed to load game data.")
            return None

        print("\nProcessing available game resources of client: " + wow_path)
        start_time = time.time()

        wow_path = os.path.join(wow_path, '')  # ensure the path has trailing slash

        casc = CASCHandler(wow_path, LocaleFlags.CASC_LOCALE_ENUS, False)

        print("\nDone initializing data packages.")
        print("Total loading time: ", time.strftime("%M minutes %S seconds", time.gmtime(time.time() - start_time)))
        return [(casc, True), (project_path.lower().strip(os.sep), False)] if project_path else [(casc, True)]

    @staticmethod
    def init_mpq_storage(wow_path, project_path=None):
        """Open game resources and store links to them in memory"""

        print("\nProcessing available game resources of client: " + wow_path)
        start_time = time.time()

        if not WoWFileData.is_wow_path_valid(wow_path):
            print("\nPath to World of Warcraft is empty or invalid. Failed to load game data.")
            return None

        data_packages = WoWFileData.list_game_data_paths(os.path.join(wow_path, "Data"))

        # project path takes top priority if it is not loaded already
        p_path = project_path.lower().strip(os.sep)
        if p_path not in data_packages:
            data_packages.append(p_path)

        resource_map = []

        for package in data_packages:
            if os.path.isfile(package):
                resource_map.append((MPQFile(package, 0x00000100), True))
                print("\nLoaded MPQ: " + os.path.basename(package))
            else:
                resource_map.append((package, False))
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



