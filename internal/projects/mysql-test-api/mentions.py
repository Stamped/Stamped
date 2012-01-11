#!/usr/bin/env python

from datetime import datetime
from dbconn import MySQLConnection
    
class Mention(MySQLConnection):

    def __init__(self):
        self.database = self.connectDatabase()
    
    ###########################################################################
    def create(self, stamp_id, user_id):
        stamp_id = int(stamp_id)
        user_id = int(user_id)
        timestamp = datetime.now().isoformat()
        
        cursor = self.getDatabase().cursor()
        
        query = ("SELECT * FROM mentions WHERE user_id = %d AND stamp_id = %d" %
                (user_id, stamp_id))
        cursor.execute(query)
        if cursor.rowcount == 0:
            insertQuery = ("""INSERT INTO mentions (stamp_id, user_id, timestamp)
                    VALUES (%d, %d, '%s')""" % (stamp_id, user_id, timestamp))
            cursor.execute(insertQuery)
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
    def destroy(self, stamp_id, user_id):
        stamp_id = int(stamp_id)
        user_id = int(user_id)
        
        cursor = self.getDatabase().cursor()
        
        query = ("DELETE FROM mentions WHERE stamp_id = %d AND user_id = %d" % 
                (stamp_id, user_id))
        cursor.execute(query)
        if cursor.rowcount > 0:
            result = "Success"
        else:
            result = "NA"
        
        cursor.close()
        self.closeDatabase()
        
        return result
    
    ###########################################################################
    def user(self, user_id):
        user_id = int(user_id)
        
        cursor = self.getDatabase().cursor()
        
        query = ("""SELECT 
                entities.entity_id,
                stamps.stamp_id,
                stamps.user_id,
                stamps.comment,
                stamps.image,
                entities.image,
                stamps.timestamp,
                users.name,
                users.image
            FROM mentions
            JOIN stamps ON mentions.stamp_id = stamps.stamp_id
            JOIN entities ON stamps.entity_id = entities.entity_id
            JOIN users ON stamps.user_id = users.user_id
            WHERE mentions.user_id = %d
            ORDER BY stamps.timestamp DESC
            LIMIT 0, 10""" %
            (user_id))
        cursor.execute(query)
        
        resultData = cursor.fetchmany(10)
        
        result = []
        for recordData in resultData:
            record = {}
            record['entity_id'] = recordData[0]
            record['stamp_id'] = recordData[1]
            record['user_id'] = recordData[2]
            record['comment'] = recordData[3]
            if recordData[4]:
                record['image'] = recordData[4]
            else: 
                record['image'] = recordData[5]
            record['timestamp'] = recordData[6]
            record['user_name'] = recordData[7]
            record['user_image'] = recordData[8]
            result.append(record)
            
        cursor.close()
        self.closeDatabase()
        
        return result
