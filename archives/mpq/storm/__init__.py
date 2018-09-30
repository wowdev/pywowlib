"""
Python wrapper around Storm C API bindings
"""
import os
import sys
from . import storm


class MPQFile(object):
    """
    An MPQ archive
    """
    ATTRIBUTES = "(attributes)"
    LISTFILE = "(listfile)"

    def __init__(self, name=None, flags=0):
        self.paths = []
        self._archives = []
        self._archive_names = {}
        if name is not None:
            self.add_archive(name, flags)

    def __contains__(self, name):
        for mpq in self._archives:
            if storm.SFileHasFile(mpq, name):
                return True
        return False

    def __repr__(self):
        return "<%s paths=%r>" % (self.__class__.__name__, self.paths)

    def _archive_contains(self, name):
        for mpq in self._archives:
            if storm.SFileHasFile(mpq, name):
                return mpq

    def _regenerate_listfile(self):
        self._listfile = []
        for mpq in self._archives:
            handle, file = storm.SFileFindFirstFile(mpq, "", "*")
            while True:
                self._listfile.append(file.replace("\\", "/"))
                try:
                    file = storm.SFileFindNextFile(handle)
                except storm.NoMoreFilesError:
                    break

    def add_archive(self, name, flags=0):
        """
        Adds an archive to the MPQFile
        """
        priority = 0  # Unused by StormLib
        mpq = storm.SFileOpenArchive(name, priority, flags)
        self._archives.append(mpq)
        self._archive_names[mpq] = name
        self.paths.append(name)
        self._listfile = []

    def close(self):
        """
        Flushes all archives in the MPQFile
        """
        for mpq in self._archives:
            storm.SFileCloseArchive(mpq)

    def flush(self):
        """
        Flushes all archives in the MPQFile
        """
        for mpq in self._archives:
            storm.SFileFlushArchive(mpq)

    def getinfo(self, f):
        """
        Returns a MPQInfo object for either a path or a MPQExtFile object.
        """
        if isinstance(f, str):
            f = self.open(f.replace("/", "\\"))
        return MPQInfo(f)

    def infolist(self):
        """
        Returns a list of class MPQInfo instances for files in all the archives
        in the MPQFile.
        """
        return [self.getinfo(x) for x in self.namelist()]

    def is_patched(self):
        """
        Returns whether at least one of the archives in the MPQFile has been patched.
        """
        for mpq in self._archives:
            if storm.SFileIsPatchedArchive(mpq):
                return True
        return False

    def namelist(self):
        """
        Returns a list of file names in all the archives in the MPQFile.
        """
        if not self._listfile:
            self._regenerate_listfile()
        return self._listfile

    def open(self, name, mode="r", patched=False):
        """
        Return file-like object for \a name in mode \a mode.
        If \a name is an int, it is treated as an index within the MPQFile.
        If \a patched is True, the file will be opened fully patched,
        otherwise unpatched.
        Raises a KeyError if no file matches \a name.
        """
        if isinstance(name, int):
            name = "File%08x.xxx" % (int)

        scope = int(bool(patched))

        mpq = self._archive_contains(name)
        if not mpq:
            raise KeyError("There is no item named %r in the archive" % (name))

        return MPQExtFile(storm.SFileOpenFileEx(mpq, name, scope), name)

    def patch(self, name, prefix=None, flags=0):
        """
        Patches all archives in the MPQFile with \a name under prefix \a prefix.
        """
        for mpq in self._archives:
            storm.SFileOpenPatchArchive(mpq, name, prefix, flags)

        # invalidate the listfile
        self._listfile = []

    def extract(self, name, path=".", patched=False):
        """
        Extracts \a name to \a path.
        If \a patched is True, the file will be extracted fully patched,
        otherwise unpatched.
        """
        scope = int(bool(patched))
        mpq = self._archive_contains(name)
        if not mpq:
            raise KeyError("There is no item named %r in the archive" % (name))
        storm.SFileExtractFile(mpq, name, path, scope)

    def printdir(self):
        """
        Print a table of contents for the MPQFile
        """
        infolist = sorted(self.infolist(), key=lambda item: item.filename.lower())
        longest_filename = max(infolist, key=lambda item: len(item.filename))
        longest_filename = len(longest_filename.filename)
        format_string = "%%-%is %%12s %%12s" % (longest_filename)

        print(format_string % ("File Name", "Size", "Packed Size"))
        for x in infolist:
            print(format_string % (x.filename, x.file_size, x.compress_size))

    def read(self, name):
        """
        Return file bytes (as a string) for \a name.
        """
        if isinstance(name, MPQInfo):
            name = name.name
        f = self.open(name)
        return f.read()

    def testmpq(self):
        pass


class MPQExtFile(object):
    def __init__(self, file, name):
        self._file = file
        self.name = name

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.name)

    def _info(self, type):
        return storm.SFileGetFileInfo(self._file, type)

    def close(self):
        storm.SFileCloseFile(self._file)

    def read(self, size=None):
        if size is None:
            size = self.size() - self.tell()
        return storm.SFileReadFile(self._file, size)

    def seek(self, offset, whence=os.SEEK_SET):
        storm.SFileSetFilePointer(self._file, offset, whence)

    def size(self):
        return storm.SFileGetFileSize(self._file)

    def tell(self):
        return storm.SFileSetFilePointer(self._file, 0, os.SEEK_CUR)


class MPQInfo(object):
    def __init__(self, file):
        self._file = file

    @property
    def basename(self):
        return os.path.basename(self.filename)

    @property
    def filename(self):
        return self._file.name.replace("\\", "/")

    @property
    def date_time(self):
        return self._file._info(storm.SFILE_INFO_FILETIME)

    @property
    def compress_type(self):
        raise NotImplementedError

    @property
    def CRC(self):
        raise NotImplementedError

    @property
    def compress_size(self):
        return self._file._info(storm.SFileInfoCompressedSize)

    @property
    def file_size(self):
        return self._file._info(storm.SFileInfoFileSize)
