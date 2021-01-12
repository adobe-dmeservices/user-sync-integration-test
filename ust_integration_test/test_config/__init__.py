import os
from os.path import dirname, realpath, join

from ust_integration_test.resources import get_resource

this_dir = dirname(realpath(__file__))


def get_test_dir(name):
    if name.startswith("setup."):
        path = get_resource(join('test_setup', name.lstrip("setup.")))
    else:
        path = join(this_dir, name)
    if not os.path.exists(path):
        raise FileNotFoundError("Error: " + path + " does not exist")
    return path
