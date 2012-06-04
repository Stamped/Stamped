#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint
from libs.applerss          import AppleRSS

class AppSearchTests(ASearchTestSuite):
    
    def test_basic(self):
        """ Test basic app searches """
        
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'Stamped', 'category': 'app', }, [ 
                SearchResultConstraint(title='stamped', types='app', 
                                       index=0, itunes_id=467924760), 
            ]), 
            ({ 'query' : 'Instagram', 'category': 'app', }, [ 
                SearchResultConstraint(title='Instagram', types='app', 
                                       index=0, itunes_id=389801252), 
            ]), 
            ({ 'query' : 'doodle jump', 'category': 'app', }, [ 
                SearchResultConstraint(title='doodle jump', types='app', 
                                       index=0, itunes_id=307727765), 
            ]), 
            ({ 'query' : 'tiny wings', 'category': 'app', }, [ 
                SearchResultConstraint(title='tiny wings', types='app', 
                                       itunes_id=417817520), 
            ]), 
            ({ 'query' : 'flipboard', 'category': 'app', }, [ 
                SearchResultConstraint(title='flipboard', types='app', 
                                       index=0, itunes_id=358801284, match='prefix'), 
            ]), 
            ({ 'query' : 'facebook app', 'category': 'app', }, [ 
                SearchResultConstraint(title='facebook', types='app', 
                                       index=0, itunes_id=284882215), 
            ]), 
            ({ 'query' : 'facebook','category': 'app',  }, [ 
                SearchResultConstraint(title='facebook', types='app', 
                                       index=0, itunes_id=284882215), 
            ]), 
            ({ 'query' : 'temple run', 'category': 'app', }, [ 
                SearchResultConstraint(title='temple run', types='app', 
                                       index=0, itunes_id=420009108), 
            ]), 
            ({ 'query' : 'pandora radio', 'category': 'app', }, [ 
                SearchResultConstraint(title='pandora radio', types='app', 
                                       index=0, itunes_id=284035177), 
            ]), 
        ]
        
        self._run_tests(tests, args)
    
    def test_top_free_apps(self):
        """ Test the top free apps from iTunes """
        
        rss  = AppleRSS()
        apps = rss.get_top_free_apps(limit=10)
        
        self.__test_apps(apps)
    
    def test_top_paid_apps(self):
        """ Test the top paid apps from iTunes """
        
        rss  = AppleRSS()
        apps = rss.get_top_paid_apps(limit=10)
        
        self.__test_apps(apps)
    
    def test_top_grosssing_apps(self):
        """ Test the top grossing apps from iTunes """
        
        rss  = AppleRSS()
        apps = rss.get_top_grossing_apps(limit=10)
        
        self.__test_apps(apps)
    
    def __test_apps(self, apps):
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = []
        
        for app in apps:
            name  = app.title.lower().strip()
            name2 = utils.normalize(name, strict=True)
            
            if name.lower() != name2:
                # don't test apps whose names contain weird unicode strings
                continue
            
            tests.append(({ 'query' : name, 'category': 'app', }, [ 
                SearchResultConstraint(title=name, types='app'), 
            ]))
        
        self._run_tests(tests, args)

if __name__ == '__main__':
    StampedTestRunner().run()

