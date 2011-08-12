#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import copy, os, unittest
from datetime import datetime
from Schemas import *
from schema import *


class ASchemaTestCase(unittest.TestCase):
    pass

    ### DEFAULT ASSERTIONS
    def assertIsInstance(self, a, b):
        self.assertTrue(isinstance(a, b))
        
    def assertIn(self, a, b):
        self.assertTrue((a in b) == True)

    def assertLength(self, a, size):
        self.assertTrue(len(a) == size)

    class SimpleSchema(Schema):
        def setSchema(self):
            self.basestring         = SchemaElement(basestring)
            self.integer            = SchemaElement(int)
            self.float              = SchemaElement(float)
            self.required           = SchemaElement(basestring, required=True)


    def sampleDataPoints(self):
        return [
            self.sampleString, 
            self.sampleInt, 
            self.sampleFloat, 
            self.sampleList, 
            self.sampleDict
        ]

class SimpleSchemaTest(ASchemaTestCase):

    def setUp(self):

        self.sampleString           = 'abc'
        self.sampleInt              = 123
        self.sampleFloat            = 123.45
        self.sampleList             = [1, 2, 3]
        self.sampleDict             = {'a': 1, 'b': 2}

        sampleData = {
            'basestring':   self.sampleString,
            'integer':      self.sampleInt,
            'float':        self.sampleFloat,
            'required':     self.sampleString
        }
        self.schema = self.SimpleSchema(sampleData)

    def tearDown(self):
        pass

    def test_retrieve(self):
        self.assertEqual(self.sampleString, self.schema.basestring.value)
        self.assertEqual(self.sampleInt, self.schema.integer.value)
        self.assertEqual(self.sampleFloat, self.schema.float.value)
        self.assertEqual(self.sampleString, self.schema.required.value)

        self.assertEqual(self.sampleString, self.schema['basestring'].value)
        self.assertEqual(self.sampleInt, self.schema['integer'].value)
        self.assertEqual(self.sampleFloat, self.schema['float'].value)
        self.assertEqual(self.sampleString, self.schema['required'].value)

        self.assertIsInstance(self.schema.basestring, SchemaElement)
        self.assertIsInstance(self.schema.integer, SchemaElement)
        self.assertIsInstance(self.schema.float, SchemaElement)
        self.assertIsInstance(self.schema.required, SchemaElement)

    def test_contain(self):
        self.assertIn('basestring', self.schema)
        self.assertIn('integer', self.schema)
        self.assertIn('float', self.schema)
        self.assertIn('required', self.schema)

    def test_valid_float(self):
        values = ['123', 123, '123.45', 123.45]
        for i in values:
            self.schema.float = i

    def test_invalid_float(self):
        values = ['a', ['1'], {'a': 1}]
        for i in values:
            try:
                self.schema.float = i
                ret = False
            except:
                ret = True
            self.assertTrue(ret)

    def test_valid_int(self):
        values = ['123', 123, 123.45]
        for i in values:
            self.schema.integer = i

    def test_invalid_int(self):
        values = ['a', ['1'], {'a': 1}, '123.45']
        for i in values:
            try:
                self.schema.integer = i
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

