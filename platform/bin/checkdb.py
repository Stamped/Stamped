#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import integrity, logs, random, time, utils

from MongoStampedAPI    import MongoStampedAPI
from optparse           import OptionParser
from pprint             import pprint
from utils              import abstract

# Index collections
#   inboxstamps
#   creditgivers
# Object stats
# Object references
# Object validation
# Data enrichment

__checks = []

class IntegrityError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

def get_friend_ids(db, user_id):
    friend_ids = db['friends'].find_one({ '_id' : user_id }, { 'ref_ids' : 1 })
    
    if friend_ids is not None:
        return friend_ids['ref_ids']
    else:
        return []

def get_stamp_ids_from_user_ids(collection, user_ids):
    if not isinstance(user_ids, (list, tuple)):
        user_ids = [ user_ids ]
    
    if 1 == len(user_ids):
        query = user_ids[0]
    else:
        query = { '$in' : user_ids }
    
    return map(lambda o: str(o['_id']), collection.find({ 'user.user_id' : query }, { '_id' : 1 }))

class AIntegrityCheck(object):
    
    def __init__(self, api, db, options):
        self.api = api
        self.db  = db
        self.options = options
    
    @staticmethod
    def register(cls):
        global __checks
        __checks.append(cls)
    
    @staticmethod
    def getRegisteredChecks():
        return __checks
    
    def _sample(self, iterable, ratio, func, print_progress=True, progress_step=5, max_retries=3, retry_delay=0.01):
        progress_count = 100 / progress_step
        count = 0
        index = 0
        
        try:
            count = len(iterable)
        except:
            try:
                count = iterable.count()
            except:
                count = utils.count(iterable)
        
        for obj in iterable:
            if print_progress and (count < progress_count or 0 == (index % (count / progress_count))):
                utils.log("%s : %s" % (func.__name__, utils.getStatusStr(index, count)))
            
            if random.random() < ratio:
                noop    = self.options.noop
                retries = 0
                
                while True:
                    try:
                        self.options.noop = (retries < max_retries) or noop
                        func(obj)
                        break
                    except Exception, e:
                        retries += 1
                        
                        if noop or retries > max_retries:
                            prefix = "ERROR: " if noop else "UNRESOLVABLE ERROR: "
                            logs.warn("%s: %s" % (prefix, str(e)))
                            break
                        
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    finally:
                        self.options.noop = noop
            
            index += 1
    
    @abstract
    def run():
        pass

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", help="db to connect to")
    
    parser.add_option("-n", "--noop", default=False, 
        action="store_true", help="noop mode (run read-only)")
    
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
    
    checks = AIntegrityCheck.getRegisteredChecks()
    for check_cls in checks:
        check = check_cks(api, db, options)
        try:
            check.run()
        except:
            utils.printException()

if __name__ == '__main__':
    main()

