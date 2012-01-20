#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import bson, logs, utils

from utils      import abstract
from checkdb    import *

class AIndexCollectionIntegrityCheck(AIntegrityCheck):
    
    def __init__(self, api, db, options, collection, stat_collection=None, stat=None):
        AIntegrityCheck.__init__(self, api, db, options)
        self._collection = collection
        self._stat_collection = stat_collection
        self._stat = stat
    
    def run(self):
        self._sample(self.db[self._collection].find(), 
                     self.options.sampleSetRatio, 
                     self.check_doc, 
                     max_retries=0, 
                     progress_delta=1)
    
    @abstract
    def _get_cmp(self, doc_id):
        pass
    
    def _is_invalid_id(self, doc_id):
        return True
    
    def check_doc(self, doc):
        doc_id  = doc['_id']
        ref_ids = set(doc['ref_ids'])
        
        cmp_ids  = set(self._get_cmp(doc_id))
        
        invalid_cmp_ids = []
        missing_cmp_ids = []
        
        for cmp_id in ref_ids:
            if cmp_id not in cmp_ids:
                if self._is_invalid_id(cmp_id):
                    invalid_cmp_ids.append(cmp_id)
        
        for cmp_id in cmp_ids:
            if cmp_id not in ref_ids:
                missing_cmp_ids.append(cmp_id)
        
        if len(invalid_cmp_ids) > 0:
            self._handle_error("%s integrity error: found %d invalid reference%s; %s" % (
                self._collection, len(invalid_cmp_ids), "" if 1 == len(invalid_cmp_ids) else "s", {
                'doc_id'  : doc_id, 
                'cmp_ids' : invalid_cmp_ids, 
            }))
        
        if len(missing_cmp_ids) > 0:
            self._handle_error("%s integrity error: found %d missing reference%s; %s" % (
                self._collection, len(missing_cmp_ids), "" if 1 == len(missing_cmp_ids) else "s", {
                'doc_id'  : doc_id, 
                'cmp_ids' : missing_cmp_ids, 
            }))
        
        for cmp_id in invalid_cmp_ids:
            ref_ids.remove(cmp_id)
        
        for cmp_id in missing_cmp_ids:
            ref_ids.add(cmp_id)
        
        doc['ref_ids'] = list(ref_ids)
        if not self.options.noop and (len(invalid_cmp_ids) > 0 or len(missing_cmp_ids) > 0):
            self.db[_collection].save(doc)
        
        if self._stat_collection is not None and self._stat is not None:
            doc2 = self.db[self._stat_collection].find_one({"_id" : bson.objectid.ObjectId(doc_id)})
            def extract(o, args):
                try:
                    if 0 == len(args):
                        return o
                    
                    return extract(o[args[0]], args[1:])
                except:
                    return None
            
            s = self._stat.split('.')
            stat = extract(doc2, s)
            
            if (stat is None and 0 == len(ref_ids)) or (stat is not None and stat != len(ref_ids)):
                self._handle_error("%s integrity error: invalid stat %s; %s" % (
                    self._collection, self._stat, {
                    'doc_id'   : doc_id, 
                    'expected' : len(ref_ids), 
                    'found'    : stat, 
                }))
                
                #if not self.options.noop:
                doc3 = doc2
                while len(s) > 1:
                    doc3 = doc3[s[0]]
                    s = s[1:]
                
                doc3[s[0]] = len(ref_ids)
                pprint(doc2)
                #self.db[self._stat_collection].save(doc2)

class InboxStampsIntegrityCheck(AIndexCollectionIntegrityCheck):
    """
        Ensures the integrity of the inboxstamps collection, which maps 
        user_ids to a list of stamp_ids in that user's inbox.
    """
    
    def __init__(self, api, db, options):
        AIndexCollectionIntegrityCheck.__init__(self, api, db, options, 'inboxstamps')
    
    def _is_invalid_id(self, doc_id):
        ret = self.db['deletedstamps'].find_one({"_id" : bson.objectid.ObjectId(cmp_id)})
        return ret is None
    
    def _get_cmp(self, doc_id):
        friend_ids = self._get_friend_ids(doc_id)
        friend_ids.append(doc_id)
        
        return self._get_stamp_ids_from_user_ids(friend_ids)

class CreditReceivedIntegrityCheck(AIndexCollectionIntegrityCheck):
    """
        Ensures the integrity of the creditreceived collection, which maps 
        user_ids to stamp_ids of stamps for which user has received credit.
    """
    
    def __init__(self, api, db, options):
        AIndexCollectionIntegrityCheck.__init__(self, api, db, options, 
                                                collection='creditreceived', 
                                                stat_collection='users', 
                                                stat='stats.num_credits')
    
    def _get_cmp(self, doc_id):
        return self._get_stamp_ids_from_credited_user_id(doc_id)

class UserFavEntitiesIntegrityCheck(AIndexCollectionIntegrityCheck):
    """
        Ensures the integrity of userfaventities collection, which maps 
        user_ids to entity_ids that user has favorited.
    """
    
    def __init__(self, api, db, options):
        AIndexCollectionIntegrityCheck.__init__(self, api, db, options, 'userfaventities')
    
    def _get_cmp(self, doc_id):
        return self._strip_ids(self.db['favorites'].find({'user_id': doc_id}, {'entity.entity_id':1}), key='entity.entity_id')

checks = [
    InboxStampsIntegrityCheck, 
    CreditReceivedIntegrityCheck, 
    UserFavEntitiesIntegrityCheck, 
]

