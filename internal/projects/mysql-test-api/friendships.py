#!/usr/bin/env python

from datetime import datetime
import MySQLdb

###############################################################################
def sqlConnection():
    return MySQLdb.connect(user='root',db='stamped_api')

###############################################################################
def create(user_id, following_id):
    user_id = int(user_id)
    following_id = int(following_id)
    timestamp = datetime.now().isoformat()
    
    db = sqlConnection()
    cursor = db.cursor()
    
    if not exists(user_id, following_id):
        privacyQuery = ("SELECT privacy FROM users WHERE user_id = %d" % 
                (following_id))
        cursor.execute(privacyQuery)
        record = cursor.fetchone()
        if record[0] == 1:
            needs_approval = 1
        else:
            needs_approval = 0
        
        query = ("""INSERT 
                INTO friends (user_id, following_id, timestamp, approved)
                VALUES (%d, %d, '%s', %d)""" %
                (user_id, following_id, timestamp, needs_approval))
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
def destroy(user_id, following_id):
    user_id = int(user_id)
    following_id = int(following_id)
    
    db = sqlConnection()
    cursor = db.cursor()
    
    query = ("DELETE FROM friends WHERE user_id = %d AND following_id = %d" %
            (user_id, following_id))
    cursor.execute(query)
    if cursor.rowcount > 0:
        result = "Success"
    else:
        result = "NA"
    
    cursor.close()
    db.commit()
    db.close()
    
    return result

###############################################################################
def exists(user_id, following_id):
    user_id = int(user_id)
    following_id = int(following_id)
    
    db = sqlConnection()
    cursor = db.cursor()
    
    query = ("SELECT * FROM friends WHERE user_id = %d AND following_id = %d" %
            (user_id, following_id))
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
def show(user_id, following_id):
    user_id = int(user_id)
    following_id = int(following_id)
    
    db = sqlConnection()
    cursor = db.cursor()
    
    query = ("""SELECT user_id, following_id, timestamp, approved 
            FROM friends WHERE user_id = %d AND following_id = %d""" %
            (user_id, following_id))
    cursor.execute(query)
    
    if cursor.rowcount > 0:
        data = cursor.fetchone()
        
        result = {}
        result['user_id'] = data[0]
        result['following_id'] = data[1]
        result['timestamp'] = data[2]
        result['approved'] = data[3]
        
    else:
        result = "NA"
        
    cursor.close()
    db.commit()
    db.close()
    
    return result

###############################################################################
def incoming(user_id):
    print 'To come'
    return

###############################################################################
def outgoing(user_id):
    print 'To come'
    return
    
