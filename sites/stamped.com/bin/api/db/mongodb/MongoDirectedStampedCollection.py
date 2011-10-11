#!/usr/bin/python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__   = 'TODO'

import Globals

from utils import lazyProperty

from AMongoCollection import AMongoCollection
from MongoUserCollection import MongoUserCollection
from MongoInboxStampsCollection import MongoInboxStampsCollection
from MongoFriendsCollection import MongoFriendsCollection
from MongoBlockCollection import MongoBlockCollection

####### TODO
# How to do this? Edge case is where two distinct users have sent one recipient the same
# directed stamp. No easy way to delete references to the stamp in the inbox, because you
# have to check to see if any other users have sent it before deleting stamps from 
# intended user. COME BACK TO.

class MongoDirectedStampsCollection(AMongoCollection):
    
    SCHEMA = {
        '_id': basestring,
        'stamp_id': basestring
    }
    
    def __init__(self, setup=False):
        AMongoCollection.__init__(self, collection='directedstamps')
    
    ### PUBLIC
    
    @lazyProperty
    def user_collection(self):
        return MongoUserCollection()
    
    @lazyProperty
    def inbox_stamps_collection(self):
        return MongoInboxStampsCollection()
    
    @lazyProperty
    def friends_collection(self):
        return MongoFriendsCollection()
    
    @lazyProperty
    def block_collection(self):
        return MongoBlockCollection()
    
    def addDirectedStamp(self, userId, stampId, recipientScreenNames, message=None):
        """
        This function allows a given user to share a stamp with multiple
        recipients. The user does not have to own the stamp in question, and
        it is assumed at this point that they have permission to view it and 
        share it. 
        
        Note that sharing the stamp is an irrevocable action (i.e. it cannot be 
        undone). Each recipient can chose to remove the shared stamp, but the
        sharer cannot undo the action once it's been taken.
        """
        
        # Validate inputs ### TODO: Improve this section
        if not isinstance(userId, basestring):
            raise KeyError("ID not valid")
        if not isinstance(stampId, basestring):
            raise KeyError("ID not valid")
        if not isinstance(recipientScreenNames, list):
            raise KeyError("Input not valid")
        if not isinstance(message, basestring):
            raise KeyError("Input not valid")
            
        # Grab display name for sender
        user = self.user_collection.getUser(userId)
        
        # Grab user id and display name for all recipients
        recipients = self.user_collection.lookupUsers(None, recipientScreenNames)
        
        # Build directed comment data
        data = {}
        data['sender'] = {
            'user_id': user.user_id,
            'display_name': user.display_name
        }
        data['recipients'] = []
        for recipient in recipients:
            data['recipients'].append({
                'user_id': recipient.user_id,
                'display_name': recipient.display_name
            })
        data['message'] = message
        
        # Cycle through recipients
        for recipient in recipients:
        
            # Add directed info to their directed stamps bucket
            self._collection.update(
                {'_id': self._getOverflowBucket(recipient.user_id)}, 
                {'$set': {stampId: data}},
                upsert=True)
                
            # Check to see if the sender is blocked by the recipient.
            # If so, no further action should be taken in this loop.
            if self.block_collection.checkBlock(recipient.user_id, user.user_id):
                continue
                
            # Add to recipient's activity
            ### TODO
            
            # Check if recipient is following user; if so, and if stamp is not
            # already in recipient's inbox, add to recipient's inbox
            if self.friends_collection.checkFriend(recipient.user_id, user.user_id):
                if not self.inbox_stamps_collection.checkInboxStamp(recipient.user_id, stampId):
                    self.inbox_stamps_collection.addInboxStamp(recipient.user_id, stampId)
        
        return True
            
    def removeDirectedStamps(self, userId, senderId):
        """
        This function allows the recipient of directed stamps to remove
        them from ir inbox. It cannot be called on individual stamps, but is
        only called when the recipient unfollows the sender.
        """
        
        # For each potential overflow bucket, search for stamps that include the
        # sender's user_id
        buckets = [userId]
        overflow = self._collection.find_one({'_id': userId}, fields={'overflow': 1})

        if overflow != None and 'overflow' in overflow:
            bucket += overflow['overflow']
            
        for bucket in buckets:
            self._collection.find({'_id': bucket, 'sender': {'user_id': senderId}})
    
    
        return self._removeRelationship(keyId=userId, refId=stampId)
            
    def getDirectedStamps(self, userId):
        ### TODO: Add limit? Add timestamp to slice?
        return False

