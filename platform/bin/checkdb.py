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

class IntegrityError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

def get_friend_ids(db, user_id):
    friend_ids = db['friends'].find_one({ '_id' : user_id }, { 'ref_ids' : 1 })
    
    if friend_ids is not None:
        return friend_ids['ref_ids']
    else:
        return []

def strip_ids(docs):
    return map(lambda o: str(o['_id']), docs)

def get_stamp_ids_from_user_ids(db, user_ids):
    if not isinstance(user_ids, (list, tuple)):
        user_ids = [ user_ids ]
    
    if 1 == len(user_ids):
        query = user_ids[0]
    else:
        query = { '$in' : user_ids }
    
    return strip_ids(db['stamps'].find({ 'user.user_id' : query }, { '_id' : 1 }))

def get_stamp_ids_from_credited_user_id(db, user_id):
    return strip_ids(db['stamps'].find({ 'credit.user_id' : user_id }, { '_id' : 1 }))

class AIntegrityCheck(object):
    
    def __init__(self, api, db, options):
        self.api = api
        self.db  = db
        self.options = options
    
    def _sample(self, iterable, ratio, func, print_progress=True, progress_delta=5, max_retries=3, retry_delay=0.05):
        progress_count = 100 / progress_delta
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
    
    def _handle_error(self, msg):
        if self.options.noop:
            raise IntegrityError(msg)
        
        logs.warn(msg)
    
    def _update_doc(self, collection, doc, key, ref_ids, invalid_stamp_ids, missing_stamp_ids):
        if not self.options.noop and (len(invalid_stamp_ids) > 0 or len(missing_stamp_ids) > 0):
            for stamp_id in invalid_stamp_ids:
                ref_ids.remove(stamp_id)
            
            for stamp_id in missing_stamp_ids:
                ref_ids.add(stamp_id)
            
            doc[key] = list(ref_ids)
            collection.save(doc)
    
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
    
    parser.add_option("-f", "--filter", default=None, 
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
    
    checks = integrity.checks
    for check_cls in checks:
        if options.filter is None or options.filter.lower() in check_cls.__name__.lower():
            check = check_cls(api, db, options)
            
            try:
                utils.log("running integrity check '%s'" % check_cls.__name__)
                check.run()
                utils.log("done running integrity check '%s'" % check_cls.__name__)
            except:
                utils.printException()
            
            utils.log()

if __name__ == '__main__':
    main()

