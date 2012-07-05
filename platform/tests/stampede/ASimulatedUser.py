#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import time

from tests.stampede.ASimulatedUserAction   import *
from gevent                 import Greenlet
from gevent.pool            import Pool

class ASimulatedUser(Greenlet):
    
    def __init__(self, name, parent):
        Greenlet.__init__(self)
        self.name      = name
        self.parent    = parent
        self.actions   = []
        self._is_ready = False
        self.entity_ids = []
        
        utils.log("[%s] new simulated user '%s'" % (self, self.name))
    
    def _run(self):
        # create a new account
        self.userID, self.token = self.parent._parent.createAccount(self.name)
        self.parent.new_users.append(self)
        
        while not self._is_ready:
            time.sleep(4)
        
        t0 = time.time()
        num_actions = 0
        
        # execute a randomly-chosen action
        while True:
            t1 = time.time()
            
            # select an action based on its relative weight
            action_index = utils.sampleCDF(self.actions, lambda i: i.weight)
            assert action_index >= 0 and action_index < len(self.actions)
            action = self.actions[action_index]
            
            utils.log("[%s-%s] performing action '%s'" % (self, self.name, action))
            try:
                if not self.parent.options.noop:
                    action(self.parent, self)
            except:
                utils.log("[%s] ERROR: unable to perform action '%s'" % (self, action))
                break
            
            num_actions += 1
            if self.parent.actions_per_user_limit is not None and \
                num_actions >= self.parent.actions_per_user_limit:
                break
            
            t2 = time.time()
            actions_per_minute = self.parent.actions_per_minute
            
            if self.parent.actions_per_minute_decay:
                # optionally apply an exponential decay to the number of actions 
                # this user may take per minute
                duration = (t2 - t0) / 60.0
                actions_per_minute = actions_per_minute * (0.8 ** duration)
            
            # if user is performing less than 1 action every N minutes, then 
            # simply disregard this user as having a negligible impact on 
            # overall perf.
            N = 10.0
            if actions_per_minute <= 1.0 / N:
                break
            
            duration = (t2 - t1)
            sleep    = max(0.1, (60.0 / actions_per_minute) - duration)
            time.sleep(sleep)
    
    def __str__(self):
        return "%s:%s" % (self.__class__.__name__, self.name)

class RealisticSimulatedUser(ASimulatedUser):
    def __init__(self, name, parent):
        ASimulatedUser.__init__(self, name, parent)
        
        self.actions = [
            # sometimes download the inbox multiple times in succession to 
            # simulate the (currently common) occurrence of pulling down 
            # the inbox to force an update multiple times in a row.
            UpdateInboxAction(90, 1), 
            UpdateInboxAction(6, 3), 
            
            # sometimes download activity multiple times in succession to 
            # simulate the (currently common) occurrence of pulling down 
            # the news view to force an update multiple times in a row.
            UpdateActivityAction(30), 
            UpdateActivityAction(5, 3), 
            
            SearchAction(30), 
            StampAction(10), 
            CommentAction(20), 
            LikeAction(25), 
        ]

class BaselineSimulatedUser(ASimulatedUser):
    def __init__(self, name, parent):
        ASimulatedUser.__init__(self, name, parent)

        self.actions = [
            # BaselineBeginAction(50),
            BaselineReadAction(50),
            BaselineWriteAction(50),
        ]

class NullSimulatedUser(ASimulatedUser):
    def __init__(self, name, parent):
        ASimulatedUser.__init__(self, name, parent)
        
        self.actions = [
            NullAction(1)
        ]

