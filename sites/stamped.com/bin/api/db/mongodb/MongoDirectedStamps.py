#!/usr/bin/python

__author__ = 'Stamped (dev@stamped.com)'
__version__ = '1.0'
__copyright__ = 'Copyright (c) 2011 Stamped.com'
__license__ = 'TODO'

import Globals
import copy

from threading import Lock
from datetime import datetime

from MongoDB import Mongo
from MongoUser import MongoUser
from MongoInboxStamps import MongoInboxStamps
from MongoFriends import MongoFriends
from MongoBlock import MongoBlock
# from api.AFriendshipDB import AFriendshipDB
# from api.Friendship import Friendship

class MongoDirectedStamps(Mongo):
        
    COLLECTION = 'directedstamps'
        
    SCHEMA = {
        '_id': basestring,
        'stamp_id': basestring
    }
    
    def __init__(self, setup=False):
        Mongo.__init__(self, collection=self.COLLECTION)
        
        self.db = self._getDatabase()
        self._lock = Lock()
        
        
    ### PUBLIC
    
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
            
        # Set up other database connections
        _userDB = MongoUser()
        _inboxStampsDB = MongoInboxStamps()
        _friendsDB = MongoFriends()
        _blockDB = MongoBlock()
        
        # Grab display name for sender
        user = _userDB.getUser(userId)
        
        # Grab user id and display name for all recipients
        recipients = _userDB.lookupUsers(None, recipientScreenNames)
        
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
            if _blockDB.checkBlock(recipient.user_id, user.user_id):
                continue
                
            # Add to recipient's activity
            ### TODO
            
            # Check if recipient is following user; if so, and if stamp is not
            # already in recipient's inbox, add to recipient's inbox
            if _friendsDB.checkFriend(recipient.user_id, user.user_id):
                if not _inboxStampsDB.checkInboxStamp(recipient.user_id, stampId):
                    _inboxStampsDB.addInboxStamp(recipient.user_id, stampId)
        
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


    ### PRIVATE
    


####### NOTES
# How to do this? Edge case is where two distinct users have sent one recipient the same
# directed stamp. No easy way to delete references to the stamp in the inbox, because you
# have to check to see if any other users have sent it before deleting stamps from 
# intended user. COME BACK TO.
