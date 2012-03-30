#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint

class MovieSearchTests(ASearchTestSuite):
    
    def test_basic_movies(self):
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'teenage mutant ninja turtles', }, [ 
                SearchResultConstraint(title='teenage mutant ninja turtles', 
                                       types='movie', 
                                       index=0), 
            ]), 
            ({ 'query' : 'the godfather', }, [ 
                SearchResultConstraint(title='the godfather', 
                                       types='movie', 
                                       index=0), 
            ]), 
            ({ 'query' : 'godfather', }, [ 
                SearchResultConstraint(title='the godfather', 
                                       types='movie'), 
            ]), 
            ({ 'query' : 'the hunger games', }, [ 
                SearchResultConstraint(title='the the hunger games', 
                                       types='movie', 
                                       index=0), 
            ]), 
            ({ 'query' : 'hunger games', }, [ 
                SearchResultConstraint(title='the the hunger games', 
                                       types='movie'), 
            ]), 
        ]
        
        self._run_tests(tests, args)

if __name__ == '__main__':
    StampedTestRunner().run()

