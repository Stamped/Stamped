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

def makeTestCase(query, coords, *expected_results):
    if coords:
        query = {'query': query, 'coords': coords}
    return SearchTestCase('place', query, *expected_results)


Matcher = PlaceResultMatcher

class PlaceSearchTests(SearchTestsRunner):
    @fixtureTest()
    def test_place_search(self):
        """ Test basic place searches """

        """
        TODO:
            * Add in source requirements.
            * More queries where the query string != the name.
            * In queries with multiple results, check that closer results are returned.
        """

        test_cases = (
            makeTestCase('bourbon and branch', None,
                Matcher(title=Equals('Bourbon and Branch'))),
            makeTestCase('empire state building', (40.736, -73.989),
                Matcher(title=Equals('Empire State Building'))),
            makeTestCase('beer bistro', (43.654828, -79.375191),
                Matcher(title=Equals('The Beer Bistro'))),
            makeTestCase('disney world', (28.344178, -81.575242),
                Matcher(title=Equals('Disney World'))),
            makeTestCase('le poisson rouge', (40.734466, -73.990742),
                Matcher(title=Equals('le poisson rouge'), unique=False)),
            makeTestCase('Galata Balikcisi', (41.025593, 28.974618),
                Matcher(title=Equals('Furreyya Galata Balikcisi'))),
            makeTestCase('Empanada Mama', (40.754632, -73.994261),
                Matcher(title=Equals('Empanada Mama'))),
            makeTestCase('Amber India', (37.765037, -122.412568),
                Matcher(title=Equals('Amber India'), unique=False)),
            makeTestCase('Evo Pizza', (37.781697, -122.392146),
                Matcher(title=Equals('Evo Pizza'))),
            makeTestCase('Azul Tequila',  (44.783160, -91.436092),
                Matcher(title=Equals('Azul Tequila'))),
            makeTestCase('Times Square', (39.481461, -6.373380),
                Matcher(title=Equals('Times Square'))),
            makeTestCase('galleria mall', (35.995347, -114.936936),
                Matcher(title=Equals('Galleria Mall'))),
            makeTestCase('SXSW', (50.172962, 8.721237),
                Matcher(title=Equals('SXSW'))),
            makeTestCase('apotheke', (29.984821, -95.338962),
                Matcher(title=Equals('apotheke'))),
            makeTestCase('per se in nyc', (29.984821, -95.338962),
                Matcher(title=Equals('Per Se'))),
            makeTestCase('australian bar', (50.121094, 8.673447),
                Matcher(title=Equals('australian bar'))),
            makeTestCase('faramita', (25.084350, 121.556224),
                Matcher(title=Equals('faramita'))),
            makeTestCase('highline park', None,
                Matcher(title=Equals('highline park'))),
            makeTestCase('PDT', None,
                Matcher(title=Equals('pdt'))),
            makeTestCase('sizzle pie pizza', (45.524149, -122.682825),
                Matcher(title=Equals('sizzle pie pizza'))),
            makeTestCase('mauds cafe', (54.593507, -5.925185),
                Matcher(title=Equals('maud\'s cafe'))),
            makeTestCase('zoka', (47.622030, -122.337103),
                Matcher(title=StartsWith('zoka'))),
            makeTestCase('prospect sf', (37.806528, -122.406511),
                Matcher(title=StartsWith('prospect'))),
            makeTestCase('A16', (37.806528, -122.406511),
                Matcher(title=Equals('A16'))),
            makeTestCase('venga empanadas', (37.806528, -122.406511),
                Matcher(title=Equals('venga empanadas'))),
            makeTestCase('mordisco', (41.386533, 2.128773),
                Matcher(title=Equals('mordisco'))),
            makeTestCase('veritas media', (41.386533, 2.128773),
                Matcher(title=Equals('veritas media'))),
            makeTestCase('nando\'s', (51.478148, -3.176642),
                Matcher(title=Equals('nando\'s'))),
            makeTestCase('enoxel', (-23.596847, -46.688728),
                Matcher(title=Equals('eNOXEL'))),
            makeTestCase('la victoria', (35.395640, 139.567383),
                Matcher(title=Equals('la victoria'))),
            makeTestCase('benihana', (35.395640, 139.567383),
                Matcher(title=Equals('benihana'))),
            makeTestCase('sakura', (39.625811, -77.773603),
                Matcher(title=StartsWith('sakura'))),
            makeTestCase('sakura japanese restaurant', (39.625811, -77.773603),
                Matcher(title=Equals('sakura japanese restaurant'))),
            makeTestCase('rocket science lab', (18.393496, -66.006503),
                Matcher(title=Equals('rocket science lab'))),
            makeTestCase('cincinnati zoo', (39.149059, -84.437150),
                Matcher(title=StartsWith('cincinnati zoo'))),
        )

        self._run_tests('place_tests', test_cases)

if __name__ == '__main__':
    main()

