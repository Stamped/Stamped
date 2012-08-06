#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import base64, Image, utils

from api.MongoStampedAPI import MongoStampedAPI
from optparse import OptionParser
from pprint import pprint

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", help="db to connect to")
    
    (options, args) = parser.parse_args()
    
    if options.db:
        utils.init_db_config(options.db)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    stampedAPI = MongoStampedAPI()
    accountDB  = stampedAPI._accountDB
    
    rs = accountDB._collection.find()
    for result in rs:
        account = accountDB._convertFromMongo(result)
        pprint(account)
        
        image = utils.getFile(account.profile_image)
        image = base64.encodestring(image)
        
        stampedAPI.updateProfileImage(account.screen_name, image)

if __name__ == '__main__':
    main()

