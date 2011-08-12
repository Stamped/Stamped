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
            ret[k] = str(v)
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

