#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from tests.StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint
from libs.applerss          import AppleRSS

class AlbumSearchTests(ASearchTestSuite):
    
    def test_basic(self):
        """ Test basic album searches """
        
        tests = [
            ({ 'query' : 'Deep Cuts', 'category' : 'music', }, [ 
                SearchResultConstraint(title='deep cuts', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'S.C.I.E.N.C.E.', 'category' : 'music', }, [ 
                SearchResultConstraint(title='s.c.i.e.n.c.e.', 
                                       types='album', 
                                       index=0), 
            ]), 
            ({ 'query' : 'hail to the thief', 'category' : 'music', }, [ 
                SearchResultConstraint(title='hail to the thief', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'eyelid movies', 'category' : 'music', }, [ 
                SearchResultConstraint(title='eyelid movies', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'musique automatique', 'category' : 'music', }, [ 
                SearchResultConstraint(title='musique automatique', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'oracular spectacular', 'category' : 'music', }, [ 
                SearchResultConstraint(title='oracular spectacular', 
                                       types='album', 
                                       index=0), 
            ]), 
            ({ 'query' : 'wolfgang amadeus phoenix', 'category' : 'music', }, [ 
                SearchResultConstraint(title='wolfgang amadeus phoenix', 
                                       types='album', 
                                       index=0), 
            ]),
            ({ 'query' : '21 adele', 'category' : 'music', }, [
                SearchResultConstraint(title='21',
                                       types='album',
                                       index=0),
            ]),
            ({ 'query' : 'the young machines', 'category' : 'music', }, [
                SearchResultConstraint(title='the young machines', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'without a sound', 'category' : 'music', }, [ 
                SearchResultConstraint(title='without a sound', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'viva wisconsin', 'category' : 'music', }, [ 
                SearchResultConstraint(title='viva wisconsin', 
                                       types='album', 
                                       index=0), 
            ]), 
            ({ 'query' : 'play the b-sides', 'category' : 'music', }, [ 
                SearchResultConstraint(title='play: the b-sides', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'astro lounge', 'category' : 'music', }, [ 
                SearchResultConstraint(title='astro lounge', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'toxicity', 'category' : 'music', }, [ 
                SearchResultConstraint(title='toxicity', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'enema of the state', 'category' : 'music', }, [ 
                SearchResultConstraint(title='enema of the state', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'I-Empire', 'category' : 'music', }, [ 
                SearchResultConstraint(title='i-empire', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'it\'s never been like that', 'category' : 'music', }, [ 
                SearchResultConstraint(title='it\'s never been like that', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'it won\'t snow where you\'re going', 'category' : 'music', }, [ 
                SearchResultConstraint(title='it won\'t snow where you\'re going', 
                                       types='album'), 
            ]), 
        ]
        
        self._run_tests(tests, {})
    
    def test_international(self):
        """ Test international album support.  """

        tests = [
            ({ 'query' : 'Kimi Ni Saku Hana', 'category' : 'music', }, [ 
                SearchResultConstraint(title='kimi ni saku hana', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'bis ans ende der welt', 'category' : 'music', }, [ 
                SearchResultConstraint(title='bis ans ende der welt', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'Befehl von ganz unten album', 'category' : 'music', }, [ 
                SearchResultConstraint(title='befehl von ganz unten', 
                                       types='album', 
                                       match='prefix'), 
            ]), 
            ({ 'query' : 'Tuskegee Lionel Richie', 'category' : 'music', }, [ 
                SearchResultConstraint(title='tuskegee', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'Tuskegee by Lionel Richie', 'category' : 'music', }, [ 
                SearchResultConstraint(title='tuskegee', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'Sorry for Party Rocking', 'category' : 'music', }, [ 
                SearchResultConstraint(title='sorry for party rocking', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'LMFAO Sorry for Party Rocking', 'category' : 'music', }, [ 
                SearchResultConstraint(title='sorry for party rocking', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'Sorry for Party Rocking LMFAO', 'category' : 'music', }, [ 
                SearchResultConstraint(title='sorry for party rocking', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'bangarang skrillex', 'category' : 'music', }, [ 
                SearchResultConstraint(title='bangarang', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'nothing but the beat david guetta', 'category' : 'music', }, [ 
                SearchResultConstraint(title='nothing but the beat', 
                                       types='album'), 
            ]), 
        ]
        
        self._run_tests(tests, {})
    
    def test_top_albums(self):
        """ Test top albums from iTunes """
        
        rss    = AppleRSS()
        albums = rss.get_top_albums(limit=10)
        
        self.__test_albums(albums)
    
    def __test_albums(self, albums):

        tests = []
        
        for album in albums:
            name  = album.title.lower().strip()
            name2 = utils.normalize(name, strict=True)
            
            # don't test albums whose names contain weird unicode strings
            if name != name2:
                continue
            
            tests.append(({ 'query' : name, 'category' : 'music', }, [ 
                SearchResultConstraint(title=name, types='album', match='contains'), 
            ]))
        
        self._run_tests(tests, {})

if __name__ == '__main__':
    StampedTestRunner().run()

