#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals
import logs

from errors                 import *
from optparse               import OptionParser

from api.db.mongodb.MongoInboxStampsCollection          import MongoInboxStampsCollection

collections = [
    MongoInboxStampsCollection
]


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

    for collection in collections:
        logs.info("Running %s" % collection.__name__)
        db = collection()
        for i in db._collection.find(fields=['_id']).limit(100):
            try:
                result = db.checkIntegrity(i['_id'], noop=options.noop)
                print i['_id'], 'PASS'
            except NotImplementedError:
                logs.warning("WARNING: Collection '%s' not implemented" % collection.__name__)
                break
            except StampedStaleRelationshipKeyError:
                print ['_id'], 'FAIL: Key deleted'
            except StampedStaleRelationshipDataError:
                print ['_id'], 'FAIL: References updated'
            except Exception as e:
                print ['_id'], 'FAIL: %s' % e

        logs.info("Done running %s" % collection.__name__)

if __name__ == '__main__':
    main()