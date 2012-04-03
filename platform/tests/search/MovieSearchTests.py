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
            ({ 'query' : 'teenage mutant ninja turtles', }, [ 
                SearchResultConstraint(title='teenage mutant ninja turtles', 
                                       types='movie', 
                                       index=0), 
            ]), 
            ({ 'query' : 'teenage mutant ninja turtles II', }, [ 
                SearchResultConstraint(title='teenage mutant ninja turtles II', 
                                       types='movie', 
                                       match='prefix'), 
            ]), 
            ({ 'query' : 'teenage mutant ninja turtles III', }, [ 
                SearchResultConstraint(title='teenage mutant ninja turtles III', 
                                       types='movie', 
                                       match='prefix'), 
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
    
    def test_in_theaters(self):
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
            tests.append( ({ 'query' : movie.title, }, [ 
                SearchResultConstraint(title=movie.title, 
                                       types='movie', 
                                       **extra_constraint_args), 
            ]))
        
        self._run_tests(tests, args)

if __name__ == '__main__':
    StampedTestRunner().run()

