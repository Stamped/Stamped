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
            ({ 'query' : 'game of thrones', 'category' : 'film', }, [ 
                SearchResultConstraint(title='game of thrones', types='tv'), 
            ]), 
            ({ 'query' : 'dexter', 'category' : 'film', }, [ 
                SearchResultConstraint(title='dexter', types='tv'), 
            ]), 
            ({ 'query' : 'family guy', 'category' : 'film', }, [ 
                SearchResultConstraint(title='family guy', types='tv'), 
            ]), 
            ({ 'query' : 'american idol', 'category' : 'film', }, [ 
                SearchResultConstraint(title='american idol', types='tv'), 
            ]), 
            ({ 'query' : 'spongebob squarepants', 'category' : 'film', }, [ 
                SearchResultConstraint(title='spongebob squarepants', types='tv'), 
            ]), 
            ({ 'query' : 'spongebob', 'category' : 'film', }, [ 
                SearchResultConstraint(title='spongebob squarepants', types='tv'), 
            ]), 
            ({ 'query' : 'trailer park boys', 'category' : 'film', }, [ 
                SearchResultConstraint(title='trailer park boys', types='tv'), 
                SearchResultConstraint(title='trailer park boys', types='movie'), 
            ]), 
            ({ 'query' : 'new girl', 'category' : 'film', }, [ 
                SearchResultConstraint(title='new girl', types='tv'), 
            ]), 
            ({ 'query' : 'up all night', 'category' : 'film', }, [ 
                SearchResultConstraint(title='up all night', types='tv'), 
            ]), 
            ({ 'query' : 'breaking bad', 'category' : 'film', }, [ 
                SearchResultConstraint(title='breaking bad', types='tv'), 
            ]), 
            ({ 'query' : 'LOST', 'category' : 'film', }, [ 
                SearchResultConstraint(title='LOST', types='tv'), 
            ]), 
            ({ 'query' : 'the sopranos', 'category' : 'film', }, [ 
                SearchResultConstraint(title='the sopranos', types='tv'), 
            ]), 
            ({ 'query' : 'the simpsons', 'category' : 'film', }, [ 
                SearchResultConstraint(title='the simpsons', types='tv'), 
            ]), 
            ({ 'query' : 'south park', 'category' : 'film', }, [ 
                SearchResultConstraint(title='south park', types='tv'), 
            ]), 
            ({ 'query' : 'saturday night live', 'category' : 'film', }, [ 
                SearchResultConstraint(title='saturday night live', types='tv'), 
            ]), 
            ({ 'query' : 'dark angel', 'category' : 'film', }, [ 
                SearchResultConstraint(title='dark angel', types='tv'), 
            ]), 
            ({ 'query' : 'misfits', 'category' : 'film', }, [ 
                SearchResultConstraint(title='misfits', types='tv'), 
            ]), 
            ({ 'query' : 'arrested development', 'category' : 'film', }, [ 
                SearchResultConstraint(title='arrested development', types='tv'), 
            ]), 
            ({ 'query' : 'big bang theory', 'category' : 'film', }, [
                SearchResultConstraint(title='the big bang theory', types='tv'), 
            ]), 
            ({ 'query' : 'how i met your mother', 'category' : 'film', }, [
                SearchResultConstraint(title='how i met your mother', types='tv'), 
            ]), 
            # TODO (travis): fails because of invalid location hint
            #({ 'query' : 'it\'s always sunny in philadelphia', 'category' : 'film', }, [
            #    SearchResultConstraint(title='it\'s always sunny in philadelphia', types='tv'), 
            #]), 
            ({ 'query' : 'the walking dead', 'category' : 'film', }, [
                SearchResultConstraint(title='the walking dead', types='tv'), 
                SearchResultConstraint(title='the walking dead', types='movie'), 
            ]), 
            ({ 'query' : 'friends', 'category' : 'film', }, [
                SearchResultConstraint(title='friends', types='tv'), 
            ]), 
            ({ 'query' : 'firefly', 'category' : 'film', }, [
                SearchResultConstraint(title='firefly', types='tv'), 
                SearchResultConstraint(title='serenity', types='movie'), 
            ]), 
            ({ 'query' : 'futurama', 'category' : 'film', }, [
                SearchResultConstraint(title='futurama', types='tv'), 
            ]), 
            ({ 'query' : '90210', 'category' : 'film', }, [
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
            ({ 'query' : 'footballer\'s wives', 'category' : 'film', }, [    # popular U.K. TV show (2002)
                SearchResultConstraint(title='footballer\'s wives', types='tv'), 
            ]), 
            ({ 'query' : 'hotel babylon', 'category' : 'film', }, [          # popular U.K. TV show (2006)
                SearchResultConstraint(title='hotel babylon', types='tv'), 
            ]), 
            ({ 'query' : 'jeeves and wooster', 'category' : 'film', }, [     # popular U.K. TV show (1990)
                SearchResultConstraint(title='jeeves and wooster', types='tv'), 
            ]), 
            ({ 'query' : 'coupling', 'category' : 'film', }, [               # popular U.K. TV show (2000-2004)
                SearchResultConstraint(title='coupling', types='tv'), 
            ]), 
            
            # TODO: add more popular foreign shows with exotic names
        ]
        
        self._run_tests(tests, args)

if __name__ == '__main__':
    StampedTestRunner().run()

