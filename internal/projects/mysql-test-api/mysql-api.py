#!/usr/bin/python

import sys
from datetime import datetime
import gc
import MySQLdb

import setup
import stamps

###############################################################################
def sqlConnection():
    return MySQLdb.connect(user='root',db='stamped_api')




###############################################################################
def listObjectsForAutocomplete(query):
    print '--listObjectsForAutocomplete: %s' % (query)
    
    query = ("""SELECT object_id, title, category, image
            FROM objects
            WHERE LEFT(title, %d) = '%s'
            ORDER BY title ASC
            LIMIT 0, 10""" % (len(query), query))
    db = sqlConnection()
    cursor = db.cursor()
    cursor.execute(query)
    resultData = cursor.fetchmany(10)
    
    result = []
    for recordData in resultData:
        record = {}
        record['object_id'] = recordData[0]
        record['title'] = recordData[1]
        record['category'] = recordData[2]
        record['image'] = recordData[3]
        result.append(record)
        
    return result
 
###############################################################################
def addCommentToThread(user_id, stamp_id, comment):
    print '--addCommentToStmp: %s %s %s' % (user_id, stamp_id, comment)
    
    user_id = int(user_id)
    stamp_id = int(stamp_id)
    
    str_now = datetime.now().isoformat()
    
    query = ("""INSERT INTO comments (user_id, stamp_id, comment, timestamp)
            VALUES (%s, %s, '%s', '%s')""" %
         (user_id, stamp_id, comment, str_now))
    db = sqlConnection()
    cursor = db.cursor() 
    cursor.execute(query)
    
    query = ("SELECT * FROM comments WHERE comment_id = %d" % (db.insert_id()))
    cursor.execute(query)
    result = cursor.fetchone()
    
    cursor.close()
    db.commit()
    db.close()
    
    return result

###############################################################################
def removeComment(comment_id):
    print '--removeComment: %s' % (comment_id)
    comment_id = int(comment_id)
    
    db = sqlConnection()
    cursor = db.cursor()
    
    query = "DELETE FROM comments WHERE comment_id = %d" % (comment_id)
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
def addMentionToStamp(stamp_id, user_id):
    stamp_id = int(stamp_id)
    user_id = int(user_id)
    str_now = datetime.now().isoformat()
    
    db = sqlConnection()
    cursor = db.cursor()
    
    query = ("SELECT * FROM mentions WHERE user_id = %d AND stamp_id = %d" %
            (user_id, stamp_id))
    cursor.execute(query)
    if cursor.rowcount == 0:
        insertQuery = ("""INSERT INTO mentions (stamp_id, user_id, timestamp)
                VALUES (%d, %d, '%s')""" % (stamp_id, user_id, str_now))
        cursor.execute(insertQuery)
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
def removeMentionFromStamp(stamp_id, user_id):
    stamp_id = int(stamp_id)
    user_id = int(user_id)
    
    db = sqlConnection()
    cursor = db.cursor()
    
    query = ("DELETE FROM mentions WHERE stamp_id = %d AND user_id = %d" % 
            (stamp_id, user_id))
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
def getStampsFromUser(user_id):
    user_id = int(user_id)
    
    db = sqlConnection()
    cursor = db.cursor()
    
    query = ("""SELECT 
            objects.object_id,
            stamps.stamp_id,
            stamps.user_id,
            stamps.comment,
            stamps.image,
            objects.image,
            stamps.timestamp,
            users.name,
            users.image
        FROM stamps
        JOIN objects ON stamps.object_id = objects.object_id
        JOIN users ON stamps.user_id = users.user_id
        WHERE users.user_id = %d
        ORDER BY stamps.timestamp DESC""" %
        (user_id))
    cursor.execute(query)
    resultData = cursor.fetchmany(10)
    
    result = []
    for recordData in resultData:
        record = {}
        record['object_id'] = recordData[0]
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

