#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils

from AStampedAPIHttpTestCase    import *
from StampedTestUtils       import *
from ASimulatedUser         import *
from AStressTest            import StressTest
from pprint                 import pprint
from utils                  import abstract

baselineParams = {
    'avg_friend_connectivity': 12, 
    'stdev_friend_connectivity': 5, 
    'users_per_minute': 400, 
    'users_per_minute_decay': False, 
    'users_limit': None, 
    'actions_per_minute': 30, 
    'actions_per_minute_decay': False, 
    'actions_per_user_limit': 180, 
    'bieber_protocol': False, 
    'user_class': BaselineSimulatedUser
}

realisticParams = {
    'avg_friend_connectivity': 12, 
    'stdev_friend_connectivity': 5, 
    'users_per_minute': 5, 
    'users_per_minute_decay': False, 
    'users_limit': None, 
    'actions_per_minute': 3, 
    'actions_per_minute_decay': False, 
    'actions_per_user_limit': None, 
    'bieber_protocol': True, 
    'user_class': RealisticSimulatedUser
}

class StressTests(AStampedAPIHttpTestCase):
    def setUp(self):
        self._test = StressTest(self, **realisticParams)
    
    def test_stress(self):
        self._test.run()
        self._test.join()
    
    def tearDown(self):
        pass

if __name__ == '__main__':
    StampedTestRunner().run()

