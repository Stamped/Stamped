#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, unittest

from datetime import datetime
# from Schemas import *
from schema import *

class SimpleSchema(Schema):
    def setSchema(self):
        self.basestring         = SchemaElement(basestring)
        self.integer            = SchemaElement(int, default=100)
        self.float              = SchemaElement(float)
        self.long               = SchemaElement(long)
        self.required           = SchemaElement(basestring, required=True)
        self.bool               = SchemaElement(bool)
        self.datetime           = SchemaElement(datetime)

class InnerSchema(Schema):
    def setSchema(self):
        self.item               = SchemaElement(basestring)
        self.required           = SchemaElement(basestring, required=True)
        self.basestring         = SchemaElement(basestring)

class NestedSchema(Schema):
    def setSchema(self):
        self.basestring         = SchemaElement(basestring)
        self.inner              = InnerSchema()

class ListSchema(Schema):
    def setSchema(self):
        self.basestring         = SchemaElement(basestring)
        self.items              = SchemaList(InnerSchema())

class ListCommaSchema(Schema):
    def setSchema(self):
        self.basestring         = SchemaElement(basestring)
        self.items              = SchemaList(SchemaElement(basestring), delimiter=',')

class SparseSchema(Schema):
    def setSchema(self):
        self.basestring         = SchemaElement(basestring)
        self.empty              = SchemaElement(basestring)
        self.none               = SchemaElement(basestring)
        self.default            = SchemaElement(basestring, default='abc')

class ASchemaTestCase(unittest.TestCase):
    pass

    ### DEFAULT ASSERTIONS
    def assertIsInstance(self, a, b):
        self.assertTrue(isinstance(a, b))
        
    def assertIn(self, a, b):
        self.assertTrue((a in b) == True)

    def assertLength(self, a, size):
        self.assertTrue(len(a) == size)

    ### DEFAULT VARIABLES

    sampleString                = 'abc'
    sampleInt                   = 123
    sampleIntB                  = '123'
    sampleFloat                 = 123.45
    sampleFloatB                = '123.45'
    sampleLong                  = 2L
    sampleList                  = [1, 2, 3]
    sampleDict                  = {'a': 1, 'b': 2}
    sampleTuple                 = (1, 2, 3, 'abc')
    sampleBool                  = True
    sampleBool2                 = 'True'
    sampleBool3                 = 1
    sampleBool4                 = 1L
    sampleNone                  = None
    sampleDatetime              = datetime.utcnow()
    sampleUTF8                  = '๓๙ใ1฿'

class SimpleSchemaTest(ASchemaTestCase):

    def setUp(self):

        """
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
            self.sampleNone,
            self.sampleDatetime,
        ]
        """

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
            try:
                self.schema.float = i
                ret = False
            except:
                ret = True
            self.assertTrue(ret)

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
            try:
                self.schema.integer = i
                ret = False
            except:
                ret = True
            self.assertTrue(ret)

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
            # self.assertEqual(self.schema.basestring.value, i)

    def test_invalid_string(self):
        values = [
            self.sampleList,
            self.sampleDict,
        ]
        for i in values:
            try:
                self.schema.basestring = i
                ret = False
            except:
                ret = True
            self.assertTrue(ret)

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
            try:
                self.schema.long = i
                ret = False
            except:
                ret = True
            self.assertTrue(ret)

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
            try:
                self.schema.bool = i
                ret = False
            except:
                ret = True
            self.assertTrue(ret)

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
            try:
                self.schema.datetime = i
                ret = False
            except:
                ret = True
            self.assertTrue(ret)

    def test_required(self):
        try:
            self.schema.required = None
            ret = False
        except:
            ret = True
        self.assertTrue(ret)

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
        self.assertIsInstance(self.schema.inner.value, dict)

        self.assertEqual(self.sampleData, self.schema.value)

        self.assertEqual(
            self.sampleData['inner']['item'], 
            self.schema.exportFields(['inner.item']).values()[0])

    def test_contain_valid(self):
        self.assertIn('inner', self.schema)
        self.assertIn('item', self.schema)

    def test_contain_invalid(self):
        try:
            'basestring' in self.schema
            ret = False
        except:
            ret = True
        self.assertTrue(ret)

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
        try:
            self.schema.inner.required = None
            ret = False
        except:
            ret = True
        self.assertTrue(ret)

    def test_set_element(self):
        self.schema.setElement('schema', {'inner': {'required': self.sampleString}})
        self.assertTrue(self.schema.basestring == None)
        self.assertTrue(self.schema.inner.item == None)

    def test_import(self):
        self.schema.importData({'inner': {'required': self.sampleString}})
        self.assertTrue(self.schema.basestring != None)
        self.assertTrue(self.schema.inner.item != None)

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
            self.schema.exportSparse()['basestring']
        )
        self.assertEqual(
            self.sampleData['none'], 
            self.schema.exportSparse()['none']
        )
        self.assertEqual(
            'abc', 
            self.schema.exportSparse()['default']
        )
        self.assertTrue('empty' not in self.schema.exportSparse())

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
        self.assertIsInstance(self.schema.items.value, list)

        self.assertEqual(self.sampleData, self.schema.value)
        self.assertEqual(self.sampleData['items'], self.schema.items.value)

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

        self.assertIsInstance(self.schema.items.value, list)

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
        try:
            self.assertIn('long', self.schema)
            ret = False
        except:
            ret = True
        self.assertTrue(ret)

        try:
            self.assertIn('madeupstring', self.schema)
            ret = False
        except:
            ret = True
        self.assertTrue(ret)

