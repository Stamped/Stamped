#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

def normalize(s):
    if isinstance(s, unicode):
        return removeNonAscii(s.encode("utf-8"))
    else:
        return s

class AObject(object):

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
    
    def __str__(self):
        return str(self._data)
    
    def __contains__(self, item):
        return item in self._data
    
    def __getattr__(self, name):
        if name == '_data':
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
        value = normalize(value)
        
        if name == '_data':
            object.__setattr__(self, name, value)
            return None
        
        return self.add({ name : value })
        
            
    def getDataAsDict(self):
#         if 'id' in self._data:
#             self._data['_id'] = self._data['id']
        return self._data
        
    def add(self, data):
        def _unionDict(source, schema, dest):
            for k, v in source.iteritems():
                if not _unionItem(k, v, schema, dest):
                    #Utils.log("item not found %s %s" % (k, v))
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
                        else:
                            isValid = False
                    except ValueError:
                        isValid = False
                    
                    if not isValid:
                        raise KeyError("Add error; key '%s' found '%s', expected '%s'" % \
                            (k, str(type(v)), str(schemaVal)))
                
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
            raise KeyError("Error %s" % str(data))
        
        return

            
    @property
    def isValid(self):
        return False
