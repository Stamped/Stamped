import sys
import datetime
import gc
import MySQLdb

def sqlConnection():
    return MySQLdb.connect(user='root',db='stamped_api')

def setup():
    db=MySQLdb.connect(user='root')
    c=db.cursor() 
    c.execute('DROP DATABASE IF EXISTS stamped_api')
    c.execute('CREATE DATABASE stamped_api') 
    print 'stamped_api db created'
    c.close()

    db=MySQLdb.connect(user='root',db='stamped_api')
    c=db.cursor()

    q = """CREATE TABLE objects (
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
    c.execute(q)
    print 'objects table created'

    q = """CREATE TABLE stamps (
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
    c.execute(q)
    print 'stamps table created'

    q = """CREATE TABLE users (
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
    c.execute(q)
    print 'users table created'

    q = """CREATE TABLE friends (
            user_id INT NOT NULL, 
            follower_id INT NOT NULL, 
            timestamp DATETIME, 
            approved INT, 
            PRIMARY KEY(user_id, follower_id))"""
    c.execute(q)
    print 'friends table created'

    q = """CREATE TABLE userstamps (
            user_id INT NOT NULL, 
            stamp_id INT NOT NULL, 
            is_read INT, 
            is_starred INT, 
            is_stamped INT, 
            is_inbox INT, 
            is_transacted INT,
            PRIMARY KEY(user_id, stamp_id))"""
    c.execute(q)
    print 'userstamps table created'

    print 

    # Add some users
    c.executemany(
          """INSERT INTO users (email, username, name, privacy)
          VALUES (%s, %s, %s, %s)""",
          [
          ('kevin@stamped.com', 'kevinpalms', 'Kevin', 0),
          ('robby@stamped.com', 'robbystein', 'Robby', 0),
          ('bart@stamped.com', 'bartstein', 'Bart', 1),
          ('travis@stamped.com', 'travisfischer', 'Travis', 0)
          ])
          
    # And add some objects
    c.executemany(
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


    c.execute('SELECT * FROM users')
    result = c.fetchmany(3)
    for record in result:
        print record
    print

    c.execute('SELECT * FROM objects')
    result = c.fetchmany(3)
    for record in result:
        print record

    c.close()
    db.commit()
    db.close()

    print


    # Examples:
    # http://www.devshed.com/c/a/Python/MySQL-Connectivity-With-Python/3/
    # http://mysql-python.sourceforge.net/MySQLdb.html#mysqldb




def addStamp(uid, object_id, comment):
    print '--addStamp: %s %s %s' % (uid, object_id, comment)
    
    now = datetime.datetime(2009,5,5)
    str_now = now.date().isoformat()
    
    q = ("""INSERT INTO stamps (object_id, user_id, comment, timestamp)
            VALUES (%s, %s, '%s', '%s')""" %
         (uid, object_id, comment, str_now))
    db = sqlConnection()
    c = db.cursor() 
    c.execute(q)
    
    q = ("SELECT * FROM stamps WHERE stamp_id = %d" % (db.insert_id()))
    c.execute(q)
    result = c.fetchone()
    
    c.close()
    db.commit()
    db.close()
    
    return result
    



def getStampDetails(stamp_id):
    print '--getStampDetails: %s' % (stamp_id)
    
    db = sqlConnection()
    c = db.cursor() 
    
    q = ("""SELECT * FROM stamps
            JOIN objects ON stamps.object_id = objects.object_id
            WHERE stamps.stamp_id = %d""" %
         (int(stamp_id)))
    c.execute(q)
    data = c.fetchone()
    
    c.close()
    db.commit()
    db.close()
    
    result = {}
    result['object_id'] = data[0]
    
    return result



def main():
    if len(sys.argv) == 1:
        print 'usage: ./stamped-api.py {--setup | --addStamp} file'
        sys.exit(1)
    
    option = sys.argv[1]
    if option == '--setup':
        setup()
    elif option == '--addStamp':
        if len(sys.argv) < 5:
            print 'usage: ./stamped-api.py --addStamp uid object_id comment'
            sys.exit(1)
        c = addStamp(sys.argv[2], sys.argv[3], sys.argv[4])
        print 'Response: ', c
    elif option == '--getStampDetails':
        if len(sys.argv) < 3:
            print 'usage: ./stamped-api.py --getStampDetails stamp_id'
            sys.exit(1)
        c = getStampDetails(sys.argv[2])
        print 'Response: ', c
    else:
        print 'unknown option: ' + option
        sys.exit(1)

if __name__ == '__main__':
    main()




















