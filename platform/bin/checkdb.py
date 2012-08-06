#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import logs, pymongo, time, utils
import libs.ec2_utils
import bin.integrity as integrity

from optparse               import OptionParser
from pprint                 import pprint
from api.MongoStampedAPI    import MongoStampedAPI
from utils                  import abstract

# Index collections
#   inboxstamps
#   creditgivers
# Object stats
# Object references
# Object validation
# Data enrichment

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", help="db to connect to")
    
    parser.add_option("-n", "--noop", default=False, 
        action="store_true", help="noop mode (run read-only)")
    
    parser.add_option("-c", "--check", default=None, 
        action="store", help="optionally filter checks based off of their name")
    
    parser.add_option("-s", "--sampleSetSize", default=None, type="int", 
        action="store", help="sample size as a percentage (e.g., 5 for 5%)")
    
    (options, args) = parser.parse_args()
    
    if options.sampleSetSize is None:
        options.sampleSetRatio = 1.0
    else:
        options.sampleSetRatio = options.sampleSetSize / 100.0
    
    if options.db:
        utils.init_db_config(options.db)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    api = MongoStampedAPI(lite_mode=True)
    db  = api._entityDB._collection._database
    
    # if we're on prod, instruct pymongo to perform integrity checks on 
    # secondaries to reduce load in primary
    if utils.is_ec2() and libs.ec2_utils.is_prod_stack():
        db.read_preference = pymongo.ReadPreference.SECONDARY
    
    checks = integrity.checks
    for check_cls in checks:
        if options.check is None or options.check.lower() in check_cls.__name__.lower():
            utils.log("Running %s" % check_cls.__name__)
            check = check_cls(api, db, options)
            
            try:
                check.run()
            except:
                utils.printException()
            
            utils.log("Done running %s" % check_cls.__name__)
            utils.log()

if __name__ == '__main__':
    main()

