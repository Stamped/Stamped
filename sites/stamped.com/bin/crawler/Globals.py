#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

while True:
    try:
        import init
        break
    except ImportError:
        sys.path.insert(0, os.path.dirname(sys.path[0]))

#__builtins__['options'] = { }
from utils import AttributeDict
options = AttributeDict()

