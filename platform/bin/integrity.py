#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import logs, utils
from checkdb import *

class InboxStampsIntegrityCheck(AIntegrityCheck):
    """ Ensure the integrity of inbox stamps """
    
    def run(self):
        self._sample(self.db['inboxstamps'].find(), 
                     self.options.sampleSetRatio, 
                     self.check_inbox, 
                     max_retries=0, 
                     progress_step=1)
    
    def check_inbox(self, doc):
        user_id = doc['_id']
        ref_ids = doc['ref_ids']
        
        friend_ids = get_friend_ids(self.db, user_id)
        friend_ids.append(user_id)
        
        stamp_ids   = get_stamp_ids_from_user_ids(self.db['stamps'], friend_ids)
        #deleted_ids = get_stamp_ids_from_user_ids(self.db['deletedstamps'], friend_ids)
        #stamp_ids.extend(deleted_ids)
        
        def correct(error):
            if self.options.noop:
                raise error
            
            logs.warn('RESOLVING: %s' % str(error))
            
            # TODO: how to resolve discrepancies here?
            #doc['ref_ids'] = stamp_ids
            #self.db['inboxstamps'].save(doc)
        
        # TODO: check deleted stamps if numbers don't match up
        
        if len(ref_ids) > len(stamp_ids):
            return correct(IntegrityError("inboxstamps integrity error: %s" % {
                    'user_id' : user_id, 
                    'actual #stamps'   : len(ref_ids), 
                    'expected #stamps' : len(stamp_ids), 
                }))
        
        for stamp_id in ref_ids:
            if stamp_id not in stamp_ids:
                ret = db['deletedstamps'].find_one({"_id" : bson.objectid.ObjectId(stamp_id)})
                
                return correct(IntegrityError("inboxstamps integrity error: %s" % {
                    'user_id'  : user_id, 
                    'stamp_id' : stamp_id, 
                }))

AIntegrityCheck.register(InboxStampsIntegrityCheck)

