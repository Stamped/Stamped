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
from libs.applerss          import AppleRSS

Matcher = ArtistResultMatcher

def makeTestCase(query, *expected_results):
    return SearchTestCase('music', query, *expected_results)

def makeSimpleTestCase(query):
    return makeTestCase(query, Matcher(title=Equals(query)))

class ArtistSearchTests(SearchTestsRunner):
    
    def test_basic(self):
        """ Test basic artist searches """
        test_cases = (
            makeSimpleTestCase('nicki minaj'),
            makeSimpleTestCase('jay-z'),
            makeTestCase('jay z', Matcher(title=Equals('jay-z'))),
            makeSimpleTestCase('passion pit'),
            makeSimpleTestCase('red hot chili peppers'),
            makeSimpleTestCase('the temper trap'),
            makeTestCase('glitch mob', Matcher(title=Equals('the glitch mob'))),
            makeTestCase('kanye', Matcher(title=Equals('kanye west'))),
            makeSimpleTestCase('justin bieber'),
            makeTestCase('carly rae', Matcher(title=Equals('carly rae jepsen'))),
            makeSimpleTestCase('johnny cash'),
            makeTestCase('waylon', Matcher(title=Equals('waylon jennings'))),
            makeTestCase('tmbg', Matcher(title=Equals('they might be giants'))),
            makeSimpleTestCase('mgmt'),
            makeSimpleTestCase('rjd2'),
            makeTestCase('B.o.B', Matcher(title=StartsWith('B.o.B'))),
            makeSimpleTestCase('50 cent'),
            makeTestCase('50', Matcher(title=Equals('50 cent'))),
            makeTestCase('fifty cent', Matcher(title=Equals('50 cent'))),
            makeSimpleTestCase('katy perry'),
            makeSimpleTestCase('alison krauss'),
            makeSimpleTestCase('the highwaymen'),
            makeSimpleTestCase('flo rida'),
            # TODO: Will this ever work? We don't have recordings by Mozart, just recordings of music he composed.
            # Do we really want to try to support composers?
            makeSimpleTestCase('mozart')
        )

        self._run_tests('basic_artist', test_cases)
    
    def test_international(self):
        """ Test international artist support """

        test_cases = (
            makeSimpleTestCase('the beatles'),
            makeSimpleTestCase('david guetta'),
            makeSimpleTestCase('susan boyle'),
            makeSimpleTestCase('rammstein'),
            makeSimpleTestCase('deadmau5'),
            makeTestCase('deadmau 5', Matcher(title=Equals('deadmau5'))),
            makeSimpleTestCase('2face idibia'),
            makeSimpleTestCase('angelique kidjo'),
            makeSimpleTestCase('gotye'),
            makeSimpleTestCase('michel telo'),
            makeSimpleTestCase('stereo total'),
            makeSimpleTestCase('yelle'),
            makeSimpleTestCase('stefanie heinzmann'),
            makeSimpleTestCase('olly murs')
        )

        self._run_tests('i18n_artist', test_cases)
    
    def test_keywords(self):
        """ Test artist searches containing other keywords (songs, albums, etc.) """

        test_cases = (
            makeTestCase('adele 21',
                AlbumResultMatcher(title=Equals('21'), artist=Equals('adele')),
                ArtistResultMatcher(title=Equals('adele'))),
            makeTestCase('kanye power',
                TrackResultMatcher(title=Equals('power', artist=Equals('kanye west'))),
                ArtistResultMatcher(title=Equals('kanye west')),
                AlbumResultMatcher(title=Equals('my beautiful dark twisted fantasy'))),
            makeTestCase('ratat party with children',
                TrackResultMatcher(title=Equals('party with children', artist=Equals('ratatat'))),
                ArtistResultMatcher(title=Equals('ratatat'))),
            makeTestCase('flobot fight with tools handlebars',
                TrackResultMatcher(title=Equals('handlebars')),
                ArtistResultMatcher(title=Equals('flobots')),
                AlbumResultMatcher(title=Equals('fight with tools')))
        )

        self._run_tests(tests, {})
    
    def test_top_songs(self):
        """ Test artists from top songs from iTunes """
        
        rss  = AppleRSS()
        objs = rss.get_top_songs(limit=10)
        
        self.__test_artists('top_songs', objs)
    
    def test_top_albums(self):
        """ Test artists from top albums from iTunes """
        
        rss  = AppleRSS()
        objs = rss.get_top_albums(limit=10)
        
        self.__test_artists('top_albums', objs)
    
    def __test_artists(self, test_name, objs):
        test_cases = []

        for obj in objs:
            try:
                artist  = obj.artists[0].title.lower().strip()
                artist2 = utils.normalize(artist, strict=True)
                
                if artist != artist2:
                    # don't test artists whose names contain weird unicode strings
                    continue

            except Exception:
                continue
            
            test_cases.append(makeSimpleTestCase(artist))

        self._run_tests(test_name, test_cases)

if __name__ == '__main__':
    main()
