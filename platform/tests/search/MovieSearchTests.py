#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint
from libs.Fandango          import Fandango

class MovieSearchTests(ASearchTestSuite):
    
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
            ({ 'query' : 'teenage mutant ninja turtles', 'category' : 'film', }, [ 
                SearchResultConstraint(title='teenage mutant ninja turtles', 
                                       types='movie', 
                                       index=0), 
            ]), 
            ({ 'query' : 'teenage mutant ninja turtles II', 'category' : 'film', }, [ 
                SearchResultConstraint(title='teenage mutant ninja turtles II', 
                                       types='movie', 
                                       match='prefix'), 
            ]), 
            ({ 'query' : 'teenage mutant ninja turtles III', 'category' : 'film', }, [ 
                SearchResultConstraint(title='teenage mutant ninja turtles III', 
                                       types='movie', 
                                       match='prefix'), 
            ]), 
            ({ 'query' : 'the godfather', 'category' : 'film', }, [ 
                SearchResultConstraint(title='the godfather', 
                                       types='movie', 
                                       index=0), 
            ]), 
            ({ 'query' : 'godfather', 'category' : 'film', }, [ 
                SearchResultConstraint(title='the godfather', 
                                       types='movie'), 
            ]), 
            ({ 'query' : 'the hunger games', 'category' : 'film', }, [ 
                SearchResultConstraint(title='the hunger games', 
                                       types='movie', 
                                       index=0), 
            ]), 
            ({ 'query' : 'hunger games', 'category' : 'film', }, [ 
                SearchResultConstraint(title='the hunger games', 
                                       types='movie', 
                                       index=0), 
            ]), 
            ({ 'query' : 'drive' }, [ 
                SearchResultConstraint(title='drive', 
                                       types='movie', 
                                       imdb_id='tt0780504', 
                                       index=0), 
            ]), 
            ({ 'query' : 'drive (2011)' }, [ 
                SearchResultConstraint(title='drive', 
                                       types='movie', 
                                       imdb_id='tt0780504', 
                                       index=0), 
            ]), 
            ({ 'query' : 'inception', 'category' : 'film', }, [ 
                SearchResultConstraint(title='inception', 
                                       types='movie', 
                                       index=0), 
            ]), 
            ({ 'query' : 'die hard', 'category' : 'film', }, [ 
                SearchResultConstraint(title='die hard', 
                                       types='movie', 
                                       imdb_id='tt0095016', 
                                       index=0), 
            ]), 
            ({ 'query' : 'the fifth element', 'category' : 'film', }, [ 
                SearchResultConstraint(title='the fifth element', 
                                       types='movie', 
                                       imdb_id='tt0119116', 
                                       index=0), 
            ]), 
            ({ 'query' : 'raiders of the lost ark', 'category' : 'film', }, [ 
                SearchResultConstraint(title='raiders of the lost ark', 
                                       types='movie', 
                                       imdb_id='tt0082971', 
                                       index=0), 
            ]), 
            ({ 'query' : 'tomorrow never dies', 'category' : 'film', }, [ 
                SearchResultConstraint(title='tomorrow never dies', 
                                       types='movie', 
                                       imdb_id='tt0120347', 
                                       index=0), 
            ]), 
        ]
        
        self._run_tests(tests, args)
    
    def test_fuzzy(self):
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'futurama movie', 'category' : 'film', }, [ 
                SearchResultConstraint(title='futurama: bender\'s game', 
                                       types='movie'), 
                SearchResultConstraint(title='futurama: into the wild green yonder', 
                                       types='movie'), 
                SearchResultConstraint(title='futurama: the beast with a million backs', 
                                       types='movie'), 
            ]), 
            ({ 'query' : 'mission impossible ghost protocol', 'category' : 'film', }, [ 
                SearchResultConstraint(title='mission impossible - ghost protocol', 
                                       types='movie', 
                                       index=0), 
            ]), 
        ]
        
        self._run_tests(tests, args)
    
    def test_international(self):
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'Le ragazze di Piazza di Spagna', 'category' : 'film', }, [ 
                SearchResultConstraint(title='Le ragazze di Piazza di Spagna', 
                                       types='movie', 
                                       index=0), 
            ]), 
            
            # TODO: add more internationl movie coverage
        ]
        
        self._run_tests(tests, args)
    
    def test_top_box_office(self):
        fandango = Fandango(verbose=True)
        movies   = fandango.get_top_box_office_movies()
        
        return self.__test_movie_search(movies, index = 0)
    
    """
    # NOTE (travis): TMDB, which is our primary source for movies, does not 
    # always have upcoming movies populated before they're released, so we're 
    # disabling these tests until we find an alternative source for upcoming 
    # movies.
    
    def test_coming_soon(self):
        fandango = Fandango(verbose=True)
        movies   = fandango.get_coming_soon_movies()
        
        return self.__test_movie_search(movies)
    
    def test_opening_this_week(self):
        fandango = Fandango(verbose=True)
        movies   = fandango.get_opening_this_week_movies()
        
        return self.__test_movie_search(movies)
    """
    
    def __test_movie_search(self, movies, **extra_constraint_args):
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = []
        
        for movie in movies:
            tests.append( ({ 'query' : movie.title, 'category' : 'film', }, [ 
                SearchResultConstraint(title=movie.title, 
                                       types='movie', 
                                       **extra_constraint_args), 
            ]))
        
        self._run_tests(tests, args)

if __name__ == '__main__':
    StampedTestRunner().run()

