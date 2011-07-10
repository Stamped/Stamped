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
        
        
        
        
           
    
#     def _commit(self):
#         if self.db:
#             self.db.commit()
#             self.db.close()
#             self.db = None
#     
#     def _setup(self):
#         def _createDB(cursor):
#             cursor.execute('DROP DATABASE IF EXISTS %s' % self.DB)
#             cursor.execute('CREATE DATABASE %s' % self.DB)
#             return True
#         
#         self.db = mysqldb.connect(user=self.USER)
#         self._transact(_createDB)
#         
#         self.db = self._getConnection()
#     
#     """ Requires mapping of object attributes to SQL column names """
# 
#     def _mapObjToSQL(self, obj):
#         result = {}
#         for mapping in self._mapping:
#             if mapping[0] in obj:
#                 result[mapping[1]] = self._encode(obj[mapping[0]])
#             else:
#                 result[mapping[1]] = None
#         return result
#     
#     def _mapSQLToObj(self, data, obj):
#         for mapping in self._mapping:
#             if mapping[1] in data:
#                 obj[mapping[0]] = self._decode(data[mapping[1]])
#             else:
#                 obj[mapping[0]] = None
#         return obj
#     
#     def _encode(self, attr):
#         return attr
#     
#     def _decode(self, attr):
#         if type(attr) == str:
#             return attr.replace("\\n", "\n").replace("\\", "")
#         else:
#             return attr
#             
#     def _transact(self, func, returnDict=False):
#         retVal = None
#         
#         self._lock.acquire()
#         try:
#             if self.db is None:
#                 self.db = self._getConnection()
#             
#             if returnDict:
#                 cursor = self.db.cursor(cursorclass=mysqldb.cursors.DictCursor)
#             else:
#                 cursor = self.db.cursor()
#             
#             retVal = func(cursor)
#             if retVal is not None and (type(retVal) is not bool or retVal == True):
#                 self._commit()
#             else:
#                 self.db.rollback()
#             
#             cursor.close()
#         finally:
#             self._lock.release()
#         
#         return retVal
        