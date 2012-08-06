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
from libs.applerss          import AppleRSS

Matcher = AlbumResultMatcher

def makeTestCase(query, *expected_results):
    return SearchTestCase('music', query, *expected_results)

def makeSimpleTestCase(query, artist=None, unique=True):
    if artist is None:
        return makeTestCase(query, Matcher(title=Equals(query), unique=unique))
    else:
        return makeTestCase(query, Matcher(title=Equals(query), artist=Equals(query), unique=unique))

class AlbumSearchTests(SearchTestsRunner):
    
    def test_basic(self):
        test_cases = (
            makeSimpleTestCase('deep cuts', unique=False),
            makeSimpleTestCase('s.c.i.e.n.c.e.'),
            makeTestCase('science', Matcher(title=Equals('s.c.i.e.n.c.e.'))),
            makeSimpleTestCase('hail to the thief'),
            makeSimpleTestCase('eyelid movies'),
            makeSimpleTestCase('musique automatique'),
            makeSimpleTestCase('oracular spectacular'),
            makeSimpleTestCase('wolfgang amadeus phoenix'),
            makeSimpleTestCase('21', artist='adele'),
            makeTestCase('21 adele', Matcher(title=Equals('21'), artist=Equals('adele'))),
            makeSimpleTestCase('the young machines'),
            makeSimpleTestCase('without a sound'),
            makeSimpleTestCase('viva wisconsin'),
            makeTestCase('play the b sides', Matcher(title=Equals('play: the b-sides'))),
            makeSimpleTestCase('astro lounge'),
            makeSimpleTestCase('toxicity'),
            makeSimpleTestCase('enema of the state'),
            makeSimpleTestCase('i-empire'),
            makeTestCase('its never like that', Matcher(title=Equals('it\'s never been like that'))),
            makeSimpleTestCase('it won\'t snow where you\'re going'),
            makeTestCase('tuskegee lionel richie', Matcher(title=Equals('tuskegee'), artist=Equals('lionel richie'))),
            makeTestCase('tuskegee by lionel richie', Matcher(title=Equals('tuskegee'), artist=Equals('lionel richie'))),
            makeTestCase('bangarang skrillex', Matcher(title=Equals('bangarang'), artist=Equals('skrillex'))),
            makeTestCase('sorry for party rocking lmfao', Matcher(title=Equals('sorry for party rocking'))),
            makeTestCase('nothing but the beat david guetta', Matcher(title=Equals('nothing but the beat'))),
        )

        self._run_tests('basic_album', test_cases)
    
    def test_international(self):
        test_cases = (
            makeSimpleTestCase('kimi ni saku hana'),
            makeSimpleTestCase('bis ans ende der welt'),
            makeTestCase('befehl von ganz unten album', Matcher(title=StartsWith('befehl von ganz unten album'))),
        )

        self._run_tests('i18n_album', test_cases)
    
    def test_top_albums(self):
        """ Test top albums from iTunes """
        
        rss    = AppleRSS()
        albums = rss.get_top_albums(limit=10)
        
        self.__test_albums('top_albums', albums)
    
    def __test_albums(self, test_name, albums):

        test_cases = []
        for album in albums:
            name  = album.title.lower().strip()
            name2 = utils.normalize(name, strict=True)
            
            # don't test albums whose names contain weird unicode strings
            if name != name2:
                continue

            test_cases.append(makeSimpleTestCase(name))

        self._run_tests(test_name, test_cases)

if __name__ == '__main__':
    main()