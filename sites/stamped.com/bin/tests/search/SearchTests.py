#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils

from MongoStampedAPI import MongoStampedAPI
from StampedTestUtils import *
from pprint import pprint

class SearchTests(AStampedTestCase):
    def setUp(self):
        self.api = MongoStampedAPI()
        self.searcher = self.api._entitySearcher
    
    def tearDown(self):
        pass
    
    def test_lazy_amazon_search(self):
        searches = [
            dict(query='Freedom', 
                 category_filter='book'), 
            dict(query='Gears of War 3'), 
            dict(query='Phantogram'), 
            dict(query='Black Eyed Peas'), 
            dict(query='Moby Dick', 
                 subcategory_filter='book'), 
        ]
        
        for search in searches:
            search['full'] = True
            results0 = self.searcher.getSearchResults(**search)
            self.assertTrue(len(results0) > 0)
            
            results1 = self.searcher.getSearchResults(**search)
            self.assertTrue(len(results1) > 0)
            
            # ensure that searching the same term multiple times returns the same results
            self.assertEqual(len(results0), len(results1))
            for i in xrange(len(results0)):
                result0 = results0[i]
                result1 = results1[i]
                
                self.assertEqual(result0[0].title, result1[0].title)
                
                self.assertIn('amazon', result0[0])
                self.assertIn('amazon', result1[0])
    
    def test_lazy_google_search(self):
        coords = [ 40.797898, -73.968148 ]
        
        searches = [
            dict(query='Shake Shack', 
                 coords=coords, 
                 category_filter='food'), 
            dict(query='Starbucks', 
                 coords=coords), 
            dict(query='Holy Land Market', 
                 coords=coords, 
                 category_filter='food'), 
        ]
        
        for search in searches:
            search['full'] = True
            results0 = self.searcher.getSearchResults(**search)
            self.assertTrue(len(results0) > 0)
            
            results1 = self.searcher.getSearchResults(**search)
            self.assertTrue(len(results1) > 0)
            
            # ensure that searching the same term multiple times returns the same results
            self.assertEqual(len(results0), len(results1))
            for i in xrange(len(results0)):
                result0 = results0[i]
                result1 = results1[i]
                #pprint(result0[0].value)
                
                self.assertEqual(result0[0].title, result1[0].title)
                self.assertIn('googlePlaces', result0[0])
                self.assertIn('googlePlaces', result1[0])

if __name__ == '__main__':
    StampedTestRunner().run()

