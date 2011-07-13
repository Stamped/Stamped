#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import copy

from threading import Lock
from datetime import datetime

from MongoDB import Mongo
from AFriendshipDB import AFriendshipDB
from Friendship import Friendship
from MongoUser import MongoUser

class MongoFriendship(AFriendshipDB, Mongo):
        
    COLLECTION = 'friendships'
        
    SCHEMA = {
        '_id': basestring,
        'following_id': basestring,
        'timestamp': basestring
    }
    
    def __init__(self, setup=False):
        AFriendshipDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addFriendship(self, friendship):
        
        friendship = self._objToMongo(friendship)
        
        # Check if friendship already exists (???)
        
        # Check if blocks exist
        
        # Check if following_id is private
        if MongoUser().checkPrivacy(friendship['following_id']):
            # Request approval before creating friendship
            print 'TODO: Locked account friendship request'
            
        else:
            # Create friendship
            self._createFriendship(friendship)
            return True
        
        
#         return self._addDocument(friendship)
    
#     def getUser(self, userID):
#         user = User(self._getDocumentFromId(userID))
#         if user.isValid == False:
#             raise KeyError('User not valid')
#         return user
#         
#     def updateUser(self, user):
#         return self._updateDocument(user)
#         
#     def removeUser(self, user):
#         return self._removeDocument(user)
#     
#     def addUsers(self, users):
#         return self._addDocuments(users)


    def approveFriendship(self, friendship):
        ### TODO
        print 'TODO'


    ### PRIVATE
    
    def _objToMongo(self, obj):
        if obj.isValid == False:
            print obj
            raise KeyError('Object not valid')
        data = copy.copy(obj.getDataAsDict())
        data['_id'] = data['user_id']
        del(data['user_id'])
        return self._mapDataToSchema(data, self.SCHEMA)
        
    def _createFriendship(self, friendship):
        bucketId = self._getOverflowBucket(friendship['_id'])
        self._collection.update({'_id': friendship['_id']}, 
                                {'$addToSet': {'following_id': friendship['following_id']}})
        return True
        
    def _getOverflowBucket(self, objId):
        overflow = self._collection.find_one({'_id': objId}, fields={'overflow': 1})
        if overflow == None:
            return objId
        else:
            # Do something to manage overflow conditions?
            # Grabs the most recent bucket to use and appends that to the id. This is our new key!
            return '%s%s' % (objId, overflow['overflow'][-1])
            
            
            