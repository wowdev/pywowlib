# PYTHON CASC EXTENSION

**Python CASC extension** can be used to manage a local folder containing an installation of WoW and to read files from it.

## Compilation
#### GCC
`python setup.py build_ext --inplace`
#### MSVC
Modify `setup.py` and change `extra_compile_args=['-O3']` to `extra_compile_args=['/Ox']`

`python setup.py build_ext --inplace`

## API
```python
def class CascHandlerLocal:
    def __init__(self):
        ## compiled code

    # folder: Path to a wow install location containing a .build.info file
    #
    # throws: RuntimeError if something during initialization went wrong
    def initialize(self, folder):
        ## compiled code

    # file: if string -> check if file exists
    #       if int    -> check if file data id exists
    #
    # return: bool (true -> exists, false -> does not exist)
    # trhows: ValueError if the 'file' parameter is neither string nor int
    def exists(self, file):
        ## compiled code    

    # file: if string -> open file by file name
    #       if int    -> open file by file data id
    # 
    # return: bytearray with the file content
    # throws: RuntimeError if the file is not found
    #         ValueError if the 'file' parameter is neither string nor int
    def openFile(self, file):
        ## compiled code
```        

## Standalone Build
Use CMakeLists.txt
```bash
mkdir build
cd build
cmake ..
cmake --build .
```

Use file `build\libcython_casc.a`