#!/usr/bin/env python

import MySQLdb

###############################################################################
def sqlConnection():
    return MySQLdb.connect(user='root',db='stamped_api')

###############################################################################
def ids(user_id):
    user_id = int(user_id)
    
    db = sqlConnection()
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