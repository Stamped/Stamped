#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from tests.StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint
from libs.applerss          import AppleRSS

class ArtistSearchTests(ASearchTestSuite):
    
    def test_basic(self):
        """ Test basic artist searches """
        tests = [
            ({ 'query' : 'nicki minaj', 'category' : 'music', }, [ 
                SearchResultConstraint(title='nicki minaj', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'jay-z', 'category' : 'music', }, [ 
                SearchResultConstraint(title='jay-z', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'jay z', 'category' : 'music', }, [ 
                SearchResultConstraint(title='jay-z', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'passion pit', 'category' : 'music', }, [ 
                SearchResultConstraint(title='passion pit', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'red hot chili peppers', 'category' : 'music', }, [ 
                SearchResultConstraint(title='red hot chili peppers', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'the temper trap', 'category' : 'music', }, [ 
                SearchResultConstraint(title='the temper trap', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'the glitch mob', 'category' : 'music', }, [ 
                SearchResultConstraint(title='the glitch mob', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'kanye west', 'category' : 'music', }, [ 
                SearchResultConstraint(title='kanye west', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'justin bieber', 'category' : 'music', }, [ 
                SearchResultConstraint(title='justin bieber', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'carly rae jepsen', 'category' : 'music', }, [ 
                SearchResultConstraint(title='carly rae jepsen', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'kelly clarkson', 'category' : 'music', }, [ 
                SearchResultConstraint(title='kelly clarkson', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'carrie underwood', 'category' : 'music', }, [ 
                SearchResultConstraint(title='carrie underwood', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'MGMT', 'category' : 'music', }, [ 
                SearchResultConstraint(title='MGMT', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'rjd2', 'category' : 'music', }, [ 
                SearchResultConstraint(title='rjd2', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'usher', 'category' : 'music', }, [ 
                SearchResultConstraint(title='usher', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'B.o.B', 'category' : 'music', }, [ 
                SearchResultConstraint(title='B.o.B', 
                                       types='artist', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : '50 cent', 'category' : 'music', }, [ 
                SearchResultConstraint(title='50 cent', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'katy perry', 'category' : 'music', }, [ 
                SearchResultConstraint(title='katy perry', 
                                       types='artist', 
                                       index=0), 
            ]), 
            # TODO: get this query working
            #({ 'query' : 'mozart', 'category' : 'music', }, [ 
            #    SearchResultConstraint(title='mozart', 
            #                           types='artist', 
            #                           index=0), 
            #]), 
        ]
        
        self._run_tests(tests, {})
    
    def test_international(self):
        """ Test international artist support """
        
        tests = [
            ({ 'query' : 'the beatles', 'category' : 'music', }, [ 
                SearchResultConstraint(title='the beatles', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'david guetta', 'category' : 'music', }, [ 
                SearchResultConstraint(title='david guetta', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'susan boyle', 'category' : 'music', }, [ 
                SearchResultConstraint(title='susan boyle', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'rammstein', 'category' : 'music', }, [ 
                SearchResultConstraint(title='rammstein', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'empire of the sun', 'category' : 'music', }, [ 
                SearchResultConstraint(title='empire of the sun', 
                                       types='artist'), 
            ]), 
            ({ 'query' : 'deadmau5', 'category' : 'music', }, [ 
                SearchResultConstraint(title='deadmau5', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : '2face idibia', 'category' : 'music', }, [ 
                SearchResultConstraint(title='2face idibia', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'angelique kidjo', 'category' : 'music', }, [ 
                SearchResultConstraint(title='angelique kidjo', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'gotye', 'category' : 'music', }, [ 
                SearchResultConstraint(title='gotye', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'michel telo', 'category' : 'music', }, [ 
                SearchResultConstraint(title='michel telo', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'stereo total', 'category' : 'music', }, [ 
                SearchResultConstraint(title='stereo total', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'yelle', 'category' : 'music', }, [ 
                SearchResultConstraint(title='yelle', 
                                       types='artist'), 
            ]), 
            ({ 'query' : 'stefanie heinzmann', 'category' : 'music', }, [ 
                SearchResultConstraint(title='stefanie heinzmann', 
                                       types='artist'), 
            ]), 
            ({ 'query' : 'flo rida', 'category' : 'music', }, [ 
                SearchResultConstraint(title='flo rida', 
                                       types='artist'), 
            ]), 
            ({ 'query' : 'olly murs', 'category' : 'music', }, [ 
                SearchResultConstraint(title='olly murs', 
                                       types='artist'), 
            ]), 
        ]
        
        self._run_tests(tests, {})
    
    def test_keywords(self):
        """ Test artist searches containing other keywords (songs, albums, etc.) """

        tests = [
            ({ 'query' : 'adele 21', 'category' : 'music', }, [ 
                SearchResultConstraint(title='adele', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'kanye power', 'category' : 'music', }, [ 
                SearchResultConstraint(title='power',               types='track'), 
                SearchResultConstraint(title='kanye west',          types='artist'), 
                SearchResultConstraint(title='my beautiful dark twisted fantasy', types='album', match='prefix'), 
            ]), 
            ({ 'query' : 'ratat party with children', 'category' : 'music', }, [ 
                SearchResultConstraint(title='party with children', types='track'), 
                SearchResultConstraint(title='ratatat',             types='artist'), 
            ]), 
            ({ 'query' : 'ratatat party with children', 'category' : 'music', }, [ 
                SearchResultConstraint(title='party with children', types='track'), 
                SearchResultConstraint(title='ratatat',             types='artist'), 
            ]), 
            ({ 'query' : 'flobot fight with tools handlebars', 'category' : 'music', }, [ 
                SearchResultConstraint(title='handlebars',          types='track'), 
                SearchResultConstraint(title='flobots',             types='artist'), 
                SearchResultConstraint(title='fight with tools',    types='album'), 
            ]), 
        ]
        
        self._run_tests(tests, {})
    
    def test_top_songs(self):
        """ Test artists from top songs from iTunes """
        
        rss  = AppleRSS()
        objs = rss.get_top_songs(limit=10)
        
        self.__test_artists(objs)
    
    def test_top_albums(self):
        """ Test artists from top albums from iTunes """
        
        rss  = AppleRSS()
        objs = rss.get_top_albums(limit=10)
        
        self.__test_artists(objs)
    
    def __test_artists(self, objs):
        tests = []
        
        for obj in objs:
            try:
                artist  = obj.artists[0].title.lower().strip()
                artist2 = utils.normalize(artist, strict=True)
                
                if artist != artist2:
                    # don't test artists whose names contain weird unicode strings
                    continue
            except Exception:
                continue
            
            tests.append(({ 'query' : artist, 'category' : 'music', }, [ 
                SearchResultConstraint(title=artist, types='artist'), 
            ]))
        
        self._run_tests(tests, {})

if __name__ == '__main__':
    StampedTestRunner().run()

