#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
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
        
        # TODO: what is type for video game?
        # TODO: add misc product support to amazon source
        tests = [
            ({ 'query' : 'gears of war 3', }, [ 
                SearchResultConstraint(title='gears of war 3', types='other'), 
            ]), 
        ]
        
        self._run_tests(tests, args)

if __name__ == '__main__':
    StampedTestRunner().run()

