#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import sys, thread
import MySQLdb

from db.mysql.MySQL import MySQL
from optparse import OptionParser

from Entity import Entity
from User import User
from Stamp import Stamp
from Mention import Mention

# import specific databases
from db.mysql.MySQLEntityDB import MySQLEntityDB
from db.mysql.MySQLUserDB import MySQLUserDB
from db.mysql.MySQLStampDB import MySQLStampDB
from db.mysql.MySQLMentionDB import MySQLMentionDB


def _setup():
    MySQL(setup=True)
    MySQLEntityDB(setup=True)
    MySQLUserDB(setup=True)
    MySQLStampDB(setup=True)
    MySQLMentionDB(setup=True)

def main():

    _setup()
    
    entityDB = MySQLEntityDB()
    userDB = MySQLUserDB()
    stampDB = MySQLStampDB()
    mentionDB = MySQLMentionDB()

    print

    # ENTITIES
    entity = Entity({
        'title' : 'Little Owl',
        'category' : 'Restaurant'
        })

    entityID = entityDB.addEntity(entity)
    print 'entityID:       ', entityID
    
    entityCopy = entityDB.getEntity(entityID)
    print 'entityCopy:     ', entityCopy
    
    entityCopy['title'] = 'Little Owl 2'
    entityCopy['description'] = 'Great Food'
    entityDB.updateEntity(entityCopy)
    
    print 'updated entity: ', entityDB.getEntity(entityID)
    
    #entityDB.removeEntity(entityID)
    
    entityDB.addEntities([entity, entityCopy])
    
    print
    
    # USERS
    user = User({
        'name' : 'Kevin',
        'email' : 'kevin@stamped.com',
        'privacy' : 0})
    
    userID = userDB.addUser(user)
    print 'userID:         ', userID
    
    userCopy = userDB.getUser(userID)
    print 'userCopy:       ', userCopy
    
    userCopy['username'] = 'kpalms'
    userCopy['privacy'] = 1
    userDB.updateUser(userCopy)
    
    print 'updated user:   ', userDB.getUser(userID)
    
    #userDB.removeUser(userID)
    
    userDB.addUsers([user, userCopy])
    
    print
    
    # STAMPS
    stamp = Stamp({
        'user_id' : userID,
        'entity_id' : entityID,
        'comment' : 'Great entity!'})
    
    stampID = stampDB.addStamp(stamp)
    print 'stampID:        ', stampID
    
    stampCopy = stampDB.getStamp(stampID)
    print 'stampCopy:      ', stampCopy
    print 'user email:     ', stampCopy['user']['email']
    print 'entity title:   ', stampCopy['entity']['title']
    
    stampCopy['comment'] = 'Really great entity...'
    stampDB.updateStamp(stampCopy)
    
    print 'updated stamp:  ', stampDB.getStamp(stampID)
    
    #stampDB.removeStamp(stampID)
    
    stampDB.addStamps([stamp, stampCopy])
    
    print
    
    # MENTIONS
    mention = Mention({
        'user_id' : userID,
        'stamp_id' : stampID})
    
    mentionDB.addMention(mention)
    
    mentionCopy = mentionDB.getMention(stampID, userID)
    print 'mentionCopy:    ', mentionCopy
    print 'user email:     ', mentionCopy['user']['email']
    print 'stamped entity: ', mentionCopy['stamp']['entity']['title']
    
    #mentionDB.removeMention(stampID, userID)
    
    print

# where all the magic starts
if __name__ == '__main__':
    main()


