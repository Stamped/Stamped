#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from tests.StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint
from libs.applerss          import AppleRSS

class TrackSearchTests(ASearchTestSuite):
    
    def test_basic(self):
        """ Test basic track searches """
        
        tests = [
            ({ 'query' : 'Simple As...', 'category' : 'music', }, [ 
                SearchResultConstraint(title='simple as...', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'What\'s wrong is everyhere', 'category' : 'music', }, [ 
                SearchResultConstraint(title='what\'s wrong is everywhere', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'midnight city', 'category' : 'music', }, [ 
                SearchResultConstraint(title='midnight city', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'lux aeterna', 'category' : 'music', }, [ 
                SearchResultConstraint(title='lux aeterna', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'mouthful of diamonds', 'category' : 'music', }, [ 
                SearchResultConstraint(title='mouthful of diamonds', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'damn it feels good to be a gangsta', 'category' : 'music', }, [ 
                SearchResultConstraint(title='damn it feels good to be a gangsta', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'good morning chamillionaire', 'category' : 'music', }, [ 
                SearchResultConstraint(title='good morning',        types='track'), 
                SearchResultConstraint(title='chamillionaire',      types='artist'), 
            ]), 
            ({ 'query' : 'let it (edit remix) machinedrum', 'category' : 'music', }, [ 
                SearchResultConstraint(title='let it (edit remix)', types='track'), 
                SearchResultConstraint(title='machinedrum',         types='artist'), 
            ]), 
            ({ 'query' : 'young blood lynx', 'category' : 'music', }, [ 
                SearchResultConstraint(title='young blood',         types='track'), 
                SearchResultConstraint(title='lynx',                types='artist'), 
            ]), 
            ({ 'query' : 'A.D.H.D. kendrick lamar', 'category' : 'music', }, [ 
                SearchResultConstraint(title='A.D.H.D',             types='track', match='prefix'), 
                SearchResultConstraint(title='kendrick lamar',      types='artist'), 
            ]), 
            ({ 'query' : 'born this way', 'category' : 'music', }, [ 
                SearchResultConstraint(title='born this way', 
                                       types='track'), 
            ]), 
        ]
        
        self._run_tests(tests, {})
    
    def test_track_album_artist_combos(self):
        """ Test track searches also containing the artist and/or album name """

        tests = [
            ({ 'query' : 'to look like you john butler trio april uprising', 'category' : 'music', }, [ 
                SearchResultConstraint(title='to look like you',    types='track', 
                                       index=0), 
                SearchResultConstraint(title='april uprising',      types='album'), 
                SearchResultConstraint(title='john butler trio',    types='artist'), 
            ]), 
            ({ 'query' : 'john butler to look like you', 'category' : 'music', }, [ 
                SearchResultConstraint(title='to look like you',    types='track', 
                                       index=0), 
                SearchResultConstraint(title='april uprising',      types='album'), 
                SearchResultConstraint(title='john butler trio',    types='artist'), 
            ]), 
            ({ 'query' : 'april uprising to look like you', 'category' : 'music', }, [ 
                SearchResultConstraint(title='to look like you',    types='track'), 
                SearchResultConstraint(title='april uprising',      types='album'), 
                SearchResultConstraint(title='john butler trio',    types='artist'), 
            ]), 
            ({ 'query' : 'american music by the violent femmes', 'category' : 'music', }, [ 
                SearchResultConstraint(title='american music',      types='track', 
                                       match='prefix', index=0), 
                SearchResultConstraint(title='violent femmes',      types='artist'), 
                #SearchResultConstraint(title='viva wisconsin',      types='album'), 
            ]), 
            ({ 'query' : 'parte stroke 9', 'category' : 'music', }, [ 
                SearchResultConstraint(title='parte', types='track', match='prefix'), 
                SearchResultConstraint(title='stroke 9',            types='artist'), 
                SearchResultConstraint(title='all in',              types='album'), 
            ]), 
            ({ 'query' : '1980 rehab graffiti the world', 'category' : 'music', }, [ 
                SearchResultConstraint(title='1980',                types='track'), 
                SearchResultConstraint(title='rehab',               types='artist'), 
                SearchResultConstraint(title='graffiti the world',  types='album'), 
            ]), 
            ({ 'query' : '1980 rehab', 'category' : 'music', }, [ 
                SearchResultConstraint(title='1980',                types='track'), 
                SearchResultConstraint(title='rehab',               types='artist'), 
                SearchResultConstraint(title='graffiti the world',  types='album'), 
            ]), 
            ({ 'query' : 'graffiti the world 1980', 'category' : 'music', }, [ 
                SearchResultConstraint(title='1980',                types='track'), 
                SearchResultConstraint(title='rehab',               types='artist'), 
                SearchResultConstraint(title='graffiti the world',  types='album'), 
            ]), 
            ({ 'query' : 'montanita ratatat', 'category' : 'music', }, [ 
                SearchResultConstraint(title='montanita',           types='track'), 
                SearchResultConstraint(title='ratatat',             types='artist'), 
                SearchResultConstraint(title='classics',            types='album'), 
            ]), 
            ({ 'query' : 'ratatat classics montanita', 'category' : 'music', }, [ 
                SearchResultConstraint(title='montanita',           types='track'), 
                SearchResultConstraint(title='ratatat',             types='artist'), 
                SearchResultConstraint(title='classics',            types='album'), 
            ]), 
            ({ 'query' : 'starry eyed surprise bunkka', 'category' : 'music', }, [ 
                SearchResultConstraint(title='starry eyed surprise',types='track'), 
                SearchResultConstraint(title='oakenfold',           types='artist', match='contains'), 
                SearchResultConstraint(title='bunkka',              types='album'), 
            ]), 
            ({ 'query' : 'afternoon youth lagoon hibernation', 'category' : 'music', }, [ 
                SearchResultConstraint(title='afternoon',               types='track'), 
                SearchResultConstraint(title='youth lagoon',            types='artist'), 
                SearchResultConstraint(title='the year of hibernation', types='album'), 
            ]), 
            ({ 'query' : 'above & beyond bassnectar divergent spectrum', 'category' : 'music', }, [ 
                SearchResultConstraint(title='above and beyond', types='track'), 
            ]), 
            ({ 'query' : 'kanye power', 'category' : 'music', }, [ 
                SearchResultConstraint(title='power',               types='track'), 
                SearchResultConstraint(title='kanye west',          types='artist'), 
                SearchResultConstraint(title='my beautiful dark twisted fantasy', types='album', match='prefix'), 
            ]), 
            ({ 'query' : 'm83 intro', 'category' : 'music', }, [ 
                SearchResultConstraint(title='intro',               types='track'), 
                SearchResultConstraint(title='M83',                 types='artist'), 
                SearchResultConstraint(title='hurry up, we\'re dreaming', types='album', match='prefix'), 
            ]), 
        ]
        
        self._run_tests(tests, {})
    
    def test_international(self):
        """ Test international track support.  """

        tests = [
            ({ 'query' : 'katy perry part of me', 'category' : 'music', }, [ 
                SearchResultConstraint(title='part of me', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'somebody that i used to know', 'category' : 'music', }, [ 
                SearchResultConstraint(title='somebody that i used to know', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'Ai Se Eu Te Pego', 'category' : 'music', }, [ 
                SearchResultConstraint(title='Ai Se Eu Te Pego', 
                                       types='track'), 
            ]),
            # 21 is totally not a track, I have no idea what's going on here.
            #({ 'query' : '21 adele', 'category' : 'music', }, [
            #    SearchResultConstraint(title='21',
            #                           types='track'),
            #]),
            ({ 'query' : 'i follow rivers lykke li', 'category' : 'music', }, [ 
                SearchResultConstraint(title='i follow rivers',     types='track'), 
                SearchResultConstraint(title='i follow rivers',     types='album'), 
                SearchResultConstraint(title='lykke li',            types='artist'), 
            ]), 
            ({ 'query' : 'my name is stain shaka', 'category' : 'music', }, [ 
                SearchResultConstraint(title='my name is stain',    types='track'), 
                SearchResultConstraint(title='shaka ponk',          types='artist'), 
                SearchResultConstraint(title='sex, plugs and vidiot\'ape',  types='album'), 
            ]), 
            ({ 'query' : 'leider geil deichkind', 'category' : 'music', }, [ 
                SearchResultConstraint(title='leider geil',         types='track', match='prefix'), 
            ]), 
            ({ 'query' : 'rising sun exile', 'category' : 'music', }, [ 
                SearchResultConstraint(title='rising sun',          types='track'), 
                SearchResultConstraint(title='rising sun',          types='album'), 
            ]), 
            ({ 'query' : 'we belong together mariah carey', 'category' : 'music', }, [ 
                SearchResultConstraint(title='we belong together',  types='track'), 
            ]), 
        ]
        
        self._run_tests(tests, {})
    
    def test_top_tracks(self):
        """ Test the top tracks from iTunes """
        
        rss    = AppleRSS()
        tracks = rss.get_top_songs(limit=10)
        
        self.__test_tracks(tracks)
    
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
    
    def __test_tracks(self, tracks):
        tests = []
        
        for track in tracks:
            name  = track.title.lower().strip()
            name2 = utils.normalize(name, strict=True)
            
            if name.lower() != name2:
                # don't test tracks whose names contain weird unicode strings
                continue
            
            tests.append(({ 'query' : name, 'category' : 'music', }, [ 
                SearchResultConstraint(title=name, types='track', match='contains'), 
            ]))
            
            # TODO: get this working consistently (track_name artist_name) => track and artist in results
            """
            try:
                artist = track.artists[0].title
                query  = "%s %s" % (name, artist)
                
                # ensure that track_name+artist_name yields both the track and artist in results
                tests.append(({ 'query' : query, 'category' : 'music', }, [ 
                    SearchResultConstraint(title=name,   types='track',  match='contains'), 
                    SearchResultConstraint(title=artist, types='artist'), 
                ]))
            except AttributeError:
                utils.printException()
            """
        
        self._run_tests(tests, {})

if __name__ == '__main__':
    StampedTestRunner().run()

