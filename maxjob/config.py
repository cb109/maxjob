#!/usr/bin/env python
# :coding: utf-8

"""Read and hold the settings from the config file."""

import os
import sys

import yaml
from easydict import EasyDict


configfile = "maxjob.yml"


def get_this_directory():
    """Support querying from inside an executable."""
    if getattr(sys, 'frozen', False):
        thisdir = os.path.dirname(sys.executable)
    else:
        thisdir = os.path.dirname(__file__)
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
