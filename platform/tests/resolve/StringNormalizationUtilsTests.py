#!/usr/bin/env python

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



if __name__ == '__main__':
    _verbose = True
    StampedTestRunner().run()
