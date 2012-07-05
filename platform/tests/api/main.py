#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from tests.StampedTestUtils import StampedTestRunner
import tests.api

if __name__ == '__main__':
    StampedTestRunner(tests.api).run()

