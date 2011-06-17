#!/usr/bin/env python

import MySQLdb

from account import Account
from blocks import Block
from users import User
from friends import Friend
from followers import Follower
from friendships import Friendship
from entities import Entity
from stamps import Stamp
from conversation import Conversation
from mentions import Mention
from collections import Collection
from favorites import Favorite

###############################################################################
def createDatabase(database):
    print
    print '## Creating Database:'
    
    db = MySQLdb.connect(user='root')
    cursor = db.cursor() 
    cursor.execute('DROP DATABASE IF EXISTS %s' % database)
    cursor.execute('CREATE DATABASE %s' % database) 
    print '%s db created' % database

    cursor.close()
    db.commit()
    db.close()
    
    return

###############################################################################
def createTables(database):
    print 
    print '## Creating Tables:'
    
    db = MySQLdb.connect(user='root',db=database)
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

    query = "CREATE INDEX ix_title ON entities (title)"
    cursor.execute(query)
    print 'index for entities.title created'

    query = "CREATE INDEX ix_category ON entities (category)"
    cursor.execute(query)
    print 'index for entities.category created'
    

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

    query = "CREATE INDEX ix_user ON stamps (user_id, entity_id, timestamp)"
    cursor.execute(query)
    print 'index for stamps.user/entity/timestamp created'
    

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

    query = "CREATE INDEX ix_email ON users (email)"
    cursor.execute(query)
    print 'index for users.email created'
    

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

    query = "CREATE INDEX ix_inbox ON userstamps (user_id, is_inbox)"
    cursor.execute(query)
    print 'index for userstamps.user/inbox created'
    

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

    query = "CREATE INDEX ix_stamp ON comments (stamp_id, user_id, timestamp)"
    cursor.execute(query)
    print 'index for comments.stamp/user/timestamp created'
    

    query = """CREATE TABLE mentions ( 
            stamp_id INT NOT NULL, 
            user_id INT NOT NULL, 
            timestamp DATETIME, 
            PRIMARY KEY(user_id, stamp_id))"""
    cursor.execute(query)
    print 'mentions table created'
    

    query = """CREATE TABLE blocks ( 
            user_id INT NOT NULL, 
            follower_id INT NOT NULL, 
            timestamp DATETIME, 
            PRIMARY KEY(user_id, follower_id))"""
    cursor.execute(query)
    print 'blocks table created'

    cursor.close()
    db.commit()
    db.close()
    
    return

###############################################################################
def sampleUsers(database = 'stamped_api'):
    db = MySQLdb.connect(user='root',db=database)
    cursor = db.cursor()
    
    print
    print '## Creating Sample Users'
    # email, password, username, name, privacy
    Account().create('kevin@stamped.com', 'asdf', 'kevinpalms', 'Kevin', 0)
    Account().create('robby@stamped.com', 'asdf', 'robbystein', 'Robby', 0)
    Account().create('bart@stamped.com', 'asdf', 'bartstein', 'Bart', 1)
    Account().create('travis@stamped.com', 'asdf', 'travisfischer', 'Travis', 0)
    
    cursor.execute('SELECT * FROM users')
    result = cursor.fetchall()
    for record in result:
        print record
    print
    
    cursor.close()
    db.commit()
    db.close()
    
    return

###############################################################################
def sampleEntities(database = 'stamped_api'):
    db = MySQLdb.connect(user='root',db=database)
    cursor = db.cursor()
    
    print 
    print '## Creating Sample Entities'
    # title, category
    Entity().create('Kanye West - Family Business', 'Music')
    Entity().create('The Fray - Vienna', 'Music')
    Entity().create('The Killers - All These Things That I\'ve Done', 'Music')
    Entity().create('Earth Wind & Fire - September', 'Music')
    Entity().create('Jay-Z - Lucifer', 'Music')
    Entity().create('The Beatles - Here Comes The Sun', 'Music')
    Entity().create('U2 - City of Blinding Lights', 'Music')
    Entity().create('Chris Brown - Beautiful People', 'Music')
    Entity().create('John Legend - It Don\'t Have To Change', 'Music')
    
    cursor.execute('SELECT * FROM entities')
    result = cursor.fetchall()
    for record in result:
        print record
    
    cursor.close()
    db.commit()
    db.close()
    
    return

