#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import bson, logs, utils
import api.Schemas as Schemas

from utils      import abstract
from checkdb    import *

"""
Index collections
Object stats
Object references
Object validation
Data enrichment

TODO:
    * ensure entities and places are in sync
"""


class ADocumentIntegrityCheck(AIntegrityCheck):
    """
        Abstract superclass for verifying the existence and correctness of 
        key fields in all documents across a collection.
    """
    
    def __init__(self, api, db, options, collection, id_field=None, schema=None, **kwargs):
        AIntegrityCheck.__init__(self, api, db, options)
        
        self._sample_kwargs = kwargs
        self._collection = collection
        self._id_field = id_field
        self._schema = schema
    
    def run(self):
        self._sample(self._get_docs(), 
                     self._check_doc, 
                     **self._sample_kwargs)
    
    def _get_docs(self):
        return self.db[self._collection].find()
    
    def _check_schema(self, obj):
        pass
    
    def _get_schema(self, doc):
        return self._schema(doc)
    
    def _verify_doc(self, doc):
        pass
    
    def _check_doc(self, doc):
        doc_id = str(doc['_id'])
        
        if self._id_field is not None:
            doc[self._id_field] = str(doc['_id'])
            del doc['_id']
        
        if self._schema is not None:
            try:
                self._verify_doc(doc)
                obj = self._get_schema(doc)
                self._check_schema(obj)
            except Exception, e:
                self._handle_error("%s integrity error: document failed %s schema check (%s); %s" % (
                    self._collection, self._schema.__name__, str(e), {
                    'doc_id' : doc_id, 
                    'doc'    : doc, 
                }))

class AReferenceIntegrityCheck(AIntegrityCheck):
    """
        Abstract superclass for verifying the existence of cross-collection 
        object references.
    """
    
    def __init__(self, api, db, options, collection, refs, **kwargs):
        AIntegrityCheck.__init__(self, api, db, options)
        
        self._sample_kwargs = kwargs
        self._collection = collection
        self._refs = refs
    
    def run(self):
        self._sample(self._get_docs(), 
                     self._check_doc, 
                     **self._sample_kwargs)
    
    def _get_docs(self):
        return self.db[self._collection].find()
    
    def _check_doc(self, doc):
        doc_id = str(doc['_id'])
        
        for reference, collection in self._refs.iteritems():
            try:
                ref_id = str(self._get_field(doc, reference))
            except KeyError:
                ref_id = None
            
            if ref_id is None:
                self._handle_error("%s integrity error: missing required object reference %s; %s" % (
                    self._collection, reference, {
                    'doc_id' : doc_id, 
                    'object' : doc, 
                }))
                break
            
            try:
                obj = self.db[collection].find({"_id" : bson.objectid.ObjectId(ref_id)})
            except:
                obj = None
            
            if obj is None:
                self._handle_error("%s integrity error: object reference %s doesn't exist in %s; %s" % (
                    self._collection, reference, collection, {
                    'doc_id' : doc_id, 
                    'ref_id' : ref_id, 
                    'object' : doc, 
                }))

