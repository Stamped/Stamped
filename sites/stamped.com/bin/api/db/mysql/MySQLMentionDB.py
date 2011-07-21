#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from MySQL import MySQL
from AMentionDB import AMentionDB
from Mention import Mention
from MySQLUserDB import MySQLUserDB
from MySQLStampDB import MySQLStampDB

class MySQLMentionDB(AMentionDB, MySQL):

    # Denotes relationship between object and SQL table structure -- primary
    # use is to map fields between both structures.
    # First item in tuple is OBJECT ATTRIBUTE, second is COLUMN NAME.
    MAPPING = [
            ('stampID', 'stamp_id'),
            ('userID', 'user_id'),
            ('date_created', 'date_created')
        ]
    
    def __init__(self, setup=False):
        AMentionDB.__init__(self, self.DESC)
        MySQL.__init__(self, mapping=self.MAPPING)
        
        self.db = self._getConnection()
        self._lock = Lock()
        if setup:
            self._createMentionTable()
        
    ### PUBLIC
    
    def addMention(self, mention):
        mention = self._mapObjToSQL(mention)
        mention['date_created'] = datetime.now().isoformat()
        
        def _addMention(cursor):
            query = """INSERT INTO mentions
                    (stamp_id, user_id, date_created) 
                    VALUES (%(stamp_id)s, %(user_id)s, %(date_created)s)"""
            cursor.execute(query, mention)
            return cursor.lastrowid

        return self._transact(_addMention)
    
    def getMention(self, stampID, userID):
        def _getMention(cursor):
            query = ("""SELECT * FROM mentions 
                WHERE stamp_id = %s AND user_id = %s""" % (stampID, userID))
            cursor.execute(query)
            
            if cursor.rowcount > 0:
                data = cursor.fetchone()
                mention = Mention()
                return self._mapSQLToObj(data, mention)
            else:
                return None
        
        mention = self._transact(_getMention, returnDict=True)
        mention['user'] = MySQLUserDB().getUser(mention['userID'])
        mention['stamp'] = MySQLStampDB().getStamp(mention['stampID'])
        
        return mention
    
    def removeMention(self, stampID, userID):
        def _removeMention(cursor):
            query = ("""DELETE FROM mentions 
                WHERE stamp_id = %s AND user_id = %s""" % (stampID, userID))
            cursor.execute(query)
            
            return (cursor.rowcount > 0)
        
        return self._transact(_removeMention)
    
    ### PRIVATE
    
    def _createMentionTable(self):
        def _createTable(cursor):
            query = """CREATE TABLE mentions ( 
                    stamp_id INT NOT NULL, 
                    user_id INT NOT NULL, 
                    date_created DATETIME, 
                    PRIMARY KEY(stamp_id, user_id))"""
            cursor.execute(query)
            
            return True
            
        return self._transact(_createTable)
        
