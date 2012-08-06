#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import Globals
import sys
import datetime
import calendar
import pprint
import keys.aws, logs, utils
from api.MongoStampedAPI import MongoStampedAPI
from boto.sdb.connection    import SDBConnection
from boto.exception         import SDBResponseError
from bson.code import Code


api = MongoStampedAPI()
collection = api._stampDB._collection

map = Code("function () {"
           "if (this.entity.category == 'food') {"
           "emit(this.entity.title, 1)} "
           ";}")

reduce = Code("function (key, values) {"
              "  var total = 0;"
              "  for (var i = 0; i < values.length; i++) {"
              "    total += values[i];"
              "  }"
              "  return total;"
              "}")

result = collection.inline_map_reduce(map, reduce)

sortedResult = sorted(result, key=lambda k: k['value'],reverse=True) 

for i in sortedResult[0:200]:
    print i