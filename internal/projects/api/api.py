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
from Comment import Comment
from Favorite import Favorite
from Friendship import Friendship
from Friends import Friends
from Friendship import Friendship

# import specific databases
from db.mysql.MySQLEntityDB import MySQLEntityDB
from db.mysql.MySQLUserDB import MySQLUserDB
from db.mysql.MySQLStampDB import MySQLStampDB
from db.mysql.MySQLMentionDB import MySQLMentionDB
from db.mysql.MySQLCommentDB import MySQLCommentDB
from db.mysql.MySQLFavoriteDB import MySQLFavoriteDB
from db.mysql.MySQLCollectionDB import MySQLCollectionDB
from db.mysql.MySQLFriendshipDB import MySQLFriendshipDB
from db.mysql.MySQLFriendsDB import MySQLFriendsDB
from db.mysql.MySQLFollowersDB import MySQLFollowersDB


def _setup():
    MySQL(setup=True)
    MySQLEntityDB(setup=True)
    MySQLUserDB(setup=True)
    MySQLStampDB(setup=True)
    MySQLMentionDB(setup=True)
    MySQLCommentDB(setup=True)
    MySQLFavoriteDB(setup=True)
    MySQLCollectionDB()
    MySQLFriendshipDB(setup=True)
    MySQLFriendsDB()
    MySQLFollowersDB()

def main():

    _setup()
    
    entityDB = MySQLEntityDB()
    userDB = MySQLUserDB()
    stampDB = MySQLStampDB()
    mentionDB = MySQLMentionDB()
    commentDB = MySQLCommentDB()
    favoriteDB = MySQLFavoriteDB()
    collectionDB = MySQLCollectionDB()
    friendshipDB = MySQLFriendshipDB()
    friendsDB = MySQLFriendsDB()
    followersDB = MySQLFollowersDB()

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
    
    entityCopy['title'] = 'Recette'
    entityCopy['description'] = 'Great Food'
    entityDB.updateEntity(entityCopy)
    
    print 'updated entity: ', entityDB.getEntity(entityID)
    
    #entityDB.removeEntity(entityID)
    
    entityDB.addEntities([entity, entityCopy])
    
    print '"lit" entities: ', entityDB.matchEntities('lit')
    
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
    
    print userDB.lookupUsers(userIDs=None, usernames=['kevin','kpalms'])
    print userDB.lookupUsers(userIDs=[1,2,3,4,5], usernames=None)
    
    print userDB.searchUsers('kpalms')
    
    print
    
    # STAMPS
    stamp = Stamp({
        'userID' : userID,
        'entityID' : entityID,
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
        'userID' : userID,
        'stampID' : stampID})
    
    mentionDB.addMention(mention)
    
    mentionCopy = mentionDB.getMention(stampID, userID)
    print 'mentionCopy:    ', mentionCopy
    print 'user email:     ', mentionCopy['user']['email']
    print 'stamped entity: ', mentionCopy['stamp']['entity']['title']
    
    #mentionDB.removeMention(stampID, userID)
    
    print
    
    # COMMENTS
    comment = Comment({
        'userID' : userID,
        'stampID' : stampID,
        'comment' : 'Oh man, I love that'})
    
    commentID = commentDB.addComment(comment)
    print 'commentID:      ', commentID
    
    commentCopy = commentDB.getComment(commentID)
    print 'commentCopy:    ', commentCopy
    print 'user email:     ', commentCopy['user']['email']
    print 'stamped entity: ', commentCopy['stamp']['entity']['title']
    
    secondComment = Comment({
        'userID' : userID,
        'stampID' : stampID,
        'comment' : 'I mean I REALLY love that'})
    commentDB.addComment(secondComment)
    
    conversation = commentDB.getConversation(stampID)
    
    for comment in conversation:
        print '                ', comment['user']['name'], 'says "', comment['comment'], '"'
        
    #commentDB.removeComment(commentID)
    #commentDB.removeConversation(commentID)
    
    print
    
    # FAVORITES
    favorite = Favorite({
        'userID' : userID,
        'stampID' : stampID})
    
    favoriteDB.addFavorite(favorite)
    favoriteDB.addFavorite(Favorite({'userID' : userID, 'stampID' : 2}))
    
    favoriteCopy = favoriteDB.getFavorite(stampID, userID)
    print 'favoriteCopy:   ', favoriteCopy
    print 'user email:     ', favoriteCopy['user']['email']
    print 'stamped entity: ', favoriteCopy['stamp']['entity']['title']
    
    #mentionDB.removeMention(stampID, userID)
    
    print
    
    # FRIENDSHIP
    friendship = Friendship({
        'userID' : 1,
        'followingID' : 2})
    
    friendshipDB.addFriendship(friendship)
    
    friendshipCopy = friendshipDB.getFriendship(1, 2)
    print 'friendshipCopy: ', friendshipCopy
    print 'user email:     ', friendshipCopy['user']['email']
    print 'following name: ', friendshipCopy['following']['name']
    
    print 'exists:         ', friendshipDB.checkFriendship(1, 2)
    print 'delete:         ', friendshipDB.removeFriendship(1, 2)
    print 'exists:         ', friendshipDB.checkFriendship(1, 2)
    
    friendshipDB.addFriendship(friendship)
    
    print
    
    #friends = Friends({'userID' : 1})
    print 'Friend list:    ', friendsDB.getFriends(1)
    print 'Follower list:  ', followersDB.getFollowers(2)
    
    print
    
    # COLLECTIONS
    
    userCollection = collectionDB.getUser(userID)
    print 'User Collection'
    for stamp in userCollection:
        print '                ', stamp['entity']['title']
        print '                 Stamped by', stamp['user']['name']
        print '                ', stamp['comment']
        print
    
    favoritesCollection = collectionDB.getFavorites(userID)
    print 'Favorites Collection'
    for stamp in favoritesCollection:
        print '                ', stamp['entity']['title']
        print '                 Stamped by', stamp['user']['name']
        print '                ', stamp['comment']
        print
    
    mentionsCollection = collectionDB.getMentions(userID)
    print 'Mentions Collection'
    for stamp in mentionsCollection:
        print '                ', stamp['entity']['title']
        print '                 Stamped by', stamp['user']['name']
        print '                ', stamp['comment'] 
        print
    
    inboxCollection = collectionDB.getInbox(userID)
    print 'Inbox Collection'
    for stamp in inboxCollection:
        print '                ', stamp['entity']['title']
        print '                 Stamped by', stamp['user']['name']
        print '                ', stamp['comment']
        print
    
    print

# where all the magic starts
if __name__ == '__main__':
    main()


