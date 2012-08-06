#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from tests.StampedTestUtils import *
from resolve.StringNormalizationUtils import *

class StringNormalizationUtilsTest(AStampedTestCase):
    def test_simplify(self):
        self.assertEquals(simplify('Abc (DEF)Ghi'), 'abc ghi')
        self.assertEquals(simplify('Abc (DEF)Ghi (gaer  )'), 'abc ghi')
        self.assertEquals(simplify('Bad par (enthe'), 'bad par')
        self.assertEquals(simplify('Br[ac]kets'), 'brkets')
        self.assertEquals(simplify('the beer pong table and the racket'), 'beer pong table and the racket')
        self.assertEquals(simplify('the lathe does not work'), 'lathe does not work')
        self.assertEquals(simplify('abc-def "hello"   (goodbye)'), 'abc def hello')
        self.assertEquals(simplify('this -- should : all; be, cleaned ... out'),
                          'this -- should : all; be, cleaned out')  # ...but only the ellipsis is.
        self.assertEquals(simplify('rum & coke'), 'rum and coke')
        self.assertEquals(simplify('rum&coke'), 'rum and coke')

    def test_regex_removal(self):
        patterns = (
            (re.compile('.*a(b)c.*'), 1),
            (re.compile('.*(ac).*'), 1, 'b'),
            (re.compile('(x)(bx)'), 2, 'yz')
        )
        self.assertEquals('xyz', regexRemoval('xaaaaaaaabccccccccx', patterns))

    def test_track_simplify(self):
        self.assertEquals(trackSimplify('my song (mix version)'), 'my song'),
        self.assertEquals(trackSimplify('my song -- remix'), 'my song'),
        self.assertEquals(trackSimplify('my song - unrated version'), 'my song'),
        self.assertEquals(trackSimplify('my song--radio version'), 'my song'),
        # TODO FIX: self.assertEquals(trackSimplify('my song featuring Guest Singer'), 'my song'),
        # TODO: Right now all shit we want to get rid of must be separated by a dash. Is this always what we see in
        # practice?
        self.assertEquals(trackSimplify('abc-def remix'), 'abc def remix')  # TODO IS THIS RIGHT?
        self.assertEquals(trackSimplify('stay single'), 'stay single')

    def test_album_simplify(self):
        self.assertEquals(albumSimplify('Abc EP'), 'abc')
        self.assertEquals(albumSimplify('Abc ---EP'), 'abc')
        self.assertEquals(albumSimplify('abc -- single'), 'abc')
        self.assertEquals(albumSimplify('stay single'), 'stay single')

    def test_artist_simplify(self):
        self.assertEquals(artistSimplify('John\'s Totally Awesome Band'), 'johns totally awesome')
        self.assertEquals(artistSimplify('my single -- remix'), 'my single -- remix')
        self.assertEquals(artistSimplify('Jay-Z'), 'jay z')

    def test_movie_simplify(self):
        self.assertEquals(movieSimplify('geoff the effeminate coworker'), 'geoff effeminate coworker')
        self.assertEquals(movieSimplify('-- IF y\'all INTRISTID in the LADIES'), 'if yall intristid in ladies')
        self.assertEquals(movieSimplify('i- -hate wri-ting test-- -  cases'), 'i hate wri ting test cases')

if __name__ == '__main__':
    _verbose = True
    StampedTestRunner().run()
