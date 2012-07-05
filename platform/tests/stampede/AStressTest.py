#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import gevent, random, time

from tests.stampede.ASimulatedUser import *
from gevent         import Greenlet

class StressTest(Greenlet):
    
    def __init__(self, 
                 parent, 
                 avg_friend_connectivity=12, 
                 stdev_friend_connectivity=5, 
                 users_per_minute=100, 
                 users_per_minute_decay=True, 
                 users_limit=None, 
                 actions_per_minute=3, 
                 actions_per_minute_decay=True, 
                 actions_per_user_limit=None, 
                 bieber_protocol=True, 
                 user_class=RealisticSimulatedUser, 
                 **kwargs):
        Greenlet.__init__(self)
        
        self._parent = parent
        self.avg_friend_connectivity    = avg_friend_connectivity
        self.stdev_friend_connectivity  = stdev_friend_connectivity
        self.users_per_minute           = users_per_minute
        self.users_per_minute_decay     = users_per_minute_decay
        self.users_limit                = users_limit
        self.actions_per_minute         = actions_per_minute
        self.actions_per_minute_decay   = actions_per_minute_decay
        self.actions_per_user_limit     = actions_per_user_limit
        self.bieber_protocol            = bieber_protocol
        self.user_class                 = user_class
        
        if kwargs is not None:
            self.options = utils.AttributeDict(kwargs)
        else:
            self.options = utils.AttributeDict()
        
        if not 'noop' in self.options:
            self.options.noop = False
        
        self.bieber     = None
        self.new_users  = []
        self.users      = []
        self.stamps     = []
        self.entities   = []
    
    def _run(self):
        gevent.spawn(self._handle_new_users)
        t0 = time.time()
        
        if self.bieber_protocol:
            username = 'bieber_%d' % int(t0)
            user = self.user_class(username, self)
            user.start()
        
        num_users = 0
        
        while True:
            t1 = time.time()
            
            username = 't_%d_%d' % (num_users, int(t1))
            user = self.user_class(username, self)
            user.start()
            
            num_users += 1
            if self.users_limit is not None and num_users >= self.users_limit:
                break
            
            t2 = time.time()
            users_per_minute = self.users_per_minute
            
            if self.users_per_minute_decay:
                # optionally apply an exponential decay to the number of users 
                # created per minute
                duration = (t2 - t0) / 60.0
                users_per_minute = users_per_minute * (0.8 ** duration)
            
            # if creating less than 1 user every N minutes, then break
            N = 1.0
            if users_per_minute <= 1.0 / N:
                break
            
            duration = (t2 - t1)
            sleep    = (60.0 / users_per_minute) - duration
            
            if sleep > 0:
                time.sleep(sleep)
            elif 0 == (num_users % 10):
                time.sleep(0.1)
        
        for user in self.users:
            user.join()
    
    def _handle_new_users(self):
        num_users = 0
        
        while True:
            if 0 == len(self.new_users):
                time.sleep(1)
                continue
            
            user = self.new_users.pop(0)
            
            utils.log("[%s] initializing user '%s'" % (self, user.name))
            try:
                if not self.options.noop:
                    if 0 == num_users:
                        for i in xrange(8):
                            self.addEntity(self._parent.createEntity(user.token))
                            self.addEntity(self._parent.createPlaceEntity(user.token))
                    else:
                        self.addEntity(self._parent.createEntity(user.token))
            except:
                utils.log("[%s] ERROR: unable to add default entities for user %s" % (self, user))
            
            if self.bieber_protocol:
                if self.bieber is not None:
                    try:
                        if not self.options.noop:
                            self._parent.createFriendship(user.token, self.bieber.userID)
                    except:
                        # purposefully ignore if friendship fails to create
                        utils.log("[%s] ERROR: unable to add bieber friendship with user %s" % (self, user))
                elif 'bieber' in user.name:
                    self.bieber = user
            
            # initialize friendships
            if len(self.users) > 0:
                num_to_follow = int(random.normalvariate(self.avg_friend_connectivity, self.stdev_friend_connectivity))
                num_to_follow = max(0, num_to_follow)
                
                for i in xrange(num_to_follow):
                    friend_index = random.randint(0, len(self.users) - 1)
                    
                    if friend_index >= 0 and not self.options.noop:
                        friend = self.users[friend_index]
                        
                        if user.userID != friend.userID:
                            try:
                                self._parent.createFriendship(user.token, friend.userID)
                            except:
                                utils.log("[%s] ERROR: unable to add friendship between users %s and %s" % (self, user, friend))
            
            num_users += 1
            self.users.append(user)
            
            # keep users that we hang onto from growing unbounded so we don't OOM
            if len(self.users) >= 100:
                self.users = self.users[-25:]
            
            user._is_ready = True
    
    def getRandomStampID(self):
        if len(self.stamps) > 0:
            index = random.randint(0, len(self.stamps) - 1)
            return self.stamps[index]['stamp_id']
        else:
            return None
    
    def addStamp(self, stamp):
        self.stamps.append(stamp)
        
        # keep stamps that we hang onto from growing unbounded so we don't OOM
        if len(self.stamps) > 100:
            self.stamps = self.stamps[-25:]
    
    def getRandomEntityID(self):
        if len(self.entities) > 0:
            index = random.randint(0, len(self.entities) - 1)
            return self.entities[index]['entity_id']
        else:
            return None
    
    def addEntity(self, entity):
        self.entities.append(entity)
        
        # keep entities that we hang onto from growing unbounded so we don't OOM
        if len(self.entities) > 100:
            self.entities = self.entities[-25:]
    
    def getRandomText(self):
        strings = [
            'The best ever!', 
            'a b c d e f g h i j k l m n o p q r s t u v w x y z', 
            'The quick brown fox jumped over the fence.'
            'beer is good for the soul', 
            'this is another comment / blurb. huzzah!', 
            'have you ever heard of this app called stamped?  it\'s baller!!', 
        ]
        
        return strings[random.randint(0, len(strings) - 1)]
    
    def getRandomSearchString(self):
        strings = [
            'Freedom', 
            'Of Mice and Men', 
            'Madden NFL', 
            'Passion Pit'
            'UFC', 
            'The Jetson\'s', 
            'Shake Shack', 
            'Beauty & Essex', 
            'Starbuck\'s', 
            'Inception', 
            'The Dark Knight', 
            'The', 
            'abc', 
            'A16', 
            'Dos', 
            'Hotel', 
            'Chinese', 
            'Pizza', 
        ]
        
        return strings[random.randint(0, len(strings) - 1)]
    
    def __str__(self):
        return self.__class__.__name__

