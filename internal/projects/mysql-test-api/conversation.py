#!/usr/bin/env python

from datetime import datetime
from dbconn import MySQLConnection
    
class Conversation(MySQLConnection):

    def __init__(self):
        self.database = self.connectDatabase()
    
    ###########################################################################
    def show(self, comment_id):
        comment_id = int(comment_id)
        
        cursor = self.getDatabase().cursor()
        
        query = ("""SELECT 
                    comments.comment_id,
                    comments.stamp_id,
                    comments.user_id,
                    comments.timestamp,
                    comments.comment,
                    comments.flagged,
                    users.name,
                    users.image
                FROM comments
                JOIN users ON comments.user_id = users.user_id
                WHERE comments.comment_id = %d""" %
             (comment_id))
        cursor.execute(query)
        
        if cursor.rowcount > 0:
            data = cursor.fetchone()
            
            result = {}
            result['comment_id'] = data[0]
            result['stamp_id'] = data[1]
            result['user_id'] = data[2]
            result['timestamp'] = data[3]
            result['comment'] = data[4]
            result['flagged'] = data[5]
            result['user_name'] = data[6]
            result['user_image'] = data[7]
    
        else: 
            result = "NA"
        
        cursor.close()
        self.closeDatabase()
        
        return result
        
    ###########################################################################
    def create(self, user_id, stamp_id, comment):
        user_id = int(user_id)
        stamp_id = int(stamp_id)
        str_now = datetime.now().isoformat()
        
        cursor = self.getDatabase().cursor() 
        
        query = ("""INSERT 
                INTO comments (user_id, stamp_id, comment, timestamp)
                VALUES (%s, %s, '%s', '%s')""" %
             (user_id, stamp_id, comment, str_now))
        cursor.execute(query)
        
        query = ("SELECT * FROM comments WHERE comment_id = %d" % 
            (self.database.insert_id()))
        cursor.execute(query)
        result = cursor.fetchone()
        
        cursor.close()
        self.closeDatabase()
        
        return result
    
    ###########################################################################
    def destroy(self, comment_id):
        comment_id = int(comment_id)
        
        cursor = self.getDatabase().cursor() 
        
        query = "DELETE FROM comments WHERE comment_id = %d" % (comment_id)
        cursor.execute(query)
        if cursor.rowcount > 0:
            result = "Success"
        else:
            result = "NA"
        
        cursor.close()
        self.closeDatabase()
        
        return result
    
    ###########################################################################
    def flag(self, comment_id, is_flagged = 1):
        # This will ultimately need to be reworked, since 'flagged' will be a 
        # separate table and not just an attribute of the comment.
        comment_id = int(comment_id)
        is_flagged = int(is_flagged)
        
        cursor = self.getDatabase().cursor() 
        
        query = ("UPDATE comments SET flagged = %d WHERE comment_id = %d" % 
                (is_flagged, comment_id))
        cursor.execute(query)
        if cursor.rowcount > 0:
            result = "Success"
        else:
            result = "NA"
        
        cursor.close()
        self.closeDatabase()
        
        return result
