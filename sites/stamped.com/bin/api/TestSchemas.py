#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, os, sys, unittest

from datetime import datetime
from Schemas import *

class ASchemaTestCase(unittest.TestCase):
    pass

    ### DEFAULT ASSERTIONS
    def assertIsInstance(self, a, b):
        self.assertTrue(isinstance(a, b))
        
    def assertIn(self, a, b):
        self.assertTrue((a in b) == True)

    def assertLength(self, a, size):
        self.assertTrue(len(a) == size)

class EntityTest(ASchemaTestCase):
    
    def test_basic(self):
        entity = Entity()
        entity.title = "test"
        entity.subcategory = "restaurant"
        entity.desc = "&lt;example summary&gt;"
        
        self.assertTrue(entity.validate())

if __name__ == '__main__':
    unittest.main()

