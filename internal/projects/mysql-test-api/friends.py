#!/usr/bin/env python

from datetime import datetime
from dbconn import MySQLConnection
    
class Friend(MySQLConnection):

    def __init__(self):
        self.database = self.connectDatabase()
    
    #######################################################################
    def ids(self, user_id):
        user_id = int(user_id)
        
        cursor = self.getDatabase().cursor()
    
        query = ("SELECT following_id FROM friends WHERE user_id = %d" % 
                (user_id))
        cursor.execute(query)
        resultData = cursor.fetchall()
            
        result = []
        for recordData in resultData:
            result.append(recordData[0])
        
        cursor.close()
        self.closeDatabase()
        
        return result
