#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import copy
from datetime import datetime

class Schema(object):
    
    def __init__(self, data=None, required=False):
        self._data = data or { }
        self.elements = {}
        self.required = required

        self.setSchema()

    def __setattr__(self, name, value):
        # value = utils.normalize(value)
        
        if name == '_data' or name == 'elements' or name == 'required':
            object.__setattr__(self, name, value)
            return None
        
        try:
            self.elements[name] = value
            return True
        except:
            raise

    def setSchema(self):
        raise NotImplementedError

    def add(self, data):
        self._data = data

    def validate(self):
        ret = {}
        data = copy.copy(self._data)
        # print 'Validating   | %s' % self
        # print 'Data         | %s' % data
        # print 'Elements     | %s' % self.elements.keys()

        for k, v in self.elements.iteritems():
            item = data.pop(k, None)
            # print 'Current run  | %s :: %s' % (k, item)

            # Value
            if isinstance(v, SchemaElement):
                v.validateElement(k, item)
            
            # Dictionary
            elif isinstance(v, Schema):
                if item == None:
                    if v.required == True:
                        msg = "Missing nested directory (%s)" % k
                        print msg
                        raise Exception(msg)
                else:
                    v.add(item)
                    v.validate()

            # List
            elif isinstance(v, SchemaList):
                ### TODO
                pass
            
            else:
                msg = "Unknown constraint in schema"
                print msg
                raise Exception(msg)

        if len(data) > 0:
            msg = "Unknown field: %s" % data
            print msg
            raise Exception(msg)

    @property
    def isValid(self):
        try:
            self.validate()
            return True
        except:
            return False


class SchemaElement(object):

    def __init__(self, requiredType, **kwargs):
        self.data = {}
        self.requiredType = requiredType
        self.required = False
        self.primary_key = False

        if 'required' in kwargs:
            self.required = kwargs['required']

    def validateElement(self, element, val=None):
        if val == None:
            if self.required == True:
                msg = "Required field empty (%s)" % element
                print msg
                raise Exception(msg)
            return
        
        if not isinstance(val, self.requiredType):
            try:
                if self.requiredType == basestring:
                    val = str(val)
                elif self.requiredType == float:
                    val = float(val)
                elif self.requiredType == int:
                    val = int(val)
                if not isinstance(val, self.requiredType):
                    msg = "Incorrect type (%s)" % element
                    print msg
                    raise KeyError(msg)
            except:
                msg = "Incorrect type (%s)" % element
                print msg
                raise KeyError(msg)
        


class EntityMiniSchema(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring, required=True)
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring, required=True)
        self.category           = SchemaElement(basestring, required=True)
        self.coordinates        = CoordinatesSchema()

class CoordinatesSchema(Schema):
    def setSchema(self):
        self.lat                = SchemaElement(float, required=True)
        self.lng                = SchemaElement(float, required=True)

class UserMiniSchema(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.display_name       = SchemaElement(basestring, required=True)
        self.profile_image      = SchemaElement(basestring, required=True)
        self.color_primary      = SchemaElement(basestring, required=True)
        self.color_secondary    = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool, required=True)

class TimestampSchema(Schema):
    def setSchema(self):
        self.created            = SchemaElement(datetime, required=True)
        self.modified           = SchemaElement(datetime)

class StampFlagsSchema(Schema):
    def setSchema(self):
        self.flagged            = SchemaElement(bool)
        self.locked             = SchemaElement(bool)

class StampStatsSchema(Schema):
    def setSchema(self):
        self.num_comments       = SchemaElement(int)
        self.num_todos          = SchemaElement(int)
        self.num_credit         = SchemaElement(int)

class StampSchema(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.entity             = EntityMiniSchema(required=True)
        self.user               = UserMiniSchema(required=True)
        self.blurb              = SchemaElement(basestring)
        self.image              = SchemaElement(basestring)
        self.mentions           = SchemaElement(list)
        self.credit             = SchemaElement(list)
        self.comment_preview    = SchemaElement(list)
        self.timestamp          = TimestampSchema(required=True)
        self.flags              = StampFlagsSchema()
        self.stats              = StampStatsSchema()




### Example implementation
stamp = {
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
        'user_id': '4321',
        'screen_name': 'kevin',
        'display_name': 'Kevin P.',
        'profile_image': 'http://img.stamped.com/kevin',
        'color_primary': '#dddddd',
        'color_secondary': '#333333',
        'privacy': False
    },
    'blurb': 'Best spot in the city',
    # 'image': 'MyImage.png',
    'mentions': ['robby'],
    'credit': ['robby'],
    'comment_preview': None,
    'timestamp': {
        'created': datetime.utcnow(),
        # 'modified': datetime.utcnow()
    },
}

Stamp = StampSchema(stamp)
print "Is valid: %s" % Stamp.isValid




### For reference
_schema = {
    'stamp_id': basestring,
    'entity': {
        'entity_id': basestring,
        'title': basestring,
        'coordinates': {
            'lat': float, 
            'lng': float
        },
        'category': basestring,
        'subtitle': basestring
    },
    'user': {
        'user_id': basestring,
        'screen_name': basestring,
        'display_name': basestring,
        'profile_image': basestring,
        'color_primary': basestring,
        'color_secondary': basestring,
        'privacy': bool
    },
    'blurb': basestring,
    'image': basestring,
    'mentions': list,
    'credit': list,
    'comment_preview': list,
    'timestamp': {
        'created': datetime,
        'modified': datetime
    },
    'flags': {
        'flagged': bool,
        'locked': bool
    },
    'stats': {
        'num_comments': int,
        'num_todos': int,
        'num_credit': int
    }
}

