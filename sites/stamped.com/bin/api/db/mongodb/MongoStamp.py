#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from api.AStampDB import AStampDB
from api.Stamp import Stamp
from MongoDB import Mongo
from MongoUserStamps import MongoUserStamps
from MongoInboxStamps import MongoInboxStamps
from MongoFriendship import MongoFriendship

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
        'timestamp': {
            'created': datetime,
            'modified': datetime
        },
        'flags': {
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
    
        ### ADDING A STAMP:
        #   - Add the stamp data to the database
        #   - Add a reference to the stamp in followers' inbox
        #   - Add a reference to the stamp in the user's collection
        #   - If stamped entity is on the to do list, mark as complete
        #   - If users are mentioned or credit is given, add stamp to their
        #     activity feed
        #   - If credit is given, add comment to credited stamp(s)
    
        stampId = self._addDocument(stamp, 'stamp_id')
        MongoUserStamps().addUserStamp(stamp['user']['user_id'], stampId)
        followerIds = MongoFriendship().getFollowers(stamp['user']['user_id'])
        MongoInboxStamps().addInboxStamps(followerIds, stampId)
        return stampId
    
    def getStamp(self, stampId):
        stamp = Stamp(self._getDocumentFromId(stampId, 'stamp_id'))
        if stamp.isValid == False:
            raise KeyError("Stamp not valid")
        return stamp
        
    def updateStamp(self, stamp):
        return self._updateDocument(stamp, 'stamp_id')
        
    def removeStamp(self, stampId, userId):
        MongoUserStamps().removeUserStamp(userId, stampId)
        ### TODO: Add removal from Inbox, etc.
        return self._removeDocument(stampId)
    
    def addStamps(self, stamps):
        stampIds = [] 
        for stampId in self._addDocuments(stamps):
            stampIds.append(self._getStringFromObjectId(stampId))
        for stamp in self.getStamps(stampIds):
            MongoUserStamps().addUserStamp(stamp['user']['user_id'], stamp['id'])
            followerIds = MongoFriendship().getFollowers(stamp['user']['user_id'])
            MongoInboxStamps().addInboxStamps(followerIds, stamp['id'])
    
    def getStamps(self, stampIds, output='object'):
        stamps = self._getDocumentsFromIds(stampIds, 'stamp_id')
        result = []
        for stamp in stamps:
            stamp = Stamp(stamp)
            if stamp.isValid == False:
                raise KeyError("Stamp not valid")
            if output == 'data' or output == 'dict':
                result.append(stamp.getDataAsDict())
            else:
                result.append(stamp)
        return result

    
    ### PRIVATE
        
