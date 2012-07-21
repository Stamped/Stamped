#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from utils import is_ec2
from distutils.core import setup, Extension

debug_macro = [] if is_ec2() else [('NDEBUG', '1')]
fast_compare_module = Extension('fastcompare', define_macros=debug_macro, sources=['platform/resolve/fastcompare.c'])

setup(name="FastCompare", ext_modules=[fast_compare_module])
