#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

from threading import Lock
from datetime import datetime

from QL import MySQL
from ockDB import ABlockDB
from ck import Block
from QLUserDB import MySQLUserDB

class MySQLBlockDB(ABlockDB, MySQL):

    # Denotes relationship between object and SQL table structure -- primary
    # use is to map fields between both structures.
    # First item in tuple is OBJECT ATTRIBUTE, second is COLUMN NAME.
    MAPPING = [
            ('userID', 'user_id'),
            ('blockingID', 'blocking_id'),
            ('timestamp', 'timestamp')
        ]
    
    def __init__(self, setup=False):
        ABlockDB.__init__(self, self.DESC)
        MySQL.__init__(self, mapping=self.MAPPING)
        
        self.db = self._getConnection()
        self._lock = Lock()
        if setup:
            self._createBlockTable()
        
    ### PUBLIC
    
    def addBlock(self, block):
        block = self._mapObjToSQL(block)
        block['timestamp'] = datetime.now().isoformat()
        
        def _addBlock(cursor):
            query = """INSERT INTO blocks 
                    (user_id, blocking_id, timestamp) 
                    VALUES (%(user_id)s, %(blocking_id)s, %(timestamp)s)"""
            cursor.execute(query, block)
            return cursor.lastrowid

        return self._transact(_addBlock)
    
    def checkBlock(self, userID, blockingID):
        ## TODO: How does approval play in here? If a friend is waiting approval, does a 
        ##       block exist?
        def _checkBlock(cursor):
            query = ("""SELECT * FROM blocks 
                WHERE user_id = %s AND blocking_id = %s""" % 
                (userID, blockingID))
            cursor.execute(query)
            
            if cursor.rowcount > 0:
                return True
            else:
                return False
        
        return self._transact(_checkBlock, returnDict=True)
    
    def getBlocking(self, userID):
        def _getBlocking(cursor):
            query = ("""SELECT * FROM blocks 
                WHERE user_id = %s""" % 
                (userID))
            cursor.execute(query)
            blocksData = cursor.fetchall()
            
            blockingIDs = []
            for user in blocksData:
                blockingIDs.append(user['user_id'])
            return blockingIDs
                    
        return self._transact(_getBlocking, returnDict=True)
      
    def removeBlock(self, userID, blockingID):
        def _removeBlock(cursor):
            query = ("""DELETE FROM blocks 
                    WHERE user_id = %s AND blocking_id = %s""" % 
                    (userID, blockingID))
            cursor.execute(query)
            
            return (cursor.rowcount > 0)
        
        return self._transact(_removeBlock)
    
    ### PRIVATE
    
    def _createBlockTable(self):
        def _createTable(cursor):
            query = """CREATE TABLE blocks ( 
                    user_id INT NOT NULL, 
                    blocking_id INT NOT NULL, 
                    timestamp DATETIME, 
                    PRIMARY KEY(user_id, blocking_id))"""
            cursor.execute(query)
            
            return True
            
        return self._transact(_createTable)
        
