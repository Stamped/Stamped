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
    
    def _sample(self, iterable, ratio, func, print_progress=True, progress_step=5, max_retries=5, retry_delay=0.5):
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
        
        utils.log(count)
        
        for obj in iterable:
            if print_progress and (count < progress_count or 0 == (index % (count / progress_count))):
                utils.log("%s : %s" % (func.__name__, utils.getStatusStr(index, count)))

            if random.random() < ratio:
                noop    = self.options.noop
                retries = 0
                
                while True:
                    try:
                        self.options.noop = (retries < max_retries) or noop
                        retval = func(obj)
                        return retval
                    except Exception, e:
                        retries += 1
                        
                        if retries > max_retries:
                            prefix = "ERROR: " if noop else "UNRESOLVABLE ERROR: "
                            logs.error("%s: %s" % (prefix, str(e)))
                        
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    finally:
                        self.options.noop = noop
            
            index += 1
    
    @abstract
    def run():
        pass

class InboxStampsIntegrityCheck(AIntegrityCheck):
    """ Ensure the integrity of inbox stamps """
    
    def run(self):
        self._sample(self.db['inboxstamps'].find(), self.options.sampleSetRatio, self.check_inbox)
    
    def check_inbox(self, doc):
        user_id = doc['_id']
        ref_ids = doc['ref_ids']
        
        friend_ids = get_friend_ids(self.db, user_id)
        friend_ids.append(user_id)
        
        stamp_ids   = get_stamp_ids_from_user_ids(self.db['stamps'], friend_ids)
        deleted_ids = get_stamp_ids_from_user_ids(self.db['deletedstamps'], friend_ids)
        stamp_ids.extend(deleted_ids)
        
        def correct(error):
            if self.options.noop:
                raise error
            
            logs.warn('RESOLVING: %s' % str(error))
            
            doc['ref_ids'] = stamp_ids
            self.db['inboxstamps'].save(doc)
        
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
    
    InboxStampsIntegrityCheck(api, db, options).run()

if __name__ == '__main__':
    main()

