#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import re

from utils import lazyProperty

from AMongoCollection import AMongoCollection
from MongoUserStamps import MongoUserStamps
from MongoInboxStamps import MongoInboxStamps
from MongoFriendship import MongoFriendship
from MongoComment import MongoComment
from MongoCreditGivers import MongoCreditGivers
from MongoCreditReceived import MongoCreditReceived
from MongoUser import MongoUser
from MongoFavorite import MongoFavorite
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
        return MongoUser()
    
    @lazyProperty
    def favorite_collection(self):
        return MongoFavorite()
    
    @lazyProperty
    def credit_givers_collection(self):
        return MongoCreditGivers()
    
    @lazyProperty
    def credit_received_collection(self):
        return MongoCreditReceived()
    
    @lazyProperty
    def activity_collection(self):
        return MongoActivityCollection()
    
    @lazyProperty
    def comment_collection(self):
        return MongoComment()
    
    @lazyProperty
    def user_stamps_collection(self):
        return MongoUserStamps()
    
    @lazyProperty
    def inbox_stamps_collection(self):
        return MongoInboxStamps()
    
    @lazyProperty
    def friendship_collection(self):
        return MongoFriendship()
    
    def addStamp(self, stamp):
        # Extract user
        user = self.user_collection.getUser(stamp['user']['user_id'])
        
        # Extract mentions
        if 'blurb' in stamp:
            mentions = self._extractMentions(stamp['blurb'])
            if len(mentions) > 0:
                stamp['mentions'] = mentions
            
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
        
        # If users are mentioned, add stamp to their activity feed
        if 'mentions' in stamp:
            recipientIds = []
            for mention in stamp['mentions']:
                if 'user_id' in mention:
                    recipientIds.append(mention['user_id'])
            if len(recipientIds) > 0:
                self.activity_collection.addActivityForMention(recipientIds, user, stamp)
        
        # Give credit
        if 'credit' in stamp and len(stamp.credit) > 0:
            for user in self.user_collection.lookupUsers(None, stamp.credit):
                # Add to 'credit received'
                numCredit = self.credit_received_collection.addCredit(user.user_id, stampId)
            
                # Add to 'credit givers'
                numGivers = self.credit_givers_collection.addGiver(user.user_id, stamp['user']['user_id'])
                
                # Increment user's total credit received
                self.user_collection.updateUserStats(user.user_id, 'num_credit', None, increment=1)
                
                # Update user's total credit givers 
                self.user_collection.updateUserStats(user.user_id, 'num_credit_givers', numGivers)
                
                # Update the number of credit on the user's stamp
                creditedStamp = Stamp(self._mongoToObj(
                    self._collection.find_one({
                        'user.user_id': user.user_id, 
                        'entity.entity_id': stamp.entity['entity_id']
                    }),
                    'stamp_id'))
                
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
                    
                    # Add to activity stream
                    self.activity_collection.addActivityForRestamp([user.user_id], stamp.user, stamp)
                    
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
        
    def addComment(self, comment):
        # Grab data
        user = self.user_collection.getUser(comment['user']['user_id'])
        stamp = self.getStamp(comment['stamp_id'])
        
        # Extract mentions
        if 'blurb' in comment:
            mentions = self._extractMentions(comment['blurb'])
            if len(mentions) > 0:
                comment['mentions'] = mentions
        
        # Get ids for stamp owner, mentioned users, and previous commenters
        recipientIds = [self.getStamp(comment['stamp_id']).user['user_id']]
        if 'mentions' in comment:
            for mention in comment['mentions']:
                if 'user_id' in mention:
                    recipientIds.append(mention['user_id'])
        ### TODO: Limit this to the last 20 comments or so...
        for prevComment in self.getComments(comment['stamp_id']):
            recipientIds.append(prevComment['user']['user_id'])
        recipientDict = {}
        for e in recipientIds:
            recipientDict[e] = 1
        recipientIds = recipientDict.keys()
        if comment['user']['user_id'] in recipientIds:
            recipientIds.remove(comment['user']['user_id'])
        
        # Add comment
        commentId = self.comment_collection.addComment(comment)
        
        # Add activity
        self.activity_collection.addActivityForMention(recipientIds, user, stamp)
        
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

