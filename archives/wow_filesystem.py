import re
import os
import time
from .mpq.storm import MPQFile
from ..wdbx.wdbc import DBCFile
from ..blp.BLP2PNG import BlpConverter


class WoWFileData:
    def __init__(self, wow_path, project_path):
        self.wow_path = wow_path
        self.files = self.open_game_resources(self.wow_path, project_path)

        self.db_files_client = DBFilesClient(self)
        self.db_files_client.init_tables()

    def __del__(self):
        print("\nUnloading game data...")

    def has_file(self, filepath):
        """ Check if the file is available in WoW filesystem """
        for storage, type in reversed(self.files):
            if type:
                file = filepath in storage
            else:
                abs_path = os.path.join(storage, filepath)
                file = os.path.exists(abs_path) and os.path.isfile(abs_path)

            if file:
                return storage, type

        return None, None

    def read_file(self, filepath):
        """ Read the latest version of the file from loaded archives and directories. """

        storage, type_ = self.has_file(filepath)
        if storage:
            if type_:
                file = storage.open(filepath).read()
            else:
                file = open(os.path.join(storage, filepath), "rb").read()

        else:
            raise KeyError("\nRequested file <<{}>> not found in WoW filesystem.".format(filepath))

        return file

    def extract_file(self, dir, filepath):
        """ Extract the latest version of the file from loaded archives to provided working directory. """

        file = self.read_file(filepath)

        if os.name != 'nt':
            filepath = filepath.replace('\\', '/')

        abs_path = os.path.join(dir, filepath)
        local_dir = os.path.dirname(abs_path)

        if not os.path.exists(local_dir):
            os.makedirs(local_dir)

        f = open(abs_path, 'wb')
        f.write(file or b'')
        f.close()

    def extract_files(self, dir, filenames):
        """ Extract the latest version of the files from loaded archives to provided working directory. """

        for filename in filenames:
            self.extract_file(dir, filename)

    def extract_textures_as_png(self, dir, filenames):
        """ Read the latest version of the texture files from loaded archives and directories and
        extract them to current working directory as PNG images. """

        pairs = []

        for filename in filenames:
            if os.name != 'nt':
                filename_ = filename.replace('\\', '/')

                abs_path = os.path.join(dir, filename_)
            else:
                abs_path = os.path.join(dir, filename)

            if not os.path.exists(os.path.splitext(abs_path)[0] + ".png"):
                try:
                    pairs.append((self.read_file(filename), filename.replace('\\', '/').encode('utf-8')))
                except KeyError as e:
                    print(e)
        if pairs:
            BlpConverter().convert(pairs, dir.encode('utf-8'))

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
        if wow_path and os.path.exists(os.path.join(wow_path, "Wow.exe")):
            return True

        return False

    @staticmethod
    def open_game_resources(wow_path, project_path=None):
        """Open game resources and store links to them in memory"""

        print("\nProcessing available game resources of client: " + wow_path)
        start_time = time.time()

        if WoWFileData.is_wow_path_valid(wow_path):
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
        else:
            print("\nPath to World of Warcraft is empty or invalid. Failed to load game data.")
            return None


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



