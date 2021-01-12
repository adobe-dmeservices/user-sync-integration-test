import os
from os.path import dirname, realpath, join

this_dir = dirname(realpath(__file__))


def get_resource(name):
    path = join(this_dir, name)
    if not os.path.exists(path):
        raise FileNotFoundError("Error: " + path + " does not exist")
    return path
