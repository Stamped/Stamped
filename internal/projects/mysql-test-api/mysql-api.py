#!/usr/bin/env python

import sys
from datetime import datetime
import gc
import MySQLdb

import setup
import entities
import stamps
import conversation
import mentions
import collections

###############################################################################
def sqlConnection():
    return MySQLdb.connect(user='root',db='stamped_api')


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
        print
        print '  --entities/show (entity_id)'
        print '  --entities/create (title, category)'
        print '  --entities/destroy (entity_id)'
        print '  --entities/update (entity_id, title, category)'
        print '  --entities/match (query)'
        print
        print '  --stamps/create (uid, entity_id, comment)'
        print '  --stamps/show (stamp_id)'
        print '  --stamps/destroy (stamp_id)'
        print '  --stamps/flag (stamp_id, [is_flagged])'
        print '  --stamps/read (stamp_id, [user_id], [is_read])'
        print 
        print '  --conversation/show (comment_id)'
        print '  --conversation/create (user_id, stamp_id, comment)'
        print '  --conversation/destroy (comment_id)'
        print '  --conversation/flag (comment_id, [is_flagged])'
        print
        print '  --mentions/create (stamp_id, user_id)'
        print '  --mentions/destroy (stamp_id, user_id)'
        print '  --mentions/user (user_id)'
        print 
        print '  --collections/inbox (user_id)'
        print '  --collections/user (user_id)'
        print '  --collections/add_stamp (stamp_id)'
        print
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
        
        
    # Entities:
    elif option == '--entities/show':
        checkNumberOfArguments(1, len(sys.argv))
        response = entities.show(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--entities/create':
        checkNumberOfArguments(2, len(sys.argv))
        response = entities.create(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
    elif option == '--entities/destroy':
        checkNumberOfArguments(1, len(sys.argv))
        response = entities.destroy(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--entities/update':
        checkNumberOfArguments(3, len(sys.argv))
        response = entities.update(sys.argv[2], sys.argv[3], sys.argv[4])
        print 'Response: ', response
        
    elif option == '--entities/match':
        checkNumberOfArguments(1, len(sys.argv))
        response = entities.match(sys.argv[2])
        print 'Response: ', response
        
        
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
        if len(sys.argv) == 4:
            response = stamps.read(sys.argv[2], sys.argv[3])
        elif len(sys.argv) == 3:
            response = stamps.read(sys.argv[2])
        else:
            print 'Missing parameters'
            sys.exit(1)
        print 'Response: ', response
        
    elif option == '--stamps/read':
        if len(sys.argv) == 5:
            response = stamps.read(sys.argv[2], sys.argv[3], sys.argv[4])
        elif len(sys.argv) == 4:
            response = stamps.read(sys.argv[2], sys.argv[3])
        elif len(sys.argv) == 3:
            response = stamps.read(sys.argv[2])
        else:
            print 'Missing parameters'
            sys.exit(1)
        print 'Response: ', response
        
        
    # Conversation:
    elif option == '--conversation/show':
        checkNumberOfArguments(1, len(sys.argv))
        response = conversation.show(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--conversation/create':
        checkNumberOfArguments(3, len(sys.argv))
        response = conversation.create(sys.argv[2], sys.argv[3], sys.argv[4])
        print 'Response: ', response
        
    elif option == '--conversation/destroy':
        checkNumberOfArguments(1, len(sys.argv))
        response = conversation.destroy(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--conversation/flag':
        if len(sys.argv) == 4:
            response = conversation.flag(sys.argv[2], sys.argv[3])
        elif len(sys.argv) == 3:
            response = conversation.flag(sys.argv[2])
        else:
            print 'Missing parameters'
            sys.exit(1)
        print 'Response: ', response
        
    
    # Mentions:
    elif option == '--mentions/create':
        checkNumberOfArguments(2, len(sys.argv))
        response = mentions.create(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
    elif option == '--mentions/destroy':
        checkNumberOfArguments(2, len(sys.argv))
        response = mentions.destroy(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
    elif option == '--mentions/user':
        checkNumberOfArguments(1, len(sys.argv))
        response = mentions.user(sys.argv[2])
        print 'Response: ', response
        
    
        
        
    # Collections:
    elif option == '--collections/inbox':
        checkNumberOfArguments(1, len(sys.argv))
        response = collections.inbox(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--collections/user':
        checkNumberOfArguments(1, len(sys.argv))
        response = collections.user(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--collections/add_stamp':
        checkNumberOfArguments(1, len(sys.argv))
        response = collections.add_stamp(sys.argv[2])
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




















