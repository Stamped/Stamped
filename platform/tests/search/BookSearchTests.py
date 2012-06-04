#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
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
            ({ 'query' : 'freedom', 'category' : 'book', }, [ 
                SearchResultConstraint(title='freedom', types='book'), 
            ]), 
            ({ 'query' : 'freedom jonathon franzen', 'category' : 'book', }, [ 
                SearchResultConstraint(title='freedom', types='book'), 
            ]), 
            #({ 'query' : 'freedom by jonathon franzen', 'category' : 'book', }, [ # TODO: handle 'X by Y'
            #    SearchResultConstraint(title='freedom', types='book'), 
            #]), 
            ({ 'query' : 'of mice and men', 'category' : 'book', }, [ 
                SearchResultConstraint(title='of mice and men', types='book'), 
            ]), 
            ({ 'query' : '1Q84', 'category' : 'book', }, [ 
                SearchResultConstraint(title='1Q84', types='book'), 
            ]), 
            ({ 'query' : '1Q84 book', 'category' : 'book', }, [ 
                SearchResultConstraint(title='1Q84', types='book'), 
            ]), 
            ({ 'query' : 'steve jobs biography', 'category' : 'book', }, [ 
                SearchResultConstraint(title='steve jobs', types='book', match='prefix'), 
            ]), 
            ({ 'query' : 'embassytown china', 'category' : 'book', }, [ 
                SearchResultConstraint(title='embassytown', types='book', index=0), 
            ]), 
            ({ 'query' : 'baking made easy', 'category' : 'book', }, [ 
                SearchResultConstraint(title='baking made easy', types='book', match='prefix'), 
            ]), 
            ({ 'query' : 'bossypants', 'category' : 'book', }, [ 
                SearchResultConstraint(title='bossypants', types='book', index=0), 
            ]), 
            ({ 'query' : 'the immortal life of henrietta lacks', 'category' : 'book', }, [ 
                SearchResultConstraint(title='the immortal life of henrietta lacks', types='book', index=0), 
            ]), 
            ({ 'query' : 'the girl who kicked the hornet\'s nest', 'category' : 'book', }, [ 
                SearchResultConstraint(title='the girl who kicked the hornet\'s nest', types='book'), 
            ]), 
            ({ 'query' : 'the boy who harnessed the wind', 'category' : 'book', }, [ 
                SearchResultConstraint(title='the boy who harnessed the wind', types='book'), 
            ]), 
            ({ 'query' : 'the girl who played with fire', 'category' : 'book', }, [ 
                SearchResultConstraint(title='the girl who played with fire', types='book'), 
            ]), 
            ({ 'query' : 'the help', 'category' : 'book', }, [ 
                SearchResultConstraint(title='the help', types='book'), 
            ]), 
            ({ 'query' : 'the fault in our stars', 'category' : 'book', }, [ 
                SearchResultConstraint(title='the fault in our stars', types='book'), 
            ]), 
            ({ 'query' : 'lord of the flies', 'category' : 'book', }, [ 
                SearchResultConstraint(title='lord of the flies', types='book'), 
            ]), 
            ({ 'query' : 'amrar', 'category' : 'book', }, [ 
                SearchResultConstraint(title='amrar va lukhar', types='book'), 
            ]), 
            ({ 'query' : 'freakonomics', 'category' : 'book', }, [ 
                SearchResultConstraint(title='freakonomics', types='book', match='prefix'), 
            ]), 
        ]
        
        self._run_tests(tests, args)

if __name__ == '__main__':
    StampedTestRunner().run()

