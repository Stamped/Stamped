#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from MongoDB import Mongo
from AStampDB import AStampDB
from Stamp import Stamp

class MongoStamp(AStampDB, Mongo):
        
    COLLECTION = 'stamps'
        
    SCHEMA = {
        '_id': object,
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
            'user_name': basestring,
            'user_img': basestring,
        },
        'blurb': basestring,
        'img': basestring,
        'mentions': list,
        'credit': list,
        'timestamp': basestring,
        'flags': {
            'privacy': bool,
            'flagged': bool,
            'locked': bool
        },
        'stats': {
            'total_comments': int,
            'total_todos': int,
            'total_credit': int
        }
    }
    
    def __init__(self, setup=False):
        AStampDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addStamp(self, stamp):
#         self.addStamps([stamp])
        return self._collection.insert(self._stampToBSON(stamp))
    
    def getStamp(self, stampID):
        stamp = Stamp(self._collection.find_one(stampID))
        if stamp.isValid == False:
            raise KeyError("Stamp not valid")
        return stamp
        
    def updateStamp(self, stamp):
        return self._collection.save(self._stampToBSON(stamp))
        
    def removeStamp(self, stamp):
        return self._collection.remove(self._stampToBSON(stamp))
    
    def addStamps(self, stamps):
        stampData = []
        for stamp in stamps:
            stampData.append(self._stampToBSON(stamp))
        return self._collection.insert(stampData)

    
    ### PRIVATE
    
    def _stampToBSON(self, stamp):
        if stamp.isValid == False:
            raise KeyError("Stamp not valid")
        data = stamp.getDataAsDict()
        return self._mapDataToSchema(data, self.SCHEMA)
        
    
#     def _createStampTable(self):
#         def _createTable(cursor):
#             query = """CREATE TABLE stamps (
#                     stamp_id INT NOT NULL AUTO_INCREMENT, 
#                     entity_id INT, 
#                     user_id INT, 
#                     comment VARCHAR(250), 
#                     image VARCHAR(100), 
#                     flagged INT,
#                     date_created DATETIME, 
#                     date_updated DATETIME, 
#                     PRIMARY KEY(stamp_id))"""
#             cursor.execute(query)
#             cursor.execute("CREATE INDEX ix_user ON stamps (user_id, entity_id, date_created)")
#             
#             return True
#             
#         return self._transact(_createTable)
        