###############################################################################
def sampleFriendships(database = 'stamped_api'):
    db = MySQLdb.connect(user='root',db=database)
    cursor = db.cursor()
    
    print 
    print '## Creating Sample Friendships'
    Friendship().create(1, 2)
    Friendship().create(1, 3)
    Friendship().create(2, 1)
    Friendship().create(4, 2)
    
    cursor.execute('SELECT * FROM friends')
    result = cursor.fetchall()
    for record in result:
        print record
    
    cursor.close()
    db.commit()
    db.close()
    
    return

###############################################################################
def sampleStamps(database = 'stamped_api'):
    db = MySQLdb.connect(user='root',db=database)
    cursor = db.cursor()
    
    print 
    print '## Creating Sample Stamps'
    Stamp().create(1, 1, 'I love this song')
    Stamp().create(2, 3, 'Reminds me of college...')
    Stamp().create(2, 1, 'Kanye is the shit')
    Stamp().create(4, 2, 'La la la')
    
    cursor.execute('SELECT * FROM stamps')
    result = cursor.fetchall()
    for record in result:
        print record
    
    cursor.close()
    db.commit()
    db.close()
    
    return

###############################################################################
def testFriendships():
    print '## Test: Friendship'
    
    print './mysql-api.py --friendships/create 2 3'
    print Friendship().create(2, 3)
    print
    
    print './mysql-api.py --friendship/exists 2 3'
    print Friendship().exists(2, 3)
    print
    
    print './mysql-api.py --friendship/show 2 3'
    print Friendship().show(2, 3)
    print
    
    print './mysql-api.py --friendship/destroy 2 3'
    print Friendship().destroy(2, 3)
    print
    
    print './mysql-api.py --friendship/exists 2 3'
    print Friendship().exists(2, 3)
    print
    
    return

###############################################################################
def testFriendsFollowers():
    print '## Test: Friends & Followers'
    
    print './mysql-api.py --friends/ids 1'
    print Friend().ids(1)
    print
    
    print './mysql-api.py --follower/ids 1'
    print Follower().ids(1)
    print
    
    return

###############################################################################
def testStamps():
    print '## Test: Stamps'
    
    print './mysql-api.py --stamps/create 1 1 \'Great Song!\''
    print Stamp().create(1, 1, 'Great Song!')
    print
    
    print './mysql-api.py --stamps/flag 1'
    print Stamp().flag(1)
    print
    
    print './mysql-api.py --stamps/read 1'
    print Stamp().read(1)
    print
    
    print './mysql-api.py --stamps/show 1'
    print Stamp().show(1)
    print
    
    print './mysql-api.py --stamps/destroy 1'
    print Stamp().destroy(1)
    print
    
    return

###############################################################################
def testEntities():
    print '## Test: Entities'
    
    print './mysql-api.py --entities/create \'The Godfather\' Movie'
    print Entity().create('The Godfather', 'Movie')
    print
    
    print './mysql-api.py --entities/match the'
    print Entity().match('the')
    print
    
    print './mysql-api.py --entities/show 1'
    print Entity().show(1)
    print
    
    print './mysql-api.py --entities/update 1 \'New Title\' Category'
    print Entity().update(1, 'New Title', 'Category')
    print
    
    print './mysql-api.py --entities/destroy 1'
    print Entity().destroy(1)
    print
    
    return

###############################################################################
def testUsers():
    print '## Test: Users'
    
    print './mysql-api.py --users/show 1'
    print User().show(1)
    print
    
    print './mysql-api.py --users/lookup 1 2 3'
    user_ids = [1, 2, 3]
    print User().lookup(user_ids)
    print
    
    print './mysql-api.py --users/search \'ke\''
    print User().search('ke')
    print
    
    print './mysql-api.py --users/flag 1'
    print User().flag(1)
    print
    
    return

