#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from api.AStampDB import AStampDB
from api.Stamp import Stamp
from api.Comment import Comment
from MongoDB import Mongo
from MongoUserStamps import MongoUserStamps
from MongoInboxStamps import MongoInboxStamps
from MongoFriendship import MongoFriendship
from MongoComment import MongoComment
from MongoCreditGivers import MongoCreditGivers
from MongoCreditReceived import MongoCreditReceived
from MongoUser import MongoUser
from MongoFavorite import MongoFavorite

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
            'num_comments': int,
            'num_todos': int,
            'num_credit': int
        }
    }
    
    def __init__(self, setup=False):
        AStampDB.__init__(self, self.DESC)
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
    def addStamp(self, stamp):
        
        # Connect
        _userDB = MongoUser()
        _favoriteDB = MongoFavorite()
        _creditGiversDB = MongoCreditGivers()
        _creditReceivedDB = MongoCreditReceived()
    
        # Add the stamp data to the database
        stampId = self._addDocument(stamp, 'stamp_id')      
        
        # Add a reference to the stamp in the user's collection
        MongoUserStamps().addUserStamp(stamp['user']['user_id'], stampId)  
        
        # Add a reference to the stamp in followers' inbox
        followerIds = MongoFriendship().getFollowers(stamp['user']['user_id'])
        MongoInboxStamps().addInboxStamps(followerIds, stampId)
        
        # If stamped entity is on the to do list, mark as complete
        favoriteId = _favoriteDB.getFavoriteIdForEntity(
            stamp['user']['user_id'], stamp['entity']['entity_id'])
        if favoriteId: 
            _favoriteDB.completeFavorite(favoriteId)
        
        # If users are mentioned or credited, add stamp to their activity feed
        ### TODO
        
        # Give credit
        if 'credit' in stamp and len(stamp.credit) > 0:
            for user in _userDB.lookupUsers(None, stamp.credit):
                # Add to 'credit received'
                numCredit = _creditReceivedDB.addCredit(user.user_id, stampId)
            
                # Add to 'credit givers'
                numGivers = _creditGiversDB.addGiver(user.user_id, stamp['user']['user_id'])
                
                # Increment user's total credit received
                _userDB.updateUserStats(user.user_id, 'num_credit', None, increment=1)
                
                # Update user's total credit givers 
                _userDB.updateUserStats(user.user_id, 'num_credit_givers', numGivers)
                
                # Update the number of credit on the user's stamp
                creditedStamp = Stamp(self._mongoToObj(
                    self._collection.find_one({
                        'user.user_id': user.user_id, 
                        'entity.entity_id': stamp.entity['entity_id']
                    }),
                    'stamp_id'))
                
                if 'stamp_id' in creditedStamp:                
                    self._collection.update(
                        {'_id': self._getObjectIdFromString(creditedStamp.stamp_id)}, 
                        {'$inc': {'num_credit': 1}, '$inc': {'num_comments': 1}},
                        upsert=True)
                    
                    # Add stamp as a comment on the user's stamp
                    comment = Comment()
                    comment.stamp_id = creditedStamp.stamp_id
                    comment.user = stamp.user
                    comment.restamp_id = stampId
                    if 'blurb' in stamp:
                        comment.blurb = stamp.blurb
                    if 'mentions' in stamp:
                        comment.mentions = stamp.mentions
                    comment.timestamp = stamp.timestamp
                    self.addComment(comment)
                    
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
        
    def incrementStatsForStamp(self, stampId, stat, increment=1):
        key = 'stats.%s' % (stat)
        self._collection.update({'_id': self._getObjectIdFromString(stampId)}, 
                                {'$inc': {key: increment}},
                                upsert=True)
        return True
        
    def addComment(self, comment):
        commentId = MongoComment().addComment(comment)
        self.incrementStatsForStamp(comment['stamp_id'], 'num_comments', 1)
        return commentId
        
    def getComments(self, stampId):
        return MongoComment().getComments(stampId)
    
    def removeComment(self, commentId):
        _commentDB = MongoComment()
        comment = _commentDB.getComment(commentId)
        if _commentDB.removeComment(commentId):
            numComments = _commentDB.getNumberOfComments(comment.stamp_id)
            self._collection.update(
                {'_id': self._getObjectIdFromString(comment.stamp_id)}, 
                {'$set': {'num_comments': numComments}},
                upsert=True)
            return True
        return False
    
    ### PRIVATE
        
        
    def _removeCredit(self, stampId):
        pass
        
        
    def _getCredit(self, userId):
        pass
        
