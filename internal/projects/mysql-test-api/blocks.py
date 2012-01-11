#!/usr/bin/env python

from datetime import datetime
from dbconn import MySQLConnection
    
class Block(MySQLConnection):

    def __init__(self):
        self.database = self.connectDatabase()
    
    ###########################################################################
    def exists(self, user_id, follower_id):
        user_id = int(user_id)
        follower_id = int(follower_id)
        
        cursor = self.getDatabase().cursor()
        
        query = ("""SELECT * FROM blocks 
                WHERE user_id = %d AND follower_id = %d""" %
                (user_id, follower_id))
        cursor.execute(query)
        if cursor.rowcount > 0:
            result = True
        else:
            result = False
            
        cursor.close()
        self.closeDatabase()
        
        return result
    
    ###########################################################################
    def blocking(self, user_id):
        user_id = int(user_id)
        
        cursor = self.getDatabase().cursor()
        
        query = ("SELECT follower_id FROM blocks WHERE user_id = %d" %
                (user_id))
        cursor.execute(query)
        resultData = cursor.fetchall()
            
        result = []
        for recordData in resultData:
            result.append(recordData[0])
        
        cursor.close()
        self.closeDatabase()
        
        return result
    
    ###########################################################################
    def create(self, user_id, follower_id):
        user_id = int(user_id)
        follower_id = int(follower_id)
        timestamp = datetime.now().isoformat()
        
        if not self.exists(user_id, follower_id):
        
            cursor = self.getDatabase().cursor()
            
            query = ("""INSERT INTO blocks (user_id, follower_id, timestamp)
                    VALUES (%d, %d, '%s')""" %
                    (user_id, follower_id, timestamp))
            cursor.execute(query)
            if cursor.rowcount > 0:
                result = "Success"
            else:
                result = "NA"
        else: 
            result = "NA"
        
        cursor.close()
        self.closeDatabase()
        
        return result
        
    ###########################################################################
    def destroy(self, user_id, follower_id):
        user_id = int(user_id)
        follower_id = int(follower_id)
        
        cursor = self.getDatabase().cursor()
        
        query = ("DELETE FROM blocks WHERE user_id = %d AND follower_id = %d" %
                (user_id, follower_id))
        cursor.execute(query)
        if cursor.rowcount > 0:
            result = "Success"
        else:
            result = "NA"
        
        cursor.close()
        self.closeDatabase()
        
        return result
    
