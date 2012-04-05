#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint

class TVSearchTests(ASearchTestSuite):
    
    def test_basic(self):
        """ Test basic tv searches """
        
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'game of thrones', }, [ 
                SearchResultConstraint(title='game of thrones', types='tv'), 
            ]), 
            ({ 'query' : 'dexter', }, [ 
                SearchResultConstraint(title='dexter', types='tv'), 
            ]), 
            ({ 'query' : 'family guy', }, [ 
                SearchResultConstraint(title='family guy', types='tv'), 
            ]), 
            ({ 'query' : 'american idol', }, [ 
                SearchResultConstraint(title='american idol', types='tv'), 
            ]), 
            ({ 'query' : 'spongebob squarepants', }, [ 
                SearchResultConstraint(title='spongebob squarepants', types='tv'), 
            ]), 
            ({ 'query' : 'spongebob', }, [ 
                SearchResultConstraint(title='spongebob squarepants', types='tv'), 
            ]), 
            ({ 'query' : 'trailer park boys', }, [ 
                SearchResultConstraint(title='trailer park boys', types='tv'), 
                SearchResultConstraint(title='trailer park boys', types='movie'), 
            ]), 
            ({ 'query' : 'new girl', }, [ 
                SearchResultConstraint(title='new girl', types='tv'), 
            ]), 
            ({ 'query' : 'up all night', }, [ 
                SearchResultConstraint(title='up all night', types='tv'), 
            ]), 
            ({ 'query' : 'breaking bad', }, [ 
                SearchResultConstraint(title='breaking bad', types='tv'), 
            ]), 
            ({ 'query' : 'LOST', }, [ 
                SearchResultConstraint(title='LOST', types='tv'), 
            ]), 
            ({ 'query' : 'the sopranos', }, [ 
                SearchResultConstraint(title='the sopranos', types='tv'), 
            ]), 
            ({ 'query' : 'the simpsons', }, [ 
                SearchResultConstraint(title='the simpsons', types='tv'), 
            ]), 
            ({ 'query' : 'south park', }, [ 
                SearchResultConstraint(title='south park', types='tv'), 
            ]), 
            ({ 'query' : 'saturday night live', }, [ 
                SearchResultConstraint(title='saturday night live', types='tv'), 
            ]), 
            ({ 'query' : 'dark angel', }, [ 
                SearchResultConstraint(title='dark angel', types='tv'), 
            ]), 
            ({ 'query' : 'misfits', }, [ 
                SearchResultConstraint(title='misfits', types='tv'), 
            ]), 
            ({ 'query' : 'arrested development', }, [ 
                SearchResultConstraint(title='arrested development', types='tv'), 
            ]), 
            ({ 'query' : 'big bang theory', }, [
                SearchResultConstraint(title='the big bang theory', types='tv'), 
            ]), 
            ({ 'query' : 'how i met your mother', }, [
                SearchResultConstraint(title='how i met your mother', types='tv'), 
            ]), 
            ({ 'query' : 'it\'s always sunny in philadelphia', }, [
                SearchResultConstraint(title='it\'s always sunny in philadelphia', types='tv'), 
            ]), 
            ({ 'query' : 'the walking dead', }, [
                SearchResultConstraint(title='the walking dead', types='tv'), 
                SearchResultConstraint(title='the walking dead', types='movie'), 
            ]), 
            ({ 'query' : 'friends', }, [
                SearchResultConstraint(title='friends', types='tv'), 
            ]), 
            ({ 'query' : 'firefly', }, [
                SearchResultConstraint(title='firefly', types='tv'), 
                SearchResultConstraint(title='serenity', types='movie'), 
            ]), 
            ({ 'query' : 'futurama', }, [
                SearchResultConstraint(title='futurama', types='tv'), 
            ]), 
            ({ 'query' : '90210', }, [
                SearchResultConstraint(title='90210', types='tv'), 
            ]), 
        ]
        
        self._run_tests(tests, args)
    
    def test_international(self):
        """ Test international tv searches """
        
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'footballer\'s wives', }, [    # popular U.K. TV show (2002)
                SearchResultConstraint(title='footballer\'s wives', types='tv'), 
            ]), 
            ({ 'query' : 'hotel babylon', }, [          # popular U.K. TV show (2006)
                SearchResultConstraint(title='hotel babylon', types='tv'), 
            ]), 
            ({ 'query' : 'jeeves and wooster', }, [     # popular U.K. TV show (1990)
                SearchResultConstraint(title='jeeves and wooster', types='tv'), 
            ]), 
            ({ 'query' : 'coupling', }, [               # popular U.K. TV show (2000-2004)
                SearchResultConstraint(title='coupling', types='tv'), 
            ]), 
            
            # TODO: add more popular foreign shows with exotic names
        ]
        
        self._run_tests(tests, args)

if __name__ == '__main__':
    StampedTestRunner().run()

