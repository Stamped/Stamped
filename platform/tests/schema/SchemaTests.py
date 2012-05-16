#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from ASchemaTestCase import *

class SimpleSchemaTest(ASchemaTestCase):
    
    def setUp(self):
        self.sampleData = {
            'basestring':   self.sampleString,
            'integer':      self.sampleInt,
            'float':        self.sampleFloat,
            'required':     self.sampleString,
            'long':         self.sampleLong,
            'bool':         self.sampleBool,
            'datetime':     self.sampleDatetime,
        }
        self.schema = SimpleSchema(self.sampleData)
    
    def tearDown(self):
        pass
    
    def test_retrieve(self):
        self.assertEqual(self.sampleString, self.schema.basestring)
        self.assertEqual(self.sampleInt, self.schema.integer)
        self.assertEqual(self.sampleFloat, self.schema.float)
        self.assertEqual(self.sampleLong, self.schema.long)
        self.assertEqual(self.sampleBool, self.schema.bool)
        self.assertEqual(self.sampleDatetime, self.schema.datetime)

        self.assertEqual(self.sampleString, self.schema['basestring'])
        self.assertEqual(self.sampleInt, self.schema['integer'])
        self.assertEqual(self.sampleFloat, self.schema['float'])
        self.assertEqual(self.sampleLong, self.schema['long'])
        self.assertEqual(self.sampleBool, self.schema['bool'])
        self.assertEqual(self.sampleDatetime, self.schema['datetime'])

        self.assertIsInstance(self.schema.basestring, basestring)
        self.assertIsInstance(self.schema.integer, int)
        self.assertIsInstance(self.schema.float, float)
        self.assertIsInstance(self.schema.long, long)
        self.assertIsInstance(self.schema.bool, bool)
        self.assertIsInstance(self.schema.datetime, datetime)

    def test_contain(self):
        self.assertIn('basestring', self.schema)
        self.assertIn('integer', self.schema)
        self.assertIn('float', self.schema)
        self.assertIn('required', self.schema)
        self.assertIn('long', self.schema)
        self.assertIn('bool', self.schema)
        self.assertIn('datetime', self.schema)

    def test_valid_float(self):
        values = [
            self.sampleInt,
            self.sampleIntB,
            self.sampleFloat,
            self.sampleFloatB,
            self.sampleLong,
            self.sampleBool,
            self.sampleNone,
        ]
        for i in values:
            self.schema.float = i

    def test_invalid_float(self):
        values = [
            self.sampleString,
            self.sampleList,
            self.sampleDict,
            self.sampleTuple,
            self.sampleBool2,
            self.sampleDatetime,
        ]
        for i in values:
            with expected_exception():
                self.schema.float = i

    def test_valid_int(self):
        values = [
            self.sampleInt,
            self.sampleIntB,
            self.sampleFloat,
            self.sampleLong,
            self.sampleBool,
            self.sampleNone,
        ]
        for i in values:
            self.schema.integer = i

    def test_invalid_int(self):
        values = [
            self.sampleString,
            self.sampleFloatB,
            self.sampleList,
            self.sampleDict,
            self.sampleTuple,
            self.sampleBool2,
            self.sampleDatetime,
        ]
        for i in values:
            with expected_exception():
                self.schema.integer = i

    def test_valid_string(self):
        values = [
            self.sampleString,
            self.sampleInt,
            self.sampleIntB,
            self.sampleFloat,
            self.sampleFloatB,
            self.sampleLong,
            self.sampleBool,
            self.sampleBool2,
            self.sampleDatetime,
            self.sampleNone,
            self.sampleTuple, ## Is this expected behavior??
            self.sampleUTF8,
        ]
        for i in values:
            self.schema.basestring = i
            # self.assertEqual(self.schema.basestring, i)

    def test_invalid_string(self):
        values = [
            self.sampleList,
            self.sampleDict,
        ]
        for i in values:
            with expected_exception():
                self.schema.basestring = i

    def test_valid_long(self):
        values = [
            self.sampleLong,
            self.sampleNone,
        ]
        for i in values:
            self.schema.long = i

    def test_invalid_long(self):
        values = [
            self.sampleString,
            self.sampleInt,
            self.sampleIntB,
            self.sampleFloat,
            self.sampleFloatB,
            self.sampleList,
            self.sampleDict,
            self.sampleTuple,
            self.sampleBool,
            self.sampleBool2,
            self.sampleDatetime,
        ]
        for i in values:
            with expected_exception():
                self.schema.long = i

    def test_valid_bool(self):
        values = [
            self.sampleBool,
            self.sampleBool2,
            self.sampleBool3,
            self.sampleBool4,
            self.sampleNone,
        ]
        for i in values:
            self.schema.bool = i

    def test_invalid_bool(self):
        values = [
            self.sampleString,
            self.sampleInt,
            self.sampleIntB,
            self.sampleFloat,
            self.sampleFloatB,
            self.sampleLong,
            self.sampleList,
            self.sampleDict,
            self.sampleTuple,
            self.sampleDatetime,
        ]
        for i in values:
            with expected_exception():
                self.schema.bool = i

    def test_valid_datetime(self):
        values = [
            self.sampleDatetime,
            self.sampleNone,
        ]
        for i in values:
            self.schema.datetime = i

    def test_invalid_datetime(self):
        values = [
            self.sampleString,
            self.sampleInt,
            self.sampleIntB,
            self.sampleFloat,
            self.sampleFloatB,
            self.sampleLong,
            self.sampleList,
            self.sampleDict,
            self.sampleTuple,
            self.sampleBool,
            self.sampleBool2,
        ]
        for i in values:
            with expected_exception():
                self.schema.datetime = i

    def test_required(self):
        with expected_exception():
            self.schema.required = None

    def test_iter(self):
        for i in self.schema:
            pass

    def test_len(self):
        self.assertEqual(len(self.schema), len(self.sampleData))

    def test_del(self):
        self.assertEqual(self.schema.basestring, self.sampleString)
        del(self.schema.basestring)
        self.assertEqual(self.schema.basestring, None)
        self.assertIn('basestring', self.schema)

    def test_default(self):
        self.assertEqual(self.schema.integer, self.sampleInt)
        del(self.schema.integer)
        self.assertEqual(self.schema.integer, 100)
        self.assertIn('integer', self.schema)

