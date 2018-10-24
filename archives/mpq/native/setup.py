#!/usr/bin/env python
import platform
import subprocess
import os
from setuptools import Extension, setup


if platform.system() != 'Darwin':
    extra_compile_args = ['-O3'] 
    extra_link_args = []
else:
    extra_compile_args = ['-O3', '-mmacosx-version-min=10.9']
    extra_link_args = ['-mmacosx-version-min=10.9']


module = Extension(
	"storm",
	sources=["stormmodule.cc"],
	language="c++",
	libraries=["storm"],
	include_dirs=["stormlib/src/"],
	library_dirs=["stormlib/"],
	extra_compile_args=extra_compile_args,
	extra_link_args=extra_link_args
)

setup(ext_modules=[module])

# fix dylib loading path
if platform.system() == 'Darwin':
	for filepath in os.listdir(os.path.abspath(os.path.dirname(__file__))):
		if 'darwin' in filepath and 'storm' in filepath:
			subprocess.call(['install_name_tool', '-change', 'libStorm.dylib', '@loader_path/libStorm.dylib', filepath])
			break