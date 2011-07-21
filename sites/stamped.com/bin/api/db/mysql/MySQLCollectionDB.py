#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from QL import MySQL
from ACollectionDB import ACollectionDB
from Collection import Collection
from Stamp import Stamp
from QLUserDB import MySQLUserDB
from QLStampDB import MySQLStampDB
from QLEntityDB import MySQLEntityDB
from QLFriendsDB import MySQLFriendsDB

class MySQLCollectionDB(ACollectionDB, MySQL):

    # Denotes relationship between object and SQL table structure -- primary
    # use is to map fields between both structures.
    # First item in tuple is OBJECT ATTRIBUTE, second is COLUMN NAME.
    MAPPING = [
            ('id', 'stamp_id'),
            ('entityID', 'entity_id'),
            ('userID', 'user_id'),
            ('comment', 'comment'),
            ('image', 'image'),
            ('flagged', 'flagged'),
            ('date_created', 'date_created'),
            ('date_updated', 'date_updated')
        ]
    
    def __init__(self):
        ACollectionDB.__init__(self, self.DESC)
        MySQL.__init__(self, mapping=self.MAPPING)
        
        self.db = self._getConnection()
        self._lock = Lock()
        
    ### PUBLIC
    
    def getInbox(self, userID):
        def _getCollection(cursor):
        
            followingIDs = MySQLFriendsDB().getFriends(userID)
            #print followingIDs
            followingIDs.append(userID)
            
            format_strings = ','.join(['%s'] * len(followingIDs))
            cursor.execute("SELECT * FROM stamps WHERE user_id IN (%s)" % 
                format_strings, tuple(followingIDs))
            collectionData = cursor.fetchall()
            
            collection = []
            for stampData in collectionData:
                stamp = Stamp()
                stamp = self._mapSQLToObj(stampData, stamp)
                # probably a more efficient way to do this (as opposed to iterating)
                stamp['entity'] = MySQLEntityDB().getEntity(stamp['entityID'])
                stamp['user'] = MySQLUserDB().getUser(stamp['userID'])
                collection.append(stamp)
                
            return collection
        
        ## TODO: Add functionality to sort the returned stamps by date created
        ##      or date modified. This should happen here and not on the database.
        
        collection = self._transact(_getCollection, returnDict=True)
        
        return collection
    
    def getUser(self, userID):
        def _getCollection(cursor):
            user = MySQLUserDB().getUser(userID)
        
            query = "SELECT * FROM stamps WHERE user_id = %s" % (userID)
            cursor.execute(query)
            collectionData = cursor.fetchall()
            
            collection = []
            for stampData in collectionData:
                stamp = Stamp()
                stamp = self._mapSQLToObj(stampData, stamp)
                # probably a more efficient way to do this (as opposed to iterating)
                stamp['entity'] = MySQLEntityDB().getEntity(stamp['entityID'])
                stamp['user'] = user
                collection.append(stamp)
                
            return collection
        
        collection = self._transact(_getCollection, returnDict=True)
        
        ## TODO: Add functionality to sort the returned stamps by date created
        ##      or date modified. This should happen here and not on the database.

        return collection
    
    def getFavorites(self, userID):
        def _getCollection(cursor):
            user = MySQLUserDB().getUser(userID)
        
            query = """SELECT stamp_id FROM favorites 
                WHERE user_id = %s""" % (userID)
            cursor.execute(query)
            collectionData = cursor.fetchall()
            stampIDs = []
            for result in collectionData:
                stampIDs.append(result['stamp_id'])
            
            stamps = MySQLStampDB().getStamps(stampIDs)
            return stamps
        
        collection = self._transact(_getCollection, returnDict=True)
        
        ## TODO: Add functionality to sort the returned stamps by date created
        ##      or date modified. This should happen here and not on the database.

        return collection
    
    def getMentions(self, userID):
        def _getCollection(cursor):
            user = MySQLUserDB().getUser(userID)
        
            query = """SELECT stamp_id FROM mentions 
                WHERE user_id = %s""" % (userID)
            cursor.execute(query)
            collectionData = cursor.fetchall()
            stampIDs = []
            for result in collectionData:
                stampIDs.append(result['stamp_id'])
            
            stamps = MySQLStampDB().getStamps(stampIDs)
            return stamps
        
        collection = self._transact(_getCollection, returnDict=True)
        
        ## TODO: Add functionality to sort the returned stamps by date created
        ##      or date modified. This should happen here and not on the database.

        return collection
    
        
