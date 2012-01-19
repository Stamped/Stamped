#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils
import time

from MongoStampedAPI    import MongoStampedAPI
from optparse           import OptionParser
from pprint             import pprint
from functools          import wraps

__integrity_checks = []

class IntegrityError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

def integrity_check(f, max_retries=0, retry_delay=0.5):
    @wraps(f)
    def wrapper(*args, **kwargs):
        retries = 0
        
        while True:
            try:
                return f(*args, **kwargs)
            except Exception, e:
                retries += 1
                
                if retries > max_retries:
                    raise
                
                time.sleep(retry_delay)
    
    __integrity_checks.append(wrapper)
    return wrapper
def sample(f, ratio):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if random.random() < ratio:
            f(*args, **kwargs)
    
    return wrapper

@integrity_check
def check_inboxstamps(api, db, options):
    def check(doc):
        user_id = doc['_id']
        ref_ids = doc['ref_ids']
        
        friend_ids = db['friends'].find_one({ '_id' : user_id }, { 'ref_ids' : 1 })['ref_ids']
        friend_ids.append(user_id)
        
        stamp_ids  = set(map(lambda o: str(o['_id']), db['stamps'].find({ 'user.user_id' : { '$in' : friend_ids } }, { '_id' : 1 })))
        
        def correct(error)
            if options.noop:
                raise error
            
            logs.warn('RESOLVING: %s' % str(error))
            doc['ref_ids'] = stamp_ids
            db['inboxstamps'].update(doc)
        
        if len(ref_ids) != len(stamp_ids):
            return correct(IntegrityError("inboxstamps integrity error: %s" % {
                    'user_id' : user_id, 
                    'len_ref_ids'   : len(ref_ids), 
                    'len_stamp_ids' : len(stamp_ids), 
                }))
        
        for ref_id in ref_ids:
            if ref_id not in stamp_ids:
                return correct(IntegrityError("inboxstamps integrity error: %s" % {
                    'user_id'  : user_id, 
                    'stamp_id' : ref_id
                }))
    
    for doc in db['inboxstamps'].find():
        check(doc)

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", help="db to connect to")
    
    parser.add_option("-n", "--noop", default=False, 
        action="store_true", help="noop mode (run read-only)")
    
    parser.add_option("-s", "--sampleSize", default=None, type="int", 
        action="store", help="sample size as a percentage (e.g., 5 for 5%)")
    
    (options, args) = parser.parse_args()
    
    if options.sampleSize is None:
        options.sampleSize = 1.0
    else:
        options.sampleSize = options.sampleSize / 100.0
    
    if options.db:
        utils.init_db_config(options.db)
    
    return (options, args)

def main():
    options, args = parseCommandLine()
    
    api = MongoStampedAPI(lite_mode=True)
    db  = api._entityDB._collection._database
    
    check_inboxstamps(api, db, options)

if __name__ == '__main__':
    main()

