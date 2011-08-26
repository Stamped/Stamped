#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils
from Schemas import *
from ASchemaTestCase import *

class EntityTest(ASchemaTestCase):
    
    def test_basic(self):
        entity = Entity()
        entity.title = "test"
        entity.subcategory = "restaurant"
        entity.validate()
    
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
        
        entity.desc = "&lt;example summary&gt;"
        self.assertEqual(entity.desc, "<example summary>")

if __name__ == '__main__':
    StampedTestRunner().run()