###############################################################################
def addFriendship(uid, user_id):
    uid = int(uid)
    user_id = int(user_id)
    str_now = datetime.now().isoformat()
    
    db = sqlConnection()
    cursor = db.cursor()
    
    if not checkFriendship(uid, user_id):
        privacyQuery = ("SELECT privacy FROM users WHERE user_id = %d" % 
                (user_id))
        cursor.execute(privacyQuery)
        record = cursor.fetchone()
        print record
        if record[0] == 1:
            needsApproval = 1
        else:
            needsApproval = 0
        
        query = ("""INSERT 
                INTO friends (user_id, following_id, timestamp, approved)
                VALUES (%d, %d, '%s', %d)""" %
                (uid, user_id, str_now, needsApproval))
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
def checkFriendship(uid, user_id):
    uid = int(uid)
    user_id = int(user_id)
    
    db = sqlConnection()
    cursor = db.cursor()
    
    query = ("SELECT * FROM friends WHERE user_id = %d AND following_id = %d" %
            (uid, user_id))
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
def getFriends(user_id):
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

###############################################################################
def getFollowers(user_id):
    user_id = int(user_id)
    
    db = sqlConnection()
    cursor = db.cursor()

    query = "SELECT user_id FROM friends WHERE following_id = %d" % (user_id)
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
def checkNumberOfArguments(expected, length):
    if length < expected + 2:
        print 'Missing parameters'
        sys.exit(1)

###############################################################################
def main():
    if len(sys.argv) == 1:
        print 'Available Functions:'
        print '  --setup'
        print '  --addStamp (uid, object_id, comment)'
        print '  --getStampFromId (stamp_id)'
        print '  --removeStamp (stamp_id)'
        print '  --addCommentToThread (user_id, stamp_id, comment)'
        print '  --removeComment (comment_id)'
        print '  --listObjectsForAutocomplete (query)'
        print '  --addMentionToStamp (stamp_id, user_id)'
        print '  --removeMentionFromStamp (stamp_id, user_id)'
        print '  --getStampsFromUser (user_id)'
        print '  --addFriendship (uid, user_id)'
        print '  --checkFriendship (uid, user_id)'
        print '  --getFriends (user_id)'
        print '  --getFollowers (user_id)'
        sys.exit(1)
    
    option = sys.argv[1]
    
    # Setup:
    if option == '--setup':
        setup.setup()
        
    # Stamps:
    elif option == '--stamps/create':
        checkNumberOfArguments(3, len(sys.argv))
        response = stamps.create(sys.argv[2], sys.argv[3], sys.argv[4])
        print 'Response: ', response
        
    elif option == '--stamps/show':
        checkNumberOfArguments(1, len(sys.argv))
        response = stamps.show(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--stamps/destroy':
        checkNumberOfArguments(1, len(sys.argv))
        response = stamps.destroy(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--stamps/flag':
        checkNumberOfArguments(1, len(sys.argv))
        response = stamps.flag(sys.argv[2])
        print 'Response: ', response
    
        
    elif option == '--addCommentToThread':
        checkNumberOfArguments(3, len(sys.argv))
        response = addCommentToThread(sys.argv[2], sys.argv[3], sys.argv[4])
        print 'Response: ', response
        
    elif option == '--removeComment':
        checkNumberOfArguments(1, len(sys.argv))
        response = removeComment(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--listObjectsForAutocomplete':
        checkNumberOfArguments(1, len(sys.argv))
        response = listObjectsForAutocomplete(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--addMentionToStamp':
        checkNumberOfArguments(2, len(sys.argv))
        response = addMentionToStamp(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
    elif option == '--removeMentionFromStamp':
        checkNumberOfArguments(2, len(sys.argv))
        response = removeMentionFromStamp(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
    elif option == '--getStampsFromUser':
        checkNumberOfArguments(1, len(sys.argv))
        response = getStampsFromUser(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--addFriendship':
        checkNumberOfArguments(2, len(sys.argv))
        response = addFriendship(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
    elif option == '--checkFriendship':
        checkNumberOfArguments(2, len(sys.argv))
        response = checkFriendship(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
    elif option == '--getFriends':
        checkNumberOfArguments(1, len(sys.argv))
        response = getFriends(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--getFollowers':
        checkNumberOfArguments(1, len(sys.argv))
        response = getFollowers(sys.argv[2])
        print 'Response: ', response
        
        
    else:
        print 'unknown option: ' + option
        sys.exit(1)


if __name__ == '__main__':
    main()




















