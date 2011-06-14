#!/usr/bin/env python

from datetime import datetime
import MySQLdb

###############################################################################
def sqlConnection():
    return MySQLdb.connect(user='root',db='stamped_api')

###############################################################################
def show(user_id):
    user_id = int(user_id)
    
    db = sqlConnection()
    cursor = db.cursor() 
    
    query = ("""SELECT 
                users.user_id,
                users.name,
                users.email,
                users.image,
                users.username,
                users.bio,
                users.website
            FROM users
            WHERE users.user_id = %d""" %
         (user_id))
    cursor.execute(query)
    
    if cursor.rowcount > 0:
        data = cursor.fetchone()
        
        result = {}
        result['user_id'] = data[0]
        result['name'] = data[1]
        result['email'] = data[2]
        result['image'] = data[3]
        result['username'] = data[4]
        result['bio'] = data[5]
        result['website'] = data[6]

    else: 
        result = "NA"
    
    cursor.close()
    db.commit()
    db.close()
    
    return result

###############################################################################
def lookup(user_ids):
    if not isinstance(user_ids, basestring):
        print user_ids
        result = []
        for user_id in user_ids:
            result.append(show(user_id))
    else: 
        result = "NA"
    
    return result

###############################################################################
def search(query):
    # This needs to be changed to a fulltext search. Using the 'match' algo
    # for now.
    db = sqlConnection()
    cursor = db.cursor()
    
    query = ("""SELECT user_id, name, username, email
            FROM users
            WHERE LEFT(name, %d) = '%s'
                OR LEFT(username, %d) = '%s'
                OR LEFT(email, %d) = '%s'
            ORDER BY email ASC, username ASC, name ASC
            LIMIT 0, 10""" % 
            (len(query), query, len(query), query, len(query), query))
    cursor.execute(query)
    
    resultData = cursor.fetchmany(10)
    result = []
    for recordData in resultData:
        record = {}
        record['user_id'] = recordData[0]
        record['name'] = recordData[1]
        record['username'] = recordData[2]
        record['email'] = recordData[3]
        result.append(record)
        
    return result

###############################################################################
def flag(user_id, is_flagged = 1):
    # This will ultimately need to be reworked, since 'flagged' will be a 
    # separate table and not just an attribute of the user.
    user_id = int(user_id)
    is_flagged = int(is_flagged)
    
    db = sqlConnection()
    cursor = db.cursor()
    
    query = ("UPDATE users SET flagged = %d WHERE user_id = %d" % 
            (is_flagged, user_id))
    cursor.execute(query)
    if cursor.rowcount > 0:
        result = "Success"
    else:
        result = "NA"
    
    cursor.close()
    db.commit()
    db.close()
    
    return result