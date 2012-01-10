#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

import Globals, re, bson

from datetime           import datetime
from math               import log10
from utils              import lazyProperty

from Schemas            import *
from AMongoCollection   import AMongoCollection
from api.AUserDB        import AUserDB

class MongoUserCollection(AMongoCollection, AUserDB):
    
    def __init__(self, setup=False):
        AMongoCollection.__init__(self, collection='users', primary_key='user_id', obj=User, overflow=True)
        AUserDB.__init__(self)
        
        self._collection.ensure_index('phone')
        self._collection.ensure_index('linked_accounts.twitter.twitter_id')
        self._collection.ensure_index('linked_accounts.facebook.facebook_id')

    ### Note that overflow=True
    def _convertFromMongo(self, document):
        if '_id' in document:
            document['user_id'] = self._getStringFromObjectId(document['_id'])
            del(document['_id'])
        return User(document, overflow=True)

    def _getAllUserIds(self):
        documents = self._collection.find({}, {})
        userIds = []
        for document in documents:
            userIds.append(self._getStringFromObjectId(document['_id']))
        return userIds
    
    ### PUBLIC
    
    def getUser(self, userId):
        documentId = self._getObjectIdFromString(userId)
        document   = self._getMongoDocumentFromId(documentId)
        
        return self._convertFromMongo(document)
    
    def getUserByScreenName(self, screenName):
        screenName = str(screenName).lower()
        document = self._collection.find_one({"screen_name_lower": screenName})
        return self._convertFromMongo(document)

    
    def checkScreenNameExists(self, screenName):
        try:
            self.getUserByScreenName(screenName)
            return True
        except:
            return False
    
    def lookupUsers(self, userIds, screenNames, limit=0):
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
        
        data = self._collection.find(query).limit(limit)
        return map(self._convertFromMongo, data)
    
    @lazyProperty
    def _valid_re(self):
        return re.compile("[^\s\w-]+", re.IGNORECASE)

    def searchUsers(self, query, limit=0):
        query = query.lower()
        query = self._valid_re.sub('', query)
        
        if len(query) == 0:
            return []

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
                return b.score - a.score;
            }
            values.forEach(function(v) {
                if (out.length < 10) {
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
            var obj = new Object();
            obj.data = out
            return obj;
        }""")

        user_query = {"$or": [{"screen_name_lower": {"$regex": query}}, \
                              {"name_lower": {"$regex": query}}]}

        result = self._collection.inline_map_reduce(m, r, query=user_query, scope={'queryString':query})

        try:
            data = result[-1]['value']['data']
        except:
            return []

        users = []
        for i in data:
            users.append(self._convertFromMongo(i['user']))

        return users
    
    def searchUsersOld(self, query, limit=0):
        query = query.lower()
        query = self._valid_re.sub('', query)
        
        if len(query) == 0:
            return []

        ### TODO: Do sorting on Mongo as a custom sort function?
        user_query = {"$or": [{"screen_name_lower": {"$regex": query}}, \
                              {"name_lower": {"$regex": query}}]}
        data = self._collection.find(user_query).limit(min(50, limit*4))

        prefix_re = re.compile(r"^%s" % query, re.IGNORECASE)

        results = []
        for item in data:
            user = self._convertFromMongo(item)
            
            # length of screen name (shorter = better)
            score = (20.0 - len(user.screen_name)) / 20.0 / 2.0

            # number of stamps
            if user.num_stamps > 0:
                score += (log10(user.num_stamps) / 4.0)

            # number of followers
            if user.num_followers > 0:
                score += (log10(user.num_followers) / 8.0)
            
            # boost 'em if it's a prefix match
            if prefix_re.match(user.screen_name):
                score += 10.0

            results.append((score, user))

        results = sorted(results, key=lambda k: -k[0])
        users = []
        for i in xrange(min(limit, len(results))):
            users.append(results[i][1])

        return users
    
    def flagUser(self, user):
        ### TODO
        raise NotImplementedError
    
    def updateUserStats(self, userIdOrIds, stat, value=None, increment=1):
        key = 'stats.%s' % stat
        
        if isinstance(userIdOrIds, (list, tuple)):
            # updating statistic for multiple users at once
            query = {'_id': { "$in" : map(self._getObjectIdFromString, userIdOrIds) } }
        else:
            # updating statistic for a single user
            query = {'_id': self._getObjectIdFromString(userIdOrIds) }
        
        if value is not None:
            self._collection.update(query, {'$set': {key: value}}, upsert=True)
        else:
            self._collection.update(query, {'$inc': {key: increment}}, upsert=True)
        
        #return self._collection.find_one({'_id': self._getObjectIdFromString(userId)})['stats'][stat]
    
    def findUsersByEmail(self, emails, limit=0):
        queryEmails = []
        for email in emails:
            queryEmails.append(str(email).lower())

        ### TODO: Add Index
        data = self._collection.find({"email": {"$in": queryEmails}}).limit(limit)
            
        result = []
        for item in data:
            user = self._convertFromMongo(item)
            user.identifier = item['email']
            result.append(user)
        return result

    def findUsersByPhone(self, phone, limit=0):
        queryPhone = []
        for number in phone:
            queryPhone.append(int(number))

        ### TODO: Add Index
        data = self._collection.find({"phone": {"$in": queryPhone}}).limit(limit)
        
        result = []
        for item in data:
            user = self._convertFromMongo(item)
            user.identifier = item['phone']
            result.append(user)
        return result

    def findUsersByTwitter(self, twitterIds, limit=0):
        twitterIds = map(str, twitterIds)

        data = self._collection.find(
            {"linked_accounts.twitter.twitter_id": {"$in": twitterIds}}
        ).limit(limit)
        
        result = []
        for item in data:
            user = self._convertFromMongo(item)
            user.identifier = item['linked_accounts']['twitter']['twitter_id']
            result.append(user)
        return result

    def findUsersByFacebook(self, facebookIds, limit=0):
        facebookIds = map(str, facebookIds)

        data = self._collection.find(
            {"linked_accounts.facebook.facebook_id": {"$in": facebookIds}}
        ).limit(limit)
            
        result = []
        for item in data:
            user = self._convertFromMongo(item)
            user.identifier = item['linked_accounts']['facebook']['facebook_id']
            result.append(user)
        return result

