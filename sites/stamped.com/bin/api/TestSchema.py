#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import copy
from datetime import datetime


class SchemaElement(object):

    def __init__(self, requiredType, **kwargs):
        self._data = None
        self._requiredType = requiredType
        self._required = kwargs.pop('required', False)
        
    def __str__(self):
        return str(self.value)

    def __len__(self):
        if self._data == None:
            return 0
        return len(self._data)

    @property
    def value(self):
        return self._data

    def validate(self, name='N/A'):
        return self.setElement(name, self._data)
        
    def setElement(self, name, value=None):
        if value == None:
            if self._required == True:
                msg = "Required field empty (%s)" % name
                print msg
                raise Exception(msg)
            self._data = value
            return
        
        if not isinstance(value, self._requiredType):
            try:
                if isinstance(value, dict):
                    msg = "Cannot set dictionary as value (%s)" % name
                    print msg
                    raise TypeError(msg)
                elif self._requiredType == basestring:
                    value = str(value)
                elif self._requiredType == float:
                    value = float(value)
                elif self._requiredType == int:
                    value = int(value)
                if not isinstance(value, self._requiredType):
                    raise
            except:
                msg = "Incorrect type (%s)" % name
                print msg
                raise KeyError(msg)
        
        self._data = value

class SchemaList(SchemaElement):
    
    def __init__(self, element, **kwargs):
        SchemaElement.__init__(self, dict, **kwargs)
        self._element = element
        self._data = []

    def __len__(self):
        return len(self._elements)

    @property
    def value(self):
        ret = []
        for item in self._data:
            ret.append(item.value)
        return ret

    def importData(self, data):
        if data == None or len(data) == 0:
            return
        if not isinstance(data, list):
            raise TypeError

        data = copy.copy(data)

        # print 'Validating   | %s' % self
        # print 'Data         | %s' % data
        # print 'Elements     | %s' % self._elements.keys()

        if not isinstance(self._element, SchemaElement):
            raise Exception("Invalid element in list")
        element = self._element

        # Dictionary
        if isinstance(element, Schema):
            for item in data:
                newSchema = copy.deepcopy(element)
                newSchema.importData(item)
                self._data.append(newSchema)

        # List
        elif isinstance(element, SchemaList):
            for item in data:
                newSchemaList = copy.deepcopy(element)
                newSchemaList.importData(item)
                self._data.append(newSchemaList)

        # Value
        elif isinstance(element, SchemaElement):
            for item in data:
                newSchemaElement = copy.deepcopy(element)
                newSchemaElement.setElement('e', item)
                self._data.append(newSchemaElement)
        
        else:
            msg = "Unrecognized element in schema"
            print msg
            raise Exception(msg)

    def validate(self):
        for item in self._data:
            if not isinstance(item, SchemaElement):
                msg = "Incorrect type (%s)" % name
                print msg
                raise TypeError(msg)
            item.validate()

