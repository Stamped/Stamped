#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from MySQL import MySQL
from AStampDB import AStampDB
from Stamp import Stamp
from MySQLUserDB import MySQLUserDB
from MySQLEntityDB import MySQLEntityDB

class MySQLStampDB(AStampDB, MySQL):

    # Denotes relationship between object and SQL table structure -- primary
    # use is to map fields between both structures.
    # First item in tuple is OBJECT ATTRIBUTE, second is COLUMN NAME.
    MAPPING = [
            ('id', 'stamp_id'),
            ('entity_id', 'entity_id'),
            ('user_id', 'user_id'),
            ('comment', 'comment'),
            ('image', 'image'),
            ('flagged', 'flagged'),
            ('date_created', 'date_created'),
            ('date_updated', 'date_updated')
        ]
    
    def __init__(self, setup=False):
        AStampDB.__init__(self, self.DESC)
        MySQL.__init__(self, mapping=self.MAPPING)
        
        self.db = self._getConnection()
        self._lock = Lock()
        if setup:
            self._createStampTable()
        
    ### PUBLIC
    
    def addStamp(self, stamp):
        stamp = self._mapObjToSQL(stamp)
        stamp['date_created'] = datetime.now().isoformat()
        
        def _addStamp(cursor):
            query = """INSERT INTO stamps 
                    (entity_id, user_id, comment, date_created) 
                    VALUES (%(entity_id)s, %(user_id)s, %(comment)s, %(date_created)s)"""
            cursor.execute(query, stamp)
            return cursor.lastrowid

        return self._transact(_addStamp)
    
    def getStamp(self, stampID):
        
        def _getStamp(cursor):
            query = "SELECT * FROM stamps WHERE stamp_id = %d" % (stampID)
            cursor.execute(query)
            
            if cursor.rowcount > 0:
                data = cursor.fetchone()
                stamp = Stamp()
                return self._mapSQLToObj(data, stamp)
            else:
                return None
        
        stamp = self._transact(_getStamp, returnDict=True)
        stamp['user'] = MySQLUserDB().getUser(stamp['user_id'])
        stamp['entity'] = MySQLEntityDB().getEntity(stamp['entity_id'])
        
        return stamp
    
    def updateStamp(self, stamp):
        stamp = self._mapObjToSQL(stamp)
        stamp['date_updated'] = datetime.now().isoformat()
                
        def _updateStamp(cursor):
            query = """UPDATE stamps SET 
                       entity_id = %(entity_id)s, 
                       user_id = %(user_id)s, 
                       comment = %(comment)s, 
                       date_updated = %(date_updated)s 
                       WHERE stamp_id = %(stamp_id)s"""
            cursor.execute(query, stamp)
            
            return (cursor.rowcount > 0)
        
        return self._transact(_updateStamp)
    
    def removeStamp(self, stampID):
        def _removeStamp(cursor):
            query = "DELETE FROM stamps WHERE stamp_id = %s" % \
                    (stampID)
            cursor.execute(query)
            
            return (cursor.rowcount > 0)
        
        return self._transact(_removeStamp)
    
    ### PRIVATE
    
    def _createStampTable(self):
        def _createTable(cursor):
            query = """CREATE TABLE stamps (
                    stamp_id INT NOT NULL AUTO_INCREMENT, 
                    entity_id INT, 
                    user_id INT, 
                    comment VARCHAR(250), 
                    image VARCHAR(100), 
                    flagged INT,
                    date_created DATETIME, 
                    date_updated DATETIME, 
                    PRIMARY KEY(stamp_id))"""
            cursor.execute(query)
            cursor.execute("CREATE INDEX ix_user ON stamps (user_id, entity_id, date_created)")
            
            return True
            
        return self._transact(_createTable)
        