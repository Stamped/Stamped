#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import bson, logs, utils

from utils      import abstract
from checkdb    import *

class AStatIntegrityCheck(AIntegrityCheck):
    
    def __init__(self, api, db, options, collection, stat, **kwargs):
        AIntegrityCheck.__init__(self, api, db, options)
        self._stat_collection = collection
        self._stat = stat
        self._sample_kwargs = kwargs
    
    def run(self):
        self._sample(self.db[self._stat_collection].find(), 
                     self.options.sampleSetRatio, 
                     self.check_doc, **self._sample_kwargs)
    
    @abstract
    def _get_cmp_value(self, doc_id):
        pass
    
    def check_doc_id(self, doc_id, value):
        if self._stat_collection is None or self._stat is None:
            return
        
        doc = self.db[self._stat_collection].find_one({"_id" : bson.objectid.ObjectId(doc_id)})
        
        if doc is None:
            return
        
        return self.check_doc(doc, value)
    
    def check_doc(self, doc, value=None):
        doc_id = str(doc['_id'])
        
        def extract(o, args):
            try:
                if 0 == len(args):
                    return o
                
                return extract(o[args[0]], args[1:])
            except:
                return None
        
        s = self._stat.split('.')
        stat = extract(doc, s)
        if value is None:
            value = self._get_cmp_value(doc_id)
        
        # update the cached stat if it doesn't match its expected value
        if (stat is None and value > 0) or (stat is not None and stat != value):
            self._handle_error("%s integrity error: invalid stat %s; %s" % (
                self._stat_collection, self._stat, {
                'doc_id'   : doc_id, 
                'expected' : value, 
                'found'    : stat, 
            }))
            
            if not self.options.noop:
                doc2 = doc
                while len(s) > 1:
                    doc2 = doc2[s[0]]
                    s = s[1:]
                
                doc2[s[0]] = value
                self.db[self._stat_collection].save(doc)

class AIndexCollectionIntegrityCheck(AStatIntegrityCheck):
    
    def __init__(self, api, db, options, collection, stat_collection=None, stat=None, **kwargs):
        AStatIntegrityCheck.__init__(self, api, db, options, stat_collection, stat, **kwargs)
        self._collection = collection
    
    def run(self):
        self._sample(self.db[self._collection].find(), 
                     self.options.sampleSetRatio, 
                     self.check_doc, 
                     **self._sample_kwargs)
    
    @abstract
    def _get_cmp(self, doc_id):
        pass
    
    def _get_cmp_value(self, doc_id):
        raise NotImplementedError("should never reach this point")
    
    def _is_invalid_id(self, doc_id):
        return True
    
    def check_doc(self, doc):
        # extract the id and reference ids from the document
        doc_id  = str(doc['_id'])
        ref_ids = set(doc['ref_ids'])
        
        # get all true comparison ids
        cmp_ids  = set(self._get_cmp(doc_id))
        
        # compare the actual ref_ids with the expected cmp_ids, keeping track 
        # of all invalid and missing ids
        invalid_cmp_ids = []
        missing_cmp_ids = []
        
        for cmp_id in ref_ids:
            if cmp_id not in cmp_ids:
                if self._is_invalid_id(cmp_id):
                    invalid_cmp_ids.append(cmp_id)
        
        for cmp_id in cmp_ids:
            if cmp_id not in ref_ids:
                missing_cmp_ids.append(cmp_id)
        
        # complain if we found unexpected ids
        if len(invalid_cmp_ids) > 0:
            self._handle_error("%s integrity error: found %d invalid reference%s; %s" % (
                self._collection, len(invalid_cmp_ids), "" if 1 == len(invalid_cmp_ids) else "s", {
                'doc_id'  : doc_id, 
                'cmp_ids' : invalid_cmp_ids, 
            }))
        
        # complain if we found missing ids
        if len(missing_cmp_ids) > 0:
            self._handle_error("%s integrity error: found %d missing reference%s; %s" % (
                self._collection, len(missing_cmp_ids), "" if 1 == len(missing_cmp_ids) else "s", {
                'doc_id'  : doc_id, 
                'cmp_ids' : missing_cmp_ids, 
            }))
        
        # optionally store the updated document after updating the reference ids
        if not self.options.noop and (len(invalid_cmp_ids) > 0 or len(missing_cmp_ids) > 0):
            for cmp_id in invalid_cmp_ids:
                ref_ids.remove(cmp_id)
            
            for cmp_id in missing_cmp_ids:
                ref_ids.add(cmp_id)
            
            doc['ref_ids'] = list(ref_ids)
            self.db[_collection].save(doc)
        
        # if there is a corresponding stat storing the count of ref_ids, ensure 
        # that it is also in sync with the underlying list of references.
        AStatIntegrityCheck.check_doc_id(self, doc_id, value=len(ref_ids))

