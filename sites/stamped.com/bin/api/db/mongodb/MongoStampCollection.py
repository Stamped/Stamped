#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import re

from datetime import datetime
from utils import lazyProperty

from AMongoCollection import AMongoCollection
from MongoUserStampsCollection import MongoUserStampsCollection
from MongoInboxStampsCollection import MongoInboxStampsCollection
from MongoFriendshipCollection import MongoFriendshipCollection
from MongoCommentCollection import MongoCommentCollection
from MongoCreditGiversCollection import MongoCreditGiversCollection
from MongoCreditReceivedCollection import MongoCreditReceivedCollection
from MongoUserCollection import MongoUserCollection
from MongoFavoriteCollection import MongoFavoriteCollection
from MongoActivityCollection import MongoActivityCollection

from api.AStampDB import AStampDB
from api.Stamp import Stamp
from api.Comment import Comment

class MongoStampCollection(AMongoCollection, AStampDB):
    
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
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='stamps')
        AStampDB.__init__(self)
    
    ### PUBLIC
    
    @lazyProperty
    def user_collection(self):
        return MongoUserCollection()
    
    @lazyProperty
    def favorite_collection(self):
        return MongoFavoriteCollection()
    
    @lazyProperty
    def credit_givers_collection(self):
        return MongoCreditGiversCollection()
    
    @lazyProperty
    def credit_received_collection(self):
        return MongoCreditReceivedCollection()
    
    @lazyProperty
    def activity_collection(self):
        return MongoActivityCollection()
    
    @lazyProperty
    def comment_collection(self):
        return MongoCommentCollection()
    
    @lazyProperty
    def user_stamps_collection(self):
        return MongoUserStampsCollection()
    
    @lazyProperty
    def inbox_stamps_collection(self):
        return MongoInboxStampsCollection()
    
    @lazyProperty
    def friendship_collection(self):
        return MongoFriendshipCollection()
    
    @lazyProperty
    def activity_collection(self):
        return MongoActivityCollection()
    
    def addStamp(self, stamp):
        # Extract user
        user = self.user_collection.getUser(stamp['user']['user_id'])
        
        # Extract mentions
        if 'blurb' in stamp:
            mentions = self._extractMentions(stamp['blurb'])
            if len(mentions) > 0:
                stamp['mentions'] = mentions
                
        # Extract credit
        if 'credit' in stamp:
            credit = []
            for creditedUser in self.user_collection.lookupUsers(None, stamp.credit):
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
        self.user_stamps_collection.addUserStamp(user.user_id, stampId)  
        
        # Add a reference to the stamp in followers' inbox
        followerIds = self.friendship_collection.getFollowers(stamp['user']['user_id'])
        followerIds.append(stamp['user']['user_id']) # Don't forget the user!
        self.inbox_stamps_collection.addInboxStamps(followerIds, stampId)
        
        # If stamped entity is on the to do list, mark as complete
        favoriteId = self.favorite_collection.getFavoriteIdForEntity(
            stamp['user']['user_id'], stamp['entity']['entity_id'])
        if favoriteId: 
            self.favorite_collection.completeFavorite(favoriteId)
        
        # Give credit
        userIdsForCredit = []
        if 'credit' in stamp and len(stamp.credit) > 0:
            for creditedUser in stamp.credit:
                # Add to 'credit received'
                numCredit = self.credit_received_collection.addCredit(creditedUser['user_id'], stampId)
            
                # Add to 'credit givers'
                numGivers = self.credit_givers_collection.addGiver(creditedUser['user_id'], user.user_id)
                
                # Increment user's total credit received
                self.user_collection.updateUserStats(creditedUser['user_id'], 'num_credit', None, increment=1)
                
                # Update user's total credit givers 
                self.user_collection.updateUserStats(creditedUser['user_id'], 'num_credit_givers', numGivers)
                
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
                        self.addComment(comment, activity=False)
        
        # Add activity for credited users
        if len(userIdsForCredit) > 0:
            self.activity_collection.addActivityForRestamp(userIdsForCredit, user, stamp)
        
        # Add activity for mentioned users
        if 'mentions' in stamp and len(stamp.mentions) > 0:
            userIdsForMention = []
            for mention in stamp['mentions']:
                if 'user_id' in mention and mention['user_id'] not in userIdsForCredit:
                    userIdsForMention.append(mention['user_id'])
            if len(userIdsForMention) > 0:
                self.activity_collection.addActivityForMention(userIdsForMention, user, stamp)
        
        return stampId
    
    def getStamp(self, stampId):
        stamp = Stamp(self._getDocumentFromId(stampId, 'stamp_id'))
        if stamp.isValid == False:
            raise KeyError("Stamp not valid")
        return stamp
        
    def updateStamp(self, stamp):
        return self._updateDocument(stamp, 'stamp_id')
        
    def removeStamp(self, stampId, userId):
        self.user_stamps_collection.removeUserStamp(userId, stampId)
        ### TODO: Add removal from ox, etc.
        return self._removeDocument(stampId)
    
    def addStamps(self, stamps):
        stampIds = [] 
        for stampId in self._addDocuments(stamps):
            stampIds.append(self._getStringFromObjectId(stampId))
        for stamp in self.getStamps(stampIds):
            self.user_stamps_collection.addUserStamp(stamp['user']['user_id'], stamp['id'])
            followerIds = self.friendship_collection.getFollowers(stamp['user']['user_id'])
            self.inbox_stamps_collection.addInboxStamps(followerIds, stamp['id'])
    
    def getStamps(self, stampIds, since=None, before=None, limit=20, sort='timestamp.created', withComments=False):
        # Set variables
        result = []
        comments = []
        
        # Get stamps
        stamps = self._getDocumentsFromIds(stampIds, objId='stamp_id', since=since, 
                                            before=before, sort=sort, limit=limit)
        
        # If comments are included, grab them
        if withComments:
            comments = self.comment_collection.getCommentsAcrossStamps(stampIds)
        
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
        
    def addComment(self, comment, activity=True):
        # Grab data
        user = self.user_collection.getUser(comment['user']['user_id'])
        stamp = self.getStamp(comment['stamp_id'])
        
        # Extract mentions
        if 'blurb' in comment:
            mentions = self._extractMentions(comment['blurb'])
            if len(mentions) > 0:
                comment['mentions'] = mentions
        
        # Add comment
        commentId = MongoCommentCollection().addComment(comment)
        comment['comment_id'] = commentId
        
        # Add activity for mentioned users
        if activity == True:
            userIdsForMention = []
            if 'mentions' in comment:
                for mention in comment['mentions']:
                    if 'user_id' in mention:
                        userIdsForMention.append(mention['user_id']) # mentioned users
                if len(userIdsForMention) > 0:
                    self.activity_collection.addActivityForMention(userIdsForMention, user, stamp, comment)
            
            # Add activity for commentor and for stamp owner
            userIdsForComment = []
            if comment['user']['user_id'] not in userIdsForMention:
                userIdsForComment.append(comment['user']['user_id'])
            stampOwner = self.getStamp(comment['stamp_id']).user['user_id']
            if stampOwner not in userIdsForMention:
                userIdsForComment.append(stampOwner)
            if len(userIdsForComment) > 0:
                self.activity_collection.addActivityForComment(userIdsForComment, user, stamp, comment)
            
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
                self.activity_collection.addActivityForReply(userIdsForReply, user, stamp, comment)
        
        # Increment comment count on stamp
        self.incrementStatsForStamp(comment['stamp_id'], 'num_comments', 1)
        return commentId
    
    def getComments(self, stampId):
        return self.comment_collection.getComments(stampId)
    
    def getComment(self, commentId):
        return self.comment_collection.getComment(commentId)
    
    def removeComment(self, commentId):
        comment = self.comment_collection.getComment(commentId)
        
        if self.comment_collection.removeComment(commentId):
            numComments = self.comment_collection.getNumberOfComments(comment.stamp_id)
            self._collection.update(
                {'_id': self._getObjectIdFromString(comment.stamp_id)}, 
                {'$set': {'num_comments': numComments}},
                upsert=True)
            return True
        
        return False
    
    ### PRIVATE
    
    def _extractMentions(self, text):
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
            user = self.user_collection.lookupUsers(None, data['screen_name'])
            if isinstance(user, list) and len(user) == 1:
                data['user_id'] = user_id(0)['user_id']
                data['display_name'] = user_id(0)['display_name']
            mentions.append(data)
            
        # Run through and grab mentions
        for user in user_regex.finditer(text):
            data = {}
            data['indices'] = [(user.start()+1), user.end()]
            data['screen_name'] = user.group(0)[2:]
            user = self.user_collection.lookupUsers(None, [data['screen_name']])
            if isinstance(user, list) and len(user) == 1:
                data['user_id'] = user[0]['user_id']
                data['display_name'] = user[0]['display_name']
            mentions.append(data)
        
        return mentions

