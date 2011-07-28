#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import re
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
from MongoActivity import MongoActivity

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
        'comment_preview': list,
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
        _activityDB = MongoActivity()
        
        # Extract user
        user = _userDB.getUser(stamp['user']['user_id'])
        
        # Extract mentions
        if 'blurb' in stamp:
            mentions = self._extractMentions(stamp['blurb'])
            if len(mentions) > 0:
                stamp['mentions'] = mentions
                
        # Extract credit
        if 'credit' in stamp:
            credit = []
            for creditedUser in _userDB.lookupUsers(None, stamp.credit):
                data = {}
                data['user_id'] = creditedUser['user_id']
                data['screen_name'] = creditedUser['screen_name']
                data['display_name'] = creditedUser['display_name']
                #data['profile_image'] = creditedUser['profile_image']
                #data['color_primary'] = creditedUser['color_primary']
                #if 'color_secondary' in creditedUser:
                #    data['color_secondary'] = creditedUser['color_secondary']
                #data['privacy'] = creditedUser['privacy']
                
                credit.append(data)
            stamp.credit = credit
            
        # Add the stamp data to the database
        stampId = self._addDocument(stamp, 'stamp_id')
        stamp['stamp_id'] = stampId
        
        # Add a reference to the stamp in the user's collection
        MongoUserStamps().addUserStamp(user.user_id, stampId)  
        
        # Add a reference to the stamp in followers' inbox
        followerIds = MongoFriendship().getFollowers(stamp['user']['user_id'])
        followerIds.append(stamp['user']['user_id']) # Don't forget the user!
        MongoInboxStamps().addInboxStamps(followerIds, stampId)
        
        # If stamped entity is on the to do list, mark as complete
        favoriteId = _favoriteDB.getFavoriteIdForEntity(
            stamp['user']['user_id'], stamp['entity']['entity_id'])
        if favoriteId: 
            _favoriteDB.completeFavorite(favoriteId)
        
        # Give credit
        userIdsForCredit = []
        if 'credit' in stamp and len(stamp.credit) > 0:
            for creditedUser in stamp.credit:

                # Add to 'credit received'
                numCredit = _creditReceivedDB.addCredit(creditedUser['user_id'], stampId)
            
                # Add to 'credit givers'
                numGivers = _creditGiversDB.addGiver(creditedUser['user_id'], user.user_id)
                
                # Increment user's total credit received
                _userDB.updateUserStats(creditedUser['user_id'], 'num_credit', None, increment=1)
                
                # Update user's total credit givers 
                _userDB.updateUserStats(creditedUser['user_id'], 'num_credit_givers', numGivers)
                
                # Append user id for activity
                userIdsForCredit.append(creditedUser['user_id'])
                
                # Update the amount of credit on the user's stamp
                creditedStamp = self._collection.find_one({
                        'user.user_id': creditedUser['user_id'], 
                        'entity.entity_id': stamp.entity['entity_id']
                    })
                if creditedStamp:                
                    creditedStamp = Stamp(self._mongoToObj(creditedStamp, 'stamp_id'))
                
                    if 'stamp_id' in creditedStamp and creditedStamp.stamp_id != None:    
                        # Just in case the credited user hasn't stamped it yet...            
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
        
        # Add activity for credited users
        if len(userIdsForCredit) > 0:
            _activityDB.addActivityForRestamp(userIdsForCredit, user, stamp)
        
        # Add activity for mentioned users
        if 'mentions' in stamp and len(stamp.mentions) > 0:
            userIdsForMention = []
            for mention in stamp['mentions']:
                if 'user_id' in mention and mention['user_id'] not in userIdsForCredit:
                    userIdsForMention.append(mention['user_id'])
            if len(userIdsForMention) > 0:
                _activityDB.addActivityForMention(userIdsForMention, user, stamp)
                    
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
        ### TODO: Add removal from ox, etc.
        return self._removeDocument(stampId)
    
    def addStamps(self, stamps):
        stampIds = [] 
        for stampId in self._addDocuments(stamps):
            stampIds.append(self._getStringFromObjectId(stampId))
        for stamp in self.getStamps(stampIds):
            MongoUserStamps().addUserStamp(stamp['user']['user_id'], stamp['id'])
            followerIds = MongoFriendship().getFollowers(stamp['user']['user_id'])
            MongoInboxStamps().addInboxStamps(followerIds, stamp['id'])
    
    def getStamps(self, stampIds, since=None, before=None, limit=20, sort='timestamp.created', withComments=False):
        # Set variables
        result = []
        comments = []
        
        # Get stamps
        stamps = self._getDocumentsFromIds(stampIds, objId='stamp_id', since=since, 
                                            before=before, sort=sort, limit=limit)
        
        # If comments are included, grab them
        if withComments:
            comments = MongoComment().getCommentsAcrossStamps(stampIds)
        
        # Build stamp object for each result
        for stamp in stamps:
            stamp = Stamp(stamp)
            stamp.comment_preview = []
            for comment in comments:
                if comment.stamp_id == stamp.stamp_id:
                    stamp.comment_preview.append(comment)
            if stamp.isValid == False:
                raise KeyError("Stamp not valid")
            result.append(stamp)
            
        return result
        
    def incrementStatsForStamp(self, stampId, stat, increment=1):
        key = 'stats.%s' % (stat)
        self._collection.update({'_id': self._getObjectIdFromString(stampId)}, 
                                {'$inc': {key: increment}},
                                upsert=True)
        return True
        
    def addComment(self, comment):
        
        # Connect
        _activityDB = MongoActivity()
    
        # Grab data
        user = MongoUser().getUser(comment['user']['user_id'])
        stamp = self.getStamp(comment['stamp_id'])
        
        # Extract mentions
        if 'blurb' in comment:
            mentions = self._extractMentions(comment['blurb'])
            if len(mentions) > 0:
                comment['mentions'] = mentions
        
        # Add comment
        commentId = MongoComment().addComment(comment)
        comment['comment_id'] = commentId
        
        # Add activity for mentioned users
        userIdsForMention = []
        if 'mentions' in comment:
            for mention in comment['mentions']:
                if 'user_id' in mention:
                    userIdsForMention.append(mention['user_id']) # mentioned users
            if len(userIdsForMention) > 0:
                _activityDB.addActivityForMention(userIdsForMention, user, stamp, comment)
        
        # Add activity for commentor and for stamp owner
        userIdsForComment = []
        if comment['user']['user_id'] not in userIdsForMention:
            userIdsForComment.append(comment['user']['user_id'])
        stampOwner = self.getStamp(comment['stamp_id']).user['user_id']
        if stampOwner not in userIdsForMention:
            userIdsForComment.append(stampOwner)
        if len(userIdsForComment) > 0:
            _activityDB.addActivityForComment(userIdsForComment, user, stamp, comment)
                    
        # Add activity for previous commenters
        userIdsForReply = []
        ### TODO: Limit this to the last 20 comments or so...
        for prevComment in self.getComments(comment['stamp_id']):
            userIdsForReply.append(prevComment['user']['user_id']) # prev comments
        recipientDict = {}
        for e in userIdsForReply:
            if e not in userIdsForComment and e not in userIdsForMention:
                recipientDict[e] = 1
        userIdsForReply = recipientDict.keys()
        if len(userIdsForReply) > 0:
            _activityDB.addActivityForReply(userIdsForReply, user, stamp, comment)
        
        # Increment comment count on stamp
        self.incrementStatsForStamp(comment['stamp_id'], 'num_comments', 1)
        return commentId
        
    def getComments(self, stampId):
        return MongoComment().getComments(stampId)
        
    def getComment(self, commentId):
        return MongoComment().getComment(commentId)
    
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
    
    def _extractMentions(self, text):
        
        # Connect
        _userDB = MongoUser()
        
        # Define patterns
        user_regex = re.compile(r'([^a-zA-Z0-9_])@([a-zA-Z0-9+_]{1,20})', re.IGNORECASE)
        reply_regex = re.compile(r'@([a-zA-Z0-9+_]{1,20})', re.IGNORECASE)
        
        mentions = [] 
        
        # Check if string match exists at beginning. Should combine with regex 
        # below once I figure out how :)
        reply = reply_regex.match(text)
        if reply:
            data = {}
            data['indices'] = [(reply.start()), reply.end()]
            data['screen_name'] = reply.group(0)[1:]
            user = _userDB.lookupUsers(None, data['screen_name'])
            if isinstance(user, list) and len(user) == 1:
                data['user_id'] = user_id(0)['user_id']
                data['display_name'] = user_id(0)['display_name']
            mentions.append(data)
            
        # Run through and grab mentions
        for user in user_regex.finditer(text):
            data = {}
            data['indices'] = [(user.start()+1), user.end()]
            data['screen_name'] = user.group(0)[2:]
            user = _userDB.lookupUsers(None, [data['screen_name']])
            if isinstance(user, list) and len(user) == 1:
                data['user_id'] = user[0]['user_id']
                data['display_name'] = user[0]['display_name']
            mentions.append(data)
        
        return mentions
        
        
    def _removeCredit(self, stampId):
        pass
        
        
    def _getCredit(self, userId):
        pass
        
