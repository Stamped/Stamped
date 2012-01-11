#!/usr/bin/env python

from datetime import datetime
from dbconn import MySQLConnection
    
class Collection(MySQLConnection):

    def __init__(self):
        self.database = self.connectDatabase()
    
    ###########################################################################
    def inbox(self, user_id):
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
            FROM userstamps
            JOIN stamps ON userstamps.stamp_id = stamps.stamp_id
            JOIN entities ON stamps.entity_id = entities.entity_id
            JOIN users ON stamps.user_id = users.user_id
            WHERE userstamps.user_id = %d
                AND userstamps.is_inbox = 1
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
            FROM stamps
            JOIN entities ON stamps.entity_id = entities.entity_id
            JOIN users ON stamps.user_id = users.user_id
            WHERE users.user_id = %d
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
    
    ###########################################################################
    def add_stamp(self, stamp_id):
        # Add specific stamp to inbox. Not sure if this will be supported...
        return 'Functionality not yet available'
