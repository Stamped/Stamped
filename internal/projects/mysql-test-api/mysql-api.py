#!/usr/bin/env python

import sys
from datetime import datetime
import gc
import MySQLdb

import setup
import blocks
import users
import friends
import followers
import friendships
import entities
import stamps
import conversation
import mentions
import collections
import favorites

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
        
        
    # Blocks:
    elif option == '--blocks/exists':
        checkNumberOfArguments(2, len(sys.argv))
        response = blocks.exists(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    elif option == '--blocks/blocking':
        checkNumberOfArguments(1, len(sys.argv))
        response = blocks.blocking(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--blocks/create':
        checkNumberOfArguments(2, len(sys.argv))
        response = blocks.create(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    elif option == '--blocks/destroy':
        checkNumberOfArguments(2, len(sys.argv))
        response = blocks.destroy(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    
    # Users:
    elif option == '--users/show':
        checkNumberOfArguments(1, len(sys.argv))
        response = users.show(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--users/lookup':
        checkNumberOfArguments(1, len(sys.argv))
        response = users.lookup(sys.argv[2:])
        print 'Response: ', response
        
    elif option == '--users/search':
        checkNumberOfArguments(1, len(sys.argv))
        response = users.search(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--users/flag':
        if len(sys.argv) == 4:
            response = users.flag(sys.argv[2], sys.argv[3])
        elif len(sys.argv) == 3:
            response = users.flag(sys.argv[2])
        else:
            print 'Missing parameters'
            sys.exit(1)
        print 'Response: ', response
        
        
    # Friends & Followers:
    elif option == '--friends/ids':
        checkNumberOfArguments(1, len(sys.argv))
        response = friends.ids(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--followers/ids':
        checkNumberOfArguments(1, len(sys.argv))
        response = followers.ids(sys.argv[2])
        print 'Response: ', response
    
    
    # Friendships:
    elif option == '--friendships/create':
        checkNumberOfArguments(2, len(sys.argv))
        response = friendships.create(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    elif option == '--friendships/destroy':
        checkNumberOfArguments(2, len(sys.argv))
        response = friendships.destroy(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    elif option == '--friendships/exists':
        checkNumberOfArguments(2, len(sys.argv))
        response = friendships.exists(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    elif option == '--friendships/show':
        checkNumberOfArguments(2, len(sys.argv))
        response = friendships.show(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
    elif option == '--friendships/incoming':
        checkNumberOfArguments(1, len(sys.argv))
        response = friendships.incoming(sys.argv[2])
        print 'Response: ', response
    
    elif option == '--friendships/outgoing':
        checkNumberOfArguments(1, len(sys.argv))
        response = friendships.outgoing(sys.argv[2])
        print 'Response: ', response
        
        
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
            response = stamps.flag(sys.argv[2], sys.argv[3])
        elif len(sys.argv) == 3:
            response = stamps.flag(sys.argv[2])
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
        
        
    # Favorites:
    elif option == '--favorites/show':
        checkNumberOfArguments(1, len(sys.argv))
        response = favorites.show(sys.argv[2])
        print 'Response: ', response
        
    elif option == '--favorites/create':
        checkNumberOfArguments(2, len(sys.argv))
        response = favorites.create(sys.argv[2], sys.argv[3])
        print 'Response: ', response
        
    elif option == '--favorites/destroy':
        checkNumberOfArguments(2, len(sys.argv))
        response = favorites.destroy(sys.argv[2], sys.argv[3])
        print 'Response: ', response
    
        
        
    else:
        print 'unknown option: ' + option
        sys.exit(1)


if __name__ == '__main__':
    main()




















