#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from tests.StampedTestUtils       import *
from resolve.Resolver       import *

# TODO: add books, movies, apps, places, etc.

class SimplifyTests(AStampedTestCase):
    
    def test_simplify(self):
        """ tests resolver's generic simplification of strings """
        
        tests = [
            ("Deep... into the Night", "deep into the night"), 
            ("the\r\none and only", "one and only"), 
            ("trailer park boys (the movie)", "trailer park boys"), 
            ("trailer park boys [the movie]", "trailer park boys"), 
            ("trailer park boys (the movie", "trailer park boys"), 
            ("\"testing \" 1'2'3", "testing 123"), 
            ("Duck & Go", "duck and go"), 
            ("Duck&Go", "duck and go"), 
        ]
        
        for key, value in tests:
            value2 = simplify(key)
            self.assertEqual(value, value2)
    
    def test_track_simplify(self):
        """ tests resolver's simplification of track names """
        
        tests = [
            ("My Guitar Wants To Kill Your Mama", "my guitar wants to kill your mama"), 
            ("What's New, Peepeecat?", "whats new, peepeecat?"), 
            ("Hungry like the wolf", "hungry like the wolf"), 
            ("Born in the U.S.A. - Single", "born in the u.s.a."), 
            ("artsy - remix", "artsy"), 
            ("artsy - remix", "artsy"), 
            ("fireworks (explicit version)", "fireworks"), 
            ("Fireworks [Explicit Version]", "fireworks"), 
            ("10 to 1 - cover", "10 to 1"), 
            ("you are you and i am i - karaoke version", "you are you and i am i"), 
            ("the reeling - remix", "reeling"), 
            ("fly like an eagle - tribute", "fly like an eagle"), 
            ("die die die (deluxe version)", "die die die"), 
            ("the pixies first to die", "first to die", "the pixies"), 
            ("blue man group deep blue song", "deep blue song", "blue man group"), 
        ]
        
        for test in tests:
            artist = None
            
            if len(test) == 3:
                key, value, artist = test
            else:
                key, value = test
            
            value2 = trackSimplify(key, artist)
            self.assertEqual(value, value2)
    
    def test_album_simplify(self):
        """ tests resolver's simplification of album names """
        
        tests = [
            ("Peso - Single", "peso"), 
            ("Shh... Don't Tell", "shh dont tell"), 
            ("Inception (Music from the Motion Picture)", "inception"), 
            ("Dance Party 2011 (Remix)", "dance party 2011"), 
            ("Skukuza - EP", "skukuza"), 
            ("Magnolia [Original Soundtrack]", "magnolia"), 
            ("Soundtrack - Good Will Hunting", "soundtrack - good will hunting"), 
            ("Armando (Deluxe Version)", "armando"), 
            ("Armando (Single)", "armando"), 
            ("Armando (Explicit Version)", "armando"), 
        ]
        
        for key, value in tests:
            value2 = albumSimplify(key)
            self.assertEqual(value, value2)
    
    def test_artist_simplify(self):
        """ tests resolver's simplification of artist names """
        
        tests = [
            ("Passion Pit", "passion pit"), 
            ("The Temper Trap", "temper trap"), 
            ("Greg Wilkinson Band", "greg wilkinson"), 
            ("M83", "m83"), 
            ("A$AP Rocky", "a$ap rocky"), 
        ]
        
        for key, value in tests:
            value2 = artistSimplify(key)
            self.assertEqual(value, value2)

if __name__ == '__main__':
    StampedTestRunner().run()

