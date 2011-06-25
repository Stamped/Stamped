#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from MySQL import MySQL
from AFriendshipDB import AFriendshipDB
from Friendship import Friendship
from MySQLUserDB import MySQLUserDB
from MySQLBlockDB import MySQLBlockDB

class MySQLFriendshipDB(AFriendshipDB, MySQL):

    # Denotes relationship between object and SQL table structure -- primary
    # use is to map fields between both structures.
    # First item in tuple is OBJECT ATTRIBUTE, second is COLUMN NAME.
    MAPPING = [
            ('userID', 'user_id'),
            ('followingID', 'following_id'),
            ('timestamp', 'timestamp'),
            ('approved', 'approved')
        ]
    
    def __init__(self, setup=False):
        AFriendshipDB.__init__(self, self.DESC)
        MySQL.__init__(self, mapping=self.MAPPING)
        
        self.db = self._getConnection()
        self._lock = Lock()
        if setup:
            self._createFriendshipTable()
        
    ### PUBLIC
    
    def addFriendship(self, friendship):
        
        # Check if friend is blocking user's request
        if MySQLBlockDB().checkBlock(userID=friendship['followingID'], blockingID=friendship['userID']):
            print 'BLOCKED'
            return False
            
        # Check if friendship already exists
        if self.checkFriendship(userID=friendship['userID'], followingID=friendship['followingID']):
            print 'ALREADY FRIENDS'
            return False
            
        # Check if friend requires approval
        if MySQLUserDB().getUser(friendship['followingID'])['privacy']:
            print 'REQUIRES APPROVAL'
            friendship['approved'] = 0
        
        friendship = self._mapObjToSQL(friendship)
        friendship['timestamp'] = datetime.now().isoformat()
        
        def _addFriendship(cursor):
            query = """INSERT INTO friends 
                    (user_id, following_id, timestamp, approved) 
                    VALUES (%(user_id)s, %(following_id)s, %(timestamp)s, %(approved)s)"""
            cursor.execute(query, friendship)
            return cursor.lastrowid

        return self._transact(_addFriendship)
    
    def checkFriendship(self, userID, followingID):
        ## TODO: How does approval play in here? If a friend is waiting approval, does a 
        ##       friendship exist?
        def _checkFriendship(cursor):
            query = ("""SELECT * FROM friends 
                WHERE user_id = %s AND following_id = %s""" % 
                (userID, followingID))
            cursor.execute(query)
            
            if cursor.rowcount > 0:
                return True
            else:
                return False
        
        return self._transact(_checkFriendship, returnDict=True)
    
    def getFriendship(self, userID, followingID):
        def _getFriendship(cursor):
            query = ("""SELECT * FROM friends 
                WHERE user_id = %s AND following_id = %s
                AND (approved IS NULL OR approved = 1)""" % 
                (userID, followingID))
            cursor.execute(query)
            
            if cursor.rowcount > 0:
                data = cursor.fetchone()
                friendship = Friendship()
                friendship = self._mapSQLToObj(data, friendship)
                friendship['user'] = MySQLUserDB().getUser(friendship['userID'])
                friendship['following'] = MySQLUserDB().getUser(friendship['followingID'])

                return friendship
            else:
                return None
        
        return self._transact(_getFriendship, returnDict=True)
      
    def removeFriendship(self, userID, followingID):
        def _removeFriendship(cursor):
            query = ("""DELETE FROM friends 
                    WHERE user_id = %s AND following_id = %s""" % 
                    (userID, followingID))
            cursor.execute(query)
            
            return (cursor.rowcount > 0)
        
        return self._transact(_removeFriendship)
    
    ### PRIVATE
    
    def _createFriendshipTable(self):
        def _createTable(cursor):
            query = """CREATE TABLE friends (
                    user_id INT NOT NULL, 
                    following_id INT NOT NULL, 
                    timestamp DATETIME, 
                    approved INT, 
                    PRIMARY KEY(user_id, following_id))"""
            cursor.execute(query)
            
            return True
            
        return self._transact(_createTable)
        