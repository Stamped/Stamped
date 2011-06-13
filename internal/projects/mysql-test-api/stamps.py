#!/usr/bin/env python

from datetime import datetime
import MySQLdb

###############################################################################
def sqlConnection():
    return MySQLdb.connect(user='root',db='stamped_api')
       
###############################################################################
def create(uid, entity_id, comment):
    str_now = datetime.now().isoformat()
    
    query = ("""INSERT INTO stamps (entity_id, user_id, comment, timestamp)
            VALUES (%s, %s, '%s', '%s')""" %
         (uid, entity_id, comment, str_now))
    db = sqlConnection()
    cursor = db.cursor() 
    cursor.execute(query)
    
    query = ("SELECT * FROM stamps WHERE stamp_id = %d" % (db.insert_id()))
    cursor.execute(query)
    result = cursor.fetchone()
    
    # Add functionality to create data in userstamps.....
    
    cursor.close()
    db.commit()
    db.close()
    
    return result

###############################################################################
def show(stamp_id):
    stamp_id = int(stamp_id)
    
    db = sqlConnection()
    cursor = db.cursor() 
    
    query = ("""SELECT 
                entities.entity_id,
                stamps.stamp_id,
                stamps.user_id,
                stamps.comment,
                stamps.image,
                entities.image,
                stamps.timestamp
            FROM stamps
            JOIN entities ON stamps.entity_id = entities.entity_id
            WHERE stamps.stamp_id = %d""" %
         (stamp_id))
    cursor.execute(query)
    
    if cursor.rowcount > 0:
        data = cursor.fetchone()
        
        result = {}
        result['entity_id'] = data[0]
        result['stamp_id'] = data[1]
        result['user_id'] = data[2]
        result['comment'] = data[3]
        if data[4]:
            result['image'] = data[4]
        else: 
            result['image'] = data[5]
        result['timestamp'] = data[6]
        
        # Comments
        commentsQuery = ("""SELECT 
                    users.name,
                    users.image,
                    users.user_id, 
                    comments.timestamp, 
                    comments.comment,
                    comments.comment_id
                FROM comments
                JOIN users ON comments.user_id = users.user_id
                WHERE comments.stamp_id = %d
                ORDER BY comments.timestamp ASC""" %
            (stamp_id))
        cursor.execute(commentsQuery)
        commentsData = cursor.fetchall()
        
        comments = []
        for commentData in commentsData:
            comment = {}
            comment['user_name'] = commentData[0]
            comment['user_image'] = commentData[1]
            comment['user_id'] = commentData[2]
            comment['timestamp'] = commentData[3]
            comment['comment'] = commentData[4]
            comment['comment_id'] = commentData[5]
            
            comments.append(comment)
            
        result['comment_thread'] = comments
        
        # Mentions        
        mentionsQuery = ("""SELECT 
                    users.name,
                    users.image,
                    users.user_id
                FROM mentions
                JOIN users ON mentions.user_id = users.user_id
                WHERE mentions.stamp_id = %d
                ORDER BY users.name ASC""" %
            (stamp_id))
        cursor.execute(mentionsQuery)
        mentionsData = cursor.fetchall()
        
        mentions = []
        for mentionData in mentionsData:
            mention = {}
            mention['user_name'] = mentionData[0]
            mention['user_image'] = mentionData[1]
            mention['user_id'] = mentionData[2]
            
            mentions.append(mention)
            
        result['mentions'] = mentions
        
    else: 
        result = "NA"
    
    cursor.close()
    db.commit()
    db.close()
    
    return result

###############################################################################
def destroy(stamp_id):
    stamp_id = int(stamp_id)
    
    db = sqlConnection()
    cursor = db.cursor()
    
    query = "DELETE FROM stamps WHERE stamp_id = %d" % (stamp_id)
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
def flag(stamp_id, is_flagged = 1):
    # This will ultimately need to be reworked, since 'flagged' will be a 
    # separate table and not just an attribute of the stamp.
    stamp_id = int(stamp_id)
    is_flagged = int(is_flagged)
    
    db = sqlConnection()
    cursor = db.cursor()
    
    query = ("UPDATE stamps SET flagged = %d WHERE stamp_id = %d" % 
            (is_flagged, stamp_id))
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
def read(stamp_id, user_id = 1, is_read = 1):
    # Remove 'user_id' as a parameter once we have authentication
    stamp_id = int(stamp_id)
    user_id = int(user_id)
    is_read = int(is_read)
    
    db = sqlConnection()
    cursor = db.cursor()
    
    existsQuery = ("""SELECT is_read FROM userstamps 
            WHERE user_id = %d AND stamp_id = %d""" % 
            (user_id, stamp_id))
    cursor.execute(existsQuery)
    
    if cursor.rowcount == 0:
        query = ("""INSERT INTO userstamps (user_id, stamp_id, is_read) 
                VALUES (%d, %d, %d)""" %
                (user_id, stamp_id, is_read))
        cursor.execute(query)
        
        if cursor.rowcount > 0:
            result = "Success"
        else:
            result = "NA"                
                
    else:
        resultData = cursor.fetchone()
        
        if resultData[0] <> is_read:
            query = ("""UPDATE userstamps SET is_read = %d
                    WHERE user_id = %d AND stamp_id = %d""" %
                    (is_read, user_id, stamp_id))
            cursor.execute(query)
            
            if cursor.rowcount > 0:
                result = "Success"
            else:
                result = "NA" 
        
        else:
            result = "NA (Unnecessary)"
    
    cursor.close()
    db.commit()
    db.close()
    
    return result
    
    






