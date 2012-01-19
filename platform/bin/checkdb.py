#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import logs, random, time, utils

from MongoStampedAPI    import MongoStampedAPI
from optparse           import OptionParser
from pprint             import pprint
from functools          import wraps

# Index collections
#   inboxstamps
#   creditgivers
# Object stats
# Object references
# Object validation
# Data enrichment

__integrity_checks = []

class IntegrityError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)

def integrity_check(max_retries=5, retry_delay=0.5):
    def decorating_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            noop    = args[0].noop
            retries = 0
            
            while True:
                try:
                    args[0].noop = (retries < max_retries)
                    retval = func(*args, **kwargs)
                    return retval
                except Exception, e:
                    retries += 1
                    
                    if retries > max_retries:
                        raise
                    
                    time.sleep(retry_delay)
                finally:
                    args[0].noop = noop
        
        __integrity_checks.append(wrapper)
        return wrapper
    
    if type(max_retries) == type(decorating_function):
        return decorating_function(max_retries)
    
    return decorating_function

def sample(iterable, ratio, func, print_progress=True, progress_step=5):
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
            func(obj)
        
        index += 1

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

@integrity_check
def check_inboxstamps(options, api, db):
    """ Ensure the integrity of inbox stamps """
    
    def check_inbox(doc):
        user_id = doc['_id']
        ref_ids = doc['ref_ids']
        
        friend_ids = get_friend_ids(db, user_id)
        friend_ids.append(user_id)
        
        stamp_ids   = get_stamp_ids_from_user_ids(db['stamps'], friend_ids)
        deleted_ids = get_stamp_ids_from_user_ids(db['deletedstamps'], friend_ids)
        stamp_ids.extend(deleted_ids)
        
        def correct(error):
            if options.noop:
                raise error
            
            logs.warn('RESOLVING: %s' % str(error))
            
            doc['ref_ids'] = stamp_ids
            db['inboxstamps'].save(doc)
        
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
    
    sample(db['inboxstamps'].find(), options.sampleSetRatio, check_inbox)

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
    
    check_inboxstamps(options, api, db)

if __name__ == '__main__':
    main()

