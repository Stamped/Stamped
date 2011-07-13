#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import sys, thread
# import MySQLdb

# from db.mysql.MySQL import MySQL
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
from Block import Block

# import specific databases
# from db.mysql.MySQLEntityDB import MySQLEntityDB
# from db.mysql.MySQLUserDB import MySQLUserDB
# from db.mysql.MySQLStampDB import MySQLStampDB
# from db.mysql.MySQLMentionDB import MySQLMentionDB
# from db.mysql.MySQLCommentDB import MySQLCommentDB
# from db.mysql.MySQLFavoriteDB import MySQLFavoriteDB
# from db.mysql.MySQLCollectionDB import MySQLCollectionDB
# from db.mysql.MySQLFriendshipDB import MySQLFriendshipDB
# from db.mysql.MySQLFriendsDB import MySQLFriendsDB
# from db.mysql.MySQLFollowersDB import MySQLFollowersDB
# from db.mysql.MySQLBlockDB import MySQLBlockDB
from db.mongodb.MongoEntity import MongoEntity
from db.mongodb.MongoUser import MongoUser
from db.mongodb.MongoStamp import MongoStamp
from db.mongodb.MongoFriendship import MongoFriendship
from db.mongodb.MongoCollection import MongoCollection


def _setup():
#     MySQL(setup=True)
#     MySQLEntityDB(setup=True)
#     MySQLUserDB(setup=True)
#     MySQLStampDB(setup=True)
#     MySQLMentionDB(setup=True)
#     MySQLCommentDB(setup=True)
#     MySQLFavoriteDB(setup=True)
#     MySQLCollectionDB()
#     MySQLFriendshipDB(setup=True)
#     MySQLFriendsDB()
#     MySQLFollowersDB()
#     MySQLBlockDB(setup=True)
#     MongoStamp()
    print 'Setup'

def main():

    _setup()
#     
#     entityDB = MySQLEntityDB()
#     userDB = MySQLUserDB()
#     stampDB = MySQLStampDB()
#     mentionDB = MySQLMentionDB()
#     commentDB = MySQLCommentDB()
#     favoriteDB = MySQLFavoriteDB()
#     collectionDB = MySQLCollectionDB()
#     friendshipDB = MySQLFriendshipDB()
#     friendsDB = MySQLFriendsDB()
#     followersDB = MySQLFollowersDB()
#     blockDB = MySQLBlockDB()
    entityDB = MongoEntity()
    userDB = MongoUser()
    stampDB = MongoStamp()
    friendshipDB = MongoFriendship()
    collectionDB = MongoCollection()

    print

    # ENTITIES
    entity = Entity({
        'title': 'Little Owl',
        'category': 'Restaurant',
        'desc': 'Restaurant on Grove St.'
        })

    entityID = entityDB.addEntity(entity)
    print 'entityID:       ', entityID
    
    entityCopy = entityDB.getEntity(entityID)
    print 'entityCopy:     ', entityCopy.id
    
    entityCopy.title = 'Recette'
    entityCopy.desc = 'Great Food'
    
    entityDB.updateEntity(entityCopy)
    
    print 'updated entity: ', entityDB.getEntity(entityID).title
    
    entityDB.removeEntity(entity)
    
    entityDB.addEntities([entity, entityCopy])
    
    print '"little" entities: '
    for entity in entityDB.matchEntities('little'):
        print '                ', entity
    
    print


    # USERS
    user = User({
        'first_name': 'Kevin',
        'last_name': 'Palms',
        'username': 'kevin',
        'email': 'kevin@stamped.com',
        'password': '12345',
        'img': 'kevin.png',
        'locale': 'EST',
        'timestamp': 'now',
        'colors': { 'primary_color': 'blue' },
        'flags': {
            'privacy' : True
        }    
    })
    
    userID = userDB.addUser(user)
    print 'userID:         ', userID
    
    userCopy = userDB.getUser(userID)
    print 'userCopy:       ', userCopy.id
    
    userCopy['username'] = 'kpalms'
    userCopy['privacy'] = False
    userDB.updateUser(userCopy)
    
    print 'updated user:   ', userDB.getUser(userID).username
    
    userDB.removeUser(user)
    
    userDB.addUsers([user, userCopy])
    
    print 'find by name:   ', len(userDB.lookupUsers(userIDs=None, usernames=['kevin','kpalms']))
    print 'find by id:     ', len(userDB.lookupUsers(userIDs=[userID, '4e1ca9bd32a7ba15ab000002'], usernames=None))
    
    print 'search string:  ', len(userDB.searchUsers('kpalms')) # Limited to 20 by default
    
    print
    
    
    # STAMPS
    stamp = Stamp({
        'entity': {
            'entity_id': entityCopy.id,
            'title': entityCopy.title,
            'subtitle': 'New York, NY',
            'category': entityCopy.category
        },
        'user': {
            'user_id': userCopy.id,
            'user_name': userCopy.first_name,
            'user_img': userCopy.img
        },
        'blurb': 'Best place.. ever?!?',
        'timestamp': 'Now',
        'flags': { 'privacy': user.flags['privacy'] },
        'credit': ['4e1c6a2532a7ba05ef000000']
    })
    
    stampID = stampDB.addStamp(stamp)
    
    print 'stampID:        ', stampID
    
    stampCopy = stampDB.getStamp(stampID)
    print 'stampCopy:      ', stampCopy.blurb
    print 'user id:        ', stampCopy.user['user_id']
    print 'entity id:      ', stampCopy.entity['entity_id']
    
    stampCopy['blurb'] = 'Really great entity...!'
    stampDB.updateStamp(stampCopy)
    
    print 'updated stamp:  ', stampDB.getStamp(stampID).blurb
    
    stampDB.removeStamp(stamp)
    
    stampDB.addStamps([stamp, stampCopy])
    
    print