if __name__ == '__main__':
    unittest.main()


"""

### Example implementation
stampData = {
    'stamp_id': '12345',
    'entity': {
        'entity_id': '567890',
        'title': 'Little Owl',
        'coordinates': {
            'lat': 123, 
            'lng': 456
        },
        'category': 'food',
        'subtitle': 'New York, NY'
    },
    'user': {
        'user_id': '432111111',
        'screen_name': 'kevin',
        'display_name': 'Kevin P.',
        'profile_image': 'http://img.stamped.com/kevin',
        'color_primary': '#dddddd',
        'color_secondary': '#333333',
        'privacy': False
    },
    'blurb': 'Best spot in the city',
    # 'image': 'MyImage.png',
    'mentions': ['robby', 'bart'],
    'credit': [
        {'user_id': '12345', 'screen_name': 'robby', 'display_name': 'Robby S.'},
        {'user_id': '23456', 'screen_name': 'bart', 'display_name': 'Bart S.'}
    ],
    'comment_preview': None,
    'timestamp': {
        'created': datetime.utcnow(),
        # 'modified': datetime.utcnow()
    },
}

print 
print 'START'

stamp = StampSchema(stampData)

print "Stamp['user']['user_id']:        %s" % stamp['user']['user_id']


stamp.stamp_id = '4321'
stamp.user.user_id = 'asdf'
stamp.entity.coordinates.lat = '123'

print "Stamp.user:                      %s" % stamp.user
print "Stamp.user.user_id:              %s" % stamp.user.user_id

print "Stamp.entity:                    %s" % stamp.entity
print "Stamp.entity.title:              %s" % stamp.entity.title
print "Stamp.entity.coordinates:        %s" % stamp.entity.coordinates
print "Stamp.entity.coordinates.lat:    %s" % stamp.entity.coordinates.lat

print "Stamp.timestamp:                 %s" % stamp.timestamp
print "Stamp.timestamp.created:         %s" % stamp.timestamp.created

del(stamp.user['color_secondary'])
del(stamp.user.color_secondary)

print "Stamp.user length:               %s" % len(stamp.user)
print "Stamp.user.user_id length:       %s" % len(stamp.user.user_id)

print
print #stamp.timestamp.modified

print stamp.exportData(format='flat')
print stamp.exportData(format='flat')['entity']
print stamp.exportData(format='flat')['entity']['coordinates']
print stamp.exportData(format='flat')['credit'][0]

#print stamp.entity.entity_id

if 'entity' in stamp:
    print 'entity: pass'
if 'eentity' not in stamp:
    print 'eentity: pass'
if 'coordinates' in stamp:
    print 'coordinates: pass'
if 'lat' in stamp:
    print 'lat: pass'

print 
print
print "Stamp.mentions:                  %s" % stamp.mentions
print "Stamp.credit:                    %s" % stamp.credit
"""

