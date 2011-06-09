import sys
from datetime import datetime
import gc
import MySQLdb

###############################################################################
def sqlConnection():
    return MySQLdb.connect(user='root',db='stamped_api')

###############################################################################
def setup():
    db = MySQLdb.connect(user='root')
    cursor = db.cursor() 
    cursor.execute('DROP DATABASE IF EXISTS stamped_api')
    cursor.execute('CREATE DATABASE stamped_api') 
    print 'stamped_api db created'
    cursor.close()

    db = MySQLdb.connect(user='root',db='stamped_api')
    cursor = db.cursor()

    query = """CREATE TABLE objects (
            object_id INT NOT NULL AUTO_INCREMENT, 
            title VARCHAR(100), 
            description TEXT, 
            category VARCHAR(50), 
            image VARCHAR(100), 
            source VARCHAR(50), 
            location VARCHAR(100), 
            locale VARCHAR(100),
            affiliate VARCHAR(100),
            date_created DATETIME,
            date_updated DATETIME, 
            PRIMARY KEY(object_id))"""
    cursor.execute(query)
    print 'objects table created'

    query = """CREATE TABLE stamps (
            stamp_id INT NOT NULL AUTO_INCREMENT, 
            object_id INT, 
            user_id INT, 
            comment VARCHAR(250), 
            comment_thread VARCHAR(250),
            image VARCHAR(100), 
            timestamp DATETIME, 
            mention VARCHAR(100),
            flagged INT,
            PRIMARY KEY(stamp_id))"""
    cursor.execute(query)
    print 'stamps table created'

    query = """CREATE TABLE users (
            user_id INT NOT NULL AUTO_INCREMENT, 
            email VARCHAR(100), 
            username VARCHAR(20), 
            name VARCHAR(50), 
            password VARCHAR(20), 
            bio TEXT, 
            website VARCHAR(250),
            image VARCHAR(100),
            privacy INT, 
            account VARCHAR(100),
            flagged INT,
            locale VARCHAR(100),
            timezone VARCHAR(10),
            PRIMARY KEY(user_id))"""
    cursor.execute(query)
    print 'users table created'

    query = """CREATE TABLE friends (
            user_id INT NOT NULL, 
            follower_id INT NOT NULL, 
            timestamp DATETIME, 
            approved INT, 
            PRIMARY KEY(user_id, follower_id))"""
    cursor.execute(query)
    print 'friends table created'

    query = """CREATE TABLE userstamps (
            user_id INT NOT NULL, 
            stamp_id INT NOT NULL, 
            is_read INT, 
            is_starred INT, 
            is_stamped INT, 
            is_inbox INT, 
            is_transacted INT,
            PRIMARY KEY(user_id, stamp_id))"""
    cursor.execute(query)
    print 'userstamps table created'

    query = """CREATE TABLE comments (
            comment_id INT NOT NULL AUTO_INCREMENT, 
            user_id INT NOT NULL, 
            stamp_id INT NOT NULL, 
            timestamp DATETIME, 
            comment VARCHAR(250),
            PRIMARY KEY(comment_id))"""
    cursor.execute(query)
    print 'userstamps table created'

    print 

    # Add some users
    cursor.executemany(
          """INSERT INTO users (email, username, name, privacy)
          VALUES (%s, %s, %s, %s)""",
          [
          ('kevin@stamped.com', 'kevinpalms', 'Kevin', 0),
          ('robby@stamped.com', 'robbystein', 'Robby', 0),
          ('bart@stamped.com', 'bartstein', 'Bart', 1),
          ('travis@stamped.com', 'travisfischer', 'Travis', 0)
          ])
          
    # And add some objects
    cursor.executemany(
          """INSERT INTO objects (title, category, source)
          VALUES (%s, %s, %s)""",
          [
          ('Kanye West - Family Business', 'Music', 'iTunes'),
          ('The Fray - Vienna', 'Music', 'iTunes'),
          ('The Killers - All These Things That I\'ve Done', 'Music', 'iTunes'),
          ('Earth Wind & Fire - September', 'Music', 'iTunes'),
          ('Jay-Z - Lucifer', 'Music', 'iTunes'),
          ('The Beatles - Here Comes The Sun', 'Music', 'iTunes'),
          ('U2 - City of Blinding Lights', 'Music', 'iTunes'),
          ('Chris Brown - Beautiful People', 'Music', 'iTunes'),
          ('John Legend - It Don\'t Have To Change', 'Music', 'iTunes')
          ])


    cursor.execute('SELECT * FROM users')
    result = cursor.fetchmany(3)
    for record in result:
        print record
    print

    cursor.execute('SELECT * FROM objects')
    result = cursor.fetchmany(3)
    for record in result:
        print record

    cursor.close()
    db.commit()
    db.close()

    print


    # Examples:
    # http://www.devshed.com/c/a/Python/MySQL-Connectivity-With-Python/3/
    # http://mysql-python.sourceforge.net/MySQLdb.html#mysqldb