class NestedSchemaTest(ASchemaTestCase):

    def setUp(self):

        self.sampleData = {
            'basestring':       self.sampleString,
            'inner': {
                'item':         self.sampleString,
                'required':     self.sampleString,
                'basestring':   self.sampleString,
            },
        }
        self.schema = NestedSchema(self.sampleData)

    def test_retrieve(self):
        self.assertEqual(self.sampleString, self.schema.basestring)
        self.assertEqual(self.sampleString, self.schema.inner.item)

        self.assertEqual(self.sampleString, self.schema['basestring'])
        self.assertEqual(self.sampleString, self.schema['inner']['item'])

        self.assertIsInstance(self.schema.basestring, basestring)
        self.assertIsInstance(self.schema.inner.item, basestring)
        self.assertIsInstance(self.schema.inner, Schema)
        self.assertIsInstance(self.schema.inner.dataExport(), dict)

        self.assertEqual(self.sampleData, self.schema.dataExport())

    def test_contain_valid(self):
        self.assertIn('inner', self.schema)
        self.assertIn('item', self.schema)

    def test_contain_invalid(self):
        with expected_exception():
            'basestring' in self.schema

    def test_iter(self):
        n = 0
        for i in self.schema:
            n += 1
        self.assertEqual(n, len(self.sampleData))
        n = 0

        for i in self.schema.inner:
            n += 1
        self.assertEqual(n, len(self.sampleData['inner']))

    def test_len(self):
        self.assertEqual(len(self.schema), len(self.sampleData))

    def test_del(self):
        self.assertEqual(self.schema.inner.item, self.sampleString)
        del(self.schema.inner.item)
        self.assertEqual(self.schema.inner.item, None)
        self.assertIn('item', self.schema)

    def test_required(self):
        with expected_exception():
            self.schema.inner.required = None

    def test_set_element(self):
        self.schema.setElement('schema', {'inner': {'required': self.sampleString}})
        self.assertTrue(self.schema.basestring == None)
        self.assertTrue(self.schema.inner.item == None)

    def test_import(self):
        self.schema.importData({'inner': {'required': self.sampleString}})
        self.assertTrue(self.schema.basestring != None)
        self.assertTrue(self.schema.inner.item != None)

    def test_path_shortcut(self):
        self.assertTrue(self.schema.required == self.sampleData['inner']['required'])

        self.schema.required = 'Required value'
        self.assertTrue(self.schema.required == 'Required value')
        self.assertTrue(self.schema.inner.required == 'Required value')
        
        self.schema.item = 'Item value'
        self.assertTrue(self.schema.item == 'Item value')
        self.assertTrue(self.schema.inner.item == 'Item value')

        self.schema.basestring = 'Outer basestring'
        self.assertTrue(self.schema.basestring == 'Outer basestring')

        self.schema.inner.basestring = 'Inner basestring'
        self.assertTrue(self.schema.inner.basestring == 'Inner basestring')

