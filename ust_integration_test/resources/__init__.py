
from os.path import dirname, realpath, join
import os
import sys

def get_resource_dir():
    if getattr(sys, 'frozen', False):
        return join(sys._MEIPASS, dirname(__file__).split(os.sep)[-1])
    else:
        return dirname(realpath(__file__))

this_dir = get_resource_dir()

def get_resource(name):
    path = join(this_dir, name)
    if not os.path.exists(path):
        raise FileNotFoundError("Error: " + path + " does not exist")
    return path

def get_ust_exe():
    binary = "user-sync.exe" if 'win' in sys.platform.lower() else "user-sync"
    return join(this_dir, binary)
