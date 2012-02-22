#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import bson, logs, pprint, pymongo, re

from datetime                       import datetime
from utils                          import lazyProperty
from Schemas                        import *

from api.AStampDB                   import AStampDB
from AMongoCollection               import AMongoCollection
from MongoUserLikesCollection       import MongoUserLikesCollection
from MongoStampLikesCollection      import MongoStampLikesCollection
from MongoStampViewsCollection      import MongoStampViewsCollection
from MongoUserStampsCollection      import MongoUserStampsCollection
from MongoInboxStampsCollection     import MongoInboxStampsCollection
from MongoDeletedStampCollection    import MongoDeletedStampCollection
from MongoCreditGiversCollection    import MongoCreditGiversCollection
from MongoCreditReceivedCollection  import MongoCreditReceivedCollection

class MongoStampCollection(AMongoCollection, AStampDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='stamps', primary_key='stamp_id', obj=Stamp)
        AStampDB.__init__(self)
        
        self._collection.ensure_index([('timestamp.modified', pymongo.ASCENDING)])
        self._collection.ensure_index([('user.user_id', pymongo.ASCENDING), \
                                        ('entity.entity_id', pymongo.ASCENDING)])
        self._collection.ensure_index([('user.user_id', pymongo.ASCENDING), \
                                        ('stats.stamp_num', pymongo.ASCENDING)])
    
    ### PUBLIC
    
    @lazyProperty
    def user_stamps_collection(self):
        return MongoUserStampsCollection()
    
    @lazyProperty
    def inbox_stamps_collection(self):
        return MongoInboxStampsCollection()
    
    @lazyProperty
    def credit_givers_collection(self):
        return MongoCreditGiversCollection()
    
    @lazyProperty
    def credit_received_collection(self):
        return MongoCreditReceivedCollection()
    
    @lazyProperty
    def stamp_likes_collection(self):
        return MongoStampLikesCollection()
    
    @lazyProperty
    def stamp_views_collection(self):
        return MongoStampViewsCollection()
    
    @lazyProperty
    def user_likes_collection(self):
        return MongoUserLikesCollection()
    
    @lazyProperty
    def deleted_stamp_collection(self):
        return MongoDeletedStampCollection()
    
    def addStamp(self, stamp):
        return self._addObject(stamp)
    
    def getStamp(self, stampId):
        documentId = self._getObjectIdFromString(stampId)
        document = self._getMongoDocumentFromId(documentId)
        return self._convertFromMongo(document)
    
    def updateStamp(self, stamp):
        return self.update(stamp)
    
    def removeStamp(self, stampId):
        documentId = self._getObjectIdFromString(stampId)
        result = self._removeMongoDocument(documentId)

        self.deleted_stamp_collection.addStamp(stampId)

        return result
    
    def addUserStampReference(self, userId, stampId):
        # Add a reference to the stamp in the user's collection
        self.user_stamps_collection.addUserStamp(userId, stampId)
    
    def removeUserStampReference(self, userId, stampId):
        # Remove a reference to the stamp in the user's collection
        self.user_stamps_collection.removeUserStamp(userId, stampId)
    
    def removeAllUserStampReferences(self, userId):
        self.user_stamps_collection.removeAllUserStamps(userId)
    
    def addInboxStampReference(self, userIds, stampId):
        # Add a reference to the stamp in followers' inbox
        self.inbox_stamps_collection.addInboxStamps(userIds, stampId)
    
    def removeInboxStampReference(self, userIds, stampId):
        # Remove a reference to the stamp in followers' inbox
        self.inbox_stamps_collection.removeInboxStamps(userIds, stampId)
    
    def addInboxStampReferencesForUser(self, userId, stampIds):
        self.inbox_stamps_collection.addInboxStampsForUser(userId, stampIds)
    
    def removeInboxStampReferencesForUser(self, userId, stampIds):
        self.inbox_stamps_collection.removeInboxStampsForUser(userId, stampIds)
    
    def removeAllInboxStampReferences(self, userId):
        self.inbox_stamps_collection.removeAllInboxStamps(userId)
    
    def getStamps(self, stampIds, **kwargs):
        sort = kwargs.pop('sort', None)
        if sort in ['modified', 'created']:
            sort = 'timestamp.%s' % sort
        else:
            sort = 'timestamp.created'
        
        params = {
            'since':    kwargs.pop('since', None),
            'before':   kwargs.pop('before', None), 
            'limit':    kwargs.pop('limit', 20),
            'sort':     sort,
            'sortOrder': pymongo.DESCENDING, 
        }
        
        ids = map(self._getObjectIdFromString, stampIds)
        
        # Get stamps
        documents = self._getMongoDocumentsFromIds(ids, **params)
        
        return map(self._convertFromMongo, documents)
    
    def getStampsSlice(self, stampIds, genericCollectionSlice):
        if stampIds is not None:
            if len(stampIds) == 0:
                return []
            
            ids     = map(self._getObjectIdFromString, stampIds)
            
            if len(ids) == 1:
                query   = { '_id' : ids[0] }
            else:
                query   = { '_id' : { '$in' : ids } }
        else:
            query   = { }
        
        time_filter = 'timestamp.created'
        sort        = None
        reverse     = genericCollectionSlice.reverse
        viewport    = (genericCollectionSlice.viewport.lowerRight.lat is not None)
        relaxed     = (viewport and genericCollectionSlice.query is not None and genericCollectionSlice.sort == 'relevance')
        
        # handle setup for sorting
        # ------------------------
        if genericCollectionSlice.sort == 'modified' or genericCollectionSlice.sort == 'created':
            sort = 'timestamp.%s' % genericCollectionSlice.sort
            time_filter = sort
        elif genericCollectionSlice.sort == 'alphabetical':
            sort = 'entity.title'
            
            reverse = not reverse
        elif genericCollectionSlice.sort == 'proximity':
            if genericCollectionSlice.coordinates.lat is None or genericCollectionSlice.coordinates.lng is None:
                raise StampedInputError("proximity sort requires a valid center parameter")
            
            query["entity.coordinates.lat"] = { "$exists" : True}
            query["entity.coordinates.lng"] = { "$exists" : True}
            
            reverse = not reverse
        
        if genericCollectionSlice.sort != 'relevance' and genericCollectionSlice.query is not None:
            raise StampedInputError("non-empty search query is only compatible with sort set to \"relevance\"")
        
        # handle before / since filters
        # -----------------------------
        since  = genericCollectionSlice.since
        before = genericCollectionSlice.before
        
        if since is not None and before is not None:
            query[time_filter] = { '$gte': since, '$lte': before }
        elif since is not None:
            query[time_filter] = { '$gte': since }
        elif before is not None:
            query[time_filter] = { '$lte': before }
        
        # handle category / subcategory filters
        # -------------------------------------
        if genericCollectionSlice.category is not None:
            query['category']    = str(genericCollectionSlice.category).lower()
        
        if genericCollectionSlice.subcategory is not None:
            query['subcategory'] = str(genericCollectionSlice.subcategory).lower()
        
        def add_or_query(args):
            if "$or" not in query:
                query["$or"] = args
            else:
                if "$and" not in query:
                    query["$and"] = []
                
                query["$and"].append([ { "$or" : query["$or"] }, { "$or" : args } ])
        
        # handle viewport filter
        # ----------------------
        if viewport:
            if relaxed:
                query["entity.coordinates.lat"] = { "$exists" : True}
                query["entity.coordinates.lng"] = { "$exists" : True}
            else:
                query["entity.coordinates.lat"] = { 
                    "$gte" : genericCollectionSlice.viewport.lowerRight.lat, 
                    "$lte" : genericCollectionSlice.viewport.upperLeft.lat, 
                }
                
                if genericCollectionSlice.viewport.upperLeft.lng <= genericCollectionSlice.viewport.lowerRight.lng:
                    query["entity.coordinates.lng"] = { 
                        "$gte" : genericCollectionSlice.viewport.upperLeft.lng, 
                        "$lte" : genericCollectionSlice.viewport.lowerRight.lng, 
                    }
                else:
                    # handle special case where the viewport crosses the +180 / -180 mark
                    add_or_query([  {
                            "entity.coordinates.lng" : {
                                "$gte" : genericCollectionSlice.viewport.upperLeft.lng, 
                            }, 
                        }, 
                        {
                            "entity.coordinates.lng" : {
                                "$lte" : genericCollectionSlice.viewport.lowerRight.lng, 
                            }, 
                        }, 
                    ])
        
        # handle search query filter
        # --------------------------
        if genericCollectionSlice.query is not None:
            # TODO: make query regex better / safeguarded
            user_query = genericCollectionSlice.query.lower().strip()
            
            add_or_query([ { "blurb"        : { "$regex" : user_query, "$options" : 'i', } }, 
                           { "entity.title" : { "$regex" : user_query, "$options" : 'i', } } ])
        
        #import pprint
        #utils.log(pprint.pformat(query))
        #utils.log(pprint.pformat(genericCollectionSlice.value))
        
        # find, sort, and truncate results
        # --------------------------------
        if sort is not None:
            # fast-path which uses built-in sorting
            # -------------------------------------
            
            # order in which to return sorted results
            order   = pymongo.ASCENDING if reverse else pymongo.DESCENDING
            
            results = self._collection.find(query) \
                      .sort(sort, order) \
                      .skip(genericCollectionSlice.offset) \
                      .limit(genericCollectionSlice.limit)
        else:
            # slow-path which uses custom map-reduce for sorting
            # --------------------------------------------------
            scope = {
                'query'    : genericCollectionSlice.query, 
                'limit'    : genericCollectionSlice.limit, 
                'offset'   : genericCollectionSlice.offset, 
                'viewport' : genericCollectionSlice.viewport.value, 
            }
            
            if genericCollectionSlice.sort == 'proximity':
                # handle proximity-based sort
                # ---------------------------
                scope['center'] = genericCollectionSlice.coordinates.exportSparse()
                
                # TODO: handle +180 / -180 meridian special case 
                _map = bson.code.Code("""function ()
                {
                    var diff0 = (this.entity.coordinates.lat - center.lat);
                    var diff1 = (this.entity.coordinates.lng - center.lng);
                    var score = Math.sqrt(diff0 * diff0 + diff1 * diff1);
                    
                    emit('query', { obj : this, score : score });
                }""")
            elif genericCollectionSlice.sort == 'popularity' or \
                (genericCollectionSlice.sort == 'relevance' and genericCollectionSlice.query is None):
                # handle popularity-based sort
                # ----------------------------
                _map = bson.code.Code("""function () {
                    var score = 0.0;
                    
                    try {
                        if (this.stats.num_credit > 0)
                            score += 10 * this.stats.num_credit;
                    } catch(err) {}
                    
                    try {
                        if (this.stats.num_likes > 0)
                            score += 3 * this.stats.num_likes;
                    } catch(err) {}
                    
                    try {
                        if (this.stats.num_comments > 0)
                            score += this.stats.num_comments;
                    } catch(err) {}
                    
                    emit('query', { obj : this, score : score });
                }""")
            elif genericCollectionSlice.sort == 'relevance':
                # handle relevancy-based sort
                # ---------------------------
                
                if relaxed:
                    scope['center'] = {
                        'lat' : (genericCollectionSlice.upperLeft.lat + genericCollectionSlice.lowerRight.lat) / 2.0, 
                        'lng' : (genericCollectionSlice.upperLeft.lng + genericCollectionSlice.lowerRight.lng) / 2.0, 
                    }
                
                # TODO: incorporate more complicated relevancy metrics into this 
                # weighting function, including possibly:
                #     * recency
                #     * popularity
                #     * other metadata sources (e.g., tags, menu, etc.)
                # NOTE: blurb & entity title matching already occurs at regex query level!
                # these scores are then completely redundant since levenshtein will never 
                # be taken into account.
                _map = bson.code.Code("""function () {
                    var title_value = 0.0, dist_value = 0.0;
                    var blurb, title;
                    
                    try {
                        title = this.entity.title.toLowerCase();
                    } catch(e) {
                        title = "";
                    }
                    
                    try {
                        blurb = this.blurb.toLowerCase();
                    } catch(e) {
                        blurb = "";
                    }
                    
                    if (title.length > 0 && title.match(query)) {
                        title_value = 1.0;
                    } else if (blurb.length > 0 && blurb.match(query)) {
                        title_value = 0.5;
                    } else {
                        title_value = 0.1;
                    }
                    
                    try {
                        var inside = false;
                        
                        if (this.entity.coordinates.lat >= viewport.lowerRight.lat && this.entity.coordinates.lat <= viewport.upperLeft.lat) {
                            if (viewport.upperLeft.lng <= viewport.lowerRight.lng) {
                                if (this.entity.coordinates.lng >= viewport.upperLeft.lng && this.entity.coordinates.lng <= viewport.lowerRight.lng) {
                                    inside = true;
                                }
                            } else {
                                if (this.entity.coordinates.lng >= viewport.upperLeft.lng || this.entity.coordinates.lng <= viewport.lowerRight.lng) {
                                    inside = true;
                                }
                            }
                        }
                        
                        if (inside) {
                            dist_value = 10000.0;
                        } else {
                            var diff0 = (this.entity.coordinates.lat - center.lat);
                            var diff1 = (this.entity.coordinates.lng - center.lng);
                            var dist  = Math.sqrt(diff0 * diff0 + diff1 * diff1);
                            
                            if (dist < 0) {
                                dist_value = 0;
                            }
                            else {
                                var x = (dist - 50);
                                var a = -0.4;
                                var b = 2.8;
                                var c = -6.3;
                                var d = 4.0;
                                
                                var x2 = x * x;
                                var x3 = x2 * x;
                                
                                var value = a * x3 + b * x2 + c * x + d;
                                
                                if (value > 0) {
                                    value = Math.log(1 + value);
                                } else {
                                    value = -Math.log(1 - value);
                                }
                                
                                dist_value = value;
                            }
                        }
                    }
                    catch (e) {
                        dist_value = 0;
                    }
                    
                    var title_weight = 1.0;
                    var dist_weight  = 1.0;
                    
                    var score = title_value * title_weight + \
                                dist_value  * dist_weight;
                    
                    emit('query', { obj : this, score : score });
                }""")
            
            # TODO: optimize reduce for offset / limit
            _reduce = bson.code.Code("""function(key, values) {
                var min = 0.0;
                var out = [];
                
                function sortOut(a, b) {
                    if (a.score > 0) { scoreA = a.score } else { scoreA = 0 }
                    if (b.score > 0) { scoreB = b.score } else { scoreB = 0 }
                    return scoreB - scoreA;
                }
                values.forEach(function(v) {
                    if (out.length < offset + limit) {
                        out[out.length] = { score : v.score, obj : v.obj }
                        if (v.score < min) { min = v.score; }
                    } else {
                        if (v.score > min) {
                            out[out.length] = { score : v.score, obj : v.obj }
                            out.sort(sortOut);
                            out.pop();
                        }
                    }
                });
                
                out.sort(sortOut);
                var obj = new Object();
                obj.data = out;
                
                return obj;
            }""")
            
            result = self._collection.inline_map_reduce(_map, _reduce, query=query, scope=scope, limit=1000)
            
            try:
                value = result[-1]['value'] 
                if 'data' in value:
                    data = value['data']
                else:
                    data = [value]
                
                assert(isinstance(data, list))
            except:
                logs.debug(utils.getFormattedException())
                return []
            
            results = map(lambda d: d['obj'], data)
            if reverse:
                results = list(reversed(results))
            
            results = results[genericCollectionSlice.offset : genericCollectionSlice.offset + genericCollectionSlice.limit]
        
        results = map(self._convertFromMongo, results)
        
        # condense results to remove duplicate entities across stamps
        if genericCollectionSlice.unique:
            seen = set()
            ret  = []
            
            for result in results:
                entity_id = result.entity_id
                
                if entity_id not in seen:
                    seen.add(entity_id)
                    ret.append(result)
            
            results = ret
        
        return results
    
    def countStamps(self, userId):
        return len(self.user_stamps_collection.getUserStampIds(userId))
    
    def getDeletedStamps(self, stampIds, genericCollectionSlice):
        return self.deleted_stamp_collection.getStamps(stampIds, genericCollectionSlice)
    
    def checkStamp(self, userId, entityId):
        try:
            document = self._collection.find_one({
                'user.user_id': userId, 
                'entity.entity_id': entityId,
            })
            if document['_id'] != None:
                return True
            raise
        except:
            return False
    
    def updateStampStats(self, stampId, stat, value=None, increment=1):
        key = 'stats.%s' % (stat)
        if value != None:
            self._collection.update(
                {'_id': self._getObjectIdFromString(stampId)}, 
                {'$set': {key: value, 'timestamp.modified': datetime.utcnow()}},
                upsert=True)
        else:
            self._collection.update(
                {'_id': self._getObjectIdFromString(stampId)}, 
                {'$inc': {key: increment}, 
                 '$set': {'timestamp.modified': datetime.utcnow()}},
                upsert=True)
    
    def getStampFromUserEntity(self, userId, entityId):
        try:
            ### TODO: Index
            document = self._collection.find_one({
                'user.user_id': userId, 
                'entity.entity_id': entityId,
            })
            return self._convertFromMongo(document)
        except:
            return None
    
    def getStampsFromEntity(self, entityId, limit=None):
        try:
            ### TODO: Index
            docs = self._collection.find({
                'entity.entity_id': entityId,
            })
            if limit is not None:
                docs = docs.limit(limit)
            
            return (self._convertFromMongo(doc) for doc in docs)
        except:
            return []
    
    def getStampFromUserStampNum(self, userId, stampNum):
        try:
            ### TODO: Index
            stampNum = int(stampNum)
            document = self._collection.find_one({
                'user.user_id': userId, 
                'stats.stamp_num': stampNum,
            })
            return self._convertFromMongo(document)
        except:
            return None
    
    def giveCredit(self, creditedUserId, stamp):
        # Add to 'credit received'
        ### TODO: Does this belong here?
        self.credit_received_collection.addCredit(creditedUserId, \
                                                    stamp.stamp_id)
        
        # Add to 'credit givers'
        ### TODO: Does this belong here?
        self.credit_givers_collection.addGiver(creditedUserId, \
                                                    stamp.user.user_id)
    
    def removeCredit(self, creditedUserId, stamp):
        # Add to 'credit received'
        ### TODO: Does this belong here?
        self.credit_received_collection.removeCredit(creditedUserId, \
                                                    stamp.stamp_id)
        
        # Add to 'credit givers'
        ### TODO: Does this belong here?
        self.credit_givers_collection.removeGiver(creditedUserId, \
                                                    stamp.user.user_id)
    
    def countCredits(self, userId):
        return self.credit_received_collection.numCredit(userId)   
    
    def giveLikeCredit(self, stampId):
        self._collection.update(
            {'_id': self._getObjectIdFromString(stampId)}, 
            {'$set': {'stats.like_threshold_hit': True}}
        )
        
    def addLike(self, userId, stampId):
        # Add a reference to the user in the stamp's 'like' collection
        self.stamp_likes_collection.addStampLike(stampId, userId) 
        # Add a reference to the stamp in the user's 'like' collection
        self.user_likes_collection.addUserLike(userId, stampId) 
        # Update the modified timestamp
        self._collection.update({'_id': self._getObjectIdFromString(stampId)}, 
            {'$set': {'timestamp.modified': datetime.utcnow()}})
    
    def removeLike(self, userId, stampId):
        # Remove a reference to the user in the stamp's 'like' collection
        stampLike = self.stamp_likes_collection.removeStampLike(stampId, userId)
        # Remove a reference to the stamp in the user's 'like' collection
        userLike = self.user_likes_collection.removeUserLike(userId, stampId) 
        
        if stampLike == True and userLike == True:
            return True
        return False
        
    def getStampLikes(self, stampId):
        # Returns user ids that have "liked" the stamp
        return self.stamp_likes_collection.getStampLikes(stampId) 
        
    def getUserLikes(self, userId):
        # Return stamp ids that a user has "liked"
        return self.user_likes_collection.getUserLikes(userId) 
    
    def countStampLikes(self, stampId):
        return len(self.getStampLikes(stampId))
    
    def countUserLikes(self, userId):
        return len(self.getUserLikes(userId))
    
    def checkLike(self, userId, stampId):
        try:
            likes = self.stamp_likes_collection.getStampLikes(stampId) 
            if userId in likes:
                return True
            raise
        except:
            return False
    
    def addView(self, userId, stampId):
        self.stamp_views_collection.addStampView(stampId, userId)
    
    def getStampViews(self, stampId):
        # Returns user ids that have viewed the stamp
        return self.stamp_views_collection.getStampViews(stampId) 
    
    def removeStamps(self, stampIds):
        documentIds = []
        for stampId in stampIds:
            documentIds.append(self._getObjectIdFromString(stampId))
        result = self._removeMongoDocuments(documentIds)
        
        return result     

