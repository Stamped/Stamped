#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
from tests.AStampedAPIHttpTestCase import *

# ########## #
# ClientLogs #
# ########## #

class StampedAPIHttpClientLogsTests(AStampedAPIHttpTestCase):
    def setUp(self):
        (self.user, self.token) = self.createAccount(name='devbot') 
    
    def tearDown(self):
        self.deleteAccount(self.token)
    
    def test_addentry(self):
        path = "private/logs/create.json"
        data = {
            "oauth_token"   : self.token['access_token'], 
            "key"           : "search", 
            "value"         : "pizza", 
        }
        
        result = self.handlePOST(path, data)
        self.assertEqual(result['result'], True)

if __name__ == '__main__':
    main()