class DoubleNestedSchemaTest(ASchemaTestCase):

    def setUp(self):

        self.sampleData = {
            'string':               self.sampleString,
            'inner': {
                'basestring':       self.sampleString,
                'inner': {
                    'item':         self.sampleString,
                    'required':     self.sampleString,
                    'basestring':   self.sampleString,
                },
            },
        }
        self.schema = DoubleNestedSchema(self.sampleData)

    def test_path_shortcut(self):
        self.assertTrue(self.schema.required == \
                        self.sampleData['inner']['inner']['required'])

        self.schema.required = 'Required value'
        self.assertTrue(self.schema.required == 'Required value')
        self.assertTrue(self.schema.inner.required == 'Required value')
        self.assertTrue(self.schema.inner.inner.required == 'Required value')
        
        self.schema.item = 'Item value'
        self.assertTrue(self.schema.item == 'Item value')
        self.assertTrue(self.schema.inner.item == 'Item value')
        self.assertTrue(self.schema.inner.inner.item == 'Item value')

        self.schema.inner.basestring = 'Outer basestring'
        self.assertTrue(self.schema.inner.basestring == 'Outer basestring')

        self.schema.inner.inner.basestring = 'Inner basestring'
        self.assertTrue(self.schema.inner.inner.basestring == 'Inner basestring')
    
    def test_path_set_shortcut(self):
        test_strs = [
            "  ", 
            "", 
            "test", 
            "test\n\n", 
        ]
        
        for s in test_strs:
            self.schema.item = s
            self.assertEqual(self.schema.item, s)
        
        self.inner = {}
    
    def test_path_shortcut_fail(self):
        with expected_exception():
            self.schema.basestring = 'Set basestring'

class SparseSchemaTest(ASchemaTestCase):

    def setUp(self):

        self.sampleData = {
            'basestring':       self.sampleString,
            'none':             None,
        }
        self.schema = SparseSchema(self.sampleData)
    
    def test_sparse(self):
        self.assertEqual(
            self.sampleData['basestring'], 
            self.schema['basestring']
        )
        self.assertEqual(
            self.sampleData['none'], 
            self.schema['none']
        )
        self.assertEqual(
            'abc', 
            self.schema['default']
        )
        self.assertTrue('empty' not in self.schema.dataExport())

