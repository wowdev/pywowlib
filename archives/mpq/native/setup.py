#!/usr/bin/env python
import platform
import argparse
import subprocess
import sys
import os
from setuptools import Extension, setup
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent.absolute()))

from cmake import check_for_cmake, CMAKE_EXE

CUR_DIR = os.path.abspath(os.path.dirname(__file__))


def print_error(*s: str):
    print("\033[91m {}\033[00m".format(' '.join(s)))


def print_succes(*s: str):
    print("\033[92m {}\033[00m".format(' '.join(s)))


def print_info(*s: str):
    print("\033[93m {}\033[00m".format(' '.join(s)))


def main(debug: bool):
    print_info('\nBuilding MPQ extension...')
    print(f'Target mode: {"Debug" if debug else "Release"}')
    # build CASCLib
    check_for_cmake()

    build_dir = os.path.join(CUR_DIR, 'StormLib', 'build')

    os.makedirs(build_dir, exist_ok=True)
    os.chdir(build_dir)

    cmake_defines = ['-DCMAKE_BUILD_TYPE=Debug' if debug else '-DCMAKE_BUILD_TYPE=Release'
        , '-DBUILD_SHARED_LIBS=OFF']

    if sys.platform != 'win32':
        cmake_defines.extend(['-DCMAKE_CXX_FLAGS=-fPIC', '-DCMAKE_C_FLAGS=-fPIC'])

    status = subprocess.call([CMAKE_EXE, '..', *cmake_defines])

    if status:
        print_error(f'\nError building StormLib. See CMake error above.')
        sys.exit(1)

    status = subprocess.check_call([CMAKE_EXE, '--build', '.', '--config', 'Debug' if debug else 'Release'])

    if status:
        print_error(f'\nError building StormLib. See build error above.')
        sys.exit(1)

    status = subprocess.call([CMAKE_EXE, '--install', '.', '--prefix', CUR_DIR])

    if status:
        print_error(f'\nError building StormLib. Error setting install configuration.')
        sys.exit(1)

    os.chdir(CUR_DIR)

    static_libraries = ['StormLib'] if sys.platform == 'win32' else ['storm']
    static_lib_dir = 'lib'
    libraries = []
    library_dirs = []
    extra_objects = []
    define_macros = []

    if sys.platform == 'win32':
        libraries.extend(static_libraries)
        libraries.append('user32')
        library_dirs.append(static_lib_dir)
        extra_objects = []
        define_macros.append(('STORMLIB_NO_AUTO_LINK', None))
    else:  # POSIX
        extra_objects = ['{}/lib{}.a'.format(static_lib_dir, l) for l in static_libraries]
        libraries.append("bz2")

    # compiler and linker settings
    if platform.system() == 'Darwin':
        if debug:
            extra_compile_args = ['-g3', '-O0', '-stdlib=libc++']
            extra_link_args = ['-stdlib=libc++']
        else:
            extra_compile_args = ['-O3', '-stdlib=libc++']
            extra_link_args = ['-stdlib=libc++']

    elif platform.system() == 'Windows':
        if debug:
            extra_compile_args = ['/std:c++17', '/Zi']
            extra_link_args = ['/DEBUG:FULL']
        else:
            extra_compile_args = ['/std:c++17']
            extra_link_args = []
    else:
        if debug:
            extra_compile_args = ['-std=c++17', '-O0', '-g']
            extra_link_args = []
        else:
            extra_compile_args = ['-std=c++17', '-O3']
            extra_link_args = []

    module = Extension(
        "storm",
        sources=["stormmodule.cc"],
        language="c++",
        libraries=libraries,
        include_dirs=["include"],
        library_dirs=library_dirs,
        extra_objects=extra_objects,
        define_macros=define_macros,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args
    )

    setup(ext_modules=[module])

    print_succes('\nSuccessfully built MPQ extension.')


'''
# fix dylib loading path
if platform.system() == 'Darwin':
    for filepath in os.listdir(os.path.abspath(os.path.dirname(__file__))):
        if 'darwin' in filepath and 'storm' in filepath:
            subprocess.call(['install_name_tool', '-change', 'libStorm.dylib', '@loader_path/libStorm.dylib', filepath])
            break
'''

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--wbs_debug', action='store_true', help='Compile CASC extension in debug mode.')
    args, unknown = parser.parse_known_args()

    if args.wbs_debug:
        sys.argv.remove('--wbs_debug')

    main(args.wbs_debug)
