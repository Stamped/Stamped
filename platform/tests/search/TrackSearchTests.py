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

Matcher = TrackResultMatcher

def makeTestCase(query, *expected_results):
    return SearchTestCase('music', query, *expected_results)

def makeSimpleTestCase(query, artist=None):
    if artist is None:
        return makeTestCase(query, Matcher(title=Equals(query)))
    else:
        return makeTestCase(query, Matcher(title=Equals(query), artist=Equals(artist)))


class TrackSearchTests(SearchTestsRunner):
    
    def test_basic(self):
        """ Test basic track searches """
        test_cases = (
            makeSimpleTestCase('simple as...'),
            makeSimpleTestCase('what\'s wrong is everywhere'),
            makeSimpleTestCase('whats wrong is everywhere', 'what\'s wrong is everywhere'),
            makeSimpleTestCase('midnight city'),
            makeSimpleTestCase('lux aeterna'),
            makeSimpleTestCase('mouthful of diamonds'),
            makeSimpleTestCase('damn it feels good to be a gangsta'),
            makeTestCase('good morning chamillionaire',
                TrackResultMatcher(title=Equals('good morning')),
                ArtistResultMatcher(title=Equals('chamillionaire'))),
            makeTestCase('let it (edit remix) machinedrum',
                TrackResultMatcher(title=Equals('let it (edit remix')),
                ArtistResultMatcher(title=Equals('machinedrum'))),
            makeTestCase('young blood lynx',
                TrackResultMatcher(title=Equals('young blood')),
                ArtistResultMatcher(title=Equals('lynx'))),
            makeTestCase('ADHD kendrick lamar',
                TrackResultMatcher(title=StartsWith('A.D.H.D')),
                ArtistResultMatcher(title=Equals('kendrick lamar'))),
            makeSimpleTestCase('born this way'),
            makeTestCase('we belong together mariah carey',
                Matcher(title=Equals('we belong together'), artist=Equals('mariah carey'))),
            makeTestCase('katy perry part of me', Matcher(title=Equals('part of me'), artist=Equals('katy perry')))
        )

        self._run_tests('basic_track', test_cases)
    
    def test_track_album_artist_combos(self):
        """ Test track searches also containing the artist and/or album name """

        test_cases = (
            makeTestCase('to look like you john butler trio april uprising',
                TrackResultMatcher(title=Equals('to look like you')),
                AlbumResultMatcher(title=Equals('april uprising')),
                ArtistResultMatcher(title=Equals('john butler trio'))),
            makeTestCase('john butler to look like you',
                TrackResultMatcher(title=Equals('to look like you')),
                ArtistResultMatcher(title=Equals('john butler trio'))),
            makeTestCase('april uprising to look like you',
                TrackResultMatcher(title=Equals('to look like you')),
                AlbumResultMatcher(title=Equals('april uprising')),
                ArtistResultMatcher(title=Equals('john butler trio'))),
            makeTestCase('american music by the violent femmes',
                TrackResultMatcher(title=StartsWith('american music')),
                ArtistResultMatcher(title=Equals('violent femmes'))),
            makeTestCase('parte stroke 9',
                TrackResultMatcher(title=StartsWith('parte')),
                ArtistResultMatcher(title=Equals('stroke 9')),
                AlbumResultMatcher(title=Equals('all in'))),
            makeTestCase('1980 rehab graffiti the world',
                TrackResultMatcher(title=Equals('1980')),
                ArtistResultMatcher(title=Equals('rehab')),
                AlbumResultMatcher(title=Equals('graffiti the world'))),
            makeTestCase('1980 rehab',
                TrackResultMatcher(title=Equals('1980')),
                ArtistResultMatcher(title=Equals('rehab')),
                AlbumResultMatcher(title=Equals('graffiti the world'))),
            makeTestCase('graffiti the world 1980',
                TrackResultMatcher(title=Equals('1980')),
                ArtistResultMatcher(title=Equals('rehab')),
                AlbumResultMatcher(title=Equals('graffiti the world'))),
            makeTestCase('montanita ratatat',
                TrackResultMatcher(title=Equals('montanita')),
                ArtistResultMatcher(title=Equals('ratatat')),
                AlbumResultMatcher(title=Equals('classics'), artist=Equals('ratatat'))),
            makeTestCase('ratatat classics montanita',
                TrackResultMatcher(title=Equals('montanita')),
                ArtistResultMatcher(title=Equals('ratatat')),
                AlbumResultMatcher(title=Equals('classics'), artist=Equals('ratatat'))),
            makeTestCase('starry eyed surprise bunkka',
                TrackResultMatcher(title=LooselyEquals('starry eyed surprise')),
                ArtistResultMatcher(title=Contains('oakenfold')),
                AlbumResultMatcher(title=Equals('bunkka'))),
            makeTestCase('afternoon youth lagoon hibernation',
                TrackResultMatcher(title=Equals('afternoon')),
                ArtistResultMatcher(title=Equals('youth lagoon')),
                AlbumResultMatcher(title=Equals('the year of hibernation'))),
            makeTestCase('m83 intro',
                TrackResultMatcher(title=Equals('intro')),
                ArtistResultMatcher(title=Equals('m83')),
                AlbumResultMatcher(title=StartsWith('hurry up, we\'re dreaming'))),
        )

        self._run_tests('track_album_artist_combos', test_cases)
    
    def test_international(self):
        """ Test international track support.  """

        test_cases = (
            makeSimpleTestCase('somebody that i used to know'),
            makeSimpleTestCase('ai se eu te pego'),
            makeTestCase('i follow rivers lykke li',
                TrackResultMatcher(title=Equals('i follow rivers'), artist=Equals('lykke li')),
                AlbumResultMatcher(title=Equals('i follow rivers'), artist=Equals('lykke li')),
                ArtistResultMatcher(title=Equals('lykke li'))),
            makeTestCase('my name is stain shaka',
                TrackResultMatcher(title=Equals('my name is stain')),
                ArtistResultMatcher(title=Equals('shaka ponk')),
                AlbumResultMatcher(title=Equals('sex, plugs and vidiot\'ape'))),
            makeTestCase('leider geil deichkind', Matcher(title=StartsWith('leider geil'))),
            makeTestCase('rising sun exile',
                TrackResultMatcher(title=Equals('rising sun'), artist=Equals('exile')),
                AlbumResultMatcher(title=Equals('rising sun'), artist=Equals('exile'))),
        )

        self._run_tests('track_i18n', test_cases)
    
    def test_top_tracks(self):
        """ Test the top tracks from iTunes """
        
        rss    = AppleRSS()
        tracks = rss.get_top_songs(limit=10)
        
        self.__test_tracks('top_tracks', tracks)
    
    ''' # TODO: these feeds are currently broken in AppleRSS
    def test_new_releases(self):
        """ Test the new releases from iTunes """
        
        rss    = AppleRSS()
        tracks = rss.get_new_releases(limit=10)
        
        self.__test_tracks(tracks)
    
    def test_just_added(self):
        """ Test the tracks just added to iTunes """
        
        rss    = AppleRSS()
        tracks = rss.get_just_added(limit=10)
        
        self.__test_tracks(tracks)
    '''
    
    def __test_tracks(self, test_name, tracks):
        test_cases = []

        for track in tracks:
            name  = track.title.lower().strip()
            name2 = utils.normalize(name, strict=True)
            
            if name.lower() != name2:
                # don't test tracks whose names contain weird unicode strings
                continue

            test_cases.append(makeSimpleTestCase(query))

            # TODO: get this working consistently (track_name artist_name) => track and artist in results
            try:
                artist = track.artists[0].title
                query  = "%s %s" % (name, artist)

                tests_cases.append(makeTestCase(query,
                    TrackResultMatcher(title=Equals(name), artist=Equals(artist)),
                    ArtistResultMatcher(title=Equals(name))))

            except AttributeError:
                pass

        self._run_tests(test_name, test_cases)

if __name__ == '__main__':
    main()

