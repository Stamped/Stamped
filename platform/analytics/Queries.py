#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals
import argparse
import sys
import datetime
import calendar
import pprint
import keys.aws, logs, utils
from MongoStampedAPI import MongoStampedAPI
from boto.sdb.connection    import SDBConnection
from boto.exception         import SDBResponseError
from db.mongodb.MongoStatsCollection            import MongoStatsCollection

#This file contains all analytics queries supported by the Stats.py module 