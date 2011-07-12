#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import pymongo
import bson

from AEntityDB import AEntityDB
from threading import Lock
from datetime import datetime

class Mongo():
    USER    = 'root'
    PASS    = None
    CONN    = 'ec2-50-19-194-148.compute-1.amazonaws.com'
    PORT    = 27017
    DB      = 'stamped_test'
    DESC    = 'MongoDB:%s' % (DB)
    
    def __init__(self, collection, mapping=None, setup=False, conn=CONN, port=PORT, db=DB):
        self.user = self.USER
        self._desc = self.DESC
        self._lock = Lock()
        self._mapping = mapping
        self._conn = conn
        self._port = port
        self._db = db
#         if setup:
#             self._setup()
        self._connection = self._connect()
        self._database = self._getDatabase()
        self._collection = self._getCollection(collection)
    
    def _connect(self):
        return pymongo.Connection(self._conn, self._port)
        
    def _getDatabase(self):
        return self._connection[self._db]
        
    def _getCollection(self, collection):
        return self._database[collection]
        
    def _endRequest(self):
        self._connection.end_request()
        
        
    def _encodeBSON(self, obj):
        return bson.BSON.encode(obj)
        
    def _getObjectIdAsString(self, objId):
        return pymongo.objectid.ObjectId(objId)

        
    def _mapDataToSchema(self, data, schema):
        
        def _unionDict(source, schema, dest):
            for k, v in source.iteritems():
                _unionItem(k, v, schema, dest)
            return dest
        
        def _unionItem(k, v, schema, dest):
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
                        raise KeyError("Entity error; key '%s' found '%s', expected '%s'" % \
                            (k, str(type(v)), str(schemaVal)))
                
                if isinstance(v, dict):
                    if k not in dest:
                        dest[k] = { }
                    
                    return _unionDict(v, schemaVal, dest[k])
                else:
                    dest[k] = v
                    return dest
            else:
                for k2, v2 in schema.iteritems():
                    if isinstance(v2, dict):
                        if k2 in dest:
                            if not isinstance(dest[k2], dict):
                                raise KeyError(k2)
                            
                            if _unionItem(k, v, v2, dest[k2]):
                                return dest
                        else:
                            temp = { }
                            
                            if _unionItem(k, v, v2, temp):
                                dest[k2] = temp
                                return dest
            return dest
        
        result = {}
        if not _unionDict(data, schema, result):
            raise KeyError("Error %s" % str(data))

        return result
        