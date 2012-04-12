#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from Schemas                import *
from StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite
from SuggestedEntities      import SuggestedEntities
from pprint                 import pformat

class SuggestedSearchTests(ASearchTestSuite):
    
    def test_basic(self):
        """ Test basic suggested entity searches """
        
        suggestedEntities = SuggestedEntities()
        
        tests = [
            {
                'category'  : 'place', 
                'coords'    : (40.144729, -74.053527), # NYC
            }, 
            {
                'category'  : 'food', 
                'coords'    : (37.7622, -122.42), # SF
            }, 
            { 'category'    : 'music', }, 
            { 'category'    : 'book', }, 
            { 'subcategory' : 'tv', }, 
            { 'subcategory' : 'movie', }, 
            { 'subcategory' : 'app', }, 
        ]
        
        for test in tests:
            suggested = suggestedEntities.getSuggestedEntities(**test)
            utils.log()
            utils.log("-" * 80)
            utils.log("%s\n%s" % (test, pformat(suggested)))
            utils.log("-" * 80)
            utils.log()
            self.assertTrue(len(suggested) > 0)
            
            seen = set()
            
            for section in suggested:
                title, entities = section
                
                self.assertIsInstance(title, basestring)
                self.assertTrue(len(title) > 0)
                self.assertTrue(len(entities) > 0)
                
                for entity in entities:
                    self.assertIsInstance(entity, BasicEntity)

if __name__ == '__main__':
    StampedTestRunner().run()

