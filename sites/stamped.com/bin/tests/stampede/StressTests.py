#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils

from AStampedAPITestCase    import *
from StampedTestUtils       import *
from ASimulatedUser         import *
from AStressTest            import StressTest
from pprint                 import pprint
from utils                  import abstract

class StressTests(AStampedAPITestCase):
    def setUp(self):
        self._test = StressTest(
            self, 
            avg_friend_connectivity=12, 
            stdev_friend_connectivity=5, 
            users_per_minute=100, 
            users_per_minute_decay=True, 
            users_limit=None, 
            actions_per_minute=3, 
            actions_per_minute_decay=False, 
            actions_per_user_limit=None, 
            bieber_protocol=True, 
            user_class=RealisticSimulatedUser, 
            noop=True
        )
    
    def test_stress(self):
        self._test.run()
        self._test.join()
    
    def tearDown(self):
        pass

if __name__ == '__main__':
    StampedTestRunner().run()

