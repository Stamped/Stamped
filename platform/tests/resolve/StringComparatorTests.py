#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from tests.StampedTestUtils import *
from resolve.StringComparator import StringComparator

class StringComparatorTests(AStampedTestCase):
    def test_basic(self):
        self.assertAlmostEqual(3, StringComparator.get_difference('abc', ''))
        self.assertAlmostEqual(4, StringComparator.get_difference('ab', 'cd'))
        self.assertAlmostEqual(1, StringComparator.get_difference('abcdef', 'abdef'))
        self.assertAlmostEqual(1, StringComparator.get_difference('abdef', 'abcdef'))
        self.assertAlmostEqual(2, StringComparator.get_difference('abcdef', 'abcd'))
        self.assertAlmostEqual(3, StringComparator.get_difference('abcdef', 'abd'))
        self.assertAlmostEqual(2, StringComparator.get_difference('abcd', 'abcdef'))
        self.assertAlmostEqual(3, StringComparator.get_difference('abd', 'abcdef'))

    def test_punctuation_is_cheap(self):
        self.assertAlmostEqual(0.4, StringComparator.get_difference('abc.', ' abc'))
        self.assertAlmostEqual(0.6, StringComparator.get_difference('a.b-c?', 'abc'))
        self.assertAlmostEqual(0.5, StringComparator.get_difference('a-b-c', 'a.b c'))

    def test_skip_words(self):
        self.assertAlmostEqual(0.6 * len('fandango'), StringComparator.get_difference('the fandango end', 'the end'))
        self.assertAlmostEqual(0.6 * len('fucking'), StringComparator.get_difference('blah fucking blah', 'blah blah'))
        self.assertAlmostEqual(0.6 * len('defghi') + 0.4,
            StringComparator.get_difference('abc   def ghi   jkl', 'abc jkl'))

    def test_skip_prefixes(self):
        self.assertAlmostEqual(0.5 * len('fantastic '),
            StringComparator.get_difference('fantastic mr fox', 'mr fox'))
        self.assertAlmostEqual(0.4 * 0.8, StringComparator.get_difference('the job', 'job'))
        self.assertAlmostEqual(0.4 * len('abc def : '), StringComparator.get_difference('abc def : ghi jkl', 'ghi jkl'))
        # One word penalty and one prefix penalty.
        self.assertAlmostEqual(0.5 * len('abcdef ') + 0.6 * len('ghij'),
            StringComparator.get_difference('abcdef powerrangers', 'ghij powerrangers'))

    def test_skip_suffixes(self):
        self.assertAlmostEqual(0.4 * len(': a fucking awesome novel'),
            StringComparator.get_difference('freedom', 'freedom: a fucking awesome novel'))
        self.assertAlmostEqual(0.5 * len(' fucking awesome novel'),
            StringComparator.get_difference('freedom', 'freedom fucking awesome novel'))

if __name__ == '__main__':
    _verbose = True
    StampedTestRunner().run()