class ListSchemaTest(ASchemaTestCase):

    def setUp(self):

        self.sampleData = {
            'basestring':       self.sampleString,
            'items': [
                {
                    'item':         self.sampleString,
                    'required':     self.sampleString,
                    'basestring':   self.sampleString,
                },
                {
                    'item':         self.sampleString,
                    'required':     self.sampleString,
                    'basestring':   self.sampleString,
                },
            ],
        }
        self.schema = ListSchema(self.sampleData)

    def test_retrieve(self):
        self.assertEqual(self.sampleString, self.schema.basestring)
        self.assertEqual(self.sampleString, self.schema.items[0].item)

        self.assertEqual(self.sampleString, self.schema['basestring'])
        self.assertEqual(self.sampleString, self.schema.items[0].item)

        self.assertIsInstance(self.schema.basestring, basestring)
        self.assertIsInstance(self.schema.items, SchemaList)
        self.assertIsInstance(self.schema.items, list)

        self.assertEqual(self.sampleData, self.schema)
        self.assertEqual(self.sampleData['items'], self.schema.items)

    def test_contain(self):
        self.assertIn('basestring', self.schema)
        self.assertIn('items', self.schema)
        self.assertFalse('item' in self.schema) # Shouldn't look in items within a list!

    def test_iter(self):
        for i in self.schema:
            pass

        for i in self.schema.items:
            self.assertIsInstance(i, SchemaElement)

    def test_len(self):
        self.assertEqual(len(self.schema), len(self.sampleData))
        self.assertEqual(len(self.schema.items), len(self.sampleData['items']))

    def test_add(self):
        self.schema.items.append(self.sampleData['items'][0])
        self.assertEqual(len(self.schema.items), len(self.sampleData['items'])+1)

        self.schema.items.insert(0, self.sampleData['items'][0])
        self.assertEqual(len(self.schema.items), len(self.sampleData['items'])+2)

        self.schema.items.extend(self.sampleData['items'][:2])
        self.assertEqual(len(self.schema.items), len(self.sampleData['items'])+4)

    def test_del(self):
        del(self.schema.items[-1])
        self.assertEqual(len(self.schema.items), len(self.sampleData['items'])-1)
        self.assertIn('items', self.schema)

    def test_remove(self):
        self.schema.items.remove(self.schema.items[0])
        self.assertEqual(len(self.schema.items), len(self.sampleData['items'])-1)
        self.assertIn('items', self.schema)

    def test_pop(self):
        self.schema.items.pop()
        self.assertEqual(len(self.schema.items), len(self.sampleData['items'])-1)
        self.assertIn('items', self.schema)

    def test_index(self):
        self.schema.items.index(self.schema.items[0])

    def test_count(self):
        self.assertEqual(
            self.schema.items.count(self.schema.items[0]), 
            self.sampleData['items'].count(self.sampleData['items'][0])
        )

    def test_sort(self):
        self.schema.items.sort()

    def test_sort(self):
        self.schema.items.reverse()

class ListCommaSchemaTest(ASchemaTestCase):

    def setUp(self):

        self.sampleData = {
            'basestring':       self.sampleString,
            'items':            '1,2,3'
        }
        self.schema = ListCommaSchema(self.sampleData)

    def test_retrieve(self):

        self.assertIsInstance(self.schema.items, list)

        self.assertEqual(
            len(self.sampleData['items'].split(',')), 
            len(self.schema.items)
        )

class ContainsSchemaTest(ASchemaTestCase):

    def setUp(self):
        self.sampleData = {
            'basestring':   self.sampleString,
            'integer':      self.sampleInt,
            'float':        self.sampleFloat,
            'required':     self.sampleString,
        }
        self.schema = SimpleSchema(self.sampleData)

    def tearDown(self):
        pass

    def test_contain(self):
        self.assertIn('basestring', self.schema)
        self.assertIn('integer', self.schema)
        self.assertIn('float', self.schema)
        self.assertIn('required', self.schema)
        
    def test_not_set(self):
        with expected_exception():
            self.assertIn('long', self.schema)
        
        with expected_exception():
            self.assertIn('madeupstring', self.schema)

class DerivedBasicSchemaTest(ASchemaTestCase):
    def setUp(self):
        self.sampleData = {
            'integerA': 1
        }
        self.schema = DerivedSchema(self.sampleData)

    def test_retrieve(self):
        self.assertEqual(self.schema.integerB, addOne(self.sampleData['integerA']))

class DerivedCategorySchemaTest(ASchemaTestCase):
    def setUp(self):
        self.sampleData = {
            'subcategory': 'restaurant'
        }
        self.schema = DerivedCategorySchema(self.sampleData)

    def test_retrieve(self):
        self.assertEqual(self.schema.category, setCategory(self.sampleData['subcategory']))

class DerivedCategorySchemaFail(ASchemaTestCase):
    def setUp(self):
        self.sampleData = {
            'subcategory': 'something else'
        }
        
        with expected_exception():
            self.schema = DerivedCategorySchema(self.sampleData)

if __name__ == '__main__':
    StampedTestRunner().run()

