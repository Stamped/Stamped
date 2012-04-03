#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint
from libs.applerss          import AppleRSS

class TrackSearchTests(ASearchTestSuite):
    
    def test_basic(self):
        """ Test basic track searches """
        
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [
            ({ 'query' : 'Simple As...', }, [ 
                SearchResultConstraint(title='simple as...', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'What\'s wrong is everyhere', }, [ 
                SearchResultConstraint(title='what\'s wrong is everyhere', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'midnight city', }, [ 
                SearchResultConstraint(title='midnight city', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'lux aeterna', }, [ 
                SearchResultConstraint(title='lux aeterna', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'mouthful of diamonds', }, [ 
                SearchResultConstraint(title='mouthful of diamonds', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'damn it feels good to be a gangsta', }, [ 
                SearchResultConstraint(title='damn it feels good to be a gangsta', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'good morning', }, [ 
                SearchResultConstraint(title='chamillionaire', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'let it (edit remix) machinedrum', }, [ 
                SearchResultConstraint(title='let it (edit remix)', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'young blood lynx', }, [ 
                SearchResultConstraint(title='young blooc', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'above & beyond bassnectar divergent spectrum', }, [ 
                SearchResultConstraint(title='above & beyond', 
                                       types='track'), 
            ]), 
        ]
    
    def test_track_album_artist_combos(self):
        """ Test track searches also containing the artist and/or album name """
        
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = [

            ({ 'query' : 'to look like you john butler trio april uprising', }, [ 
                SearchResultConstraint(title='to look like you', 
                                       types='track', 
                                       index=0), 
            ]), 
            ({ 'query' : 'john butler to look like you', }, [ 
                SearchResultConstraint(title='to look like you', 
                                       types='track', 
                                       index=0), 
            ]), 
            ({ 'query' : 'april uprising to look like you', }, [ 
                SearchResultConstraint(title='to look like you', 
                                       types='track', 
                                       index=0), 
            ]), 
            ({ 'query' : 'american music by the violent femmes', }, [ 
                SearchResultConstraint(title='american music', 
                                       types='track', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : 'parte stroke 9', }, [ 
                SearchResultConstraint(title='parte', 
                                       types='track', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : '1980 rehab graffiti the world', }, [ 
                SearchResultConstraint(title='1980', 
                                       types='track'), 
            ]), 
            ({ 'query' : '1980 rehab', }, [ 
                SearchResultConstraint(title='1980', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'graffiti the world 1980', }, [ 
                SearchResultConstraint(title='1980', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'montanita ratatat', }, [ 
                SearchResultConstraint(title='montanita', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'ratatat classics montanita', }, [ 
                SearchResultConstraint(title='montanita', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'starry eyed surprise bunkka', }, [ 
                SearchResultConstraint(title='starry eyed surprise', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'afternoon youth lagoon hibernation', }, [ 
                SearchResultConstraint(title='afternoon', 
                                       types='track'), 
            ]), 
            ({ 'query' : 'above & beyond bassnectar divergent spectrum', }, [ 
                SearchResultConstraint(title='above & beyond', 
                                       types='track'), 
            ]), 
        ]
        
        self._run_tests(tests, args)
    
    '''
    def test_international(self):
        """ Test international track support.  """
        
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
                                       types='track'), 
            ]), 
        ]
        
        self._run_tests(tests, args)
    
    def test_top_tracks(self):
        """ Test top tracks from iTunes """
        
        rss    = AppleRSS()
        tracks = rss.get_top_tracks(limit=10)
        
        self.__test_tracks(tracks)
    
    def __test_tracks(self, tracks):
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        tests = []
        
        for track in tracks:
            name = track.title
            
            tests.append(({ 'query' : name, }, [ 
                SearchResultConstraint(title=name, types='track', match='contains'), 
            ]))
        
        self._run_tests(tests, args)
        '''

if __name__ == '__main__':
    StampedTestRunner().run()

