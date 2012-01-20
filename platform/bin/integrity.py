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
    
    def __init__(self, api, db, options, collection):
        AIntegrityCheck.__init__(self, api, db, options)
        self._collection = collection
    
    def run(self):
        self._sample(self.db[self._collection].find(), 
                     self.options.sampleSetRatio, 
                     self.check_doc, 
                     max_retries=0, 
                     progress_delta=1)
    
    @abstract
    def _get_cmp(self, doc_id):
        pass
    
    def check_doc(self, doc):
        doc_id  = doc['_id']
        ref_ids = set(doc['ref_ids'])
        
        cmp_ids  = set(self._get_cmp(doc_id))
        
        invalid_cmp_ids = []
        missing_cmp_ids = []
        
        for cmp_id in ref_ids:
            if cmp_id not in cmp_ids:
                ret = self.db['deletedstamps'].find_one({"_id" : bson.objectid.ObjectId(cmp_id)})
                
                if ret is None:
                    invalid_cmp_ids.append(cmp_id)
        
        for cmp_id in cmp_ids:
            if cmp_id not in ref_ids:
                missing_cmp_ids.append(cmp_id)
        
        if len(invalid_cmp_ids) > 0:
            self._handle_error("%s integrity error: found %d invalid stamps; %s" % (
                self._collection, len(invalid_cmp_ids), {
                'doc_id'  : doc_id, 
                'cmp_ids' : invalid_cmp_ids, 
            }))
        
        if len(missing_cmp_ids) > 0:
            self._handle_error("%s integrity error: found %d missing stamps; %s" % (
                self._collection, len(missing_cmp_ids), {
                'doc_id'  : doc_id, 
                'cmp_ids' : missing_cmp_ids, 
            }))
        
        if not self.options.noop and (len(invalid_cmp_ids) > 0 or len(missing_cmp_ids) > 0):
            for cmp_id in invalid_cmp_ids:
                ref_ids.remove(cmp_id)
            
            for cmp_id in missing_cmp_ids:
                ref_ids.add(cmp_id)
            
            doc[key] = list(ref_ids)
            self.db[_collection].save(doc)

class InboxStampsIntegrityCheck(AIndexCollectionIntegrityCheck):
    """ Ensures the integrity of inbox stamps """
    
    def __init__(self, api, db, options):
        AIndexCollectionIntegrityCheck.__init__(self, api, db, options, 'inboxstamps')
    
    def _get_cmp(self, doc_id):
        friend_ids = self._get_friend_ids(doc_id)
        friend_ids.append(doc_id)
        
        return self._get_stamp_ids_from_user_ids(friend_ids)

class UserStatsIntegrityCheck(AIndexCollectionIntegrityCheck):
    """ Ensures the integrity of creditreceived """
    
    def __init__(self, api, db, options):
        AIndexCollectionIntegrityCheck.__init__(self, api, db, options, 'creditreceived')
    
    def _get_cmp(self, doc_id):
        return self._get_stamp_ids_from_credited_user_id(doc_id)

checks = [
    InboxStampsIntegrityCheck, 
    UserStatsIntegrityCheck, 
]

