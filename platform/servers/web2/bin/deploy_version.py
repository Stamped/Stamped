#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, utils

PROJ_ROOT     = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
__version__   = utils.shell("cd %s && make version" % PROJ_ROOT)[0]

def get_current_version():
    return __version__

def parse_current_version():
    version = get_current_version().split(".")
    
    version[-1] = str(int(version[-1]) + 1)
    
    return ".".join(version)

def update_version():
    version = parse_current_version()
    utils.shell(r"sed %s 's/^\(ASSET_VERSION_NUMBER *= *\).*$/\1%s/' %s" % ("-i ''", version, "../Makefile"))
    
    print version

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    args = parser.parse_args()
    
    update_version()

