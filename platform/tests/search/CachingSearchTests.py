#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import inspect, time

from tests.StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint

from libs.Amazon            import Amazon
from libs.Factual           import Factual
from libs.GooglePlaces      import GooglePlaces
from libs.Rdio              import Rdio
from libs.Spotify           import Spotify
from libs.TMDB              import TMDB
from libs.TheTVDB           import TheTVDB

class CachingSearchTests(ASearchTestSuite):
    
    """
        Test suite to ensure that local and global caching are both working properly 
        for key caching priorities.
    """
    
    def __test_api_caching(self, api, cases):
        api_name = api.__class__.__name__
        delay = 0.5
        
        for case in cases:
            times = [ ]
            rets  = [ ]
            
            func = inspect.getsource(case).strip()
            utils.log("%s) testing %s" % (api_name, func))
            
            # invoke the same function 5 times in a row and expect:
            #    1) the same result each time
            #    2) the time taken to decrease after the first invocation due to caching
            for i in xrange(5):
                t0  = time.time()
                ret = case(api)
                t1  = time.time()
                
                d0  = (t1 - t0) * 1000.0
                
                times.append(d0)
                rets.append(ret)
                time.sleep(delay)
            
            t0   = times[0]
            ret0 = rets[0]
            
            utils.log("%s) %.2f vs [ %s ] (ms)" % 
                      (api_name, t0, ', '.join('%.2f' % s for s in times[1:])))
            
            # ensure that the same value is returned each iteration
            for ret1 in rets[1:]:
                if type(ret0) == type(ret1):
                    if repr(ret0) == repr(ret1):
                        continue
                
                raise Exception("%s(%s) inconsistent retvals (%s vs %s)" % 
                                (api_name, func, ret0, ret1))
            
            # ensure that subsequent calls return at least as fast as the first call
            # (the result of which should've been cached)
            for t1 in times[1:]:
                if t1 > t0 + (t0 * .10):
                    raise Exception("%s(%s) should've been cached (%.2f vs %.2f ms)" % 
                                    (api_name, func, t0, t1))
    
    def test_amazon(self):
        self.__test_api_caching(Amazon(),[
                lambda api: api.item_search(Keywords='gears of war 3', 
                                            ResponseGroup='ItemAttributes', 
                                            SearchIndex='All'), 
                lambda api: api.item_lookup(ItemId='1452101183', 
                                            ResponseGroup='AlternateVersions,Large'), 
        ])
    
    def test_factual(self):
        self.__test_api_caching(Factual(),[
            lambda api: api.search(query='tilth'), 
            lambda api: api.menu('5b1d03d6-3572-4d4f-8e1b-e1ed071e8e1c'), 
        ])
    
    def test_google_places(self):
        self.__test_api_caching(GooglePlaces(),[
            lambda api: api.getEntityAutocompleteResults(query='tilth'), 
            lambda api: api.getEntityAutocompleteResults(query='brook'), 
        ])
    
    def test_rdio(self):
        self.__test_api_caching(Rdio(),[
            lambda api: api.method('get', keys='t13593139'), 
            lambda api: api.method('get', keys='r92384'), 
            lambda api: api.method('getAlbumsForArtist', keys='r92384'), 
            lambda api: api.method('getTracksForArtist', keys='r92384'), 
        ])
    
    def test_spotify(self):
        self.__test_api_caching(Spotify(),[
            lambda api: api.lookup('spotify:artist:2AsusXITU8P25dlRNhcAbG'), 
            lambda api: api.lookup('spotify:artist:5pKCCKE2ajJHZ9KAiaK11H', 'albumdetail'), 
            lambda api: api.lookup('spotify:album:3GnlXbxysjS5whsCrTeoAG',  'trackdetail'), 
            lambda api: api.search('track',  q='orange rhyming dictionary'), 
            lambda api: api.search('album',  q='the reeling'), 
            lambda api: api.search('artist', q='passion pit'), 
        ])
    
    def test_tmdb(self):
        self.__test_api_caching(TMDB(),[
            lambda api: api.movie_search('the godfather'), 
            lambda api: api.movie_search('office space'), 
            lambda api: api.movie_info ('1542'), # office space
            lambda api: api.movie_casts('1542'), # office space
        ])
    
    def test_the_tvdb(self):
        self.__test_api_caching(TheTVDB(),[
            lambda api: api.search('friends', detailed=True), 
            lambda api: api.search('dark angel', transform=False, detailed=False), 
            lambda api: api.lookup('76148'), # dark angel
        ])

if __name__ == '__main__':
    StampedTestRunner().run()

