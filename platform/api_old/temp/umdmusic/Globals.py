#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import os, sys

try:
    import stamped
except ImportError:
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    while os.path.basename(curr_dir) != 'platform':
        next_dir = os.path.dirname(curr_dir)
        if next_dir == curr_dir:
            # We blew it somehow.
            raise Exception('Unable to find platform directory to import!')
        curr_dir = next_dir
    sys.path.insert(0, next_dir)

import stamped
