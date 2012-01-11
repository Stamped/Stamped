#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

from threading import Lock
from datetime import datetime

from QL import MySQL
from AFavoriteDB import AFavoriteDB
from Favorite import Favorite
from QLUserDB import MySQLUserDB
from QLStampDB import MySQLStampDB

class MySQLFavoriteDB(AFavoriteDB, MySQL):

    # Denotes relationship between object and SQL table structure -- primary
    # use is to map fields between both structures.
    # First item in tuple is OBJECT ATTRIBUTE, second is COLUMN NAME.
    MAPPING = [
            ('stampID', 'stamp_id'),
            ('userID', 'user_id'),
            ('timestamp', 'timestamp')
        ]
    
    def __init__(self, setup=False):
        AFavoriteDB.__init__(self, self.DESC)
        MySQL.__init__(self, mapping=self.MAPPING)
        
        self.db = self._getConnection()
        self._lock = Lock()
        if setup:
            self._createFavoriteTable()
        
    ### PUBLIC
    
    def addFavorite(self, favorite):
        favorite = self._mapObjToSQL(favorite)
        favorite['timestamp'] = datetime.now().isoformat()
        
        def _addFavorite(cursor):
            query = """INSERT INTO favorites
                    (stamp_id, user_id, timestamp) 
                    VALUES (%(stamp_id)s, %(user_id)s, %(timestamp)s)"""
            cursor.execute(query, favorite)
            return cursor.lastrowid

        return self._transact(_addFavorite)
    
    def getFavorite(self, stampID, userID):
        def _getFavorite(cursor):
            query = ("""SELECT * FROM favorites 
                WHERE stamp_id = %s AND user_id = %s""" % 
                (stampID, userID))
            cursor.execute(query)
            
            if cursor.rowcount > 0:
                data = cursor.fetchone()
                favorite = Favorite()
                return self._mapSQLToObj(data, favorite)
            else:
                return None
        
        favorite = self._transact(_getFavorite, returnDict=True)
        favorite['user'] = MySQLUserDB().getUser(userID)
        favorite['stamp'] = MySQLStampDB().getStamp(stampID)
        
        return favorite
    
    def removeFavorite(self, stampID, userID):
        def _removeFavorite(cursor):
            query = ("""DELETE FROM favorites 
                WHERE stamp_id = %s AND user_id = %s""" % 
                (stampID, userID))
            cursor.execute(query)
            
            return (cursor.rowcount > 0)
        
        return self._transact(_removeFavorite)
    
    ### PRIVATE
    
    def _createFavoriteTable(self):
        def _createTable(cursor):
            query = """CREATE TABLE favorites ( 
                    stamp_id INT NOT NULL, 
                    user_id INT NOT NULL, 
                    timestamp DATETIME, 
                    PRIMARY KEY(user_id, stamp_id))"""
            cursor.execute(query)
            
            return True
            
        return self._transact(_createTable)
        
