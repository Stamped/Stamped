#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for MongoCache.
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import datetime
import functools
import time
from logs import log, report

from AStampedAPIHttpTestCase            import *
from libs.MongoCache                    import mongoCachedFn, SerializationError
from schema                             import Schema
from api.db.mongodb.AMongoCollection    import MongoDBConfig

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

def usageCountingFunction(className=None):
    def decoratorFn(userFunction):
        funcName = userFunction.func_name
        if className is not None:
            funcName = '%s.%s' % (className, funcName)
        # At the very beginning we clear out any prior cached results for this function so that we're starting the test
        # from a clean state.
        MongoDBConfig.getInstance().connection.stamped.cache.remove({'func_name':funcName})

        @functools.wraps(userFunction)
        def wrappedFn(*args, **kwargs):
            usageCounters.count(funcName)
            return userFunction(*args, **kwargs)
        return wrappedFn
    return decoratorFn

@mongoCachedFn(memberFn=False)
@usageCountingFunction()
def sumThree(x, y, z):
    return x+x+x+y+y+z

@mongoCachedFn(memberFn=False)
@usageCountingFunction()
def sumContainers(x, y, z):
    return (4*sum(x)) + (3*sum(y.keys())) + (2*sum(y.values())) + (1*sum(z))

@mongoCachedFn(maxStaleness=datetime.timedelta(0, 1), memberFn=False)
@usageCountingFunction()
def sumSquares(l):
    return sum([x*x for x in l])

@mongoCachedFn(memberFn=False)
@usageCountingFunction()
def sumSeveralWithKwargs(a=0, b=0, c=0, d=[]):
    return a + (b*b) + (c*c*c) + sum(d)

@mongoCachedFn(memberFn=False)
@usageCountingFunction()
def specialSum(a, b, c):
    return a + b + c

class DummyClass1(object):
    @mongoCachedFn()
    @usageCountingFunction(className='DummyClass1')
    def specialSum(self, a, b, c):
        return a - b + c

class DummyClass2(object):
    @mongoCachedFn()
    @usageCountingFunction(className='DummyClass2')
    def specialSum(self, a, b, c):
        return a + b - c

@mongoCachedFn(memberFn=False)
def randomTestFn(*args, **kwargs):
    return (args, kwargs)

@mongoCachedFn(memberFn=False)
@usageCountingFunction()
def sumValues(**kwargs):
    return sum(kwargs.values())

@mongoCachedFn(memberFn=False)
@usageCountingFunction()
def returnTheArguments(*args):
    return args

