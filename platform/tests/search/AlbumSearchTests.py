#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint
from libs.applerss          import AppleRSS

class AlbumSearchTests(ASearchTestSuite):
    
    def test_basic(self):
        """ Test basic album searches """
        
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'Deep Cuts', }, [ 
                SearchResultConstraint(title='deep cuts', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'S.C.I.E.N.C.E.', }, [ 
                SearchResultConstraint(title='s.c.i.e.n.c.e.', 
                                       types='album', 
                                       index=0), 
            ]), 
            ({ 'query' : 'hail to the thief', }, [ 
                SearchResultConstraint(title='hail to the thief', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'eyelid movies', }, [ 
                SearchResultConstraint(title='eyelid movies', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'musique automatique', }, [ 
                SearchResultConstraint(title='musique automatique', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'oracular spectacular', }, [ 
                SearchResultConstraint(title='oracular spectacular', 
                                       types='album', 
                                       index=0), 
            ]), 
            ({ 'query' : 'wolfgang amadeus phoenix', }, [ 
                SearchResultConstraint(title='wolfgang amadeus phoenix', 
                                       types='album', 
                                       index=0), 
            ]), 
            ({ 'query' : 'the young machines', }, [ 
                SearchResultConstraint(title='the young machines', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'without a sound', }, [ 
                SearchResultConstraint(title='without a sound', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'viva wisconsin', }, [ 
                SearchResultConstraint(title='viva wisconsin', 
                                       types='album', 
                                       index=0), 
            ]), 
            ({ 'query' : 'play the b-sides', }, [ 
                SearchResultConstraint(title='play: the b-sides', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'astro lounge', }, [ 
                SearchResultConstraint(title='astro lounge', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'toxicity', }, [ 
                SearchResultConstraint(title='toxicity', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'enema of the state', }, [ 
                SearchResultConstraint(title='enema of the state', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'I-Empire', }, [ 
                SearchResultConstraint(title='i-empire', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'it\'s never been like that', }, [ 
                SearchResultConstraint(title='it\'s never been like that', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'it won\'t snow where you\'re going', }, [ 
                SearchResultConstraint(title='it won\'t snow where you\'re going', 
                                       types='album'), 
            ]), 
        ]
        
        self._run_tests(tests, args)
    
    def test_international(self):
        """ Test international album support.  """
        
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'Kimi Ni Saku Hana', }, [ 
                SearchResultConstraint(title='kimi ni saku hana', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'bis ans ende der welt', }, [ 
                SearchResultConstraint(title='bis ans ende der welt', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'Befehl von ganz unten album', }, [ 
                SearchResultConstraint(title='befehl von ganz unten', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'Tuskegee Lionel Richie', }, [ 
                SearchResultConstraint(title='tuskegee', 
                                       types='album', 
                                       index=0), 
            ]), 
            ({ 'query' : 'Tuskegee by Lionel Richie', }, [ 
                SearchResultConstraint(title='tuskegee', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'Sorry for Party Rocking', }, [ 
                SearchResultConstraint(title='sorry for party rocking', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'LMFAO Sorry for Party Rocking', }, [ 
                SearchResultConstraint(title='sorry for party rocking', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'Sorry for Party Rocking LMFAO', }, [ 
                SearchResultConstraint(title='sorry for party rocking', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'bangarang skrillex', }, [ 
                SearchResultConstraint(title='bangarang', 
                                       types='album'), 
            ]), 
            ({ 'query' : 'nothing but the beat david guetta', }, [ 
                SearchResultConstraint(title='nothing but the beat', 
                                       types='album'), 
            ]), 
        ]
        
        self._run_tests(tests, args)
    
    def test_top_albums(self):
        """ Test top albums from iTunes """
        
        rss    = AppleRSS()
        albums = rss.get_top_albums(limit=10)
        
        self.__test_albums(albums)
    
    def __test_albums(self, albums):
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = []
        
        for album in albums:
            name = album.title
            
            tests.append(({ 'query' : name, }, [ 
                SearchResultConstraint(title=name, types='album', match='contains'), 
            ]))
        
        self._run_tests(tests, args)

if __name__ == '__main__':
    StampedTestRunner().run()

