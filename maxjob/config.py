#!/usr/bin/env python
# :coding: utf-8

"""Read and hold the settings from the config file."""

import os
import sys

import yaml
from easydict import EasyDict


configfile = "maxjob.yml"


def get_this_directory(unpacked=False):
    """Support querying from inside an executable.

    unpacked: When frozen, use the unpacked temp directory instead of
        the one where the .exe distribution resides in. This is needed
        for bundles files vs files that must lie next to the .exe.

    """
    if getattr(sys, 'frozen', False):
        if unpacked:
            thisdir = os.path.abspath(sys._MEIPASS)
        else:
            thisdir = os.path.abspath(sys.executable)
    else:
        thisdir = os.path.dirname(os.path.abspath(__file__))
    return thisdir


def _expand_variables_in_paths(dct):
    """Modify dict recursively and expand the vars in all paths."""
    for key, value in dct.items():
        try:
            _expand_variables_in_paths(dct[key])
        except AttributeError:
            try:
                dct[key] = os.path.expandvars(value)
            except TypeError:
                pass


def get_settings():
    """Return settings as dot-access dictionary."""
    thisdir = get_this_directory()
    rootdir = os.path.dirname(thisdir)
    configfilepath = os.path.join(rootdir, configfile)
    with open(configfilepath) as f:
        content = f.read()
    settings = yaml.load(content)
    _expand_variables_in_paths(settings)
    return EasyDict(settings)


cfg = get_settings()


if __name__ == '__main__':
    from pprint import pprint
    pprint(cfg)