###############################################################################
def testBlocks():
    print '## Test: Blocks'
    
    print './mysql-api.py --blocks/exists 1 2'
    print Block().exists(1, 2)
    print
    
    print './mysql-api.py --blocks/create 1 2'
    print Block().create(1, 2)
    print
    
    print './mysql-api.py --blocks/blocking 1'
    print Block().blocking(1)
    print
    
    print './mysql-api.py --blocks/exists 1 2'
    print Block().exists(1, 2)
    print
    
    print './mysql-api.py --blocks/destroy 1 2'
    print Block().destroy(1, 2)
    print
    
    return

###############################################################################
def testAccount():
    print '## Test: Account'
    
    print './mysql-api.py --account/verify_credentials kevin@stamped.com asdf'
    print Account().verify_credentials('kevin@stamped.com', 'asdf')
    print
    
    print './mysql-api.py --account/settings 1'
    print Account().settings(1)
    print
    
    print './mysql-api.py --account/update_settings 1 updated_email@stamped.com asdf 0 0 0'
    print Account().update_settings(1, 'updated_email@stamped.com', 'asdf', 0, 0, 0)
    print
    
    print './mysql-api.py --account/update_profile 1 updated_username Kevin 0 0 0'
    print Account().update_profile(1, 'updated_username', 'Kevin', 0, 0, 0)
    print
    
    print './mysql-api.py --account/create test@stamped.com asdf test Test 0'
    print Account().create('test@stamped.com', 'asdf', 'test', 'Test', 0)
    print
    
    return

###############################################################################
def testConversation():
    print '## Test: Conversation'
    
    print './mysql-api.py --conversation/create 1 1 \'Love this\''
    print Conversation().create(1, 1, 'Love this')
    print
    
    print './mysql-api.py --conversation/flag 1'
    print Conversation().flag(1)
    print
    
    print './mysql-api.py --conversation/show 1'
    print Conversation().show(1)
    print
    
    print './mysql-api.py --conversation/destroy 1'
    print Conversation().destroy(1)
    print
    
    return

###############################################################################
def testMentions():
    print '## Test: Mentions'
    
    print './mysql-api.py --mentions/create 2 2'
    print Mention().create(2, 2)
    print
    
    print './mysql-api.py --mentions/user 2'
    print Mention().user(2)
    print
    
    print './mysql-api.py --mentions/destroy 2 2'
    print Mention().destroy(2, 2)
    print
    
    return

###############################################################################
def testCollections():
    print '## Test: Collections'
    
    print './mysql-api.py --collections/inbox 1'
    print Collection().inbox(2)
    print
    
    print './mysql-api.py --collections/user 1'
    print Collection().user(2)
    print
    
    print './mysql-api.py --collections/add_stamp 3'
    print Collection().add_stamp(3)
    print
    
    return

###############################################################################
def testFavorites():
    print '## Test: Favorites'
    
    print './mysql-api.py --favorites/create 2 2'
    print Favorite().create(2, 2)
    print
    
    print './mysql-api.py --favorites/show 2'
    print Favorite().show(2)
    print
    
    print './mysql-api.py --favorites/destroy 2 2'
    print Favorite().destroy(2, 2)
    print
    
    return

###############################################################################
def testEverything():
    
    print 
    print '#### BEGIN TESTS ####'
    print
    
    testAccount()
    testBlocks()
    testCollections()
    testConversation()
    testEntities()
    testFavorites()
    testFriendsFollowers()
    testFriendships()
    testMentions()
    testStamps()
    testUsers()
    
    
    return

###############################################################################
def setup(database = 'stamped_api'):

    createDatabase(database)
    
    createTables(database)

    sampleUsers(database)
    
    sampleEntities(database)
    
    sampleFriendships(database)
    
    sampleStamps(database)
    
    testEverything()
    

