import logging
import logging.config
import os
import platform
import sys
from collections import Mapping
from copy import deepcopy


def get_test_name():
    return sys._getframe(1).f_code.co_name


def is_windows():
    return platform.system().lower() == "windows"


def normalize_text(text):
    try:
        text = text.decode()
    except:
        pass
    return str(text).strip().lower()


def init_logger(level=logging.DEBUG):
    results_dir = "results"
    log_file = os.path.join(results_dir, 'test.log')
    test_out_file = os.path.join(results_dir, 'test_output.log')

    cfg = {
        "version": 1.0,
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
            },
            "file": {
                "class": "logging.FileHandler",
                "mode": "w",
                "filename": log_file
            },
            "test_output": {
                "class": "logging.FileHandler",
                "mode": "w",
                "filename": test_out_file
            }
        },
        "loggers": {
            "": {
                "level": level,
                "handlers": ["console", "file"],
            },
            "test": {
                'level': level,
                'handlers': ['console', 'test_output'],
                'propagate': False
            }
        }
    }

    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    logging.config.dictConfig(cfg)


def merge_dict(d1, d2, immutable=False):
    """
    # Combine dictionaries recursively
    # preserving the originals
    # assumes d1 and d2 dictionaries!!
    :param d1: original dictionary
    :param d2: update dictionary
    :return:
    """

    d1 = {} if d1 is None else d1
    d2 = {} if d2 is None else d2
    d1 = deepcopy(d1) if immutable else d1

    for k in d2:
        # if d1 and d2 have dict for k, then recurse
        # else assign the new value to d1[k]
        if (k in d1 and isinstance(d1[k], Mapping)
                and isinstance(d2[k], Mapping)):
            merge_dict(d1[k], d2[k])
        else:
            d1[k] = d2[k]
    return d1
