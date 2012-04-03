#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
from api.Schemas            import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint

class BookSearchTests(ASearchTestSuite):
    
    def test_basic(self):
        """ Test basic book searches """
        
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'freedom', }, [ 
                SearchResultConstraint(title='freedom', types='book'), 
            ]), 
            ({ 'query' : 'freedom jonathon franzen', }, [ 
                SearchResultConstraint(title='freedom', types='book'), 
            ]), 
            #({ 'query' : 'freedom by jonathon franzen', }, [ # TODO: handle 'X by Y'
            #    SearchResultConstraint(title='freedom', types='book'), 
            #]), 
            ({ 'query' : 'of mice and men', }, [ 
                SearchResultConstraint(title='of mice and men', types='book'), 
            ]), 
            ({ 'query' : '1Q84', }, [ 
                SearchResultConstraint(title='1Q84', types='book'), 
            ]), 
            ({ 'query' : '1Q84 book', }, [ 
                SearchResultConstraint(title='1Q84', types='book'), 
            ]), 
            ({ 'query' : 'steve jobs biography', }, [ 
                SearchResultConstraint(title='steve jobs', types='book', match='prefix'), 
            ]), 
            ({ 'query' : 'embassytown china', }, [ 
                SearchResultConstraint(title='embassytown', types='book', index=0), 
            ]), 
            ({ 'query' : 'baking made easy', }, [ 
                SearchResultConstraint(title='baking made easy', types='book', match='prefix'), 
            ]), 
            ({ 'query' : 'bossypants', }, [ 
                SearchResultConstraint(title='bossypants', types='book', index=0), 
            ]), 
            ({ 'query' : 'the immortal life of henrietta lacks', }, [ 
                SearchResultConstraint(title='the immortal life of henrietta lacks', types='book', index=0), 
            ]), 
            ({ 'query' : 'the girl who kicked the hornet\'s nest', }, [ 
                SearchResultConstraint(title='the girl who kicked the hornet\'s nest', types='book'), 
                SearchResultConstraint(title='the girl who kicked the hornet\'s nest', types='movie'), 
            ]), 
            ({ 'query' : 'the boy who harnessed the wind', }, [ 
                SearchResultConstraint(title='the boy who harnessed the wind', types='book'), 
            ]), 
            ({ 'query' : 'the girl who played with fire', }, [ 
                SearchResultConstraint(title='the girl who played with fire', types='book'), 
                SearchResultConstraint(title='the girl who played with fire', types='movie'), 
            ]), 
            ({ 'query' : 'the help', }, [ 
                SearchResultConstraint(title='the help', types='book'), 
                SearchResultConstraint(title='the help', types='movie'), 
            ]), 
            ({ 'query' : 'the fault in our stars', }, [ 
                SearchResultConstraint(title='the fault in our stars', types='book'), 
            ]), 
        ]
        
        self._run_tests(tests, args)

if __name__ == '__main__':
    StampedTestRunner().run()

