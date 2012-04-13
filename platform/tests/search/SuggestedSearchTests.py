#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from Schemas                            import *
from StampedTestUtils                   import *
from ASearchTestSuite                   import ASearchTestSuite
from db.mongodb.MongoSuggestedEntities  import MongoSuggestedEntities
from pprint                             import pformat

# TODO: ensure unique results

class SuggestedSearchTests(ASearchTestSuite):
    
    def _test_suggestions(self, **kwargs):
        """ Test basic suggested entity searches """
        
        suggestedEntities = MongoSuggestedEntities()
        suggested = suggestedEntities.getSuggestedEntities(**kwargs)
        
        utils.log()
        utils.log("-" * 80)
        utils.log("TEST %s" % pformat(kwargs))
        
        for section in suggested:
            utils.log()
            utils.log("SECTION %s:" % section[0])
            
            for i in xrange(len(section[1])):
                entity = section[1][i]
                types  = list(entity.types)[0] if len(entity.types) == 1 else entity.types
                
                utils.log("   %d) %s (%s)" % (i + 1, entity.title, types))
        
        utils.log("-" * 80)
        utils.log()
        self.assertTrue(len(suggested) > 0)
        
        count = 0
        seen  = set()
        
        for section in suggested:
            title, entities = section
            
            self.assertIsInstance(title, basestring)
            self.assertTrue(len(title) > 0)
            self.assertTrue(len(entities) > 0)
            count += len(entities)
            
            for entity in entities:
                self.assertIsInstance(entity, BasicEntity)
        
        # if we set a limit on the number of results returned, ensure that 
        # that limit was satisfied.
        limit = kwargs.get('limit', None)
        if limit is not None:
            self.assertTrue(count <= limit)
    
    def test_place(self):
        self._test_suggestions(category='place', coords=(40.144729, -74.053527)) # NYC
    
    def test_food(self):
        self._test_suggestions(category='food', coords=(37.7622, -122.42)) # SF
    
    def test_music(self):
        self._test_suggestions(category='music')
    
    def test_book(self):
        self._test_suggestions(category='book')
    
    def test_tv(self):
        self._test_suggestions(subcategory='tv')
    
    def test_movie(self):
        self._test_suggestions(subcategory='movie')
    
    def test_app(self):
        self._test_suggestions(subcategory='app')
        self._test_suggestions(subcategory='app', limit=10)

if __name__ == '__main__':
    StampedTestRunner().run()

