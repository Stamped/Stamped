#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import os, sys

base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, base)

sys.path.append(os.path.join(base, "api"))

import init

#__builtins__['options'] = { }
from utils import AttributeDict
options = AttributeDict()

