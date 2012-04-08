#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from StampedTestUtils       import *
from ASearchTestSuite       import ASearchTestSuite, SearchResultConstraint

class PlaceSearchTests(ASearchTestSuite):
    
    def test_basic(self):
        """ Test basic place searches """
        
        args = {
            'query'  : '', 
            'coords' : None, 
            'full'   : True, 
            'local'  : False, 
            'offset' : 0, 
            'limit'  : 10, 
        }
        
        """
        TODO:
            * target national search
            * target google places search
            * target factual
            * target opentable
            * 
        """
        
        tests = [
            ({ 'query' : 'bourbon and branch', }, [ # TODO: 'bourbon & branch' query doesn't work...
                SearchResultConstraint(title='bourbon and branch', 
                                       types='place'), 
            ]), 
            ({ 'query' : 'empire state building', 'coords' : (40.736, -73.989) }, [ 
                SearchResultConstraint(title='empire state building', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'beer bistro', 'coords' : (43.654828, -79.375191) }, [ 
                SearchResultConstraint(title='beer bistro', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'disney world', 'coords' : (28.344178, -81.575242) }, [ 
                SearchResultConstraint(title='disney world', 
                                       types='place', 
                                       index=0), 
            ]), 
            #({ 'query' : 'paddy\'s irish', 'coords' : (35.042481, -78.928133) }, [ 
            #    SearchResultConstraint(title='paddy\'s irish pub', 
            #                           types='place', 
            #                           index=0), 
            #]), 
            ({ 'query' : 'le poisson rouge', 'coords' : (40.734466, -73.990742) }, [ 
                SearchResultConstraint(title='le poisson rouge', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'kyoto japanese sushi', 'coords' : (53.606024, -113.379279) }, [ 
                SearchResultConstraint(title='kyoto japanese sushi', 
                                       types='place', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : 'el pomodoro', 'coords' : (20.727698, -103.437507) }, [ 
                SearchResultConstraint(title='pizzeria el pomodoro', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'Galata Balikcisi', 'coords' : (41.025593, 28.974618) }, [ 
                SearchResultConstraint(title='Furreyya Galata Balikcisi', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'empanada mama', 'coords' : (40.754632, -73.994261) }, [ 
                SearchResultConstraint(title='empanada mama', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'amber india', 'coords' : (37.765037, -122.412568) }, [ 
                SearchResultConstraint(title='amber india', 
                                       types='place', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : 'evo pizza', 'coords' : (37.781697, -122.392146) }, [ 
                SearchResultConstraint(title='evo pizza', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'azul tequila', 'coords' : (44.783160, -91.436092) }, [ 
                SearchResultConstraint(title='azul tequila', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'times square', 'coords' : (39.481461, -6.373380) }, [ 
                SearchResultConstraint(title='times square', 
                                       types='place'), 
            ]), 
            ({ 'query' : 'SXSW', 'coords' : (50.172962, 8.721237) }, [ 
                SearchResultConstraint(title='SXSW', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'galleria mall', 'coords' : (35.995347, -114.936936) }, [ 
                SearchResultConstraint(title='galleria mall', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'apotheke', 'coords' : (29.984821, -95.338962) }, [ 
                SearchResultConstraint(title='apotheke', 
                                       types='place'), 
            ]), 
            ({ 'query' : 'apotheke', 'coords' : (29.984821, -95.338962) }, [ 
                SearchResultConstraint(title='apotheke', 
                                       types='place'), 
            ]), 
            ({ 'query' : 'per se in nyc', 'coords' : (29.984821, -95.338962) }, [ 
                SearchResultConstraint(title='per se', 
                                       types='place', 
                                       match='prefix'), 
            ]), 
            ({ 'query' : 'australian bar', 'coords' : (50.121094, 8.673447) }, [ 
                SearchResultConstraint(title='australian bar', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'faramita', 'coords' : (25.084350, 121.556224) }, [ 
                SearchResultConstraint(title='faramita', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'highline park', }, [ 
                SearchResultConstraint(title='highline park', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'PDT', }, [ 
                SearchResultConstraint(title='pdt', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'sizzle pie pizza', 'coords' : (45.524149, -122.682825) }, [ 
                SearchResultConstraint(title='sizzle pie pizza', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'mauds cafe', 'coords' : (54.593507, -5.925185) }, [ 
                SearchResultConstraint(title='maud\'s cafe', 
                                       types='place', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : 'zoka', 'coords' : (47.622030, -122.337103) }, [ 
                SearchResultConstraint(title='zoka', 
                                       types='place', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : 'prospect sf', 'coords' : (37.806528, -122.406511) }, [ 
                SearchResultConstraint(title='prospect', 
                                       types='place', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : 'A16', 'coords' : (37.806528, -122.406511) }, [ 
                SearchResultConstraint(title='A16', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'venga empanadas', 'coords' : (37.806586,-122.406520) }, [ 
                SearchResultConstraint(title='venga empanadas', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'mordisco', 'coords' : (41.386533, 2.128773) }, [ 
                SearchResultConstraint(title='mordisco', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'veritas media', 'coords' : (41.386533, 2.128773) }, [ 
                SearchResultConstraint(title='veritas media', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'nando\'s', 'coords' : (51.478148, -3.176642) }, [ 
                SearchResultConstraint(title='nando\'s', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'enoxel', 'coords' : (-23.596847, -46.688728) }, [ 
                SearchResultConstraint(title='eNOXEL', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'la victoria', 'coords' : (35.395640, 139.567383) }, [ 
                SearchResultConstraint(title='la victoria', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'benihana', 'coords' : (35.395640, 139.567383) }, [ 
                SearchResultConstraint(title='benihana', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'sakura', 'coords' : (39.625811, -77.773603) }, [ 
                SearchResultConstraint(title='sakura', 
                                       types='place', 
                                       match='prefix', 
                                       index=0), 
            ]), 
            ({ 'query' : 'sakura japanese restaurant', 'coords' : (39.625811, -77.773603) }, [ 
                SearchResultConstraint(title='sakura japanese restaurant', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'rocket science lab', 'coords' : (18.393496, -66.006503) }, [ 
                SearchResultConstraint(title='rocket science lab', 
                                       types='place', 
                                       index=0), 
            ]), 
            ({ 'query' : 'cincinnati zoo', 'coords' : (39.149059, -84.437150) }, [ 
                SearchResultConstraint(title='cincinnati zoo', 
                                       types='place', 
                                       match='prefix', 
                                       index=0), 
            ]), 
        ]
        
        self._run_tests(tests, args, test_coords=False)

if __name__ == '__main__':
    StampedTestRunner().run()

