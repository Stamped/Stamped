#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

from threading import Lock
from datetime import datetime

from QL import MySQL
from llowersDB import AFollowersDB
from lowers import Followers
from QLUserDB import MySQLUserDB

class MySQLFollowersDB(AFollowersDB, MySQL):

    # Denotes relationship between object and SQL table structure -- primary
    # use is to map fields between both structures.
    # First item in tuple is OBJECT ATTRIBUTE, second is COLUMN NAME.
    MAPPING = [
            ('userID', 'user_id'),
            ('followingID', 'following_id'),
            ('timestamp', 'timestamp'),
            ('approved', 'approved')
        ]
    
    def __init__(self):
        AFollowersDB.__init__(self, self.DESC)
        MySQL.__init__(self, mapping=self.MAPPING)
        
        self.db = self._getConnection()
        self._lock = Lock()
        
    ### PUBLIC
    
    def getFollowers(self, userID):
        def _getFollowers(cursor):
            query = ("SELECT user_id FROM friends WHERE following_id = %s" % 
                (userID))
            cursor.execute(query)
            friendsData = cursor.fetchall()
            
            friendIDs = []
            for friendData in friendsData:
                friendIDs.append(friendData['user_id'])
            return friendIDs
        
        return self._transact(_getFollowers, returnDict=True)
        
