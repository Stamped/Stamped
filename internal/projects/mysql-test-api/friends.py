#!/usr/bin/env python

from datetime import datetime
from dbconn import DatabaseConnection
    
class Friend:

    def __init__(self):
        self.database = DatabaseConnection().connect()
    
    #######################################################################
    def ids(self, user_id):
        user_id = int(user_id)
        
        db = self.database
        cursor = db.cursor()
    
        query = "SELECT following_id FROM friends WHERE user_id = %d" % (user_id)
        cursor.execute(query)
        resultData = cursor.fetchall()
            
        result = []
        for recordData in resultData:
            result.append(recordData[0])
        
        cursor.close()
        db.commit()
        db.close()
        
        return result