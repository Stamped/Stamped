#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import logs, re, bson
import pymongo

from logs                       import report
from datetime                   import datetime
from math                       import log10
from utils                      import lazyProperty
from pprint                     import pformat
from errors                     import *

from api_old.Schemas                import *
from db.mongodb.AMongoCollection           import AMongoCollection
from db.mongodb.MongoFollowersCollection   import MongoFollowersCollection
from db.mongodb.MongoFriendsCollection     import MongoFriendsCollection
from api_old.AUserDB                import AUserDB
from libs.Memcache                              import globalMemcache

try:
    from pyes.filters           import *
    from pyes.query             import *
except:
    report()

class MongoUserCollection(AMongoCollection, AUserDB):
    
    def __init__(self):
        AMongoCollection.__init__(self, collection='users', primary_key='user_id', obj=User, overflow=True)
        AUserDB.__init__(self)
        
        self._collection.ensure_index('phone')
        self._collection.ensure_index('linked.twitter.linked_user_id')
        self._collection.ensure_index('linked.facebook.linked_user_id')
        self._collection.ensure_index([('screen_name_lower', pymongo.ASCENDING), ('_id', pymongo.ASCENDING)])
        self._collection.ensure_index([('name_lower', pymongo.ASCENDING), ('_id', pymongo.ASCENDING)])

        self._cache = globalMemcache()

    ### Note that overflow=True
    def _convertFromMongo(self, document):
        if '_id' in document:
            document['user_id'] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
        return User().dataImport(document, overflow=True)

    def _getAllUserIds(self):
        documents = self._collection.find({}, {})
        userIds = []
        for document in documents:
            userIds.append(self._getStringFromObjectId(document['_id']))
        return userIds

    def _getAllScreenNames(self):
        documents = self._collection.find({}, fields=['screen_name_lower'])
        screenNames = []
        for document in documents:
            if 'screen_name_lower' in document:
                screenNames.append(document['screen_name_lower'])
        return screenNames


    def _getCachedUserMini(self, userId):
        key = str("obj::usermini::%s" % userId)
        return self._cache[key]

    def _setCachedUserMini(self, user):
        key = str("obj::usermini::%s" % user.user_id)
        ttl = 60 * 10 # 10 minutes
        try:
            self._cache.set(key, user, time=ttl)
        except Exception as e:
            logs.warning("Unable to set cache for %s: %s" % (user.user_id, e))

    def _delCachedUserMini(self, userId):
        key = str("obj::usermini::%s" % userId)
        try:
            del(self._cache[key])
        except KeyError:
            pass
    
    ### PUBLIC
    
    def getUser(self, userId):
        documentId = self._getObjectIdFromString(userId)
        document   = self._getMongoDocumentFromId(documentId)
        if document is None:
            raise StampedAccountNotFoundError("Unable to find user (%s)" % userId)
        return self._convertFromMongo(document)
    
    def getUserByScreenName(self, screenName):
        screenName = str(screenName).lower()
        document = self._collection.find_one({"screen_name_lower": screenName})
        if document is None:
            raise StampedAccountNotFoundError("Unable to find user (%s)" % screenName)
        return self._convertFromMongo(document)
    
    def checkScreenNameExists(self, screenName):
        try:
            self.getUserByScreenName(screenName)
            return True
        except StampedUnavailableError:
            return False
    
    def lookupUsers(self, userIds=None, screenNames=None, limit=0):
        assert userIds is None or isinstance(userIds, list)
        assert screenNames is None or isinstance(screenNames, list)
        
        queryUserIds = map(self._getObjectIdFromString, userIds) if userIds else []
        queryScreenNames = map(lambda s: str(s).lower(), screenNames) if screenNames else []
        
        user_id_query = {"_id": {"$in": queryUserIds}}
        screen_name_query = {"screen_name_lower": {"$in": queryScreenNames}}
        
        if len(queryUserIds) > 0 and len(queryScreenNames) > 0:
            query = { "$or": [user_id_query, screen_name_query]}
        elif len(queryUserIds) > 0:
            query = user_id_query
        elif len(queryScreenNames) > 0:
            query = screen_name_query
        else:
            return []
        
        results = self._collection.find(query)
        if limit is not None:
            results = results.limit(limit)
        
        return map(self._convertFromMongo, results)
    
    def getUserMinis(self, userIds):
        result = []

        documentIds = []
        for userId in userIds:
            try:
                result.append(self._getCachedUserMini(userId))
            except KeyError:
                documentIds.append(self._getObjectIdFromString(userId))
        documents = self._getMongoDocumentsFromIds(documentIds)

        for document in documents:
            user = self._convertFromMongo(document).minimize()
            self._setCachedUserMini(user)
            result.append(user)

        return result

    @lazyProperty
    def _valid_re(self):
        return re.compile("[^\s\w-]+", re.IGNORECASE)
    
    @lazyProperty
    def followers_collection(self):
        return MongoFollowersCollection()
    
    @lazyProperty
    def friends_collection(self):
        return MongoFriendsCollection()
    
    def searchUsers(self, authUserId, query, limit=0, relationship=None):
        query = query.lower()
        query = self._valid_re.sub('', query)
        
        if len(query) == 0:
            return []
        
        users  = []
        domain = None
        
        if relationship is not None:
            if relationship == 'followers':
                domain = self.followers_collection.getFollowers(authUserId)
            elif relationship == 'following':
                domain = self.friends_collection.getFriends(authUserId)
            else:
                raise StampedInvalidRelationshipError("invalid relationship: %s" % relationship)
            
            domain = set(domain)
        
        try:
            user = self.getUserByScreenName(query)
            if user is not None and (domain is None or user.user_id in domain):
                users.append(user)
        except Exception as e:
            logs.warning("Exact user match not found for '%s': %s" % (query, e))
        
        m = bson.code.Code("""function () {
            var score = 0.0;
            score = (20.0 - this.screen_name.length) / 40.0;
            if (this.stats.num_stamps > 0) {
                score = score + Math.log(this.stats.num_stamps) / 4.0;
            }
            if (this.stats.num_followers > 0) {
                score = score + Math.log(this.stats.num_followers) / 8.0;
            }
            if (this.screen_name_lower == queryString) {
                score = score + 10.0;
            }
            emit('query', {user: this, score:score});
        }""")
        
        r = bson.code.Code("""function(key, values) {
            var out = [];
            var min = 0.0;
            function sortOut(a, b) {
                if (a.score > 0) { scoreA = a.score } else { scoreA = 0 }
                if (b.score > 0) { scoreB = b.score } else { scoreB = 0 }
                return scoreB - scoreA;
            }
            values.forEach(function(v) {
                if (out.length < 20) {
                    out[out.length] = {score:v.score, user:v.user}
                    if (v.score < min) { min = v.score; }
                } else {
                    if (v.score > min) {
                        out[out.length] = {score:v.score, user:v.user}
                        out.sort(sortOut);
                        out.pop()
                    }
                }
            });
            out.sort(sortOut);
            var obj = new Object();
            obj.data = out
            return obj;
        }""")
        
        user_query = {"$or": [{"screen_name_lower": {"$regex": query}}, \
                              {"name_lower": {"$regex": query}}]}
        
        if domain is not None:
            user_query["_id"] = { "$in" : map(bson.objectid.ObjectId, list(domain)) }
        
        result = self._collection.inline_map_reduce(m, r, query=user_query, 
                                                    scope={'queryString':query}, limit=1000)
        
        try:
            # Parse out the data from the result depending on how many results exist
            # If one user found, result is in format:
            #   [{u'_id': u'query', u'value': <user>}]
            # If multiple users found, result is in format:
            #   [{u'_id': u'query', u'value': {u'data': [<user1>, ..., <userN>]}}]
            
            value = result[-1]['value'] 
            if 'data' in value:
                data = value['data']
            else:
                data = [value]
            assert(isinstance(data, list))
        except Exception as e:
            logs.warning("User search mapreduce error for '%s': %s" % (user_query, e))
            return users
        
        for i in data:
            try:
                user = self._convertFromMongo(i['user'])
                if user.screen_name.lower() != query:
                    users.append(user)
            except Exception as e:
                logs.warning("Unable to convert user (%s) from mongo: %s" % (i, e))
                continue
        
        return users[:20]

    
    def flagUser(self, user):
        ### TODO
        raise NotImplementedError
    
    def updateUserStats(self, userIdOrIds, stat, value=None, increment=1):
        if userIdOrIds is None or len(userIdOrIds) == 0:
            raise Exception("Invalid ids")

        # TODO: Note that the following check and conversion is necessary for backward compatability
        if stat == 'num_todos':
            stat = 'num_faves'
            
        key = 'stats.%s' % stat
        
        if isinstance(userIdOrIds, (list, tuple, set)):
            # updating statistic for multiple users at once
            query = {'_id': { "$in" : map(self._getObjectIdFromString, userIdOrIds) } }
        else:
            # updating statistic for a single user
            query = {'_id': self._getObjectIdFromString(userIdOrIds) }
        
        if value is not None:
            self._collection.update(query, {'$set': {key: value}}, upsert=True)
        else:
            self._collection.update(query, {'$inc': {key: increment}}, upsert=True)

    def updateDistribution(self, userId, distribution):
        r = []
        for i in distribution:
            r.append(i.dataExport())
        query = {'_id': self._getObjectIdFromString(userId)}
        self._collection.update(query, {'$set': {'stats.distribution': r}}, upsert=True)
    
    def findUsersByEmail(self, emails, limit=0):
        queryEmails = []
        for email in emails:
            queryEmails.append(str(email).lower())

        ### TODO: Add Index
        data = self._collection.find({"email": {"$in": queryEmails}}).limit(limit)
            
        result = []
        for item in data:
            user = SuggestedUser().importUser(self._convertFromMongo(item))
            user.search_identifier = item['email']
            result.append(user)
        return result

    def findUsersByPhone(self, phone, limit=0):
        queryPhone = [int(num) for num in phone if len(str(num)) >= 10]
        queryPhone.extend( [str(num) for num in phone if len(str(num)) >= 10] )
        
        ### TODO: Add Index
        data = self._collection.find( {"phone": {"$in": queryPhone}} ).limit(limit)
        
        result = []
        for item in data:
            user = SuggestedUser().importUser(self._convertFromMongo(item))
            user.search_identifier = item['phone']
            result.append(user)
        return result

    def findUsersByTwitter(self, twitterIds, limit=0):
        twitterIds = map(str, twitterIds)

        result = []

        # Loop in chunks
        CHUNK_SIZE = 10000

        for i in range(int(len(twitterIds) / CHUNK_SIZE) + 1):
            chunk = twitterIds[CHUNK_SIZE*i:CHUNK_SIZE*(i+1)]

            data = self._collection.find({"linked.twitter.linked_user_id": {"$in": chunk}}).limit(limit)

            for item in data:
                user = SuggestedUser().importUser(self._convertFromMongo(item))
                user.search_identifier = item['linked']['twitter']['linked_user_id']
                result.append(user)

        return result

    def findUsersByFacebook(self, facebookIds, limit=0):
        facebookIds = map(str, facebookIds)
        
        result = []

        # Loop in chunks
        CHUNK_SIZE = 10000
        
        for i in range(int(len(facebookIds) / CHUNK_SIZE) + 1):
            chunk = facebookIds[CHUNK_SIZE*i:CHUNK_SIZE*(i+1)]

            data = self._collection.find({"linked.facebook.linked_user_id": {"$in": chunk}}).limit(limit)

            for item in data:
                user = SuggestedUser().importUser(self._convertFromMongo(item))
                user.search_identifier = item['linked']['facebook']['linked_user_id']
                result.append(user)
        
        return result

