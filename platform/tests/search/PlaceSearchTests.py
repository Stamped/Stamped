#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from tests.StampedTestUtils       import *
from tests.framework.FixtureTest  import fixtureTest, main
from tests.search.SearchTestsRunner import *
from tests.search.SearchResultMatcher import *
from tests.search.SearchResultsScorer import *

def makeTestCase(query, coords, *expected_results):
    print 'EXPECTED RESULTS IS', expected_results
    if coords:
        query = {'query': query, 'coords': coords}
    return SearchTestCase('place', query, *expected_results)

class PlaceSearchTests(AStampedTestCase, SearchTestsRunner):
    @fixtureTest()
    def test_place_search(self):
        """ Test basic place searches """

        """
        TODO:
            * target national search
            * target google places search
            * target factual
            * target opentable
            * 
        """

        test_cases = (
            makeTestCase('bourbon and branch', None,
                PlaceResultMatcher(title=Equals('Bourbon and Branch'), all_components_must_match=True)),
            makeTestCase('empire state building', (40.736, -73.989),
                PlaceResultMatcher(title=Equals('Empire State Building'), all_components_must_match=True)),
            makeTestCase('beer bistro', (43.654828, -79.375191),
                PlaceResultMatcher(title=Equals('The Beer Bistro'))),
            makeTestCase('disney world', (28.344178, -81.575242),
                PlaceResultMatcher(title=Equals('Disney World'))),
            makeTestCase('le poisson rouge', (40.734466, -73.990742),
                PlaceResultMatcher(title=Equals('le poisson rouge'), all_components_must_match=True, unique=False)),
            makeTestCase('Galata Balikcisi', (41.025593, 28.974618),
                PlaceResultMatcher(title=Equals('Furreyya Galata Balikcisi'), all_components_must_match=True)),
            makeTestCase('Empanada Mama', (40.754632, -73.994261),
                PlaceResultMatcher(title=Equals('Empanada Mama'), all_components_must_match=True)),
            makeTestCase('Amber India', (37.765037, -122.412568),
                PlaceResultMatcher(title=Equals('Amber India'), all_components_must_match=True, unique=False)),
            makeTestCase('Evo Pizza', (37.781697, -122.392146),
                PlaceResultMatcher(title=Equals('Evo Pizza'), all_components_must_match=True)),
            makeTestCase('Azul Tequila',  (44.783160, -91.436092),
                PlaceResultMatcher(title=Equals('Azul Tequila'), all_components_must_match=True)),
            makeTestCase('Times Square', (39.481461, -6.373380),
                PlaceResultMatcher(title=Equals('Times Square'))),
            makeTestCase('galleria mall', (35.995347, -114.936936),
                PlaceResultMatcher(title=Equals('Galleria Mall'))),
            makeTestCase('SXSW', (50.172962, 8.721237),
                PlaceResultMatcher(title=Equals('SXSW'))),
        )

        """
        tests = [
            ({ 'query' : 'apotheke', 'category' : 'place', 'coords' : (29.984821, -95.338962) }, [
                SearchResultConstraint(title='apotheke', 
                                       types='place'), 
            ]), 
            ({ 'query' : 'apotheke', 'category' : 'place', 'coords' : (29.984821, -95.338962) }, [ 
                SearchResultConstraint(title='apotheke', 
                                       types='place'), 
            ]), 
            ({ 'query' : 'per se in nyc', 'category' : 'place', 'coords' : (29.984821, -95.338962) }, [ 
                SearchResultConstraint(title='per se', 
                                       types='place', 
                                       match='prefix'), 
            ]), 
            ({ 'query' : 'australian bar', 'category' : 'place', 'coords' : (50.121094, 8.673447) }, [ 
                SearchResultConstraint(title='australian bar', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'faramita', 'category' : 'place', 'coords' : (25.084350, 121.556224) }, [ 
                SearchResultConstraint(title='faramita', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'highline park', 'category' : 'place', }, [ 
                SearchResultConstraint(title='highline park', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'PDT', 'category' : 'place', }, [ 
                SearchResultConstraint(title='pdt', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'sizzle pie pizza', 'category' : 'place', 'coords' : (45.524149, -122.682825) }, [ 
                SearchResultConstraint(title='sizzle pie pizza', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'mauds cafe', 'category' : 'place', 'coords' : (54.593507, -5.925185) }, [ 
                SearchResultConstraint(title='maud\'s cafe', 
                                       types='place', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : 'zoka', 'category' : 'place', 'coords' : (47.622030, -122.337103) }, [ 
                SearchResultConstraint(title='zoka', 
                                       types='place', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : 'prospect sf', 'category' : 'place', 'coords' : (37.806528, -122.406511) }, [ 
                SearchResultConstraint(title='prospect', 
                                       types='place', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : 'A16', 'category' : 'place', 'coords' : (37.806528, -122.406511) }, [ 
                SearchResultConstraint(title='A16', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'venga empanadas', 'category' : 'place', 'coords' : (37.806586,-122.406520) }, [ 
                SearchResultConstraint(title='venga empanadas', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'mordisco', 'category' : 'place', 'coords' : (41.386533, 2.128773) }, [ 
                SearchResultConstraint(title='mordisco', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'veritas media', 'category' : 'place', 'coords' : (41.386533, 2.128773) }, [ 
                SearchResultConstraint(title='veritas media', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'nando\'s', 'category' : 'place', 'coords' : (51.478148, -3.176642) }, [ 
                SearchResultConstraint(title='nando\'s', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'enoxel', 'category' : 'place', 'coords' : (-23.596847, -46.688728) }, [ 
                SearchResultConstraint(title='eNOXEL', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'la victoria', 'category' : 'place', 'coords' : (35.395640, 139.567383) }, [ 
                SearchResultConstraint(title='la victoria', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'benihana', 'category' : 'place', 'coords' : (35.395640, 139.567383) }, [ 
                SearchResultConstraint(title='benihana', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'sakura', 'category' : 'place', 'coords' : (39.625811, -77.773603) }, [ 
                SearchResultConstraint(title='sakura', 
                                       types='place', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : 'sakura japanese restaurant', 'category' : 'place', 'coords' : (39.625811, -77.773603) }, [ 
                SearchResultConstraint(title='sakura japanese restaurant', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'rocket science lab', 'category' : 'place', 'coords' : (18.393496, -66.006503) }, [ 
                SearchResultConstraint(title='rocket science lab', 
                                       types='place',
                                       index=0), 
            ]), 
            ({ 'query' : 'cincinnati zoo', 'category' : 'place', 'coords' : (39.149059, -84.437150) }, [ 
                SearchResultConstraint(title='cincinnati zoo', 
                                       types='place', 
                                       match='prefix', 
                                       index=0), 
            ]), 
        ]
        """
        
        self._run_tests('place_tests', test_cases)

if __name__ == '__main__':
    main()

