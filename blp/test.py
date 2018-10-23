import os
from itertools import chain
from glob import glob
from BLP2PNG import BlpConverter
import time

base_folder = "some folder"


def convert_file(cur_file):
    in_file = open(cur_file, 'rb')
    data = in_file.read()
    in_file.close()
    rel_path = os.path.relpath(cur_file, base_folder).replace('\\', '/')
    return data, rel_path


def main():
    result = (chain.from_iterable(glob(os.path.join(x[0], '*.blp')) for x in os.walk(base_folder)))
    pairs = (convert_file(f) for f in result)
    pairs = list(pairs)

    print "Handling %i files" % len(pairs)
    now = time.time()
    BlpConverter().convert(pairs, ".\\output")
    end = time.time()
    print (end - now)


if __name__ == '__main__':
    main()