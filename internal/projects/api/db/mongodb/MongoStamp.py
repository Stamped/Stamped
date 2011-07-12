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
        return self._addDocument(stamp)
    
    def getStamp(self, stampID):
        stamp = Stamp(self._getDocumentFromId(stampID))
        if stamp.isValid == False:
            raise KeyError("Stamp not valid")
        return stamp
        
    def updateStamp(self, stamp):
        return self._updateDocument(stamp)
        
    def removeStamp(self, stamp):
        return self._removeDocument(stamp)
    
    def addStamps(self, stamps):
        return self._addDocuments(stamps)

    
    ### PRIVATE
        