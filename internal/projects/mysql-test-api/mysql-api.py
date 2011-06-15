#!/usr/bin/env python

import sys
from datetime import datetime
import gc
import MySQLdb

import setup
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
def sqlConnection():
    return MySQLdb.connect(user='root',db='stamped_api')


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
        print '  --account/verify_credentials(email, password)'
        print '  --account/settings (user_id)'
        print '  --account/update_settings (user_id, email, password, privacy, locale, timezone)'
        print '  --account/update_profile(user_id, username, name, bio, website, image)'
        print '  --account/create(email, password, username, name, privacy)'
        print 
        print '  --blocks/exists (user_id, follower_id)'
        print '  --blocks/blocking/ids (user_id)'
        print '  --blocks/create (user_id, follower_id)'
        print '  --blocks/destroy (user_id, follower_id)'
        print
        print '  --users/show (user_id)'
        print '  --users/lookup (user_ids)'
        print '  --users/search (query)'
        print '  --users/flag (user_id)'
        print
        print '  --friends/ids (user_id)'
        print '  --followers/ids (user_id)'
        print
        print '  --friendships/create (user_id, following_id)'
        print '  --friendships/destroy (user_id, following_id)'
        print '  --friendships/exists (user_id, following_id)'
        print '  --friendships/show (user_id, following_id)'
        print '  --friendships/incoming (user_id)'
        print '  --friendships/outgoing (user_id)'
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
        print '  --favorites/show (user_id)'
        print '  --favorites/create (stamp_id, user_id)'
        print '  --favorites/destroy (stamp_id, user_id)'
        print
        sys.exit(1)
    
    option = sys.argv[1]
    
    
    # Setup:
    if option == '--setup':
        setup.setup()
    
    
    # Account:
    elif option == '--account/verify_credentials':
        account = Account()
        checkNumberOfArguments(2, len(sys.argv))
        response = account.verify_credentials(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
    elif option == '--account/settings':
        account = Account()
        checkNumberOfArguments(1, len(sys.argv))
        response = account.settings(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--account/update_settings':
        account = Account()
        checkNumberOfArguments(6, len(sys.argv))
        response = account.update_settings(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
        print 'Response: ', response
        
    elif option == '--account/update_profile':
        account = Account()
        checkNumberOfArguments(6, len(sys.argv))
        response = account.update_profile(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
        print 'Response: ', response
        
    elif option == '--account/create':
        account = Account()
        checkNumberOfArguments(5, len(sys.argv))
        response = account.create(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
        print 'Response: ', response
        
        
    # Blocks:
    elif option == '--blocks/exists':
        block = Block()
        checkNumberOfArguments(2, len(sys.argv))
        response = block.exists(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    elif option == '--blocks/blocking':
        block = Block()
        checkNumberOfArguments(1, len(sys.argv))
        response = block.blocking(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--blocks/create':
        block = Block()
        checkNumberOfArguments(2, len(sys.argv))
        response = block.create(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    elif option == '--blocks/destroy':
        block = Block()
        checkNumberOfArguments(2, len(sys.argv))
        response = block.destroy(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    
    # Users:
    elif option == '--users/show':
        user = User()
        checkNumberOfArguments(1, len(sys.argv))
        response = user.show(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--users/lookup':
        user = User()
        checkNumberOfArguments(1, len(sys.argv))
        response = user.lookup(sys.argv[2:])
        print 'Response: ', response
        
    elif option == '--users/search':
        user = User()
        checkNumberOfArguments(1, len(sys.argv))
        response = user.search(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--users/flag':
        user = User()
        if len(sys.argv) == 4:
            response = user.flag(sys.argv[2], sys.argv[3])
        elif len(sys.argv) == 3:
            response = user.flag(sys.argv[2])
        else:
            print 'Missing parameters'
            sys.exit(1)
        print 'Response: ', response
        
        
    # Friends & Followers:
    elif option == '--friends/ids':
        friend = Friend()
        checkNumberOfArguments(1, len(sys.argv))
        response = friend.ids(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--followers/ids':
        follower = Follower()
        checkNumberOfArguments(1, len(sys.argv))
        response = follower.ids(sys.argv[2])
        print 'Response: ', response
    
    
    # Friendships:
    elif option == '--friendships/create':
        friendship = Friendship()
        checkNumberOfArguments(2, len(sys.argv))
        response = friendship.create(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    elif option == '--friendships/destroy':
        friendship = Friendship()
        checkNumberOfArguments(2, len(sys.argv))
        response = friendship.destroy(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    elif option == '--friendships/exists':
        friendship = Friendship()
        checkNumberOfArguments(2, len(sys.argv))
        response = friendship.exists(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    elif option == '--friendships/show':
        friendship = Friendship()
        checkNumberOfArguments(2, len(sys.argv))
        response = friendship.show(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    elif option == '--friendships/incoming':
        friendship = Friendship()
        checkNumberOfArguments(1, len(sys.argv))
        response = friendship.incoming(sys.argv[2])
        print 'Response: ', response
    
    elif option == '--friendships/outgoing':
        friendship = Friendship()
        checkNumberOfArguments(1, len(sys.argv))
        response = friendship.outgoing(sys.argv[2])
        print 'Response: ', response
        
        
    # Entities:
    elif option == '--entities/show':
        entity = Entity()
        checkNumberOfArguments(1, len(sys.argv))
        response = entity.show(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--entities/create':
        entity = Entity()
        checkNumberOfArguments(2, len(sys.argv))
        response = entity.create(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
    elif option == '--entities/destroy':
        entity = Entity()
        checkNumberOfArguments(1, len(sys.argv))
        response = entity.destroy(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--entities/update':
        entity = Entity()
        checkNumberOfArguments(3, len(sys.argv))
        response = entity.update(sys.argv[2], sys.argv[3], sys.argv[4])
        print 'Response: ', response
        
    elif option == '--entities/match':
        entity = Entity()
        checkNumberOfArguments(1, len(sys.argv))
        response = entity.match(sys.argv[2])
        print 'Response: ', response
        
        
    # Stamps:
    elif option == '--stamps/create':
        stamp = Stamp()
        checkNumberOfArguments(3, len(sys.argv))
        response = stamp.create(sys.argv[2], sys.argv[3], sys.argv[4])
        print 'Response: ', response
        
    elif option == '--stamps/show':
        stamp = Stamp()
        checkNumberOfArguments(1, len(sys.argv))
        response = stamp.show(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--stamps/destroy':
        stamp = Stamp()
        checkNumberOfArguments(1, len(sys.argv))
        response = stamp.destroy(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--stamps/flag':
        stamp = Stamp()
        if len(sys.argv) == 4:
            response = stamp.flag(sys.argv[2], sys.argv[3])
        elif len(sys.argv) == 3:
            response = stamp.flag(sys.argv[2])
        else:
            print 'Missing parameters'
            sys.exit(1)
        print 'Response: ', response
        
    elif option == '--stamps/read':
        stamp = Stamp()
        if len(sys.argv) == 5:
            response = stamp.read(sys.argv[2], sys.argv[3], sys.argv[4])
        elif len(sys.argv) == 4:
            response = stamp.read(sys.argv[2], sys.argv[3])
        elif len(sys.argv) == 3:
            response = stamp.read(sys.argv[2])
        else:
            print 'Missing parameters'
            sys.exit(1)
        print 'Response: ', response
        
        
    # Conversation:
    elif option == '--conversation/show':
        conversation = Conversation()
        checkNumberOfArguments(1, len(sys.argv))
        response = conversation.show(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--conversation/create':
        conversation = Conversation()
        checkNumberOfArguments(3, len(sys.argv))
        response = conversation.create(sys.argv[2], sys.argv[3], sys.argv[4])
        print 'Response: ', response
        
    elif option == '--conversation/destroy':
        conversation = Conversation()
        checkNumberOfArguments(1, len(sys.argv))
        response = conversation.destroy(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--conversation/flag':
        conversation = Conversation()
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
        mention = Mention()
        checkNumberOfArguments(2, len(sys.argv))
        response = mention.create(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
    elif option == '--mentions/destroy':
        mention = Mention()
        checkNumberOfArguments(2, len(sys.argv))
        response = mention.destroy(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
    elif option == '--mentions/user':
        mention = Mention()
        checkNumberOfArguments(1, len(sys.argv))
        response = mention.user(sys.argv[2])
        print 'Response: ', response
        
        
    # Collections:
    elif option == '--collections/inbox':
        collection = Collection()
        checkNumberOfArguments(1, len(sys.argv))
        response = collection.inbox(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--collections/user':
        collection = Collection()
        checkNumberOfArguments(1, len(sys.argv))
        response = collection.user(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--collections/add_stamp':
        collection = Collection()
        checkNumberOfArguments(1, len(sys.argv))
        response = collection.add_stamp(sys.argv[2])
        print 'Response: ', response
        
        
    # Favorites:
    elif option == '--favorites/show':
        favorite = Favorite()
        checkNumberOfArguments(1, len(sys.argv))
        response = favorite.show(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--favorites/create':
        favorite = Favorite()
        checkNumberOfArguments(2, len(sys.argv))
        response = favorite.create(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
    elif option == '--favorites/destroy':
        favorite = Favorite()
        checkNumberOfArguments(2, len(sys.argv))
        response = favorite.destroy(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
        
    else:
        print 'unknown option: ' + option
        sys.exit(1)


if __name__ == '__main__':
    main()
