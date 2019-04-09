from distutils.core import run_setup


def build_project():

    try:
        import Cython
    except ImportError:
        raise Exception("\nCython is required to build this project")

    try:
        from pip import main as pipmain
    except ImportError:
        try:
            from pip._internal import main as pipmain
        except ImportError:
            raise Exception("\npip is required to build this project")

    import os

    addon_root_path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)).replace('\\', '/'))

    extension_dirs = (
        "archives/casc/",
        "archives/mpq/native/",
        "blp/BLP2PNG/",
        "blp/PNG2BLP/"
    )

    print('\nBuilding pywowlib C++ extensions.')
    try:
        for module_relpath in extension_dirs:
            os.chdir(os.path.join(addon_root_path, module_relpath))
            run_setup('setup.py', script_args=['build_ext', '--inplace'])

    except PermissionError:
        raise PermissionError("\nThis build script may need to be called with admin (root) rights.")

    os.chdir(addon_root_path)


if __name__ == "__main__":
    build_project()

