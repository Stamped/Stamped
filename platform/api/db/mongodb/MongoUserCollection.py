#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import logs, re, bson

from logs                       import report
from datetime                   import datetime
from math                       import log10
from utils                      import lazyProperty
from pprint                     import pformat
from errors                     import *

from Schemas                    import *
from AMongoCollection           import AMongoCollection
from MongoFollowersCollection   import MongoFollowersCollection
from MongoFriendsCollection     import MongoFriendsCollection
from api.AUserDB                import AUserDB

try:
    from pyes.filters           import *
    from pyes.query             import *
except:
    report()

class MongoUserCollection(AMongoCollection, AUserDB):
    
    def __init__(self, api):
        AMongoCollection.__init__(self, collection='users', primary_key='user_id', obj=User, overflow=True)
        AUserDB.__init__(self)
        
        self.api = api
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
        if document is None:
            raise StampedUnavailableError("Unable to find user (%s)" % userId)
        return self._convertFromMongo(document)
    
    def getUserByScreenName(self, screenName):
        screenName = str(screenName).lower()
        document = self._collection.find_one({"screen_name_lower": screenName})
        if document is None:
            raise StampedUnavailableError("Unable to find user (%s)" % screenName)
        return self._convertFromMongo(document)
    
    def checkScreenNameExists(self, screenName):
        try:
            self.getUserByScreenName(screenName)
            return True
        except:
            return False
    
    def lookupUsers(self, userIds, screenNames=None, limit=0):
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
        
        results = self._collection.find(query).limit(limit)
        return map(self._convertFromMongo, results)
    
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
        seen   = set()
        domain = None
        
        if relationship is not None:
            if relationship == 'followers':
                domain = self.followers_collection.getFollowers(authUserId)
            elif relationship == 'following':
                domain = self.friends_collection.getFriends(authUserId)
            else:
                raise StampedInputError("invalid relationship")
            
            domain = set(domain)
        
        try:
            user = self.getUserByScreenName(query)
            if user is not None and (domain is None or user.user_id in domain):
                seen.add(user.user_id)
                users.append(user)
        except:
            pass
        
        q = StringQuery(query, default_operator="AND", search_fields=[ "name", "screen_name" ])
        q = CustomScoreQuery(q, lang="mvel", script="""
            ns = doc.?num_stamps.value;
            ns = (ns != null) ? log(ns) : 0;
            nf = doc.?num_friends.value;
            nf = (nf != null) ? log(nf) : 0;
            return _score + ns / 4.0 + nf / 8.0
        """)
        
        if domain:
            q = FilteredQuery(q, IdsFilter('user', list(domain)))
        
        utils.log(str(domain))
        
        results = self.api._elasticsearch.search(q, 
                                                 indexes = [ 'users' ], 
                                                 doc_types = [ 'user' ], 
                                                 size = limit)
        
        try:
            user_ids = map(lambda result: result['_id'], results['hits']['hits'])
            users2   = self.lookupUsers(user_ids)
            id_user  = {}
            
            for user in users2:
                id_user[user.user_id] = user
            
            for user_id in user_ids:
                if user_id not in seen:
                    seen.add(user_id)
                    users.append(id_user[user_id])
        except Exception:
            logs.warn("received invalid results from pyes")
            logs.warn(pformat(results))
            return []
        
        return users
    
    def flagUser(self, user):
        ### TODO
        raise NotImplementedError
    
    def updateUserStats(self, userIdOrIds, stat, value=None, increment=1):
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

