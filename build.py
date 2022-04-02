#!/usr/bin/env python
import subprocess
import sys

PYTHON_PATH = sys.executable


def build_project():

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

    print('\nBuilding pywowlib C++ extensions.')

    for module_relpath in extension_dirs:
        try:
            os.chdir(os.path.join(root_path, module_relpath))
            status = subprocess.call([PYTHON_PATH, "setup.py", 'build_clib', 'build_ext', '--inplace'])

            if status:
                print(f"\nProcess returned error code {status} while building module \"{module_relpath}\"")
                sys.exit(1)

        except PermissionError:
            print("\nThis build script may need to be called with admin (root) rights.")
            sys.exit(1)

        except RuntimeError:
            print("\nUnknown error occured.")
            sys.exit(1)


    os.chdir(root_path)


if __name__ == "__main__":
    build_project()
