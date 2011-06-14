#!/usr/bin/env python

import MySQLdb

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

    query = """CREATE TABLE entities (
            entity_id INT NOT NULL AUTO_INCREMENT, 
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
            PRIMARY KEY(entity_id))"""
    cursor.execute(query)
    print 'entities table created'

    query = """CREATE TABLE stamps (
            stamp_id INT NOT NULL AUTO_INCREMENT, 
            entity_id INT, 
            user_id INT, 
            comment VARCHAR(250), 
            image VARCHAR(100), 
            flagged INT,
            timestamp DATETIME, 
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
            following_id INT NOT NULL, 
            timestamp DATETIME, 
            approved INT, 
            PRIMARY KEY(user_id, following_id))"""
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
            flagged INT,
            PRIMARY KEY(comment_id))"""
    cursor.execute(query)
    print 'comments table created'

    query = """CREATE TABLE mentions ( 
            stamp_id INT NOT NULL, 
            user_id INT NOT NULL, 
            timestamp DATETIME, 
            PRIMARY KEY(stamp_id, user_id))"""
    cursor.execute(query)
    print 'mentions table created'

    query = """CREATE TABLE blocks ( 
            user_id INT NOT NULL, 
            follower_id INT NOT NULL, 
            timestamp DATETIME, 
            PRIMARY KEY(user_id, follower_id))"""
    cursor.execute(query)
    print 'blocks table created'

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
          
    # And add some entities
    cursor.executemany(
          """INSERT INTO entities (title, category, source)
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

    cursor.execute('SELECT * FROM entities')
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
