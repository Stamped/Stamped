#!/usr/bin/env python

from datetime import datetime
from dbconn import DatabaseConnection
    
class Favorite:

    def __init__(self):
        self.database = DatabaseConnection().connect()
    
    ###########################################################################
    def show(self, user_id):
        user_id = int(user_id)
        
        db = self.database
        cursor = db.cursor()
        
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
                AND userstamps.is_starred = 1
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
        db.commit()
        db.close()
        
        return result
    
    ###########################################################################
    def create(self, stamp_id, user_id):
        stamp_id = int(stamp_id)
        user_id = int(user_id)
        
        db = self.database
        cursor = db.cursor()
        
        query = ("""SELECT is_starred FROM userstamps 
                WHERE stamp_id = %d AND user_id = %d""" %
                (stamp_id, user_id))
        cursor.execute(query)
        
        if cursor.rowcount > 0:
            update = ("""UPDATE userstamps SET is_starred = 1
                    WHERE stamp_id = %d AND user_id = %d""" %
                    (stamp_id, user_id))
            cursor.execute(update)
            if cursor.rowcount > 0:
                result = "Success"
            else:
                result = "NA"
        
        else:
            insert = ("""INSERT INTO userstamps (
                        user_id, 
                        stamp_id, 
                        is_read, 
                        is_starred, 
                        is_stamped, 
                        is_inbox, 
                        is_transacted
                    )
                    VALUES (%d, %d, 1, 1, 0, 0, 0)""" %
                    (user_id, stamp_id))
            cursor.execute(insert)
            if cursor.rowcount > 0:
                result = "Success"
            else:
                result = "NA"
        
        cursor.close()
        db.commit()
        db.close()
        
        return result
    
    ###########################################################################
    def destroy(self, stamp_id, user_id):
        stamp_id = int(stamp_id)
        user_id = int(user_id)
        
        db = self.database
        cursor = db.cursor()
        
        query = ("""SELECT is_starred FROM userstamps 
                WHERE stamp_id = %d AND user_id = %d""" %
                (stamp_id, user_id))
        cursor.execute(query)
        
        if cursor.rowcount > 0:
            delete = ("""DELETE FROM userstamps
                    WHERE stamp_id = %d AND user_id = %d""" %
                    (stamp_id, user_id))
            cursor.execute(delete)
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