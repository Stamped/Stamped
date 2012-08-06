#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

"""
Tests for LRUCache.
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import functools
from libs.LRUCache import lru_cache
from tests.AStampedAPIHttpTestCase            import *

# TODO: Eliminate code duplication here -- all the usage counting shit is common to MongoCacheTests.
class UsageCounters(object):
    def __init__(self):
        self.__counts = {}

    def count(self, funcName):
        funcName = funcName.replace('.', '_')
        self.__counts[funcName] = self.__counts.get(funcName, 0) + 1

    def __getattr__(self, attrName):
        try:
            return super(UsageCounters, self).__getattr__(attrName)
        except AttributeError:
            return self.__counts.get(attrName, 0)

usageCounters = UsageCounters()

def usageCountingFunction(userFunction):
    @functools.wraps(userFunction)
    def wrappedFn(*args, **kwargs):
        usageCounters.count(userFunction.func_name)
        return userFunction(*args, **kwargs)
    return wrappedFn

@lru_cache(maxsize=2)
@usageCountingFunction
def addOneMaxTwo(x):
    return x + 1

@lru_cache()
@usageCountingFunction
def reverseArgs(*args):
    return list(reversed(args))

class LRUCacheTests(AStampedAPIHttpTestCase):
    def test_basic_caching(self):
        self.assertEqual(0, usageCounters.addOneMaxTwo)
        self.assertEqual(2, addOneMaxTwo(1))
        self.assertEqual(2, addOneMaxTwo(1))
        self.assertEqual(2, addOneMaxTwo(1))
        self.assertEqual(2, addOneMaxTwo(1))

        # That all counts as one call.
        self.assertEqual(1, usageCounters.addOneMaxTwo)
        self.assertEqual(3, addOneMaxTwo(2))
        self.assertEqual(2, addOneMaxTwo(1))
        self.assertEqual(3, addOneMaxTwo(2))

        self.assertEqual(2, usageCounters.addOneMaxTwo)
        self.assertEqual(4, addOneMaxTwo(3))
        self.assertEqual(2, addOneMaxTwo(1))

        # Once we're cycling through three elements, every attempt is a miss.
        self.assertEqual(4, usageCounters.addOneMaxTwo)
        self.assertEqual(3, addOneMaxTwo(2))
        self.assertEqual(4, addOneMaxTwo(3))
        self.assertEqual(2, addOneMaxTwo(1))

        self.assertEqual(7, usageCounters.addOneMaxTwo)

    def test_mutable_args_and_values(self):
        self.assertEqual(0, usageCounters.reverseArgs)
        self.assertEqual([1, 2, 3], reverseArgs(3, 2, 1))
        self.assertEqual([1, 2, 3], reverseArgs(3, 2, 1))
        self.assertEqual(1, usageCounters.reverseArgs)

        l = ['a', 'bc']
        s = set(['def', 'ghij'])
        self.assertEqual([l, s, 14], reverseArgs(14, s, l))
        self.assertEqual([l, s, 14], reverseArgs(14, s, l))
        self.assertEqual(2, usageCounters.reverseArgs)

        # No longer matches.
        l.append('foo')
        self.assertEqual([l, s, 14], reverseArgs(14, s, l))
        self.assertEqual(3, usageCounters.reverseArgs)

        s.add('bar')
        self.assertEqual([l, s, 14], reverseArgs(14, s, l))
        self.assertEqual(4, usageCounters.reverseArgs)

        result1 = reverseArgs(3, 2, 1)
        result2 = reverseArgs(3, 2, 1)
        self.assertTrue(result1 is not result2)

        # With a request being newly entered in the cache now.
        result1 = reverseArgs(4, 3, 2, 1)
        result2 = reverseArgs(4, 3, 2, 1)
        self.assertTrue(result1 is not result2)

        result1.append(0)
        result1.append(-1)
        self.assertEqual([1, 2, 3, 4], reverseArgs(4, 3, 2, 1))

    def test_uncopyable_values(self):
        def myGeneratorFn():
            for i in range(10):
                yield i

        myGenerator = myGeneratorFn()
        myGenerator.next()
        myGenerator.next()
        result = reverseArgs(12, myGenerator)
        self.assertEqual(2, len(result))
        self.assertEqual(12, result[1])
        generatorCopy = result[0]
        self.assertTrue(myGenerator is generatorCopy)

if __name__ == '__main__':
    _verbose = True
    main()