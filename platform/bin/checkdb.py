#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from bin import integrity
import logs, pymongo, random, time, utils

from api.MongoStampedAPI    import MongoStampedAPI
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

class AIntegrityCheck(object):
    
    def __init__(self, api, db, options):
        self.api = api
        self.db  = db
        self.options = options
    
    def _sample(self, iterable, func, 
                print_progress=True, progress_delta=5, 
                max_retries=0, retry_delay=0.05):
        progress_count = 100 / progress_delta
        ratio = self.options.sampleSetRatio
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
                utils.log("%s : %s" % (self.__class__.__name__, utils.getStatusStr(index, count)))
            
            if random.random() < ratio:
                noop    = self.options.noop
                retries = 0
                
                while True:
                    try:
                        self.options.noop = (retries < max_retries) or noop
                        func(obj)
                        break
                    except Exception, e:
                        utils.printException()
                        retries += 1
                        
                        if noop or retries > max_retries:
                            prefix = "ERROR" if noop else "UNRESOLVABLE ERROR"
                            utils.log("%s: %s" % (prefix, str(e)))
                            break
                        
                        time.sleep(retry_delay)
                        retry_delay *= 2
                    finally:
                        self.options.noop = noop
            
            index += 1
    
    def _handle_error(self, msg):
        #if self.options.noop:
        #    raise IntegrityError(msg)
        
        utils.log('ERROR: %s' % msg)
    
    def _get_friend_ids(self, user_id):
        friend_ids = self.db['friends'].find_one({ '_id' : user_id }, { 'ref_ids' : 1 })
        
        if friend_ids is not None:
            return friend_ids['ref_ids']
        else:
            return []
    
    def _get_field(self, doc, key):
        if '.' in key:
            def _extract(o, args):
                try:
                    if 0 == len(args):
                        return o
                    
                    return _extract(o[args[0]], args[1:])
                except:
                    return None
            
            s = key.split('.')
            return _extract(doc, s)
        else:
            return doc[key]
    
    def _strip_ids(self, docs, key='_id'):
        if '.' in key:
            def __extract(doc):
                def _extract(o, args):
                    try:
                        if 0 == len(args):
                            return o
                        
                        return _extract(o[args[0]], args[1:])
                    except:
                        return None
                
                s = key.split('.')
                return _extract(doc, s)
            
            extract = __extract
        else:
            extract = lambda o: str(o[key])
        
        return map(extract, docs)
    
    def _get_stamp_ids_from_user_ids(self, user_ids):
        if not isinstance(user_ids, (list, tuple)):
            user_ids = [ user_ids ]
        
        if 1 == len(user_ids):
            query = user_ids[0]
        else:
            query = { '$in' : user_ids }
        
        return self._strip_ids(self.db['stamps'].find({ 'user.user_id' : query }, { '_id' : 1 }))
    
    def _get_stamp_ids_from_credited_user_id(self, user_id):
        return self._strip_ids(self.db['stamps'].find({ 'credit.user_id' : user_id }, { '_id' : 1 }))
    
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