class InboxStampsIntegrityCheck(AIndexCollectionIntegrityCheck):
    """
        Ensures the integrity of the inboxstamps collection, which maps 
        user_ids to stamp_ids in the user's inbox.
    """
    
    def __init__(self, api, db, options):
        AIndexCollectionIntegrityCheck.__init__(self, api, db, options, 
                                                collection='inboxstamps', 
                                                progress_delta=1)
    
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
        user_ids to stamp_ids for which the user has received credit.
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
        Ensures the integrity of the userfaventities collection, which maps 
        user_ids to entity_ids the user has favorited.
    """
    
    def __init__(self, api, db, options):
        AIndexCollectionIntegrityCheck.__init__(self, api, db, options, 
                                                collection='userfaventities', 
                                                stat_collection='users', 
                                                stat='stats.num_faves')
    
    def _get_cmp(self, doc_id):
        return self._strip_ids(self.db['favorites'].find({'user_id' : doc_id}, {'entity.entity_id' :1}), key='entity.entity_id')

class UserLikesIntegrityCheck(AIndexCollectionIntegrityCheck):
    """
        Ensures the integrity of the userlikes collection, which maps 
        user_ids to stamp_ids the user has liked.
    """
    
    def __init__(self, api, db, options):
        AIndexCollectionIntegrityCheck.__init__(self, api, db, options, 
                                                collection='userlikes', 
                                                stat_collection='users', 
                                                stat='stats.num_likes_given')
    
    def _get_cmp(self, doc_id):
        return self._strip_ids(self.db['stamplikes'].find({'ref_ids' : doc_id}, {'_id' :1}))

class UserStampsIntegrityCheck(AIndexCollectionIntegrityCheck):
    """
        Ensures the integrity of the userstamps collection, which maps 
        user_ids to stamp_ids created by the user.
    """
    
    def __init__(self, api, db, options):
        AIndexCollectionIntegrityCheck.__init__(self, api, db, options, 
                                                collection='userstamps', 
                                                stat_collection='users', 
                                                stat='stats.num_stamps')
    
    def _get_cmp(self, doc_id):
        return self._strip_ids(self.db['stamps'].find({'user.user_id' : doc_id}, {'_id' : 1}))

class NumFriendsIntegrityCheck(AStatIntegrityCheck):
    """
        Ensures the integrity of the the num_friends user statistic.
    """
    
    def __init__(self, api, db, options):
        AStatIntegrityCheck.__init__(self, api, db, options, 
                                     collection='users', 
                                     stat='stats.num_friends', 
                                     progress_delta=1)
    
    def _get_cmp_value(self, doc_id):
        followers = self.db['followers'].find_one({'_id' : doc_id}, {'ref_ids' : 1, '_id' : 0})
        if followers != None:
            return len(followers['ref_ids'])

checks = [
    InboxStampsIntegrityCheck, 
    CreditReceivedIntegrityCheck, 
    UserFavEntitiesIntegrityCheck, 
    UserLikesIntegrityCheck, 
    UserStampsIntegrityCheck, 
    NumFriendsIntegrityCheck, 
]

