#!/usr/bin/env python
from __future__ import absolute_import

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

Matcher = TvResultMatcher

def makeTestCase(query, *expected_results):
    return SearchTestCase('film', query, *expected_results)

def makeSimpleTestCase(title):
    return makeTestCase(title, Matcher(title=Equals(title)))

class TVSearchTests(SearchTestsRunner):
    
    def test_basic(self):
        """ Test basic tv searches """

        test_cases = (
            makeSimpleTestCase('game of thrones'),
            makeSimpleTestCase('dexter'),
            makeSimpleTestCase('family guy'),
            makeSimpleTestCase('american idol'),
            makeSimpleTestCase('spongebob squarepants'),
            makeTestCase('spongebob', Matcher(title=Equals('spongebob squarepants'))),
            makeTestCase('trailer park boys',
                TvResultMatcher(title=Equals('trailer park boys')),
                MovieResultMatcher(title=Equals('trailer park boys'))),
            makeSimpleTestCase('new girl'),
            makeSimpleTestCase('up all night'),
            makeSimpleTestCase('breaking bad'),
            makeSimpleTestCase('lost'),
            makeSimpleTestCase('the sopranos'),
            makeSimpleTestCase('the simpsons'),
            makeSimpleTestCase('south park'),
            makeSimpleTestCase('saturday night live'),
            makeTestCase('snl', Matcher(title=Equals('Saturday Night Live'))),
            makeSimpleTestCase('dark angel'),
            makeSimpleTestCase('misfits'),
            makeSimpleTestCase('arrested development'),
            makeSimpleTestCase('the big bang theory'),
            makeSimpleTestCase('how i met your mother'),
            makeTestCase('the walking dead',
                TvResultMatcher(title=Equals('the walking dead')),
                MovieResultMatcher(title=Equals('the walking dead'))),
            makeSimpleTestCase('friends'),
            makeTestCase('firefly',
                TvResultMatcher(title=Equals('firefly')),
                MovieResultMatcher(title=Equals('serenity'))),
            makeSimpleTestCase('futurama'),
            makeSimpleTestCase('90210'),
            makeTestCase('always sunny philadelphia', Matcher(title=Equals('It\'s Always Sunny in Philadelphia')))
        )

        self._run_tests('basic_tv_tests', test_cases)

    def test_international(self):
        """ Test international tv searches """

        # TODO: add more popular foreign shows with exotic names
        test_cases = (
            makeTestCase('footballer\'s wives', Matcher(title=Equals('footballers\' wives'))),
            makeTestCase('football wives', Matcher(title=Equals('footballers\' wives'))),
            makeSimpleTestCase('hotel babylon'),
            makeSimpleTestCase('jeeves and wooster'),
            makeSimpleTestCase('coupling')
        )

        self._run_tests('i18n_tv_tests', test_cases)


if __name__ == '__main__':
    main()

