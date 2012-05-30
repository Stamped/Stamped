#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import Entity

from Schemas                            import *
from StampedTestUtils                   import *
from ASearchTestSuite                   import ASearchTestSuite
from db.mongodb.MongoSuggestedEntities  import MongoSuggestedEntities
from pprint                             import pformat
from collections                        import defaultdict

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
            utils.log("SECTION %s:" % section['name'])
            
            for i in xrange(len(section['entities'])):
                entity = section['entities'][i]
                types  = list(entity.types)[0] if len(entity.types) == 1 else entity.types
                
                utils.log("   %d) %s (%s) (id=%s)" % (i + 1, entity.title, types, entity.search_id))
        
        utils.log("-" * 80)
        utils.log()
        self.assertTrue(len(suggested) > 0)
        
        count = 0
        seen  = defaultdict(set)
        
        for section in suggested:
            title = section['name']
            entities = section['entities']
            
            # ensure the entities and title are valid for this section
            self.assertIsInstance(title, basestring)
            self.assertTrue(len(title) > 0)
            self.assertTrue(len(entities) > 0)
            count += len(entities)
            
            for entity in entities:
                self.assertIsInstance(entity, BasicEntity)
                self.assertTrue(entity.search_id is not None)
                self.assertTrue(len(entity.search_id) > 0)
                self.assertTrue(entity.title is not None)
                self.assertTrue(len(entity.title) > 0)
            
            # ensure the sections contain no obvious duplicates
            entities2 = Entity.fast_id_dedupe(entities, seen)
            self.assertEqual(len(entities), len(entities2))
        
        # if we set a limit on the number of results returned, ensure that 
        # that limit was satisfied.
        limit = kwargs.get('limit', None)
        if limit is not None:
            self.assertTrue(count <= limit)
    
    def test_place(self):
        self._test_suggestions(category='place', coords=(40.7360067, -73.98884296)) # NYC
    
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

