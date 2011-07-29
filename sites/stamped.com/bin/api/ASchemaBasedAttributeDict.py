#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import copy, utils
"""
class ASchemaBasedAttributeDict(object):
    
    _schema = {}
    
    def __init__(self, d=None, schema=None):
        if d:
            super(ASchemaBasedAttributeDict, self).__setattr__("_dict", d)
        if schema:
            self._schema = schema
    
    #def __init__(self, *args, **kwargs):
    #    d = kwargs
    #    if args:
    #        d = args[0]
    #    
    #    super(ASchemaBasedAttributeDict, self).__setattr__("_dict", d)
    
    @property
    def isValid(self):
        return False
    
    def __setattr__(self, name, value):
        self[name] = value
    
    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        
        try:
            return self[name]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
    
    def __setitem__(self, name, value):
        if name == '_dict' or name == '_schema':
            return super(ASchemaBasedAttributeDict, self).__setitem__(self, name, value)
        
        if name not in self._schema:
            raise AttributeError("'%s' received unknown attribute '%s'" % (self.__class__.__name__, name))
        
        schemaVal = self._schema[name]
        
        if isinstance(schemaVal, type):
            schemaValType = schemaVal
        else:
            schemaValType = type(schemaVal)
        
        # basic type checking
        if not isinstance(value, schemaValType):
            isValid = True
            
            # basic implicit type conversion s.t. if you pass in, for example, 
            # "23.4" for longitude as a string, it'll automatically cast to 
            # the required float format.
            try:
                if schemaValType == basestring:
                    value = str(value)
                elif schemaValType == float:
                    value = float(value)
                elif schemaValType == int:
                    value = int(value)
                else:
                    isValid = False
            except ValueError:
                isValid = False
            
            if not isValid:
                raise AttributeError("Set error; key '%s' found '%s', expected '%s'" % \
                    (name, str(type(value)), str(schemaVal)))
        
        self._dict[name] = self._convert_value(value, schemaVal)
    
    def __getitem__(self, name):
        if name == '_dict' or name == '_schema':
            return super(ASchemaBasedAttributeDict, self).__getitem__(self, name)
        
        if name not in self._schema:
            raise AttributeError("'%s' received unknown attribute '%s'" % (self.__class__.__name__, name))
        
        schemaVal = self._schema[name]
        
        if name not in self._dict:
            self[name] = ASchemaBasedAttributeDict(schemaVal)
        return self._convert_value(self._dict[name], self._schema[name])
    
    def _convert_value(self, value, schema):
        if isinstance(value, dict) and not isinstance(value, ASchemaBasedAttributeDict):
            return ASchemaBasedAttributeDict(value, schema)
        
        return value
    
    def copy(self):
        return self.__class__(self._dict.copy(), copy.copy(self._schema))
    
    def update(self, *args, **kwargs):
        self._dict.update(*args, **kwargs)
    
    def items(self):
        return self._dict.items()
    
    def values(self):
        return self._dict.values()
    
    def keys(self):
        return self._dict.keys()
    
    def pop(self, *args, **kwargs):
        return self._dict.pop(*args, **kwargs)
    
    def get(self, *args, **kwargs):
        return self._dict.get(*args, **kwargs)
    
    def __repr__(self):
        return self._dict.__repr__()
    
    def __unicode__(self):
        return self._dict.__unicode__()
    
    def __str__(self):
        return self._dict.__str__()
    
    def __iter__(self):
        return self._dict.__iter__()
    
    def __getstate__(self):
        return self._dict
    
    def __setstate__(self, state):
        super(ASchemaBasedAttributeDict, self).__setattr__("_dict", state)

"""

class ASchemaBasedAttributeDict(object):
    
    _schema = {}
    
    def __init__(self, data=None):
        self._data = data or { }
    
    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self.add({key : value})
    
    def __delitem__(self, key):
        del self._data[key]
    
    def __len__(self):
        return len(self._data)
    
    def __repr__(self):
        return str(self._dict)
    
    def __str__(self):
        return str(self._dict)
    
    def __contains__(self, item):
        return item in self._data
    
    def __getattr__(self, name):
        if name == '_data' or name == '_schema':
            return object.__getattr__(self, name)
        
        def _get(dic):
            if name in dic:
                return dic[name]
            else:
                for k, v in dic.iteritems():
                    if isinstance(v, dict):
                        retVal = _get(v)
                        if retVal:
                            return retVal
            return None
        
        return _get(self._data)
    
    def __setattr__(self, name, value):
        #print "__setattr__ %s, %s" % (name, str(value))
        value = utils.normalize(value)
        
        if name == '_data' or name == '_schema':
            object.__setattr__(self, name, value)
            return None
        
        return self.add({ name : value })
    
    def getDataAsDict(self):
        return self._data
    
    def add(self, data):
        def _unionDict(source, schema, dest):
            for k, v in source.iteritems():
                if not _unionItem(k, v, schema, dest):
                    #utils.log("item not found %s %s" % (k, v))
                    return False
            
            return True
        
        def _unionItem(k, v, schema, dest):
            #print "_union %s %s %s" % (type(source), type(schema), type(dest))
            
            if k in schema:
                schemaVal = schema[k]
                
                if isinstance(schemaVal, type):
                    schemaValType = schemaVal
                else:
                    schemaValType = type(schemaVal)
                
                # basic type checking
                if not isinstance(v, schemaValType):
                    isValid = True
                    
                    # basic implicit type conversion s.t. if you pass in, for example, 
                    # "23.4" for longitude as a string, it'll automatically cast to 
                    # the required float format.
                    try:
                        if schemaValType == basestring:
                            v = str(v)
                        elif schemaValType == float:
                            v = float(v)
                        elif schemaValType == int:
                            v = int(v)
                        elif schemaValType == bool:
                            v = bool(int(v))
                        else:
                            isValid = False
                    except ValueError:
                        isValid = False
                    
                    if not isValid:
                        raise KeyError("Add error; key '%s' found '%s', expected '%s' (value %s)" % \
                            (k, str(type(v)), str(schemaVal), v))
                
                if isinstance(v, dict):
                    if k not in dest:
                        dest[k] = { }
                    
                    return _unionDict(v, schemaVal, dest[k])
                else:
                    dest[k] = v
                    return True
            else:
                for k2, v2 in schema.iteritems():
                    if isinstance(v2, dict):
                        if k2 in dest:
                            if not isinstance(dest[k2], dict):
                                raise KeyError(k2)
                            
                            if _unionItem(k, v, v2, dest[k2]):
                                return True
                        else:
                            temp = { }
                            
                            if _unionItem(k, v, v2, temp):
                                dest[k2] = temp
                                return True
            
            return False
        
        if not _unionDict(data, self._schema, self._data):
            raise KeyError("Error (%s) %s ---- %s ---- %s" % \
                           (self.__class__.__name__, data, self._schema, self._data))
        
        return
    
    @property
    def isValid(self):
        return False
    
    def __getstate__(self):
        return dict(
            data = self._data, 
            schema = self._schema
        )
    
    def __setstate__(self, state):
        self.__init__()
        self._schema = state['schema']
        self._data = state['data']

