#!/usr/bin/env python
from __future__ import absolute_import

import Globals, utils
import sys, time

from api.MongoStampedAPI    import MongoStampedAPI
from pprint                 import pprint

if len(sys.argv) < 1:
    utils.log("must include query")
    sys.exit(1)

query   = sys.argv[1]
api     = MongoStampedAPI(lite_mode = True)
user_id = '4e57048dccc2175fca000005'
users   = api._userDB.searchUsers(user_id, query, limit = 10)

for user in users:
    pprint(user)

