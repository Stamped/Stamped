#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import calendar, pprint, datetime, sys, argparse,math
import keys.aws, logs, utils

from MongoStampedAPI                            import MongoStampedAPI
from bson.objectid import ObjectId


class Converter(object):
    
    def __init__(self,api):
        self.collection = api._userDB._collection
    
    def convert(self,uid):
        cursor = self.collection.find({'_id': ObjectId(uid)},'screen_name_lower')
        
        for sname in cursor:
            return str(sname['screen_name_lower'])