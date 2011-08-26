#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import logging

from StampedTestUtils import *
from datetime import datetime
from schema import *

### Turn off logging
log = logging.getLogger('stamped')
log.setLevel(logging.ERROR)

### Derivative Functions

def addOne(i):
    return int(i) + 1

def setCategory(subcategory):
    subcategories = {
        'restaurant' : 'food', 
        'bar' : 'food', 
        'book' : 'book', 
        'movie' : 'film', 
        'artist' : 'music', 
        'song' : 'music', 
        'album' : 'music', 
        'app' : 'other', 
        'other' : 'other',
    }
    
    return subcategories[subcategory]

### Schemas

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

class DoubleNestedSchema(Schema):
    def setSchema(self):
        self.string             = SchemaElement(basestring)
        self.inner              = NestedSchema()

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

class DerivedSchema(Schema):
    def setSchema(self):
        self.integerA           = SchemaElement(int)
        self.integerB           = SchemaElement(int, derivedFrom='integerA', derivedFn=addOne)

class DerivedCategorySchema(Schema):
    def setSchema(self):
        self.category           = SchemaElement(basestring, derivedFrom='subcategory', derivedFn=setCategory)
        self.subcategory        = SchemaElement(basestring)

class ASchemaTestCase(AStampedTestCase):
    
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

