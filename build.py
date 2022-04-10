#!/usr/bin/env python
import subprocess
import argparse
import shutil
import sys
import os

from typing import Iterable

PYTHON_PATH = sys.executable


def print_error(*s: str):
    print("\033[91m {}\033[00m".format(' '.join(s)))


def print_succes(*s: str):
    print("\033[92m {}\033[00m".format(' '.join(s)))


def print_info(*s: str):
    print("\033[93m {}\033[00m".format(' '.join(s)))


def build_type_mismatch(debug: bool) -> bool:

    has_mismatch = False
    if os.path.exists("build/build.cache"):
        with open("build/build.cache", 'rb') as f:
            f.seek(0, 2)
            pos = f.tell()
            if pos:
                f.seek(0)
                cur_mode = b'\x00' if debug else b'\x01'
                old_mode = f.read(1)
                if old_mode != cur_mode:
                    has_mismatch = True
            else:
                has_mismatch = True
    else:
        has_mismatch = True

    with open("build/build.cache", 'wb') as f:
        f.write(b'\x00' if debug else b'\x01')

    return has_mismatch


def clean_build_data(ext_dirs: Iterable[str]):
    for ext_dir in ext_dirs:
        shutil.rmtree(os.path.join(ext_dir, "build"), ignore_errors=True)

    shutil.rmtree("archives/casc/CASCLib/build", ignore_errors=True)
    shutil.rmtree("archives/mpq/native/StormLib/build", ignore_errors=True)


def build_project(debug: bool, clean: bool):

    try:
        import Cython
    except ImportError:
        raise Exception("\nCython is required to build this project.")

    try:
        from pip import main as pipmain
    except ImportError:
        try:
            from pip._internal import main as pipmain
        except ImportError:
            raise Exception("\npip is required to build this project.")

    import os

    root_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)).replace('\\', '/'))

    extension_dirs = (
        "archives/casc/",
        "archives/mpq/native/",
        "blp/BLP2PNG/",
        "blp/PNG2BLP/"
    )

    os.chdir(root_path)
    os.makedirs("build", exist_ok=True)

    # clean up build data if previous build type does not match with current, or if set manually with an option
    if build_type_mismatch(debug) or clean:
        clean_build_data(extension_dirs)

    print_info('\nBuilding pywowlib C++ extensions.')

    for module_relpath in extension_dirs:
        try:
            os.chdir(os.path.join(root_path, module_relpath))
            command_args = [PYTHON_PATH, "setup.py", 'build_clib', 'build_ext', '--inplace']

            if debug:
                command_args.append('--wbs_debug')

            status = subprocess.call(command_args)

            if status:
                print_error(f"\nProcess returned error code {status} while building module \"{module_relpath}\"")
                sys.exit(1)

        except PermissionError:
            print_error("\nThis build script may need to be called with admin (root) rights.")
            sys.exit(1)

        except RuntimeError:
            print_error("\nUnknown error occured.")
            sys.exit(1)

    os.chdir(root_path)

    print_succes('\nSuccessfully built pywowlib.')


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Build pywowlib."
                                                 "\nRequired dependencies are:"
                                                 "\n    All:"
                                                 "\n    * pip (https://pip.pypa.io/en/stable/installation/)"
                                                 "\n    * Cython (pip install Cython)"
                                                 "\n    * CMake (commandline CMake is required, see: https://cmake.org"
                                                 "\n    * C++ compiler (MSVC for Windows, GCC/Clang for Linux/Mac)"
                                                 "\n"
                                                 "\n    Linux:"
                                                 "\n    * Python headers (sudo apt install python3-dev)"
                                     , formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--debug', action='store_true', help='compile pywowlib in debug mode.=')
    parser.add_argument('--clean', action='store_true', help='erase previous build files and recompile from scratch')
    args = parser.parse_args()

    build_project(args.debug, args.clean)