class AStatIntegrityCheck(AIntegrityCheck):
    
    def __init__(self, api, db, options, collection, stat, **kwargs):
        AIntegrityCheck.__init__(self, api, db, options)
        
        self._stat_collection = collection
        self._stat = stat
        self._sample_kwargs = kwargs
    
    def run(self):
        self._sample(self.db[self._stat_collection].find(), 
                     self._check_doc, **self._sample_kwargs)
    
    @abstract
    def _get_cmp_value(self, doc_id):
        pass
    
    def check_doc_id(self, doc_id, value):
        if self._stat_collection is None or self._stat is None:
            return
        
        doc = self.db[self._stat_collection].find_one({"_id" : bson.objectid.ObjectId(doc_id)})
        
        if doc is None:
            return
        
        return self.check_doc_value(doc, value)
    
    def _check_doc(self, doc):
        doc_id = str(doc['_id'])
        value = self._get_cmp_value(doc_id)
        
        return self.check_doc_value(doc, value)
    
    def check_doc_value(self, doc, value):
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
        
        # update the cached stat if it doesn't match its expected value
        if (stat is None and value > 0) or (stat is not None and stat != value):
            self._handle_error("%s integrity error: invalid value for stat %s; %s" % (
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
    """
        Abstract superclass for all index collection integrity checks. An index
        collection is 
    """
    
    def __init__(self, api, db, options, collection, stat_collection=None, stat=None, **kwargs):
        AStatIntegrityCheck.__init__(self, api, db, options, stat_collection, stat, **kwargs)
        self._collection = collection
    
    def run(self):
        self._sample(self.db[self._collection].find(), 
                     self._check_doc, 
                     **self._sample_kwargs)
    
    @abstract
    def _get_cmp(self, doc_id):
        pass
    
    def _get_cmp_value(self, doc_id):
        raise NotImplementedError("should never reach this point")
    
    def _is_invalid_id(self, doc_id):
        return True
    
    def _check_doc(self, doc):
        # extract the id and reference ids from the document
        doc_id  = str(doc['_id'])
        ref_ids = set(doc['ref_ids'])
        
        # get all true comparison ids
        cmp_ids = set(self._get_cmp(doc_id))
        
        # compare the actual ref_ids with the expected cmp_ids, keeping track 
        # of all invalid and missing ids
        invalid_ids = []
        missing_ids = []
        
        for ref_id in ref_ids:
            if ref_id not in cmp_ids:
                if self._is_invalid_id(ref_id):
                    invalid_ids.append(ref_id)
        
        for cmp_id in cmp_ids:
            if cmp_id not in ref_ids:
                missing_ids.append(cmp_id)
        
        #utils.log("%d vs %d" % (len(invalid_ids), len(missing_ids)))
        
        # complain if we found unexpected ids
        if len(invalid_ids) > 0:
            self._handle_error("%s integrity error: found %d invalid reference%s; %s" % (
                self._collection, len(invalid_ids), "" if 1 == len(invalid_ids) else "s", {
                '_id'  : doc_id, 
                '_ids' : invalid_ids, 
            }))
        
        # complain if we found missing ids
        if len(missing_ids) > 0:
            self._handle_error("%s integrity error: found %d missing reference%s; %s" % (
                self._collection, len(missing_ids), "" if 1 == len(missing_ids) else "s", {
                '_id'  : doc_id, 
                '_ids' : missing_ids, 
            }))
        
        # optionally store the updated document after updating the reference ids
        if not self.options.noop and (len(invalid_ids) > 0 or len(missing_ids) > 0):
            for cmp_id in invalid_ids:
                ref_ids.remove(cmp_id)
            
            for cmp_id in missing_ids:
                ref_ids.add(cmp_id)
            
            doc['ref_ids'] = list(ref_ids)
            self.db[_collection].save(doc)
        
        # if there is a corresponding stat storing the count of ref_ids, ensure 
        # that it is also in sync with the underlying list of references.
        AStatIntegrityCheck.check_doc_id(self, doc_id, value=len(cmp_ids))

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
        ret = self.db['deletedstamps'].find_one({"_id" : bson.objectid.ObjectId(doc_id)})
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

class StampCommentsIntegrityCheck(AIndexCollectionIntegrityCheck):
    """
        Ensures the integrity of the stampcomments collection, which maps 
        stamp_ids to comment_ids associated with the stamp.
    """
    
    def __init__(self, api, db, options):
        AIndexCollectionIntegrityCheck.__init__(self, api, db, options, 
                                                collection='stampcomments', 
                                                stat_collection='stamps', 
                                                stat='stats.num_comments')
    
    def _get_cmp(self, doc_id):
        return self._strip_ids(self.db['comments'].find({'stamp_id' : doc_id}, {'_id' : 1}))

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
        friends = self.db['friends'].find_one({'_id' : doc_id}, {'ref_ids' : 1, '_id' : 0})
        
        return 0 if friends is None else len(friends['ref_ids'])

class NumFollowersIntegrityCheck(AStatIntegrityCheck):
    """
        Ensures the integrity of the the num_followers user statistic.
    """
    
    def __init__(self, api, db, options):
        AStatIntegrityCheck.__init__(self, api, db, options, 
                                     collection='users', 
                                     stat='stats.num_followers', 
                                     progress_delta=1)
    
    def _get_cmp_value(self, doc_id):
        followers = self.db['followers'].find_one({'_id' : doc_id}, {'ref_ids' : 1, '_id' : 0})
        
        return 0 if followers is None else len(followers['ref_ids'])

class NumLikesIntegrityCheck(AStatIntegrityCheck):
    """
        Ensures the integrity of the the num_likes stamp statistic.
    """
    
    def __init__(self, api, db, options):
        AStatIntegrityCheck.__init__(self, api, db, options, 
                                     collection='stamps', 
                                     stat='stats.num_likes', 
                                     progress_delta=1)
    
    def _get_cmp_value(self, doc_id):
        likes = self.db['stamplikes'].find_one({'_id' : doc_id}, {'ref_ids' : 1, '_id' : 0})
        
        return 0 if likes is None else len(likes['ref_ids'])

class StampsReferenceIntegrityCheck(AReferenceIntegrityCheck):
    """
        Verifies all external document references in the stamps collection.
    """
    
    def __init__(self, api, db, options):
        AReferenceIntegrityCheck.__init__(self, api, db, options, 
                                          collection='stamps', 
                                          refs={
                                              'entity.entity_id' : 'entities', 
                                              'user.user_id' : 'users', 
                                          })

class FavoritesReferenceIntegrityCheck(AReferenceIntegrityCheck):
    """
        Verifies all external document references in the favorites collection.
    """
    
    def __init__(self, api, db, options):
        AReferenceIntegrityCheck.__init__(self, api, db, options, 
                                          collection='favorites', 
                                          refs={
                                              'entity.entity_id' : 'entities', 
                                              'user_id' : 'users', 
                                          })

class FavoritesStampReferenceIntegrityCheck(AReferenceIntegrityCheck):
    """
        Verifies all external document references in the favorites collection, 
        specifically for favorites which are based off of a stamp.
    """
    
    def __init__(self, api, db, options):
        AReferenceIntegrityCheck.__init__(self, api, db, options, 
                                          collection='favorites', 
                                          refs={
                                              'stamp.stamp_id' : 'stamps', 
                                              'stamp.entity.entity_id' : 'entities', 
                                              'stamp.user.user_id' : 'users', 
                                          })
    
    def _get_docs(self):
        return self.db[self._collection].find({"stamp" : {"$exists" : True}})

class CommentsReferenceIntegrityCheck(AReferenceIntegrityCheck):
    """
        Verifies all external document references in the comments collection.
    """
    
    def __init__(self, api, db, options):
        AReferenceIntegrityCheck.__init__(self, api, db, options, 
                                          collection='comments', 
                                          refs={
                                              'user.user_id' : 'users', 
                                              'stamp_id' : 'stamps', 
                                          })

class EntityDocumentIntegrityCheck(ADocumentIntegrityCheck):
    
    def __init__(self, api, db, options):
        ADocumentIntegrityCheck.__init__(self, api, db, options, 
                                         collection='entities', 
                                         id_field='entity_id', 
                                         schema=Schemas.Entity, 
                                         progress_delta=1)
    
    def _check_schema(self, obj):
        assert obj.title is not None
        assert obj.titlel is not None
        assert obj.subcategory is not None

class PlaceDocumentIntegrityCheck(ADocumentIntegrityCheck):
    
    def __init__(self, api, db, options):
        ADocumentIntegrityCheck.__init__(self, api, db, options, 
                                         collection='places', 
                                         id_field='entity_id', 
                                         schema=Schemas.Entity, 
                                         progress_delta=1)
        
        self._entity_checker = EntityDocumentIntegrityCheck(api, db, options)
    
    def _get_schema(self, doc):
        coords = doc['coordinates']
        
        doc['coordinates'] = {
            'lat' : coords[1], 
            'lng' : coords[0], 
        }
        
        return ADocumentIntegrityCheck._get_schema(self, doc)
    
    def _check_schema(self, obj):
        self._entity_checker._check_schema(obj)
        
        # ensure that we have valid lat / lng for place entity
        assert obj.coordinates.lat is not None
        assert obj.coordinates.lng is not None

class StampDocumentIntegrityCheck(ADocumentIntegrityCheck):
    
    def __init__(self, api, db, options):
        ADocumentIntegrityCheck.__init__(self, api, db, options, 
                                         collection='stamps', 
                                         id_field='stamp_id', 
                                         schema=Schemas.Stamp)

class AccountDocumentIntegrityCheck(ADocumentIntegrityCheck):
    
    def __init__(self, api, db, options):
        ADocumentIntegrityCheck.__init__(self, api, db, options, 
                                         collection='users', 
                                         id_field='user_id', 
                                         schema=Schemas.Account)
    
    def _check_schema(self, obj):
        assert obj.screen_name_lower == obj.screen_name.lower()
        assert obj.name_lower == obj['name'].lower()

class FavoriteDocumentIntegrityCheck(ADocumentIntegrityCheck):
    
    def __init__(self, api, db, options):
        ADocumentIntegrityCheck.__init__(self, api, db, options, 
                                         collection='favorites', 
                                         id_field='favorite_id', 
                                         schema=Schemas.Favorite)

class CommentDocumentIntegrityCheck(ADocumentIntegrityCheck):
    
    def __init__(self, api, db, options):
        ADocumentIntegrityCheck.__init__(self, api, db, options, 
                                         collection='comments', 
                                         id_field='comment_id', 
                                         schema=Schemas.Comment)

class ActivityDocumentIntegrityCheck(ADocumentIntegrityCheck):
    
    def __init__(self, api, db, options):
        ADocumentIntegrityCheck.__init__(self, api, db, options, 
                                         collection='activity', 
                                         id_field='activity_id', 
                                         schema=Schemas.Activity, 
                                         progress_delta=1)

class StampNumIntegrityCheck(AIntegrityCheck):
    """
        Verifies the uniqueness of stamp_num across stamps for a given user.
    """
    
    def __init__(self, api, db, options, **kwargs):
        AIntegrityCheck.__init__(self, api, db, options)
        
        self._sample_kwargs = kwargs
    
    def run(self):
        self._sample(self.db.users.find(), self._check_doc, **self._sample_kwargs)
    
    def _check_doc(self, doc):
        doc_id = str(doc['_id'])
        
        stamps = self.db.stamps.find({"user.user_id" : doc_id}, {"stats.stamp_num" : 1, })
        seen   = {}
        
        for stamp in stamps:
            stamp_num = stamp['stats']['stamp_num']
            stamp_id  = str(stamp['_id'])
            
            if stamp_num in seen:
                self._handle_error("stamps integrity error: duplicate stamp_num %d for user %s (%s); %s" % (
                    stamp_num, doc_id, doc['screen_name'], {
                        'stamp_id0' : seen[stamp_num], 
                        'stamp_id1' : stamp_id, 
                }))
            else:
                seen[stamp_num] = stamp_id

# TODO: replace this hard-coded array with an auto-registered array of 
# AIntegrityCheck subclasses
checks = [
    # index collection integrity checks
    InboxStampsIntegrityCheck, 
    CreditReceivedIntegrityCheck, 
    UserFavEntitiesIntegrityCheck, 
    UserLikesIntegrityCheck, 
    UserStampsIntegrityCheck, 
    StampCommentsIntegrityCheck, 
    
    # stat integrity checks
    NumFriendsIntegrityCheck, 
    NumFollowersIntegrityCheck, 
    NumLikesIntegrityCheck, 
    
    # reference integrity checks
    StampsReferenceIntegrityCheck, 
    FavoritesReferenceIntegrityCheck, 
    FavoritesStampReferenceIntegrityCheck, 
    CommentsReferenceIntegrityCheck, 
    
    # document integrity checks
    EntityDocumentIntegrityCheck, 
    PlaceDocumentIntegrityCheck, 
    StampDocumentIntegrityCheck, 
    AccountDocumentIntegrityCheck, 
    FavoriteDocumentIntegrityCheck, 
    CommentDocumentIntegrityCheck, 
    ActivityDocumentIntegrityCheck, 
    
    # misc
    StampNumIntegrityCheck, 
]

