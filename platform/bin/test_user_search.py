#!/usr/bin/python

import Globals, utils
import sys, time

from api.MongoStampedAPI    import MongoStampedAPI
from pprint                 import pprint

if len(sys.argv) < 1:
    utils.log("must include query")
    sys.exit(1)

query = sys.argv[1]
api   = MongoStampedAPI(lite_mode = True)
users = api._userDB.searchUsers(None, query, limit = 10, relationship='following')

for user in users:
    pprint(user.value)

