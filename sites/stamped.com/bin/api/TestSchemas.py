#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, sys, unittest

from datetime import datetime
from Schemas import *

class ASchemaTestCase(unittest.TestCase):
    
    ### DEFAULT ASSERTIONS
    def assertIsInstance(self, a, b):
        self.assertTrue(isinstance(a, b))
        
    def assertIn(self, a, b):
        self.assertTrue(a in b)

    def assertLength(self, a, size):
        self.assertEqual(len(a), size)

class EntityTest(ASchemaTestCase):
    
    def test_basic(self):
        entity = Entity()
        entity.title = "test"
        entity.subcategory = "restaurant"
        entity.desc = "&lt;example summary&gt;"
        entity.validate()
        
        self.assertEqual(entity.desc, "<example summary>")
    
    def test_normalization(self):
        strs = [
            '&lt;test', 
            '&quot;test&reg;', 
            '&#8216;test&#8217;s', 
        ]
        
        entity = Entity()
        for s in strs:
            entity.title = s
            self.assertEqual(entity.title, utils.normalize(s))
            self.assertTrue('&' not in entity.title)
            self.assertTrue(';' not in entity.title)
        
        #entity.title = 'test&#8217;s'
        entity.title = 'test&rsquo;s'
        self.assertEqual(entity.title, "test's")

if __name__ == '__main__':
    unittest.main()

