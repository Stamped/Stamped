#!/usr/bin/env python

from datetime import datetime
from dbconn import DatabaseConnection
    
class Block:

    def __init__(self):
        self.database = DatabaseConnection().connect()
    
    #######################################################################
    def exists(self, user_id, follower_id):
        user_id = int(user_id)
        follower_id = int(follower_id)
        
        db = self.database
        cursor = db.cursor()
        
        query = ("""SELECT * FROM blocks 
                WHERE user_id = %d AND follower_id = %d""" %
                (user_id, follower_id))
        cursor.execute(query)
        if cursor.rowcount > 0:
            result = True
        else:
            result = False
            
        cursor.close()
        db.commit()
        db.close()
        
        return result
    
    ###############################################################################
    def blocking(self, user_id):
        user_id = int(user_id)
        
        db = self.database
        cursor = db.cursor()
        
        query = ("SELECT follower_id FROM blocks WHERE user_id = %d" %
                (user_id))
        cursor.execute(query)
        resultData = cursor.fetchall()
            
        result = []
        for recordData in resultData:
            result.append(recordData[0])
        
        cursor.close()
        db.commit()
        db.close()
        
        return result
    
    ###############################################################################
    def create(self, user_id, follower_id):
        user_id = int(user_id)
        follower_id = int(follower_id)
        timestamp = datetime.now().isoformat()
        
        db = self.database
        cursor = db.cursor()
        
        if not exists(user_id, follower_id):
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
        db.commit()
        db.close()
        
        return result
        
    ###############################################################################
    def destroy(self, user_id, follower_id):
        user_id = int(user_id)
        follower_id = int(follower_id)
        
        db = self.database
        cursor = db.cursor()
        
        query = ("DELETE FROM blocks WHERE user_id = %d AND follower_id = %d" %
                (user_id, follower_id))
        cursor.execute(query)
        if cursor.rowcount > 0:
            result = "Success"
        else:
            result = "NA"
        
        cursor.close()
        db.commit()
        db.close()
        
        return result
    