class MongoCacheHttpTest(AStampedAPIHttpTestCase):
    def test_basic_calls(self):
        self.assertEqual(0, usageCounters.sumThree)
        self.assertEqual(6, sumThree(1,1,1))
        self.assertEqual(10, sumThree(1,2,3))
        self.assertEqual(2, usageCounters.sumThree)
        self.assertEqual(6, sumThree(1,1,1))
        self.assertEqual(10, sumThree(1,2,3))
        self.assertEqual(2, usageCounters.sumThree)

    def test_calls_with_containers(self):
        self.assertEqual(0, usageCounters.sumContainers)
        result = sumContainers([1,2,3], {4:5, 6:7}, (8, 9))
        expected = ((1+2+3)*4) + ((4+6)*3) + ((5+7)*2) + ((8+9)*1)
        self.assertEqual(result, expected)
        result = sumContainers([1,2,3], {4:5, 6:7}, (8, 9))
        self.assertEqual(result, expected)
        result = sumContainers([], {}, (1, 2,))
        result = sumContainers([], {}, (1, 2,))
        result = sumContainers([], {}, (1, 2,))
        expected = 3
        self.assertEqual(result, expected)
        self.assertEqual(2, usageCounters.sumContainers)

    def test_collisions_and_expiring_results(self):
        self.assertEqual(sumSquares([2, 3, 4]), 4+9+16)
        self.assertEqual(sumSquares((2,3,4)), 4+9+16)
        self.assertEqual(1, usageCounters.sumSquares)
        # Cache expires in this time, because I set a maxStaleness of 1 second.
        time.sleep(1.5)
        self.assertEqual(sumSquares([2, 3, 4]), 4+9+16)
        self.assertEqual(2, usageCounters.sumSquares)

    def test_with_kwargs(self):
        self.assertEqual(sumSeveralWithKwargs(1, 2, 3), 1+4+27)
        self.assertEqual(sumSeveralWithKwargs(c=3,b=2,a=1), 1+4+27)
        self.assertEqual(sumSeveralWithKwargs(1, c=3, b=2), 1+4+27)
        # The arguments are the same, but distributed differently amongst args and kwargs.
        self.assertEqual(3, usageCounters.sumSeveralWithKwargs)

        self.assertEqual(sumSeveralWithKwargs(c=3,b=2,a=1), 1+4+27)
        self.assertEqual(sumSeveralWithKwargs(c=3,b=2,a=1), 1+4+27)
        self.assertEqual(sumSeveralWithKwargs(1, 2, 3), 1+4+27)
        self.assertEqual(3, usageCounters.sumSeveralWithKwargs)

        self.assertEqual(sumSeveralWithKwargs(12, d=[1, 2, 3]), 18)
        self.assertEqual(sumSeveralWithKwargs(12, d=[1, 2, 3]), 18)
        self.assertEqual(4, usageCounters.sumSeveralWithKwargs)

    def test_with_member_functions(self):
        dummy1 = DummyClass1()
        dummy1Sibling = DummyClass1()
        # dummy1 and its sibling are different. See? They have a different x and everything.
        dummy1.x = 12
        dummy1Sibling.x = 13

        dummy2 = DummyClass2()

        # Dummy 1 and its sibling should hit the same cache. In spite of the different x.
        self.assertEqual(dummy1.specialSum(1, 20, 300), 1-20+300)
        self.assertEqual(dummy1Sibling.specialSum(1, 20, 300), 1-20+300)
        self.assertEqual(1, usageCounters.DummyClass1_specialSum)

        # Dummy 2 should hit a different cache key.
        self.assertEqual(dummy2.specialSum(1, 20, 300), 1+20-300)
        self.assertEqual(1, usageCounters.DummyClass1_specialSum)
        self.assertEqual(1, usageCounters.DummyClass2_specialSum)

        # Make sure nothing has changed.
        self.assertEqual(dummy1.specialSum(1, 20, 300), 1-20+300)
        self.assertEqual(1, usageCounters.DummyClass1_specialSum)
        self.assertEqual(1, usageCounters.DummyClass2_specialSum)
        self.assertEqual(dummy1.specialSum(2, 30, 400), 2-30+400)
        self.assertEqual(2, usageCounters.DummyClass1_specialSum)
        self.assertEqual(1, usageCounters.DummyClass2_specialSum)

        # This should hit yet a third cache key.
        self.assertEqual(specialSum(1, 20, 300), 1+20+300)
        self.assertEqual(2, usageCounters.DummyClass1_specialSum)
        self.assertEqual(1, usageCounters.DummyClass2_specialSum)
        self.assertEqual(1, usageCounters.specialSum)

    def test_with_complicated_values(self):
        arg1 = {'1': [2, set([3, 'four'])], '5':None}
        arg2 = ('a', 'b', (12, 'DEE', {'five':6}))
        result1 = returnTheArguments(arg1, arg2)
        result2 = returnTheArguments(arg1, arg2)
        self.assertEqual(1, usageCounters.returnTheArguments)
        self.assertTrue(len(result1) == 2)
        self.assertTrue(result1[0] is arg1)
        self.assertTrue(result1[1] is arg2)
        self.assertTrue(len(result2) == 2)
        self.assertTrue(result2[0] is not arg1)
        self.assertTrue(result2[1] is not arg2)

        arg1v2 = result2[0]
        arg2v2 = result2[1]

        self.assertTrue(isinstance(arg1v2, dict))
        self.assertEqual(len(arg1v2), 2)
        self.assertTrue('1' in arg1v2)
        self.assertTrue('5' in arg1v2)
        self.assertTrue(arg1v2['5'] is None)
        self.assertTrue(isinstance(arg1v2['1'], list))
        self.assertEqual(len(arg1v2['1']), 2)
        self.assertEqual(arg1v2['1'][0], 2)
        self.assertTrue(isinstance(arg1v2['1'][1], set))
        self.assertEqual(len(arg1v2['1'][1]), 2)
        self.assertTrue(3 in arg1v2['1'][1])
        self.assertTrue('four' in arg1v2['1'][1])

        self.assertTrue(isinstance(arg2v2, tuple))
        self.assertEqual(len(arg2v2), 3)
        self.assertEqual('a', arg2v2[0])
        self.assertEqual('b', arg2v2[1])
        self.assertTrue(isinstance(arg2v2[2], tuple))
        self.assertEqual(3, len(arg2v2[2]))
        self.assertEqual(12, arg2v2[2][0])
        self.assertEqual('DEE', arg2v2[2][1])
        self.assertTrue(isinstance(arg2v2[2][2], dict))
        self.assertEqual(len(arg2v2[2][2]), 1)
        self.assertEqual(arg2v2[2][2]['five'], 6)

    def test_with_schema_values(self):
        class MySimpleSchema(Schema):
            @classmethod
            def setSchema(cls):
                cls.addProperty('name', basestring)
                cls.addProperty('favorite_director', basestring)
                cls.addProperty('randnum', float)
                cls.addProperty('missing_property', basestring)

        schemaElement = MySimpleSchema()
        schemaElement.name = 'Mike'
        schemaElement.favorite_director = 'Joss Whedon'  # Totally.
        schemaElement.randnum = 0.137

        @mongoCachedFn(memberFn=False, schemaClasses=(MySimpleSchema,))
        @usageCountingFunction()
        def returnMySchemaElement():
            return schemaElement

        self.assertEqual(0, usageCounters.returnMySchemaElement)
        result1 = returnMySchemaElement()
        self.assertEqual(1, usageCounters.returnMySchemaElement)
        result2 = returnMySchemaElement()
        self.assertEqual(1, usageCounters.returnMySchemaElement)

        self.assertTrue(result1 is schemaElement)
        self.assertTrue(result2 is not schemaElement)
        self.assertTrue(isinstance(result2, MySimpleSchema))
        self.assertEqual(result2.name, 'Mike')
        self.assertEqual(result2.favorite_director, 'Joss Whedon')
        self.assertEqual(result2.randnum, 0.137)
        self.assertEqual(result2.missing_property, None)

    def test_with_nested_schema_values(self):
        class InnerSchema(Schema):
            @classmethod
            def setSchema(cls):
                cls.addProperty('name', basestring)
                cls.addProperty('num', int)

        class OuterSchema(Schema):
            @classmethod
            def setSchema(cls):
                cls.addProperty('name', basestring)
                cls.addNestedProperty('inner1', InnerSchema)
                cls.addNestedProperty('inner2', InnerSchema)

            def __init__(self):
                Schema.__init__(self)
                self.inner1 = InnerSchema()
                self.inner2 = InnerSchema()

        schemaElement = OuterSchema()
        schemaElement.name = 'outer'
        schemaElement.inner1.name = 'inner1'
        schemaElement.inner2.num = 2

        @mongoCachedFn(memberFn=False, schemaClasses=(OuterSchema,))
        @usageCountingFunction()
        def returnMyNestedSchemaElement():
            return schemaElement

        self.assertEqual(0, usageCounters.returnMyNestedSchemaElement)
        result1 = returnMyNestedSchemaElement()
        self.assertEqual(1, usageCounters.returnMyNestedSchemaElement)
        result2 = returnMyNestedSchemaElement()
        self.assertEqual(1, usageCounters.returnMyNestedSchemaElement)

        self.assertTrue(result1 is schemaElement)
        self.assertTrue(result2 is not schemaElement)
        self.assertEqual(result2.name, 'outer')
        self.assertEqual(result2.inner1.name, 'inner1')
        self.assertEqual(result2.inner1.num, None)
        self.assertEqual(result2.inner2.name, None)
        self.assertEqual(result2.inner2.num, 2)

    def expect_failure(self, *args, **kwargs):
        testFn = kwargs.pop('testFn', randomTestFn)
        try:
            testFn(*args, **kwargs)
        except SerializationError:
            pass # expected
        else:
            self.assertFalse("Expected SerializationError with args: (%s), kwargs: (%s)" % (str(args), str(kwargs)))

    def test_with_failures(self):
        # Dict keys must be strings.
        self.expect_failure({1:2})
        self.expect_failure(('a', 'b', 2.345, {'x':'y', (1, 2):27.4}))

        class Foo(object):
            pass

        foo = Foo()
        foo.x = 12
        self.expect_failure(foo)
        self.expect_failure(1, "a", x=foo)

        class MySimplerSchema(Schema):
            @classmethod
            def setSchema(cls):
                cls.addProperty('name', basestring)

        mySchemaElement = MySimplerSchema()
        mySchemaElement.name = 'foo'

        @mongoCachedFn(memberFn=False)
        def failToReturnSchemaElementsWithoutPassingToDecorator():
            return mySchemaElement

        self.expect_failure(testFn=failToReturnSchemaElementsWithoutPassingToDecorator)


def test_force_recalculate(self):
        self.assertEqual(12, sumValues(x=4, y=3, z=5))
        self.assertEqual(12, sumValues(x=4, z=5, y=3))
        self.assertEqual(12, sumValues(z=5, y=3, x=4))
        self.assertEqual(1, usageCounters.sumValues)

        self.assertEqual(12, sumValues(x=4, y=3, z=5, force_recalculate=True))
        self.assertEqual(2, usageCounters.sumValues)

if __name__ == '__main__':
    _verbose = True
    main()

