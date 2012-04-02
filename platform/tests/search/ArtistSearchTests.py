#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint

class ArtistSearchTests(ASearchTestSuite):
    
    def test_basic(self):
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'nicki minaj', }, [ 
                SearchResultConstraint(title='nicki minaj', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'jay-z', }, [ 
                SearchResultConstraint(title='jay-z', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'jay z', }, [ 
                SearchResultConstraint(title='jay-z', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'passion pit', }, [ 
                SearchResultConstraint(title='passion pit', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'red hot chili peppers', }, [ 
                SearchResultConstraint(title='red hot chili peppers', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'the temper trap', }, [ 
                SearchResultConstraint(title='the temper trap', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'the glitch mob', }, [ 
                SearchResultConstraint(title='the glitch mob', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'kanye west', }, [ 
                SearchResultConstraint(title='kanye west', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'justin bieber', }, [ 
                SearchResultConstraint(title='justin bieber', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'carly rae jepsen', }, [ 
                SearchResultConstraint(title='carly rae jepsen', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'kelly clarkson', }, [ 
                SearchResultConstraint(title='kelly clarkson', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'carrie underwood', }, [ 
                SearchResultConstraint(title='carrie underwood', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'MGMT', }, [ 
                SearchResultConstraint(title='MGMT', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'rjd2', }, [ 
                SearchResultConstraint(title='rjd2', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'usher', }, [ 
                SearchResultConstraint(title='usher', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'B.o.B', }, [ 
                SearchResultConstraint(title='B.o.B', 
                                       types='artist', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : '50 cent', }, [ 
                SearchResultConstraint(title='50 cent', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'katy perry', }, [ 
                SearchResultConstraint(title='katy perry', 
                                       types='artist', 
                                       index=0), 
            ]), 
            # TODO: get this query working
            #({ 'query' : 'mozart', }, [ 
            #    SearchResultConstraint(title='mozart', 
            #                           types='artist', 
            #                           index=0), 
            #]), 
        ]
        
        self._run_tests(tests, args)

if __name__ == '__main__':
    StampedTestRunner().run()

