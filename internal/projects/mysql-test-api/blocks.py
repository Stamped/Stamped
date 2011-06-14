#!/usr/bin/env python

from datetime import datetime
import MySQLdb

###############################################################################
def sqlConnection():
    return MySQLdb.connect(user='root',db='stamped_api')

###############################################################################
def exists(user_id, follower_id):
    user_id = int(user_id)
    follower_id = int(follower_id)
    
    db = sqlConnection()
    cursor = db.cursor()
    
    query = ("SELECT * FROM blocks WHERE user_id = %d AND follower_id = %d" %
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
def blocking(user_id):
    user_id = int(user_id)
    
    db = sqlConnection()
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
def create(user_id, follower_id):
    user_id = int(user_id)
    follower_id = int(follower_id)
    timestamp = datetime.now().isoformat()
    
    db = sqlConnection()
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
def destroy(user_id, follower_id):
    user_id = int(user_id)
    follower_id = int(follower_id)
    
    db = sqlConnection()
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
    