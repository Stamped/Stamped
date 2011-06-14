#!/usr/bin/env python

from datetime import datetime
import MySQLdb

###############################################################################
def sqlConnection():
    return MySQLdb.connect(user='root',db='stamped_api')

###############################################################################
def verify_credentials(email, password):
    # Temporarily set to "True" for everything
    return True

###############################################################################
def settings(user_id):
    user_id = int(user_id)
    
    db = sqlConnection()
    cursor = db.cursor() 
    
    query = ("""SELECT 
                users.user_id,
                users.email,
                users.password,
                users.privacy,
                users.locale,
                users.timezone
            FROM users
            WHERE users.user_id = %d""" %
         (user_id))
    cursor.execute(query)
    
    if cursor.rowcount > 0:
        data = cursor.fetchone()
        
        result = {}
        result['user_id'] = data[0]
        result['email'] = data[1]
        result['password'] = data[2]
        result['privacy'] = data[3]
        result['locale'] = data[4]
        result['timezone'] = data[5]

    else: 
        result = "NA"
    
    cursor.close()
    db.commit()
    db.close()
    
    return result

###############################################################################
def update_settings(user_id, email, password, privacy, locale, timezone):
    # Might want to rename to 'settings' and differentiate between GET and 
    # POST a la Twitter. But I'm renaming it to 'update_settings' for now.
    user_id = int(user_id)
    privacy = int(privacy)
    
    db = sqlConnection()
    cursor = db.cursor() 
    
    query = ("""UPDATE users SET
                users.email = '%s',
                users.password = '%s',
                users.privacy = %d,
                users.locale = '%s',
                users.timezone = '%s'
            WHERE users.user_id = %d""" %
         (email, password, privacy, locale, timezone, user_id))
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
def update_profile(user_id, username, name, bio, website, image):
    user_id = int(user_id)
    
    db = sqlConnection()
    cursor = db.cursor() 
    
    query = ("""UPDATE users SET
                users.username = '%s',
                users.name = '%s',
                users.bio = '%s',
                users.website = '%s',
                users.image = '%s'
            WHERE users.user_id = %d""" %
         (username, name, bio, website, image, user_id))
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
def create(email, password, username, name, privacy):
    privacy = int(privacy)
    
    db = sqlConnection()
    cursor = db.cursor() 
    
    exists = ("""SELECT user_id FROM users
            WHERE username = '%s' OR email = '%s'""" %
         (username, email))
    cursor.execute(exists)
    
    if cursor.rowcount > 0:
        result = "NA"
    else:
        query = ("""INSERT 
                INTO users (email, name, username, password, privacy)
                VALUES ('%s', '%s', '%s', '%s', %d)""" %
                (email, name, username, password, privacy))
        data = cursor.execute(query)
        
        if cursor.rowcount > 0:
            result = "Success"
        else:
            result = "NA"
    
    cursor.close()
    db.commit()
    db.close()
    
    return result
    
