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
        self._isSet = False
        self._requiredType = self._validateRequiredType(requiredType)
        self._required = kwargs.pop('required', False)
        self._default = kwargs.pop('default', None)
        self._case = kwargs.pop('case', None)
        if self._default != None:
            self.setElement('N/A', self._default)
        
    def __str__(self):
        return str(self.value)

    def __len__(self):
        if self._data == None:
            return 0
        return len(self._data)

    @property
    def value(self):
        return self._data

    @property
    def isSet(self):
        return self._isSet

    def _validateRequiredType(self, requiredType):
        validTypes = [
            basestring,
            bool,
            int,
            long,
            float,
            dict,
            list,
            datetime,
        ]
        if requiredType in validTypes:
            return requiredType
        raise TypeError("Invalid type requested")

    def validate(self, name='N/A'):
        if self._data == None and self._required == True:
            msg = "Required field empty (%s)" % name
            print msg
            raise Exception(msg)

        if self._data != None and not isinstance(self._data, self._requiredType):
            msg = "Incorrect type (%s)" % name
            print msg
            raise KeyError(msg)
        
    def setElement(self, name, value):

        def _checkType(value):
            if value != None and not isinstance(value, self._requiredType):
                try:
                    if isinstance(value, dict):
                        msg = "Cannot set dictionary as value (%s)" % name
                        print msg
                        raise TypeError(msg)
                    elif isinstance(value, list):
                        msg = "Cannot set list as value (%s)" % name
                        print msg
                        raise TypeError(msg)
                    elif self._requiredType == bool:
                        b = str(value).lower()
                        if b == 'true' or b == '1':
                            value = True
                        elif b == 'false' or b == '0':
                            value = False
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
            return value

        if value == None and self._default != None:
            value = self._default
            
        self._data = _checkType(value)
        self._isSet = True
        self.validate(name=name)

class SchemaList(SchemaElement):
    
    def __init__(self, element, **kwargs):
        SchemaElement.__init__(self, dict, **kwargs)
        self._element = element
        self._data = []
        self._delimiter = kwargs.pop('delimiter', None)

    def __len__(self):
        return len(self._data)
    
    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, item):
        self._data[key] = self._import(item)
        self.validate()
    
    def __delitem__(self, key):
        del(self._data[key])
        self.validate()

    def _import(self, item):
        element = self._element
        if isinstance(item, SchemaElement):
            return item
        elif isinstance(element, Schema) or isinstance(element, SchemaList):
            newSchemaItem = copy.deepcopy(element)
            newSchemaItem.importData(item)
            return newSchemaItem

        elif isinstance(element, SchemaElement):
            newSchemaElement = copy.deepcopy(element)
            newSchemaElement.setElement('e', item)
            return newSchemaElement

        else:
            msg = "Cannot set item (invalid element)"
            print msg
            raise Exception(msg)

    # List functions

    def append(self, item):
        self._data.append(self._import(item))

    def insert(self, position, item):
        self._data.insert(position, self._import(item))

    def extend(self, items):
        data = []
        for item in items:
            data.append(self._import(item))
        self._data.extend(data)

    def remove(self, item):
        return self._data.remove(self._import(item))
    
    def pop(self, i=-1):
        return self._data.pop(i).value

    def index(self, item):
        if isinstance(item, SchemaElement):
            item = item.value
        return self.value.index(item)

    def count(self, item):
        if isinstance(item, SchemaElement):
            item = item.value
        return self.value.count(item)

    def sort(self):
        self._data.sort()
    
    def reverse(self):
        self._data.reverse()

    @property
    def value(self):
        ret = []
        for item in self._data:
            ret.append(item.value)
        return ret

    def importData(self, data):
        self._data = []
        if data == None or len(data) == 0:
            return
        if self._delimiter != None and isinstance(data, basestring):
            data = data.split(self._delimiter)
        if not isinstance(data, list):
            raise TypeError

        data = copy.copy(data)

        if not isinstance(self._element, SchemaElement):
            raise Exception("Invalid element in list")
        element = self._element

        for item in data:
            self.append(item)

    def validate(self, name='SchemaList'):
        if len(self._data) == 0 and self._required == True:
            msg = "Missing list (%s)" % name
            print msg
            raise Exception(msg)
        for item in self._data:
            if not isinstance(item, SchemaElement):
                msg = "Incorrect type in list (%s)" % item
                print msg
                raise TypeError(msg)
            item.validate()

    def setElement(self, name, value):
        if value == None:
            self._data = []
            return
        self.importData(value)

class Schema(SchemaElement):
    
    def __init__(self, data=None, **kwargs):
        SchemaElement.__init__(self, dict, **kwargs)
        self._elements = {}
        self._discardExcess = kwargs.pop('discardExcess', False)

        self.setSchema()
        self.importData(data)

    def __setattr__(self, name, value):
        # value = utils.normalize(value)
        if name[:1] == '_':
            object.__setattr__(self, name, value)
            return None
        elif isinstance(value, SchemaElement):
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
            if isinstance(self._elements[name], Schema) \
            or isinstance(self._elements[name], SchemaList):
                return self._elements[name]
            return self._elements[name].value
        
        raise KeyError(name)
        
    def __getitem__(self, key):
        return self.__getattr__(key)
    
    def __len__(self):
        return len(self._elements)

    def __iter__(self):
        return self.value.__iter__()

    def __contains__(self, item):
        ### TODO: Only if isSet?
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

    def validate(self, name='Schema'):
        if len(self._elements) == 0 and self._required == True:
            msg = "Required Schema is missing (%s)" % name
            print msg
            raise Exception(msg)

        for k, v in self._elements.iteritems():
            
            if isinstance(v, SchemaElement):
                v.validate(k)
            
            else:
                msg = "Unrecognized element in schema (%s)" % name
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
            item = None
            isSet = False
            if k in data:
                item = data.pop(k)
                isSet = True
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
                if isSet:
                    v.setElement(k, item)
                else:
                    v.validate()
            
            else:
                msg = "Unrecognized constraint in schema"
                print msg
                raise Exception(msg)

        if len(data) > 0 and self._discardExcess == False:
            msg = "Unknown field: %s" % data
            print msg
            raise Exception(msg)

    def removeElement(self, key):
        del(self._elements[key])

    def exportData(self, format=None):
        if str(format).lower() in ['flat', 'http']:
            return self._exportFlat()
        else:
            return self.value

    def exportFields(self, fields):
        ret = {}
        for field in fields:
            result = self
            path = field.split('.')
            for level in path:
                result = result[level]
            if isinstance(result, Schema) or isinstance(result, SchemaList):
                ret[field] = result.value
            else:
                ret[field] = result
        return ret

    def exportSparse(self):
        ret = {}
        for k, v in self._elements.iteritems():
            if isinstance(v, Schema):
                data = v.exportSparse()
                if len(data) > 0:
                    ret[k] = data
            elif isinstance(v, SchemaList):
                if len(v) > 0:
                    ret[k] = v.value
            elif isinstance(v, SchemaElement):
                if v.isSet == True:
                    ret[k] = v.value
            else:
                raise Exception("Unknown type")
        return ret
    def _exportFlat(self):
        raise NotImplementedError

    def setSchema(self):
        raise NotImplementedError

    # DEPRECATED
    def getDataAsDict(self):
        return self.exportData()

