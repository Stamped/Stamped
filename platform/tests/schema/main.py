#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from StampedTestUtils import *
import tests.schema

if __name__ == '__main__':
    StampedTestRunner(tests.schema).run()
