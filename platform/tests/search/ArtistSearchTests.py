#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint
from libs.applerss          import AppleRSS

class ArtistSearchTests(ASearchTestSuite):
    
    def test_basic(self):
        """ Test basic artist searches """
        
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'nicki minaj', }, [ 
                SearchResultConstraint(title='nicki minaj', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'jay-z', }, [ 
                SearchResultConstraint(title='jay-z', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'jay z', }, [ 
                SearchResultConstraint(title='jay-z', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'passion pit', }, [ 
                SearchResultConstraint(title='passion pit', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'red hot chili peppers', }, [ 
                SearchResultConstraint(title='red hot chili peppers', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'the temper trap', }, [ 
                SearchResultConstraint(title='the temper trap', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'the glitch mob', }, [ 
                SearchResultConstraint(title='the glitch mob', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'kanye west', }, [ 
                SearchResultConstraint(title='kanye west', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'justin bieber', }, [ 
                SearchResultConstraint(title='justin bieber', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'carly rae jepsen', }, [ 
                SearchResultConstraint(title='carly rae jepsen', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'kelly clarkson', }, [ 
                SearchResultConstraint(title='kelly clarkson', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'carrie underwood', }, [ 
                SearchResultConstraint(title='carrie underwood', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'MGMT', }, [ 
                SearchResultConstraint(title='MGMT', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'rjd2', }, [ 
                SearchResultConstraint(title='rjd2', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'usher', }, [ 
                SearchResultConstraint(title='usher', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'B.o.B', }, [ 
                SearchResultConstraint(title='B.o.B', 
                                       types='artist', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : '50 cent', }, [ 
                SearchResultConstraint(title='50 cent', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'katy perry', }, [ 
                SearchResultConstraint(title='katy perry', 
                                       types='artist', 
                                       index=0), 
            ]), 
            # TODO: get this query working
            #({ 'query' : 'mozart', }, [ 
            #    SearchResultConstraint(title='mozart', 
            #                           types='artist', 
            #                           index=0), 
            #]), 
        ]
        
        self._run_tests(tests, args)
    
    def test_international(self):
        """ Test international artist support """
        
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'the beatles', }, [ 
                SearchResultConstraint(title='the beatles', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'david guetta', }, [ 
                SearchResultConstraint(title='david guetta', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'susan boyle', }, [ 
                SearchResultConstraint(title='susan boyle', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'rammstein', }, [ 
                SearchResultConstraint(title='rammstein', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'empire of the sun', }, [ 
                SearchResultConstraint(title='empire of the sun', 
                                       types='artist'), 
            ]), 
            ({ 'query' : 'deadmau5', }, [ 
                SearchResultConstraint(title='deadmau5', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : '2face idibia', }, [ 
                SearchResultConstraint(title='2face idibia', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'angelique kidjo', }, [ 
                SearchResultConstraint(title='angelique kidjo', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'gotye', }, [ 
                SearchResultConstraint(title='gotye', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'michel telo', }, [ 
                SearchResultConstraint(title='michel telo', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'stereo total', }, [ 
                SearchResultConstraint(title='stereo total', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'yelle', }, [ 
                SearchResultConstraint(title='yelle', 
                                       types='artist'), 
            ]), 
            ({ 'query' : 'stefanie heinzmann', }, [ 
                SearchResultConstraint(title='stefanie heinzmann', 
                                       types='artist'), 
            ]), 
            ({ 'query' : 'flo rida', }, [ 
                SearchResultConstraint(title='flo rida', 
                                       types='artist'), 
            ]), 
            ({ 'query' : 'olly murs', }, [ 
                SearchResultConstraint(title='olly murs', 
                                       types='artist'), 
            ]), 
        ]
        
        self._run_tests(tests, args)
    
    def test_keywords(self):
        """ Test artist searches containing other keywords (songs, albums, etc.) """
        
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'adele 21', }, [ 
                SearchResultConstraint(title='adele', 
                                       types='artist', 
                                       index=0), 
            ]), 
            ({ 'query' : 'kanye power', }, [ 
                SearchResultConstraint(title='power',               types='track'), 
                SearchResultConstraint(title='kanye west',          types='artist'), 
                SearchResultConstraint(title='my beautiful dark twisted fantasy', types='album', match='prefix'), 
            ]), 
            ({ 'query' : 'ratat party with children', }, [ 
                SearchResultConstraint(title='party with children', types='track'), 
                SearchResultConstraint(title='ratatat',             types='artist'), 
            ]), 
            ({ 'query' : 'ratatat party with children', }, [ 
                SearchResultConstraint(title='party with children', types='track'), 
                SearchResultConstraint(title='ratatat',             types='artist'), 
            ]), 
            ({ 'query' : 'flobot fight with tools handlebars', }, [ 
                SearchResultConstraint(title='handlebars',          types='track'), 
                SearchResultConstraint(title='flobots',             types='artist'), 
                SearchResultConstraint(title='fight with tools',    types='album'), 
            ]), 
        ]
        
        self._run_tests(tests, args)
    
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
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
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
            
            tests.append(({ 'query' : artist, }, [ 
                SearchResultConstraint(title=artist, types='artist'), 
            ]))
        
        self._run_tests(tests, args)

if __name__ == '__main__':
    StampedTestRunner().run()

