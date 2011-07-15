#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from threading import Lock
from datetime import datetime

from MySQL import MySQL
from ACommentDB import ACommentDB
from Comment import Comment
from MySQLUserDB import MySQLUserDB
from MySQLStampDB import MySQLStampDB

class MySQLCommentDB(ACommentDB, MySQL):

    # Denotes relationship between object and SQL table structure -- primary
    # use is to map fields between both structures.
    # First item in tuple is OBJECT ATTRIBUTE, second is COLUMN NAME.
    MAPPING = [
            ('id', 'comment_id'),
            ('stampID', 'stamp_id'),
            ('userID', 'user_id'),
            ('timestamp', 'timestamp'),
            ('comment', 'comment'),
            ('flagged', 'flagged')
        ]
    
    def __init__(self, setup=False):
        ACommentDB.__init__(self, self.DESC)
        MySQL.__init__(self, mapping=self.MAPPING)
        
        self.db = self._getConnection()
        self._lock = Lock()
        if setup:
            self._createCommentTable()
        
    ### PUBLIC
    
    def addComment(self, comment):
        comment = self._mapObjToSQL(comment)
        comment['timestamp'] = datetime.now().isoformat()
        
        def _addComment(cursor):
            query = """INSERT INTO comments
                    (stamp_id, user_id, comment, timestamp) 
                    VALUES (%(stamp_id)s, %(user_id)s, 
                        %(comment)s, %(timestamp)s)"""
            cursor.execute(query, comment)
            return cursor.lastrowid

        return self._transact(_addComment)
    
    def getComment(self, commentID):
        def _getComment(cursor):
            query = ("SELECT * FROM comments WHERE comment_id = %s" % 
                (commentID))
            cursor.execute(query)
            
            if cursor.rowcount > 0:
                data = cursor.fetchone()
                comment = Comment()
                return self._mapSQLToObj(data, comment)
            else:
                return None
        
        comment = self._transact(_getComment, returnDict=True)
        comment['user'] = MySQLUserDB().getUser(comment['userID'])
        comment['stamp'] = MySQLStampDB().getStamp(comment['stampID'])
        
        return comment
        
    def getConversation(self, stampID):
        def _getConversation(cursor):
            stamp = MySQLStampDB().getStamp(stampID)
        
            query = ("SELECT * FROM comments WHERE stamp_id = %s" % 
                (stampID))
            cursor.execute(query)
            conversastionData = cursor.fetchall()
            
            conversation = []
            for commentData in conversastionData:
                comment = Comment()
                comment = self._mapSQLToObj(commentData, comment)
                comment['user'] = MySQLUserDB().getUser(comment['userID'])
                comment['stamp'] = stamp
                conversation.append(comment)
                
            return conversation
        
        conversation = self._transact(_getConversation, returnDict=True)
        
        return conversation
    
    def removeComment(self, commentID):
        def _removeComment(cursor):
            query = ("""DELETE FROM comments 
                WHERE comment_id = %s""" % (commentID))
            cursor.execute(query)
            
            return (cursor.rowcount > 0)
        
        return self._transact(_removeComment)
    
    def removeConversation(self, stampID):
        def _removeConversation(cursor):
            query = ("""DELETE FROM comments 
                WHERE stamp_id = %s""" % (stampID))
            cursor.execute(query)
            
            return (cursor.rowcount > 0)
        
        return self._transact(_removeConversation)
    
    ### PRIVATE
    
    def _createCommentTable(self):
        def _createTable(cursor):
            query = """CREATE TABLE comments (
                    comment_id INT NOT NULL AUTO_INCREMENT, 
                    stamp_id INT NOT NULL, 
                    user_id INT NOT NULL, 
                    timestamp DATETIME, 
                    comment VARCHAR(250),
                    flagged INT,
                    PRIMARY KEY(comment_id))"""
            cursor.execute(query)
            
            cursor.execute("""CREATE INDEX ix_stamp 
                ON comments (stamp_id, timestamp, user_id)""")
            return True
            
        return self._transact(_createTable)
        