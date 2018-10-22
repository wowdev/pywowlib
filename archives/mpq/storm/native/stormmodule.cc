#include <Python.h>
#define STORM_MODULE
#include "stormmodule.h"

#include "python_wrapper.hpp"

#include <vector>

#ifdef __cplusplus
extern "C" {
#endif

static PyObject *StormError;
static PyObject *NoMoreFilesError;

/*
 * Manipulating MPQ archives
 */

static PyObject * Storm_SFileOpenArchive(PyObject *self, PyObject *args) {
	HANDLE mpq = NULL;
	TCHAR *name;
	DWORD priority;
	int flags;

	if (!python::parse_tuple(args, "SFileOpenArchive", &name, &priority, &flags)) {
		return NULL;
	}
	bool result = SFileOpenArchive(name, priority, MPQ_OPEN_READ_ONLY, &mpq);

	if (!result) {
		DWORD error = GetLastError();
		switch (error) {
			case ERROR_FILE_NOT_FOUND:
				PyErr_Format(PyExc_IOError, "Could not open archive: No such file or directory: %s", name);
				break;

			default:
				PyErr_Format(StormError, "Error opening archive %s: %i", name, error);
				break;
		}
		return NULL;
	}

	return python::build_value(mpq);
}

static PyObject * Storm_SFileAddListFile(PyObject *self, PyObject *args) {
	HANDLE mpq = NULL;
	TCHAR *name;

	if (!python::parse_tuple(args, "SFileAddListFile", &mpq, &name)) {
		return NULL;
	}
	int result = SFileAddListFile(mpq, name);

	if (result != ERROR_SUCCESS) {
		PyErr_SetString(StormError, "Error adding listfile");
		return NULL;
	}

	Py_RETURN_NONE;
}

static PyObject * Storm_SFileFlushArchive(PyObject *self, PyObject *args) {
	HANDLE mpq = NULL;

	if (!python::parse_tuple(args, "SFileFlushArchive", &mpq)) {
		return NULL;
	}
	bool result = SFileFlushArchive(mpq);

	if (!result) {
		PyErr_SetString(StormError, "Error flushing archive, archive may be corrupted!");
		return NULL;
	}

	Py_RETURN_NONE;
}

static PyObject * Storm_SFileCloseArchive(PyObject *self, PyObject *args) {
	HANDLE mpq = NULL;

	if (!python::parse_tuple (args, "SFileCloseArchive", &mpq)) {
		return NULL;
	}
	bool result = SFileCloseArchive(mpq);

	if (!result) {
		PyErr_SetString(StormError, "Error closing archive");
		return NULL;
	}

	Py_RETURN_NONE;
}

static PyObject * Storm_SFileCompactArchive(PyObject *self, PyObject *args) {
	HANDLE mpq = NULL;
	TCHAR *listfile;
	bool reserved = 0; /* Unused */

	if (!python::parse_tuple(args, "SFileCompactArchive", &mpq, &listfile)) {
		return NULL;
	}
	bool result = SFileCompactArchive(mpq, listfile, reserved);

	if (!result) {
		PyErr_SetString(StormError, "Error compacting archive");
		return NULL;
	}

	Py_RETURN_NONE;
}

/*
 * Using Patched archives
 */

static PyObject * Storm_SFileOpenPatchArchive(PyObject *self, PyObject *args) {
	HANDLE mpq = NULL;
	TCHAR *name;
	char *prefix;
	DWORD flags;

	if (!python::parse_tuple(args, "SFileOpenPatchArchive", &mpq, &name, &prefix, &flags)) {
		return NULL;
	}
	bool result = SFileOpenPatchArchive(mpq, name, prefix, flags);

	if (!result) {
		DWORD error = GetLastError();
		switch (error) {
			case ERROR_INVALID_HANDLE:
				PyErr_SetString(PyExc_TypeError, "Could not patch archive: Invalid handle");
				break;

			case ERROR_INVALID_PARAMETER:
				PyErr_SetString(PyExc_TypeError, "Could not patch archive: Invalid file name or patch prefix");
				break;

			case ERROR_FILE_NOT_FOUND:
				PyErr_Format(PyExc_IOError, "Could not patch archive: No such file or directory: %s", name);
				break;

			case ERROR_ACCESS_DENIED:
				PyErr_SetString(PyExc_IOError, "Could not patch archive: Access denied");
				break;

			default:
				PyErr_Format(StormError, "Could not patch archive: %i", error);
				break;
		}
		return NULL;
	}

	Py_RETURN_TRUE;
}

static PyObject * Storm_SFileIsPatchedArchive(PyObject *self, PyObject *args) {
	HANDLE mpq = NULL;

	if (!python::parse_tuple(args, "SFileIsPatchedArchive", &mpq)) {
		return NULL;
	}
	bool result = SFileIsPatchedArchive(mpq);

	if (!result) {
		Py_RETURN_FALSE;
	}

	Py_RETURN_TRUE;
}

/*
 * Reading Files
 */

static PyObject * Storm_SFileOpenFileEx(PyObject *self, PyObject *args) {
	HANDLE mpq = NULL;
	char *name;
	DWORD scope;
	HANDLE file = NULL;

	if (!python::parse_tuple(args, "SFileOpenFileEx", &mpq, &name, &scope)) {
		return NULL;
	}
	bool result = SFileOpenFileEx(mpq, name, scope, &file);

	if (!result) {
		PyErr_SetString(StormError, "Error opening file");
		return NULL;
	}

	return python::build_value(file);
}

static PyObject * Storm_SFileGetFileSize(PyObject *self, PyObject *args) {
	HANDLE file = NULL;

	if (!python::parse_tuple(args, "SFileGetFileSize", &file)) {
		return NULL;
	}
	DWORD sizeHigh;
	DWORD sizeLow = SFileGetFileSize(file, &sizeHigh);

	if (sizeLow == SFILE_INVALID_SIZE) {
		PyErr_SetString(StormError, "Error getting file size");
		return NULL;
	}

	return python::build_value ( (((uint64_t)sizeLow  << 0)  & 0x00000000FFFFFFFF)
	                           | (((uint64_t)sizeHigh << 32) & 0xFFFFFFFF00000000)
	                           );
}

static PyObject * Storm_SFileSetFilePointer(PyObject *self, PyObject *args) {
	HANDLE file = NULL;
	uint64_t offset = 0;
	DWORD whence;

	if (!python::parse_tuple(args, "SFileSetFilePointer", &file, &offset, &whence)) {
		return NULL;
	}

	//! \note The StormLib API is broken here: LONG is signed, while it surely
	//! should be unsigned.
	LONG posLow =  (offset & 0x00000000FFFFFFFF) >> 0;
	LONG posHigh = (offset & 0xFFFFFFFF00000000) >> 32;
	DWORD result = SFileSetFilePointer(file, posLow, &posHigh, whence);

	if (result == SFILE_INVALID_SIZE) {
		DWORD error = GetLastError();
		switch (error) {
			case ERROR_INVALID_HANDLE:
				PyErr_SetString(PyExc_TypeError, "Could not seek within file: Invalid handle");
				break;
			case ERROR_INVALID_PARAMETER:
				if (whence != FILE_BEGIN && whence != FILE_CURRENT && whence != FILE_END) {
					PyErr_Format(PyExc_TypeError, "Could not seek within file: %i is not a valid whence", whence);
				} else {
					PyErr_Format(PyExc_TypeError, "Could not seek within file: offset %lu is too large", offset);
				}
				break;
			default:
				PyErr_Format(StormError, "Error seeking in file: %i", GetLastError());
				break;
		}
		return NULL;
	}

	return python::build_value ( (((uint64_t)result  << 0)  & 0x00000000FFFFFFFF)
	                           | (((uint64_t)posHigh << 32) & 0xFFFFFFFF00000000)
	                           );
}

static PyObject * Storm_SFileReadFile(PyObject *self, PyObject *args) {
	HANDLE file = NULL;
	DWORD size;
	DWORD bytesRead;

	if (!python::parse_tuple(args, "SFileReadFile", &file, &size)) {
		return NULL;
	}

	std::vector<char> buffer (size);

	bool result = SFileReadFile(file, buffer.data(), size, &bytesRead, NULL);

	if (!result) {
		DWORD error = GetLastError();
		if (error != ERROR_HANDLE_EOF) {
			switch (error) {
				case ERROR_INVALID_HANDLE:
					PyErr_SetString(PyExc_TypeError, "Could not read file: Invalid handle");
					break;
				case ERROR_FILE_CORRUPT:
					PyErr_SetString(PyExc_IOError, "Could not read file: File is corrupt");
					break;
				default:
					PyErr_Format(StormError, "Could not read file: %i", error);
					break;
			}
			/* Emulate python's read() behaviour => we don't care if we go past EOF */
			return NULL;
		}
	}

	assert (bytesRead <= (DWORD)std::numeric_limits<int>::max());
	return python::build_value(std::pair<char*, int> (buffer.data(), bytesRead));
}

static PyObject * Storm_SFileCloseFile(PyObject *self, PyObject *args) {
	HANDLE file = NULL;

	if (!python::parse_tuple(args, "SFileCloseFile", &file)) {
		return NULL;
	}
	bool result = SFileCloseFile(file);

	if (!result) {
		PyErr_SetString(StormError, "Error closing file");
		return NULL;
	}

	Py_RETURN_NONE;
}

static PyObject * Storm_SFileHasFile(PyObject *self, PyObject *args) {
	HANDLE mpq = NULL;
	char *name;

	if (!python::parse_tuple(args, "SFileHasFile", &mpq, &name)) {
		return NULL;
	}
	bool result = SFileHasFile(mpq, name);

	if (!result) {
		if (GetLastError() == ERROR_FILE_NOT_FOUND) {
			Py_RETURN_FALSE;
		} else {
			PyErr_SetString(StormError, "Error searching for file");
			return NULL;
		}
	}

	Py_RETURN_TRUE;
}

static PyObject * Storm_SFileGetFileName(PyObject *self, PyObject *args) {
	HANDLE file = NULL;
	char name[MAX_PATH];

	if (!python::parse_tuple(args, "SFileGetFileName", &file)) {
		return NULL;
	}
	bool result = SFileGetFileName(file, name);

	if (!result) {
		PyErr_SetString(StormError, "Error getting file name");
		return NULL;
	}

	return python::build_value(name);
}

static PyObject * Storm_SFileGetFileInfo(PyObject *self, PyObject *args) {
	HANDLE file = NULL;
	SFileInfoClass infoClass;

	if (!python::parse_tuple(args, "SFileGetFileInfo", &file, &infoClass)) {
		return NULL;
	}

	int value = 0;
	DWORD size = sizeof(value);
	bool result = SFileGetFileInfo(file, infoClass, &value, size, 0);

	if (!result) {
		if (GetLastError() == ERROR_INVALID_PARAMETER) {
			PyErr_SetString(PyExc_TypeError, "Invalid INFO_TYPE queried");
			return NULL;
		} else {
			PyErr_SetString(StormError, "Error getting info");
			return NULL;
		}
	}

	return python::build_value(value);
}

static PyObject * Storm_SFileExtractFile(PyObject *self, PyObject *args) {
	HANDLE mpq = NULL;
	char *name;
	TCHAR *localName;
	DWORD scope;

	if (!python::parse_tuple(args, "SFileExtractFile", &mpq, &name, &localName, &scope)) {
		return NULL;
	}
	bool result = SFileExtractFile(mpq, name, localName, scope);

	if (!result) {
		if (GetLastError() == ERROR_UNKNOWN_FILE_KEY) {
			PyErr_Format(StormError, "Error extracting file: File Key `%s' unknown", name);
			return NULL;
		} else {
			PyErr_Format(StormError, "Error extracting file: %i", GetLastError());
			return NULL;
		}
	}

	Py_RETURN_NONE;
}

static PyObject * Storm_SFileFindFirstFile(PyObject *self, PyObject *args) {
	HANDLE mpq = NULL;
	char *mask;
	SFILE_FIND_DATA findFileData;
	TCHAR *listFile; // XXX Unused for now

	if (!python::parse_tuple(args, "SFileFindFirstFile", &mpq, &listFile, &mask)) {
		return NULL;
	}
	HANDLE result = SFileFindFirstFile(mpq, mask, &findFileData, NULL);

	if (!result) {
		PyErr_SetString(StormError, "Error searching archive");
		return NULL;
	}

	return python::build_value(result, findFileData.cFileName);
}

static PyObject * Storm_SFileFindNextFile(PyObject *self, PyObject *args) {
	HANDLE find = NULL;
	SFILE_FIND_DATA findFileData;

	if (!python::parse_tuple(args, "SFileFindFirstFile", &find)) {
		return NULL;
	}
	bool result = SFileFindNextFile(find, &findFileData);

	if (!result) {
		if (GetLastError() == ERROR_NO_MORE_FILES) {
			PyErr_SetString(NoMoreFilesError, "");
			return NULL;
		} else {
			PyErr_SetString(StormError, "Error searching for next result in archive");
			return NULL;
		}
	}

	return python::build_value(findFileData.cFileName);
}

static PyObject * Storm_SFileFindClose(PyObject *self, PyObject *args) {
	HANDLE find = NULL;

	if (!python::parse_tuple(args, "SFileFindFirstFile", &find)) {
		return NULL;
	}
	bool result = SFileFindClose(find);

	if (!result) {
		PyErr_SetString(StormError, "Error closing archive search");
		return NULL;
	}

	Py_RETURN_NONE;
}

static PyObject * Storm_SListFileFindFirstFile(PyObject *self, PyObject *args) {
	HANDLE mpq = NULL;
	char *mask;
	char *listFile; // XXX Unused for now
	SFILE_FIND_DATA findFileData;

	if (!python::parse_tuple(args, "SListFileFindFirstFile", &mpq, &listFile, &mask)) {
		return NULL;
	}
	HANDLE result = SListFileFindFirstFile(mpq, NULL, mask, &findFileData);

	if (!result) {
		PyErr_SetString(StormError, "Error searching listfile");
		return NULL;
	}

	return python::build_value(result, findFileData.cFileName);
}

static PyObject * Storm_SListFileFindNextFile(PyObject *self, PyObject *args) {
	HANDLE find = NULL;
	SFILE_FIND_DATA findFileData;

	if (!python::parse_tuple(args, "SListFileFindFirstFile", &find)) {
		return NULL;
	}
	bool result = SListFileFindNextFile(find, &findFileData);

	if (!result) {
		if (GetLastError() == ERROR_NO_MORE_FILES) {
			PyErr_SetString(NoMoreFilesError, "");
			return NULL;
		} else {
			PyErr_SetString(StormError, "Error searching for next result in listfile");
			return NULL;
		}
	}

	return python::build_value(findFileData.cFileName);
}

static PyObject * Storm_SListFileFindClose(PyObject *self, PyObject *args) {
	HANDLE find = NULL;

	if (!python::parse_tuple(args, "SListFileFindFirstFile", &find)) {
		return NULL;
	}
	bool result = SListFileFindClose(find);

	if (!result) {
		PyErr_SetString(StormError, "Error closing listfile search");
		return NULL;
	}

	Py_RETURN_NONE;
}


static PyMethodDef StormMethods[] = {
	{"SFileOpenArchive",  Storm_SFileOpenArchive, METH_VARARGS, "Open an MPQ archive."},
	/* SFileCreateArchive */
	{"SFileAddListFile", Storm_SFileAddListFile, METH_VARARGS, "Adds an in-memory listfile to an open MPQ archive"},
	/* SFileSetLocale (unimplemented) */
	/* SFileGetLocale (unimplemented) */
	{"SFileFlushArchive", Storm_SFileFlushArchive, METH_VARARGS, "Flushes all unsaved data in an MPQ archive to the disk"},
	{"SFileCloseArchive",  Storm_SFileCloseArchive, METH_VARARGS, "Close an MPQ archive."},
	{"SFileCompactArchive", Storm_SFileCompactArchive, METH_VARARGS, "Compacts (rebuilds) the MPQ archive, freeing all gaps that were created by write operations"},
	/* SFileSetMaxFileCount */
	/* SFileSetCompactCallback (unimplemented) */

	{"SFileIsPatchedArchive",  Storm_SFileIsPatchedArchive, METH_VARARGS, "Determines if an MPQ archive has been patched"},
	{"SFileOpenPatchArchive", Storm_SFileOpenPatchArchive, METH_VARARGS, "Adds a patch archive to an MPQ archive"},

	{"SFileOpenFileEx", Storm_SFileOpenFileEx, METH_VARARGS, "Open a file from an MPQ archive"},
	{"SFileGetFileSize", Storm_SFileGetFileSize, METH_VARARGS, "Retrieve the size of a file within an MPQ archive"},
	{"SFileSetFilePointer", Storm_SFileSetFilePointer, METH_VARARGS, "Seeks to a position within archive file"},
	{"SFileReadFile", Storm_SFileReadFile, METH_VARARGS, "Reads bytes in an open file"},
	{"SFileCloseFile", Storm_SFileCloseFile, METH_VARARGS, "Close an open file"},
	{"SFileHasFile", Storm_SFileHasFile, METH_VARARGS, "Check if a file exists within an MPQ archive"},
	{"SFileGetFileName", Storm_SFileGetFileName, METH_VARARGS, "Retrieve the name of an open file"},
	{"SFileGetFileInfo", Storm_SFileGetFileInfo, METH_VARARGS, "Retrieve information about an open file or MPQ archive"},
	/* SFileVerifyFile (unimplemented) */
	/* SFileVerifyArchive (unimplemented) */
	{"SFileExtractFile", Storm_SFileExtractFile, METH_VARARGS, "Extracts a file from an MPQ archive to the local drive"},

	/* File searching */
	{"SFileFindFirstFile", Storm_SFileFindFirstFile, METH_VARARGS, "Finds the first file matching the specification in the archive"},
	{"SFileFindNextFile", Storm_SFileFindNextFile, METH_VARARGS, "Finds the next file matching the specification in the archive"},
	{"SFileFindClose", Storm_SFileFindClose, METH_VARARGS, "Stops searching files in the archive"},
	{"SListFileFindFirstFile", Storm_SListFileFindFirstFile, METH_VARARGS, "Finds the first file matching the specification in the listfile"},
	{"SListFileFindNextFile", Storm_SListFileFindNextFile, METH_VARARGS, "Finds the next file matching the specification in the listfile"},
	{"SListFileFindClose", Storm_SListFileFindClose, METH_VARARGS, "Stops searching files in the listfile"},
	{NULL, NULL, 0, NULL} /* Sentinel */
};


#define storm_doc "Python bindings for StormLib"
#define DECLARE(x) PyObject_SetAttrString(m, #x, PyLong_FromLong((long) x));

static struct PyModuleDef moduledef = {
	PyModuleDef_HEAD_INIT,
	"storm", /* m_name */
	storm_doc, /* m_doc */
	-1, /* m_size */
	StormMethods, /* m_methods */
	NULL, /* m_reload */
	NULL, /* m_traverse */
	NULL, /* m_clear */
	NULL, /* m_free */
};
#define MOD_INIT(name) PyMODINIT_FUNC PyInit_##name(void)

MOD_INIT(storm) {
	PyObject *m;

	m = PyModule_Create(&moduledef);
	if (m == NULL) return NULL;

	StormError = PyErr_NewException((char *)"storm.error", NULL, NULL);
	Py_INCREF(StormError);
	PyModule_AddObject(m, "error", StormError);

	NoMoreFilesError = PyErr_NewException((char *)"storm.NoMoreFilesError", NULL, NULL);
	Py_INCREF(NoMoreFilesError);
	PyModule_AddObject(m, "NoMoreFilesError", NoMoreFilesError);

	/* SFileOpenArchive */
	DECLARE(MPQ_OPEN_NO_LISTFILE);
	DECLARE(MPQ_OPEN_NO_ATTRIBUTES);
	DECLARE(MPQ_OPEN_FORCE_MPQ_V1);
	DECLARE(MPQ_OPEN_CHECK_SECTOR_CRC);
	DECLARE(MPQ_OPEN_READ_ONLY);

	/* SFileGetFileInfo */
	DECLARE(SFileInfoPatchChain);
	DECLARE(SFileInfoFileEntry);
	DECLARE(SFileInfoHashEntry);
	DECLARE(SFileInfoHashIndex);
	DECLARE(SFileInfoNameHash1);
	DECLARE(SFileInfoNameHash2);
	DECLARE(SFileInfoNameHash3);
	DECLARE(SFileInfoLocale);
	DECLARE(SFileInfoFileIndex);
	DECLARE(SFileInfoByteOffset);
	DECLARE(SFileInfoFileTime);
	DECLARE(SFileInfoFlags);
	DECLARE(SFileInfoFileSize);
	DECLARE(SFileInfoCompressedSize);
	DECLARE(SFileInfoEncryptionKey);
	DECLARE(SFileInfoEncryptionKeyRaw);

	/* SFileOpenFileEx, SFileExtractFile */
	DECLARE(SFILE_OPEN_FROM_MPQ);

	return m;
}

#ifdef __cplusplus
}
#endif