class Schema(SchemaElement):
    
    def __init__(self, data=None, **kwargs):
        SchemaElement.__init__(self, dict, **kwargs)
        self._elements = {}

        self.setSchema()
        self.importData(data)

    def __setattr__(self, name, value):
        # value = utils.normalize(value)
        if name[:1] == '_':
            object.__setattr__(self, name, value)
            return None
        elif isinstance(value, SchemaElement) or isinstance(value, Schema):
            try:
                self._elements[name] = value
                return True
            except:
                raise
        else:
            try:
                # print 'Set element: (%s, %s)' % (name, value)
                self._elements[name].setElement(name, value)
                return True
            except:
                print "Error: (%s, %s)" % (name, value)
                raise
    
    def __setitem__(self, key, value):
        self.__setattr__(key, value)
    
    def __delattr__(self, key):
        self.__setattr__(key, None)
    
    def __delitem__(self, key):
        self.__setattr__(key, None)
    
    def __getattr__(self, name):
        if name[:1] == '_':
            return SchemaElement.__getattr__(self, name)
        
        if name in self._elements:
            return self._elements[name]
        
        raise KeyError(name)
        
    def __getitem__(self, key):
        return self.__getattr__(key)
    
    def __len__(self):
        return len(self._elements)

    def __contains__(self, item):
        def _contains(_item, data):
            output = 0
            if _item in data:
                output += 1
            for k, v in data.iteritems():
                if isinstance(v, Schema):
                    if _item in v:
                        output += 1
            return output
        
        if _contains(item, self._elements) == 1:
            return True
        if _contains(item, self._elements) == 0:
            return False
        raise Exception("Multiple keys!")

    @property
    def value(self):
        ret = {}
        for k, v in self._elements.iteritems():
            ret[k] = v.value
        return ret

    def validate(self):
        for k, v in self._elements.iteritems():
            
            # Dictionary
            if isinstance(v, Schema):
                if item == None:
                    if v._required == True:
                        msg = "Missing nested directory (%s)" % k
                        print msg
                        raise Exception(msg)
                else:
                    v.validate()

            # List
            elif isinstance(v, SchemaList):
                if item == None:
                    if v._required == True:
                        msg = "Missing list (%s)" % k
                        print msg
                        raise Exception(msg)
                else:
                    v.validate()

            # Value
            elif isinstance(v, SchemaElement):
                v.validate(k)
            
            else:
                msg = "Unrecognized element in schema"
                print msg
                raise Exception(msg)

    def importData(self, data):
        if data == None or len(data) == 0:
            return
        if not isinstance(data, dict):
            raise TypeError

        ret = {}
        data = copy.copy(data)

        # print 'Validating   | %s' % self
        # print 'Data         | %s' % data
        # print 'Elements     | %s' % self._elements.keys()

        for k, v in self._elements.iteritems():
            item = data.pop(k, None)
            # print 'Current run  | %s :: %s' % (k, item)
            
            # Dictionary
            if isinstance(v, Schema):
                if item == None:
                    if v._required == True:
                        msg = "Missing nested directory (%s)" % k
                        print msg
                        raise Exception(msg)
                else:
                    v.importData(item)

            # List
            elif isinstance(v, SchemaList):
                if item == None:
                    if v._required == True:
                        msg = "Missing nested list (%s)" % k
                        print msg
                        raise Exception(msg)
                else:
                    v.importData(item)

            # Value
            elif isinstance(v, SchemaElement):
                v.setElement(k, item)
            
            else:
                msg = "Unrecognized constraint in schema"
                print msg
                raise Exception(msg)

        if len(data) > 0:
            msg = "Unknown field: %s" % data
            print msg
            raise Exception(msg)

    def exportData(self, format=None):
        if str(format).lower() in ['flat', 'http']:
            return self._exportFlat()
        else:
            return self.value

    def _exportFlat(self):
        raise NotImplementedError

    def setSchema(self):
        raise NotImplementedError

    # DEPRECATED
    def getDataAsDict(self):
        return self.exportData()


class UserTinySchema(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.display_name       = SchemaElement(basestring, required=True)


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
        self.mentions           = SchemaList(SchemaElement(basestring, required=True))
        self.credit             = SchemaList(UserTinySchema())
        self.comment_preview    = SchemaElement(list)
        self.timestamp          = TimestampSchema(required=True)
        self.flags              = StampFlagsSchema()
        self.stats              = StampStatsSchema()

    def _exportFlatOld(self):
        ret = {}
        ret['stamp_id']         = self.stamp_id.value
        ret['entity']           = self.entity.value
        ret['user']             = self.user.value
        ret['blurb']            = self.blurb.value
        ret['image']            = self.image.value
        ret['mentions']         = self.mentions.value
        ret['credit']           = self.credit.value
        ret['comment_preview']  = self.comment_preview.value
        ret['created']          = self.timestamp.created.value
        ret['flags']            = self.flags.locked.value
        ret['num_comments']     = self.stats.num_comments.value

        ret['entity']['coordinates'] = '%s,%s' % (
            self.entity.coordinates.lat,
            self.entity.coordinates.lng)

        return ret

    def _exportFlat(self):
        ret = self.value

        ret['created']          = self.timestamp.created.value
        ret['flags']            = self.flags.locked.value
        ret['num_comments']     = self.stats.num_comments.value
        
        ret['entity']['coordinates'] = '%s,%s' % (
            self.entity.coordinates.lat,
            self.entity.coordinates.lng)

        del(ret['timestamp'])
        del(ret['stats'])

        return ret



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

testStamp = StampSchema(stampData)
# print 'ASDFS'
# print "Is valid: %s" % testStamp.isValid
# print

# stamp = Stamp(stampData)
# print stamp.user['display_name']
# stamp.user['screen_name'] = None
# del(stamp.entity['coordinates']['lat'])
# print stamp.entity
# print stamp.coordinates
# stamp = StampSchema()
# print 'ASDFS'
# stamp.stamp_id = '4321'
# print stampData
stamp = StampSchema(stampData)
# print 'ASDFS'
# stamp.validate()
# print stamp
#stamp.entity['title'] = 'The Little Owl'
# print stamp._elements
# print "New: ", stamp.stamp_id

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

print
print
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

