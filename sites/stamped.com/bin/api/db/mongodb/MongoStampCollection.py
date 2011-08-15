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
    
    def _convertToMongo(self, stamp):
        document = stamp.exportSparse()
        if 'stamp_id' in document:
            document['_id'] = self._getObjectIdFromString(document['stamp_id'])
            del(document['stamp_id'])
        return document

    def _convertFromMongo(self, document):
        if '_id' in document:
            document['stamp_id'] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
        return Stamp(document)
    
    ### PUBLIC
    
    @lazyProperty
    def user_stamps_collection(self):
        return MongoUserStampsCollection()
    
    @lazyProperty
    def inbox_stamps_collection(self):
        return MongoInboxStampsCollection()
    
    @lazyProperty
    def credit_givers_collection(self):
        return MongoCreditGiversCollection()
    
    @lazyProperty
    def credit_received_collection(self):
        return MongoCreditReceivedCollection()

    
    def addStamp(self, stamp):
        # Add the stamp data to the database
        document = self._convertToMongo(stamp)
        document = self._addMongoDocument(document)
        stamp = self._convertFromMongo(document)

        return stamp
    
    def getStamp(self, stampId):
        documentId = self._getObjectIdFromString(stampId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)
    
    def updateStamp(self, stamp):
        document = self._convertToMongo(stamp)
        document = self._updateMongoDocument(document)
        return self._convertFromMongo(document)
    
    def removeStamp(self, stampId):
        documentId = self._getObjectIdFromString(stampId)
        return self._removeMongoDocument(documentId)
        
    def addUserStampReference(self, userId, stampId):
        # Add a reference to the stamp in the user's collection
        self.user_stamps_collection.addUserStamp(userId, stampId) 
        
    def removeUserStampReference(self, userId, stampId):
        # Remove a reference to the stamp in the user's collection
        self.user_stamps_collection.removeUserStamp(userId, stampId) 

    def addInboxStampReference(self, userIds, stampId):
        # Add a reference to the stamp in followers' inbox
        self.inbox_stamps_collection.addInboxStamps(userIds, stampId)

    def removeInboxStampReference(self, userIds, stampId):
        # Remove a reference to the stamp in followers' inbox
        self.inbox_stamps_collection.removeInboxStamps(userIds, stampId)


    def giveCredit(self, creditedUserId, stamp):
        # Add to 'credit received'
        ### TODO: Does this belong here?
        self.credit_received_collection.addCredit(creditedUserId, stamp.stamp_id)
    
        # Add to 'credit givers'
        ### TODO: Does this belong here?
        self.credit_givers_collection.addGiver(creditedUserId, stamp.user.user_id)

        # Update the amount of credit on the user's stamp
        try:
            creditedStamp = self._collection.find_one({
                'user.user_id': creditedUserId, 
                'entity.entity_id': stamp.entity.entity_id,
            })
        except:
            creditedStamp = None

        return creditedStamp


    @lazyProperty
    def user_collection(self):
        return MongoUserCollection()
    
    @lazyProperty
    def favorite_collection(self):
        return MongoFavoriteCollection()
    
    @lazyProperty
    def activity_collection(self):
        return MongoActivityCollection()
    
    @lazyProperty
    def comment_collection(self):
        return MongoCommentCollection()
    
    @lazyProperty
    def friendship_collection(self):
        return MongoFriendshipCollection()
    
    @lazyProperty
    def activity_collection(self):
        return MongoActivityCollection()

        
    
    def addStamps(self, stamps):
        stampIds = [] 
        for stampId in self._addDocuments(stamps):
            stampIds.append(self._getStringFromObjectId(stampId))
        for stamp in self.getStamps(stampIds):
            self.user_stamps_collection.addUserStamp(stamp['user']['user_id'], stamp['id'])
            followerIds = self.friendship_collection.getFollowers(stamp['user']['user_id'])
            self.inbox_stamps_collection.addInboxStamps(followerIds, stamp['id'])
    
    def getStamps(self, stampIds, since=None, before=None, limit=20, \
        sort='timestamp.created', withComments=False):
        # Set variables
        result = []
        comments = []
        
        # Get stamps
        stamps = self._getDocumentsFromIds(stampIds, objId='stamp_id', \
                                            since=since, before=before, \
                                            sort=sort, limit=limit)
        
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
            user = self.user_collection.lookupUsers(None, [data['screen_name']])
            if isinstance(user, list) and len(user) == 1:
                data['user_id'] = user[0]['user_id']
                data['display_name'] = user[0]['display_name']
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

