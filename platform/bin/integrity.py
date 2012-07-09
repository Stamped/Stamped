#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import bson, logs, utils, random
import api.Schemas as Schemas

from utils      import abstract
# from bin.checkdb    import *

"""
Index collections
Object stats
Object references
Object validation
Data enrichment

"""

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

class ADocumentIntegrityCheck(AIntegrityCheck):
    """
        Abstract superclass for verifying the existence and correctness of 
        key fields in all documents across a collection.
    """
    
    def __init__(self, api, db, options, collection, id_field=None, schema=None, **kwargs):
        AIntegrityCheck.__init__(self, api, db, options)
        
        self._sample_kwargs     = kwargs
        self._collection        = collection
        self._collection_name   = collection._collection_name
        self._id_field          = id_field
        self._schema            = schema
    
    def run(self):
        self._sample(self._get_docs(), self._check_doc, **self._sample_kwargs)
    
    def _get_docs(self):
        return self.db[self._collection_name].find()
    
    def _check_schema(self, obj):
        pass
    
    def _get_schema(self, doc):
        print self.__dict__
        return self._collection._convertFromMongo(doc)
    
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
                    self._collection_name, self._schema.__name__, str(e), {
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
        self._sample(self._get_docs(), self._check_doc, **self._sample_kwargs)
    
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
        self._sample(self.db[self._stat_collection].find(), self._check_doc, **self._sample_kwargs)
    
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
                self.db[self._stat_collection].update({'_id': doc['_id']}, {'$set': {self._stat: value}})

class AIndexCollectionIntegrityCheck(AStatIntegrityCheck):
    """
        Abstract superclass for all index collection integrity checks. An index
        collection is a collection that stores references from one id (e.g. a user)
        to a set of ids (e.g. stamps). It is a convenience collection used to 
        make querying faster, and can be regenerated entirely from underlying data.
    """
    
    def __init__(self, api, db, options, collection, stat_collection=None, stat=None, **kwargs):
        AStatIntegrityCheck.__init__(self, api, db, options, stat_collection, stat, **kwargs)
        self._collection = collection
    
    def run(self):
        self._sample(self.db[self._collection].find(), self._check_doc, **self._sample_kwargs)
    
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
        
        # optionally update the document with valid reference ids
        if not self.options.noop:

            if len(invalid_ids) > 0:
                query = {'$pullAll': {'ref_ids': invalid_ids}}
                self.db[self._collection].update({'_id': doc['_id']}, query)
            
            if len(missing_ids) > 0:
                query = {'$addToSet': {'ref_ids': {'$each': missing_ids}}}
                self.db[self._collection].update({'_id': doc['_id']}, query)
        
        # if there is a corresponding stat storing the count of ref_ids, ensure 
        # that it is also in sync with the underlying list of references.
        AStatIntegrityCheck.check_doc_id(self, doc_id, value=len(cmp_ids))
'''
class InboxStampsIndexIntegrityCheck(AIndexCollectionIntegrityCheck):
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

class CreditReceivedIndexIntegrityCheck(AIndexCollectionIntegrityCheck):
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

class UserFavEntitiesIndexIntegrityCheck(AIndexCollectionIntegrityCheck):
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

class UserLikesIndexIntegrityCheck(AIndexCollectionIntegrityCheck):
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

class UserStampsIndexIntegrityCheck(AIndexCollectionIntegrityCheck):
    """
        Ensures the integrity of the userstamps collection, which maps 
        user_ids to stamp_ids created by the user.
    """
    
    def __init__(self, api, db, options):
        AIndexCollectionIntegrityCheck.__init__(self, api, db, options, 
                                                collection='userstamps', 
                                                stat_collection='users', 
                                                stat='stats.num_stamps')
    
    """
    NOTE: we do *not* want to retain deleted stamps in userstamps
    def _is_invalid_id(self, doc_id):
        ret = self.db['deletedstamps'].find_one({"_id" : bson.objectid.ObjectId(doc_id)})
        return ret is None
    """
    
    def _get_cmp(self, doc_id):
        return self._strip_ids(self.db['stamps'].find({'user.user_id' : doc_id}, {'_id' : 1}))

class StampCommentsIndexIntegrityCheck(AIndexCollectionIntegrityCheck):
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

class NumFriendsStatIntegrityCheck(AStatIntegrityCheck):
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

class NumFollowersStatIntegrityCheck(AStatIntegrityCheck):
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

class NumLikesStatIntegrityCheck(AStatIntegrityCheck):
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
'''
class EntityDocumentIntegrityCheck(ADocumentIntegrityCheck):
    
    def __init__(self, api, db, options):
        ADocumentIntegrityCheck.__init__(self, api, db, options, 
                                         collection=api._entityDB, 
                                         id_field='entity_id', 
                                         schema=Schemas.BasicEntity, 
                                         progress_delta=1)
    
    def _check_schema(self, obj):
        assert obj.title is not None
        assert obj.titlel is not None
        assert obj.subcategory is not None
'''
class PlaceDocumentIntegrityCheck(ADocumentIntegrityCheck):
    
    def __init__(self, api, db, options):
        ADocumentIntegrityCheck.__init__(self, api, db, options, 
                                         collection='places', 
                                         id_field='entity_id', 
                                         schema=Schemas.BasicEntity, 
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
                                         id_field='todo_id', 
                                         schema=Schemas.Todo)

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
    InboxStampsIndexIntegrityCheck, 
    CreditReceivedIndexIntegrityCheck, 
    UserFavEntitiesIndexIntegrityCheck, 
    UserLikesIndexIntegrityCheck, 
    UserStampsIndexIntegrityCheck, 
    StampCommentsIndexIntegrityCheck, 
    
    # stat integrity checks
    NumFriendsStatIntegrityCheck, 
    NumFollowersStatIntegrityCheck, 
    NumLikesStatIntegrityCheck, 
    
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
'''
checks = [ EntityDocumentIntegrityCheck ]

