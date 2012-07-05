#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from tests.StampedTestUtils       import *
from api.Schemas            import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint

class OtherSearchTests(ASearchTestSuite):
    
    def test_basic(self):
        """ 
            Test basic searches for misc entities that don't fall into any of 
            the main category verticals.
        """
        
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'gears of war 3', }, [ 
                SearchResultConstraint(title='gears of war 3', types='video_game'), 
            ]), 
            ({ 'query' : 'super smash brothers', }, [ 
                SearchResultConstraint(title='super smash bros.', types='video_game'), 
                SearchResultConstraint(title='super smash bros melee', types='video_game'), 
            ]), 
            ({ 'query' : 'elder scrolls v: skyrim', }, [ 
                SearchResultConstraint(title='elder scrolls v: skyrim', types='video_game', 
                                       index=0), 
            ]), 
            ({ 'query' : 'skyrim', }, [ 
                SearchResultConstraint(title='elder scrolls v: skyrim', types='video_game'), 
            ]), 
            ({ 'query' : 'mass effect 3', }, [ 
                SearchResultConstraint(title='mass effect 3', types='video_game'), 
                SearchResultConstraint(title='mass effect 3', types='book'), 
            ]), 
            ({ 'query' : 'halo reach', }, [ 
                SearchResultConstraint(title='halo reach', types='video_game'), 
            ]), 
        ]
        
        self._run_tests(tests, args)

if __name__ == '__main__':
    StampedTestRunner().run()