###############################################################################
def addStamp(uid, object_id, comment):
    print '--addStamp: %s %s %s' % (uid, object_id, comment)
    
    str_now = datetime.now().isoformat()
    
    query = ("""INSERT INTO stamps (object_id, user_id, comment, timestamp)
            VALUES (%s, %s, '%s', '%s')""" %
         (uid, object_id, comment, str_now))
    db = sqlConnection()
    cursor = db.cursor() 
    cursor.execute(query)
    
    query = ("SELECT * FROM stamps WHERE stamp_id = %d" % (db.insert_id()))
    cursor.execute(query)
    result = cursor.fetchone()
    
    cursor.close()
    db.commit()
    db.close()
    
    return result

###############################################################################
def getStampFromId(stamp_id):
    stamp_id = int(stamp_id)
    print '--getStampDetails: %s' % (stamp_id)
    
    db = sqlConnection()
    cursor = db.cursor() 
    
    query = ("""SELECT 
                objects.object_id,
                stamps.stamp_id,
                stamps.user_id,
                stamps.comment,
                stamps.image,
                objects.image,
                stamps.timestamp
            FROM stamps
            JOIN objects ON stamps.object_id = objects.object_id
            WHERE stamps.stamp_id = %d""" %
         (stamp_id))
    cursor.execute(query)
    
    if cursor.rowcount > 0:
        data = cursor.fetchone()
        
        result = {}
        result['object_id'] = data[0]
        result['stamp_id'] = data[1]
        result['user_id'] = data[2]
        result['comment'] = data[3]
        if data[4]:
            result['image'] = data[4]
        else: 
            result['image'] = data[5]
        result['timestamp'] = data[6]
        
        query = ("""SELECT 
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
        cursor.execute(query)
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
        
    else: 
        result = "NA"
    
    cursor.close()
    db.commit()
    db.close()
    
    return result

###############################################################################
def removeStamp(stamp_id):
    stamp_id = int(stamp_id)
    print '--removeStamp: %d' % (stamp_id)
    
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
def addCommentToStamp(user_id, stamp_id, comment):
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
    print '--removeStamp: %s' % (comment_id)
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
def checkNumberOfArguments(expected, length):
    if length < expected + 2:
        print 'Missing parameters'
        sys.exit(1)

###############################################################################
def main():
    if len(sys.argv) == 1:
        print 'usage: ./stamped-api.py {--setup | --addStamp | ' \
            '--getStampFromId | --removeStamp} file'
        sys.exit(1)
    
    option = sys.argv[1]
    if option == '--setup':
        setup()
        
    elif option == '--addStamp':
        if len(sys.argv) < 5:
            print 'usage: ./stamped-api.py --addStamp uid object_id comment'
            sys.exit(1)
        response = addStamp(sys.argv[2], sys.argv[3], sys.argv[4])
        print 'Response: ', response
        
    elif option == '--getStampFromId':
        if len(sys.argv) < 3:
            print 'usage: ./stamped-api.py --getStampDetails stamp_id'
            sys.exit(1)
        response = getStampFromId(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--removeStamp':
        checkNumberOfArguments(1, len(sys.argv))
        response = removeStamp(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--addCommentToStamp':
        checkNumberOfArguments(3, len(sys.argv))
        response = addCommentToStamp(sys.argv[2], sys.argv[3], sys.argv[4])
        print 'Response: ', response
        
    else:
        print 'unknown option: ' + option
        sys.exit(1)


if __name__ == '__main__':
    main()




