#     
#     # MENTIONS
#     mention = Mention({
#         'userID' : userID,
#         'stampID' : stampID})
#     
#     mentionDB.addMention(mention)
#     
#     mentionCopy = mentionDB.getMention(stampID, userID)
#     print 'mentionCopy:    ', mentionCopy
#     print 'user email:     ', mentionCopy['user']['email']
#     print 'stamped entity: ', mentionCopy['stamp']['entity']['title']
#     
#     #mentionDB.removeMention(stampID, userID)
#     
#     print
#     
#     # COMMENTS
#     comment = Comment({
#         'userID' : userID,
#         'stampID' : stampID,
#         'comment' : 'Oh man, I love that'})
#     
#     commentID = commentDB.addComment(comment)
#     print 'commentID:      ', commentID
#     
#     commentCopy = commentDB.getComment(commentID)
#     print 'commentCopy:    ', commentCopy
#     print 'user email:     ', commentCopy['user']['email']
#     print 'stamped entity: ', commentCopy['stamp']['entity']['title']
#     
#     secondComment = Comment({
#         'userID' : userID,
#         'stampID' : stampID,
#         'comment' : 'I mean I REALLY love that'})
#     commentDB.addComment(secondComment)
#     
#     conversation = commentDB.getConversation(stampID)
#     
#     for comment in conversation:
#         print '                ', comment['user']['name'], 'says "', comment['comment'], '"'
#         
#     #commentDB.removeComment(commentID)
#     #commentDB.removeConversation(commentID)
#     
#     print
#     
#     # FAVORITES
#     favorite = Favorite({
#         'userID' : userID,
#         'stampID' : stampID})
#     
#     favoriteDB.addFavorite(favorite)
#     favoriteDB.addFavorite(Favorite({'userID' : userID, 'stampID' : 2}))
#     
#     favoriteCopy = favoriteDB.getFavorite(stampID, userID)
#     print 'favoriteCopy:   ', favoriteCopy
#     print 'user email:     ', favoriteCopy['user']['email']
#     print 'stamped entity: ', favoriteCopy['stamp']['entity']['title']
#     
#     #mentionDB.removeMention(stampID, userID)
#     
#     print
    
    # FRIENDSHIP
    friendship = Friendship({
        'user_id': '4e1cac6d32a7ba16a4000002',
        'friend_id': userCopy.id})
    
    print 'add friendship: ', friendshipDB.addFriendship(friendship)
    
    checkFriendship = Friendship({
        'user_id': '4e1cac6d32a7ba16a4000002',
        'friend_id': '4e1dc66e32a7ba4a26000002'
    })
    
    print 'get friends:    ', len(friendshipDB.getFriendships('4e1cac6d32a7ba16a4000002'))
    
#     print 'is friend:      ', friendshipDB.checkFriendship(friendship)
    
#     friendshipCopy = friendshipDB.getFriendship(1, 2)
#     print 'friendshipCopy: ', friendshipCopy
#     print 'user email:     ', friendshipCopy['user']['email']
#     print 'following name: ', friendshipCopy['following']['name']
    
    print 'exists:         ', friendshipDB.checkFriendship(friendship)
    print 'delete:         ', friendshipDB.removeFriendship(friendship)
    print 'exists:         ', friendshipDB.checkFriendship(friendship)
    
    print 'get friends:    ', len(friendshipDB.getFriendships('4e1cac6d32a7ba16a4000002'))
    
#     friendshipDB.addFriendship(friendship)
#     
#     print
#     
#     #friends = Friends({'userID' : 1})
#     print 'Friend list:    ', friendsDB.getFriends(1)
#     print 'Follower list:  ', followersDB.getFollowers(2)
    
    print
    
    # COLLECTIONS
    
    userCollection = collectionDB.getUserStamps(userCopy.id)
    print 'User Collection'
    for stamp in userCollection:
        print '                ', stamp['entity']['title'], '-', stamp['blurb']
    print
    
#     favoritesCollection = collectionDB.getFavorites(userID)
#     print 'Favorites Collection'
#     for stamp in favoritesCollection:
#         print '                ', stamp['entity']['title']
#         print '                 Stamped by', stamp['user']['name']
#         print '                ', stamp['comment']
#         print
#     
#     mentionsCollection = collectionDB.getMentions(userID)
#     print 'Mentions Collection'
#     for stamp in mentionsCollection:
#         print '                ', stamp['entity']['title']
#         print '                 Stamped by', stamp['user']['name']
#         print '                ', stamp['comment'] 
#         print
#     
#     inboxCollection = collectionDB.getInbox(userID)
#     print 'Inbox Collection'
#     for stamp in inboxCollection:
#         print '                ', stamp['entity']['title']
#         print '                 Stamped by', stamp['user']['name']
#         print '                ', stamp['comment']
#         print
#     
#     print
#     
#     # BLOCK
#     block = Block({
#         'userID' : 1,
#         'blockingID' : 2})
#     
#     print 'Add block'
#     blockDB.addBlock(block)
#     
#     print 'exists:         ', blockDB.checkBlock(1, 2)
#     print 'delete:         ', blockDB.removeBlock(1, 2)
#     print 'exists:         ', blockDB.checkBlock(1, 2)
#     
#     blockDB.addBlock(block)
#     
#     print
#     print 'Add block'
#     print 'Block list:    ', blockDB.getBlocking(1)
#     
#     print
#     
#     friendshipDB.addFriendship({'userID' : 2, 'followingID' : 1})
#     friendshipDB.addFriendship({'userID' : 2, 'followingID' : 3})
#     friendshipDB.addFriendship({'userID' : 1, 'followingID' : 3})

# where all the magic starts
if __name__ == '__main__':
    main()



