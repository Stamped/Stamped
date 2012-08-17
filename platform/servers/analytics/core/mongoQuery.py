#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

#Imports
import Globals

import keys.aws, logs, utils, pymongo

from datetime                               import timedelta
from utils                                  import lazyProperty
from api.MongoStampedAPI                    import MongoStampedAPI
from bson.objectid                          import ObjectId
from AnalyticsUtils                         import v1_init, v2_init, now

# Class containing most popular and useful mongodb queries 
# This module is dependent on the stack from which it is run
class mongoQuery(object):
    
    def __init__(self, api=MongoStampedAPI()):
        self.api = api
        
    # Mongo Collections
    @lazyProperty
    def stamp_collection(self):
        return self.api._stampDB._collection
    
    @lazyProperty
    def user_collection(self):
        return self.api._userDB._collection
    
    @lazyProperty
    def friends_collection(self):
        return self.api._friendshipDB.friends_collection._collection
    
    @lazyProperty
    def entity_collection(self):
        return self.api._entityDB._collection
    
    @lazyProperty
    def todo_collection(self):
        return self.api._todoDB._collection

    # Functions
    def newStamps(self, bgn, end):
        collection = self.stamp_collection
        field = 'timestamp.created'
        return collection.find({field: {"$gte": bgn,"$lte": end }}).count()
    
    def newAccounts(self, bgn, end):
        collection = self.user_collection
        field = "timestamp.created"
        return collection.find({field: {"$gte": bgn,"$lte": end }}).count()
    
    def topUsers(self, limit):
        top_followed = self.user_collection.find().sort('stats.num_followers', pymongo.DESCENDING).limit(limit)
        results = []
        for user in top_followed:
            results.append((str(user['screen_name']), str(user['stats']['num_followers'])))
        return results
    
    # Counts the number of users with at least one mutual relationship on stamped      
    def usersWithMutualRelationships(self, version="v2"):
        if version not in ["v1","v2"]:
            return 0
        
        if version == "v2":
            ids = self.user_collection.find({'timestamp.created': {'$gte': v2_init()}})
        else:
            ids = self.user_collection.find({'timestamp.created': {'$lt': v2_init()}})
        
        user_ids = map(lambda x: str(x['_id']), ids)
                                                          
        count = 0
        for user_id in user_ids:
            friends = set(self.api._friendshipDB.getFriends(user_id))
            followers = set(self.api._friendshipDB.getFollowers(user_id))
            if len(set.intersection(friends,followers)) > 0:
                count += 1
                
        return count
    
    # Returns the number of users following somebody not on the suggested users list
    def usersFollowingNonSuggested(self,version="v2"):
        if version not in ["v1","v2"]:
            return 0
        
        non_suggested_users = self.friends_collection.find({'ref_ids': {'$elemMatch': {'$nin': ['4ff72c599713965571000984',
                                                                                                               '4ff2279797139655710004bb',
                                                                                                               '4ff72cd097139667e50001c8',
                                                                                                               '4ff72d3a9713960355000509',
                                                                                                               '4f590e37b951fe37730005ad',
                                                                                                               '4ff48142d56d834b79000744',
                                                                                                               '4ff47ff0971396601500057c',
                                                                                                               '4e972d8dfe4a1d22d30002d1',
                                                                                                               '4e9b41f0fe4a1d44dd000601',
                                                                                                               '4ecc1f01e8ef215a42000339',
                                                                                                               '4e792021d6970356a5000042',
                                                                                                               '5011d981c5fc3e11461b6ee8',
                                                                                                               '500f3833d56d83787e000647',
                                                                                                               '4fc107f2b951fe2f75000d36',
                                                                                                               '4f567cdcd56d833b66000165',
                                                                                                               '4ecaedd2366b3c15540004f0',
                                                                                                               '4fe3721b9713967a5000007e',
                                                                                                               '4e8dfef6967ed34b3e00086c',
                                                                                                               '4e985cc7fe4a1d2fc4000220',
                                                                                                               '4f5279b5591fa45c3700053b']}}})
        non_suggested_user_ids = map(lambda x: ObjectId(x['_id']), users)
        
        if version == "v1":
            result = self.user_collection.find({'timestamp.created': {'$lt': v2_init()}, '_id': {'$in': non_suggested_user_ids}}).count()
        else:
            result = self.user_collection.find({'timestamp.created': {'$gte': v2_init()}, '_id': {'$in': non_suggested_user_ids}}).count()

        return result
    
    
    # Calculates the number of stamps created in a certain time window after its user's account creation
    # bgn and end are integers representing the number of hours after account creation
    def stampDistributionByAccountTime(self, bgn, end, version="v2"):
        if version not in ["v1","v2"]:
            return 0
        
        count = 0
        
        if version == "v2":
            all_stamps = self.stamp_collection.find({'timestamp.created' : {'$gte' : v2_init()}})
        else:
            all_stamps = self.stamp_collection.find({'timestamp.created' : {'$lt' : v2_init()}})
        
        for stamp in all_stamps:
            
            userId = str(stamp['user']['user_id'])
            stamp_time = stamp['timestamp']['created']
            
            try:
                user = self.api._userDB.getUser(userId)
            except:
                continue
            
            user_time = user.timestamp.created
            
            if stamp_time > user_time + timedelta(hours=bgn) and stamp_time <= user_time + timedelta(hours=end):
                count += 1
                
        return count
    
    # Number of users who stamped something in the first n days after launch and returned to stamp something again
    def launchDayStampRetention(self, version="v2", days=2):
        
        if version == "v2":
            bgn = v2_init()
            end = now()
        else:
            bgn = v1_init()
            end = v2_init()
            
        cutoff = bgn + timedelta(days=days)
            
        launch_stamps = self.stamp_collection.find({'timestamp.created': {'$gte': bgn, '$lt': cutoff}})
        
        launch_user_ids = set()
        for stamp in launch_stamps:
            launch_user_ids.add(str(stamp['user']['user_id']))

        new_stamps = self.stamp_collection.find({'timestamp.created': {'$gte': cutoff, '$lt': end}})

        new_user_ids = map(lambda x: str(x['user']['user_id']), new_stamps)
        
        returning_users = set(filter(lambda x: x in launch_user_ids,new_user_ids))
        
        rate = float(len(returning_users)) / len(launch_user_ids)
        
        print "Users stamping in first %s days: %s" % (days, len(launch_user_ids))
        print "Users stamping again more recently: %s" % (len(returning_users))
        print "Retention rate: %.3f" % (rate * 100.0)        
        
        
        
        
        
        