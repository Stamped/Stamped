#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from tests.StampedTestUtils       import *
from tests.framework.FixtureTest  import fixtureTest
from tests.search.SearchTestsRunner import SearchTestCase, SearchTestsRunner, main
from tests.search.SearchResultMatcher import *
from tests.search.SearchResultsScorer import *

from libs.Fandango                import Fandango

Matcher = MovieResultMatcher

def makeTestCase(query, *expected_results):
    return SearchTestCase('film', query, *expected_results)

def makeSimpleTestCase(query):
    return makeTestCase(query, Matcher(title=Equals(query)))


class MovieSearchTests(SearchTestsRunner):
    
    def test_basic(self):
        test_cases = (
            makeSimpleTestCase('teenage mutant ninja turtles'),
            makeTestCase('teenage mutant ninja turtles II',
                Matcher(title=LooselyEquals('teenage mutant ninja turtles ii: the secret of the ooze'))),
            makeSimpleTestCase('teenage mutant ninja turtles III'),
            # TODO make this ordering-agnostic
            makeTestCase('the godfather',
                Matcher(title=Equals('the godfather')),
                Matcher(title=LooselyEquals('the godfather: part ii')),
                Matcher(title=LooselyEquals('the godfather: part iii'))),
            # TODO make this ordering-agnostic
            makeTestCase('godfather',
                Matcher(title=Equals('the godfather')),
                Matcher(title=LooselyEquals('the godfather: part ii')),
                Matcher(title=LooselyEquals('the godfather: part iii'))),
            makeSimpleTestCase('the hunger games'),
            makeTestCase('hunger games', Matcher(title=Equals('the hunger games'))),
            makeSimpleTestCase('drive'),
            # TODO: test that drive 2011 gets the right version of 'drive'
            # TODO: ugh, that movie sucked a lot of balls
            makeSimpleTestCase('inception'),
            makeTestCase('die hard',
                Matcher(title=Equals('die hard')),
                Matcher(title=Equals('live free or die hard')),
                Matcher(title=Equals('die hard 2: die harder')),
                Matcher(title=LooselyEquals('die hard with a vengeance'))),
            makeSimpleTestCase('the fifth element'),
            makeSimpleTestCase('raiders of the lost ark'),
            makeSimpleTestCase('tomorrow never dies'),
            # TODO make this ordering-agnostic
            makeTestCase('indiana jones',
                Matcher(title=Equals('raiders of the lost ark')),
                Matcher(title=Equals('indiana jones and the last crusade')),
                Matcher(title=Equals('indiana jones and the temple of doom')),
                Matcher(title=Equals('indiana jones and the kingdom of the crystal skull'))),
            # The rest of them were garbage and I don't give a fuck if Attack of the Clones comes before Phantom Menace
            # or whatever, but when people say Star Wars, these are the movies they mean.
            makeTestCase('star wars',
                Matcher(title=LooselyEquals('star wars: episode iv - a new hope')),
                Matcher(title=LooselyEquals('star wars: episode v - the empire strikes back')),
                Matcher(title=LooselyEquals('star wars: episode vi - return of the jedi'))),
        )

        self._run_tests('basic_film', test_cases)
    
    def test_fuzzy(self):
        test_cases = (
            # TODO make this ordering-agnostic
            makeTestCase('futurama movie',
                Matcher(title=LooselyEquals('futurama: bender\'s game')),
                Matcher(title=LooselyEquals('futurama: into the wild green yonder')),
                Matcher(title=LooselyEquals('futurama: the beast with a billion backs'))),
            makeTestCase('mission impossible ghost', Matcher(title=Contains('ghost protocol')))
        )

        self._run_tests('fuzzy_film', test_cases)
    
    def test_international(self):
        # TODO: add more international movie coverage
        test_cases = (
            makeTestCase('ragazze di piazza', Matcher(title=Equals('le ragazze di piazza di spagna'))),
        )

        self._run_tests('i18n_film', test_cases)
    
    def test_top_box_office(self):
        fandango = Fandango(verbose=True)
        movies   = fandango.get_top_box_office_movies()
        
        return self.__test_movie_search('top_box_office', movies)
    
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
    
    def __test_movie_search(self, test_name, movies):
        test_cases = []
        
        for movie in movies:
            test_cases.append(makeSimpleTestCase(movie.title))

        self._run_tests(test_name, test_cases)

if __name__ == '__main__':
    main()

