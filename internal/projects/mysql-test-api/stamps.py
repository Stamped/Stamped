#!/usr/bin/env python

from datetime import datetime
from dbconn import MySQLConnection
    
class Stamp(MySQLConnection):

    def __init__(self):
        self.database = self.connectDatabase()

    ###########################################################################
    def create(self, uid, entity_id, comment):
        uid = int(uid)
        entity_id = int(entity_id)
        str_now = datetime.now().isoformat()
        
        cursor = self.getDatabase().cursor()
        
        query = ("""INSERT INTO stamps (entity_id, user_id, comment, timestamp)
                VALUES (%d, %d, '%s', '%s')""" %
             (uid, entity_id, comment, str_now))
        cursor.execute(query)
        
        if cursor.rowcount > 0:
            stamp_id = self.database.insert_id()
            
            followerInsert = ("""INSERT 
                    INTO userstamps (
                        user_id, 
                        stamp_id, 
                        is_read, 
                        is_starred, 
                        is_stamped, 
                        is_inbox, 
                        is_transacted
                    )
                    SELECT user_id, %d, 0, 0, 0, 1, 0
                    FROM friends
                    WHERE following_id = %d""" %
                    (stamp_id, uid))
            cursor.execute(followerInsert)
            if cursor.rowcount > 0:
                result = "Success"
            else:
                result = "Warning: No followers"
        else:
            result = "NA"
        
        cursor.close()
        self.closeDatabase()
        
        return result

    ###########################################################################
    def show(self, stamp_id):
        stamp_id = int(stamp_id)
        
        cursor = self.getDatabase().cursor() 
        
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
        self.closeDatabase()
        
        return result

    ###########################################################################
    def destroy(self, stamp_id):
        stamp_id = int(stamp_id)
        
        cursor = self.getDatabase().cursor()
        
        query = "DELETE FROM stamps WHERE stamp_id = %d" % (stamp_id)
        cursor.execute(query)
        if cursor.rowcount > 0:
            result = "Success"
        else:
            result = "NA"
        
        cursor.close()
        self.closeDatabase()
        
        return result
    
    ###########################################################################
    def flag(self, stamp_id, is_flagged = 1):
        # This will ultimately need to be reworked, since 'flagged' will be a 
        # separate table and not just an attribute of the stamp.
        stamp_id = int(stamp_id)
        is_flagged = int(is_flagged)
        
        cursor = self.getDatabase().cursor()
        
        query = ("UPDATE stamps SET flagged = %d WHERE stamp_id = %d" % 
                (is_flagged, stamp_id))
        cursor.execute(query)
        if cursor.rowcount > 0:
            result = "Success"
        else:
            result = "NA"
        
        cursor.close()
        self.closeDatabase()
        
        return result
    
    ###########################################################################
    def read(self, stamp_id, user_id = 1, is_read = 1):
        # Remove 'user_id' as a parameter once we have authentication
        stamp_id = int(stamp_id)
        user_id = int(user_id)
        is_read = int(is_read)
        
        cursor = self.getDatabase().cursor()
        
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
        self.closeDatabase()
        
        return result