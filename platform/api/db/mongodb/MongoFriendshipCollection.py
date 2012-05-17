#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals, logs, utils
import heapq, math
import libs.worldcities

from collections                import defaultdict
from utils                      import lazyProperty
from pprint                     import pprint
from api.Schemas                import *

from AMongoCollection           import AMongoCollection
from MongoUserCollection        import MongoUserCollection
from MongoFriendsCollection     import MongoFriendsCollection
from MongoFollowersCollection   import MongoFollowersCollection
from MongoStampCollection       import MongoStampCollection
from MongoBlockCollection       import MongoBlockCollection

from api.AFriendshipDB          import AFriendshipDB

class MongoFriendshipCollection(AFriendshipDB):
    
    def __init__(self, api):
        self.api = api
        
        if api is not None:
            request = SuggestedUserRequest()
            request.personalized = False
            self._suggested = set(user.user_id for user in api.getSuggestedUsers(None, request))
        else:
            self._suggested = set()
    
    ### PUBLIC
    
    @lazyProperty
    def block_collection(self):
        return MongoBlockCollection()
    
    @lazyProperty
    def user_collection(self):
        return MongoUserCollection(self.api)
    
    @lazyProperty
    def friends_collection(self):
        return MongoFriendsCollection()
    
    @lazyProperty
    def followers_collection(self):
        return MongoFollowersCollection()
    
    @lazyProperty
    def stamp_collection(self):
        return MongoStampCollection()
    
    @lazyProperty
    def collection_collection(self):
        from MongoCollectionCollection  import MongoCollectionCollection
        
        return MongoCollectionCollection()
    
    @lazyProperty
    def world_cities(self):
        return libs.worldcities.get_world_cities_kdtree()
    
    def addFriendship(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Add Friendship: %s -> %s" % (userId, friendId))
        self.friends_collection.addFriend(userId=userId, friendId=friendId)
        self.followers_collection.addFollower(userId=friendId, followerId=userId)
        return True
    
    def checkFriendship(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Check Friendship: %s -> %s" % (userId, friendId))
        status = self.friends_collection.checkFriend(userId=userId, \
            friendId=friendId)
        return status
    
    def removeFriendship(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Remove Friendship: %s -> %s" % (userId, friendId))
        self.friends_collection.removeFriend(userId=userId, friendId=friendId)
        self.followers_collection.removeFollower(userId=friendId, followerId=userId)
        return True
    
    def getFriends(self, userId):
        return self.friends_collection.getFriends(userId)

    def getFriendsOfFriends(self, userId, distance=2, inclusive=True):
        if distance <= 0:
            logs.warning('Invalid distance for friends of friends: %s' % distance)
            raise Exception

        friends = {0: set([userId])}
        maxDistance = distance

        def visitUser(userId, distance):
            friendIds = self.friends_collection.getFriends(userId)
            
            if distance not in friends:
                friends[distance] = set()
            
            for friendId in friendIds:
                friends[distance].add(friendId)
                
                if distance < maxDistance:
                    visitUser(friendId, distance + 1)

        visitUser(userId, 1)

        result = friends[distance]

        if not inclusive:
            prevDistance = distance - 1
            while prevDistance >= 0:
                result = result.difference(friends[prevDistance])
                prevDistance = prevDistance - 1

        return list(result)
    
    def getFollowers(self, userId):
        # TODO: Remove limit, add cursor instead
        followers = self.followers_collection.getFollowers(userId)
        return followers[-10000:]
    
    def countFriends(self, userId):
        return len(self.friends_collection.getFriends(userId))
    
    def countFollowers(self, userId):
        return len(self.followers_collection.getFollowers(userId))
    
    def approveFriendship(self, friendship):
        ### TODO
        raise NotImplementedError
    
    def addBlock(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Add Block: %s -> %s" % (userId, friendId))
        self.block_collection.addBlock(userId=userId, friendId=friendId)
    
    # One Way (Is User A blocking User B?)
    def checkBlock(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Check Block: %s -> %s" % (userId, friendId))
        status = self.block_collection.checkBlock(userId=userId, \
            friendId=friendId)
        return status
    
    # Two Way (Is User A blocking User B or blocked by User B?)
    def blockExists(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Check Block: %s -> %s" % (userId, friendId))
        statusA = self.block_collection.checkBlock(userId=userId, \
            friendId=friendId)
        
        logs.debug("Check Block: %s -> %s" % (friendId, userId))
        statusB = self.block_collection.checkBlock(userId=friendId, \
            friendId=userId)
        
        if statusA or statusB:
            return True
        return False
    
    def removeBlock(self, friendship):
        userId      = friendship.user_id
        friendId    = friendship.friend_id
        
        logs.debug("Remove Block: %s -> %s" % (userId, friendId))
        return self.block_collection.removeBlock(userId=userId, \
            friendId=friendId)
    
    def getBlocks(self, userId):
        return self.block_collection.getBlocks(userId)
    
    def getSuggestedUserIds(self, userId, request):
        """
            Returns personalized user suggestions based on several weighting 
            signals, namely:  friend overlap, stamp overlap, stamp category 
            overlap, geographical proximity of stamp clusters, FB / Twitter 
            friendship, as well as several smaller quality signals.
        """
        
        # TODO: support ignoring a friend suggestion
        # TODO: ignore previously followed friends that you've since unfollowed
        # TODO: better support for new users w/out stamps or friends
        
        friends_of_friends  = {}
        visited_users       = set()
        pruned              = set()
        todo                = []
        max_distance        = 2
        count               = 0
        friends             = None
        coords              = None
        
        if request.coordinates is not None and request.coordinates.lat is not None and request.coordinates.lng is not None:
            coords = (request.coordinates.lat, request.coordinates.lng)
        
        def visit_user(user_id, distance):
            if user_id in visited_users:
                return
            
            if distance == max_distance:
                try:
                    count = friends_of_friends[user_id]
                    friends_of_friends[user_id] = count + 1
                except Exception:
                    friends_of_friends[user_id] = 1
            else:
                visited_users.add(user_id)
                heapq.heappush(todo, (distance, user_id))
        
        # seed the algorithm with the initial user at distance 0
        visit_user(userId, 0)
        
        while True:
            try:
                distance, user_id = heapq.heappop(todo)
            except IndexError:
                break # heap is empty
            
            if distance < max_distance:
                friend_ids  = self.getFriends(user_id)
                distance    = distance + 1
                
                if friends is None:
                    friends = set(friend_ids)
                    friends.add(userId)
                
                for friend_id in friend_ids:
                    visit_user(friend_id, distance)
        
        potential_friends = defaultdict(dict)
        
        total  = sum(friends_of_friends.itervalues())
        weight = 1.0 / total if total > 0 else 0.0
        
        for user_id, friend_overlap in friends_of_friends.iteritems():
            if friend_overlap > 1:
                value = (friend_overlap ** 3) * weight
                
                potential_friends[user_id]['num_friend_overlap'] = friend_overlap
                potential_friends[user_id]['friend_overlap']     = value
        
        user_entity_ids, user_categories, user_clusters, user = self._get_stamp_info(userId)
        inv_len_user_entity_ids = len(user_entity_ids)
        inv_len_user_entity_ids = 1.0 / inv_len_user_entity_ids if inv_len_user_entity_ids > 0 else 0.0
        
        #for cluster in user_clusters:
        #    print "(%s) %d %s" % (cluster['avg'], len(cluster['data']), cluster['data'])
        
        # seed potential friends with users who have stamped at least one of the same entities
        for entity_id in user_entity_ids:
            stamps = self.stamp_collection.getStampsSliceForEntity(entity_id, GenericCollectionSlice(limit=200))
            
            for stamp in stamps:
                user_id = stamp.user.user_id
                
                if user_id not in friends:
                    try:
                        potential_friends[user_id]['num_stamp_overlap'] = potential_friends[user_id]['num_stamp_overlap'] + 1
                    except Exception:
                        potential_friends[user_id]['num_stamp_overlap'] = 1
        
        # seed potential friends with facebook friends
        if request.facebook_token is not None:
            facebook_friends = self.api._getFacebookFriends(request.facebook_token)
            
            for friend in facebook_friends:
                user_id = friend.user_id
                
                if user_id not in friends:
                    potential_friends[user_id]['facebook_friend'] = True
        
        # seed potential friends with twitter friends
        if request.twitter_key is not None and request.twitter_secret is not None:
            twitter_friends = self.api._getTwitterFriends(request.facebook_token)
            
            for friend in twitter_friends:
                user_id = friend.user_id
                
                if user_id not in friends:
                    potential_friends[user_id]['twitter_friend'] = True
        
        # process each potential friend
        for user_id, values in potential_friends.iteritems():
            try:
                if user_id in self._suggested:
                    raise
                
                if 'num_friend_overlap' not in values and 'facebook_friend' not in values and 'twitter_friend' not in values and values['num_stamp_overlap'] <= 1:
                    raise
            except Exception:
                pruned.add(user_id)
                continue
            
            count = count + 1
            entity_ids, categories, clusters, friend = self._get_stamp_info(user_id)
            overlap = 0
            
            try:
                overlap = values['num_stamp_overlap']
                values['stamp_overlap'] = overlap * overlap * inv_len_user_entity_ids
            except Exception:
                pass
            
            summation = 0.0
            for category in [ 'food', 'music', 'film', 'book', 'other' ]:
                diff = user_categories[category] - categories[category]
                summation += diff * diff
            
            category_dist = 1.0 - math.sqrt(summation)
            values['category_overlap'] = category_dist
            
            earthRadius = 3959.0 # miles
            sum0    = len(user_entity_ids)
            sum1    = len(entity_ids)
            sum0    = 1.0 / sum0 if sum0 > 0 else 0.0
            sum1    = 1.0 / sum1 if sum1 > 0 else 0.0
            score   = -1
            max_val = [ (0, None), (0, None) ]
            
            # compare seed user's stamp clusters with this user's stamp clusters
            for cluster0 in user_clusters:
                ll0  = cluster0['avg']
                len0 = len(cluster0['data']) * sum0
                
                min_dist = 10000000
                min_len  = -1
                
                for cluster1 in clusters:
                    ll1  = cluster1['avg']
                    len1 = len(cluster1['data']) * sum1
                    
                    dist = earthRadius * utils.get_spherical_distance(ll0, ll1)
                    
                    if dist >= 0 and dist < min_dist:
                        min_dist = dist
                        min_len  = len1
                
                if min_len > 0:
                    inv_dist = 1.0 / math.log(min_dist) if min_dist > 1.0 else 0.0
                    value    = len0 * min_len * inv_dist
                    score    = score + value
                    
                    if max_val[0][1] is None or value > max_val[0][0]:
                        if max_val[1][1] is None or value > max_val[1][0]:
                            max_val[0] = max_val[1]
                            max_val[1] = (value, ll0)
                        else:
                            max_val[0] = (value, ll0)
            
            if score >= 0 and len(user_clusters) > 0:
                score = score / len(user_clusters)
            
            if score < 0:
                score = None
            
            values['proximity'] = score
            values['clusters']  = max_val
            
            if coords is not None:
                min_dist = None
                
                for cluster in clusters:
                    ll0  = cluster['avg']
                    #len0 = len(cluster['data']) * sum1
                    dist = earthRadius * utils.get_spherical_distance(coords, ll0)
                    
                    if min_dist is None or dist < min_dist:
                        min_dist = dist
                        values['current_proximity'] = dist
            
            num_stamps  = friend.num_stamps if 'num_stamps' in friend else 0
            num_stamps -= overlap
            
            values['has_stamps'] = (num_stamps >= 1)
            values['num_stamps'] = math.log(num_stamps) if num_stamps >= 1 else 0.0
        
        logs.info("potential friends:  %d" % len(potential_friends))
        logs.info("friends of friends: %d" % len(friends_of_friends))
        logs.info("processed: %d; pruned: %d" % (count, len(pruned)))
        
        limit  = request.limit  if request.limit  is not None else 10
        offset = request.offset if request.offset is not None else 0
        
        if len(pruned) > 0 and len(potential_friends) - len(pruned) >= offset + limit:
            logs.debug("pruning %d potential friends (out of %d)" % (len(pruned), len(potential_friends)))
            potential_friends = dict(filter(lambda f: f[0] not in pruned, potential_friends.iteritems()))
            logs.debug("removed %d potential friends (now %d)" % (len(pruned), len(potential_friends)))
        
        """
        # debugging utility to view top scores across certain categories
        def print_top(key, reverse=True, default=-1):
            print "%s %s %s" % ("-" * 40, key, "-" * 40)
            users2 = sorted(potential_friends.iteritems(), key=lambda kv: kv[1][key] if key in kv[1] else default, reverse=True)[:10]
            
            for user in users2:
                import pprint as p
                p.pprint(user)
        
        print_top('friend_overlap')
        print_top('stamp_overlap')
        print_top('category_overlap')
        print_top('proximity')
        """
        
        # TODO: optimize this sorted loop to only retain the top n results?
        users  = sorted(potential_friends.iteritems(), key=self._get_potential_friend_score, reverse=True)
        users  = users[offset : offset + limit]
        
        func   = lambda kv: (kv[0], self._get_potential_friend_score(kv, explain=True, coords=coords)[1])
        return map(func, users)
    
    def _get_potential_friend_score(self, kv, explain=False, coords=None):
        values = kv[1]
        
        try:
            friend_overlap_value    = float(values['friend_overlap'])
        except Exception:
            friend_overlap_value    = 0
        
        try:
            num_friend_overlap      = int(values['num_friend_overlap'])
        except Exception:
            num_friend_overlap      = 0
        
        try:
            stamp_overlap_value     = float(values['stamp_overlap'])
        except Exception:
            stamp_overlap_value     = 0
        
        try:
            num_stamp_overlap       = int(values['num_stamp_overlap'])
        except Exception:
            num_stamp_overlap       = 0
        
        try:
            category_overlap_value  = float(values['category_overlap'])
        except Exception:
            category_overlap_value  = 0
        
        try:
            proximity_value         = float(values['proximity'])
        except Exception:
            proximity_value         = 0
        
        try:
            current_proximity_value = float(values['current_proximity'])
        except Exception:
            current_proximity_value = 0
        
        try:
            facebook_friend_value   = int(values['facebook_friend'])
        except Exception:
            facebook_friend_value   = 0
        
        try:
            twitter_friend_value    = int(values['twitter_friend'])
        except Exception:
            twitter_friend_value    = 0
        
        try:
            has_stamps_value        = int(values['has_stamps'])
        except Exception:
            has_stamps_value        = False
        
        try:
            num_stamps_value        = float(values['num_stamps'])
        except Exception:
            num_stamps_value        = 0.0
        
        try:
            clusters                = values['clusters']
        except Exception:
            clusters                = [ (0, None), (0, None) ]
        
        friend_overlap_weight       = 15.0
        stamp_overlap_weight        = 15.0
        category_overlap_weight     = 1.0
        proximity_weight            = 2.0
        current_proximity_weight    = 2.0
        facebook_friend_weight      = 2.0
        twitter_friend_weight       = 2.0
        num_stamps_weight           = 1.0
        has_stamps_weight           = 100.0
        
        max_val = [ (0, None), (0, None) ]
        score   = 0.0
        
        metrics = {
            'friend_overlap'    : friend_overlap_value    * friend_overlap_weight, 
            'stamp_overlap'     : stamp_overlap_value     * stamp_overlap_weight, 
            'category_overlap'  : category_overlap_value  * category_overlap_weight, 
            'proximity'         : proximity_value         * proximity_weight, 
            'current_proximity' : current_proximity_value * current_proximity_weight, 
            'facebook_friend'   : facebook_friend_value   * facebook_friend_weight, 
            'twitter_friend'    : twitter_friend_value    * twitter_friend_weight, 
        }
        
        if explain:
            import pprint as p
            utils.log('-' * 40)
            utils.log("%s)" % kv[0])
            utils.log(p.pformat(values))
            utils.log(p.pformat(metrics))
        
        for key, value in metrics.iteritems():
            score += value
            
            if explain and value > 0:
                if max_val[0][1] is None or value > max_val[0][0]:
                    if max_val[1][1] is None or value > max_val[1][0]:
                        max_val[0] = max_val[1]
                        max_val[1] = (value, key)
                    else:
                        max_val[0] = (value, key)
        
        private_metrics = {
            'num_stamps'        : num_stamps_value  * num_stamps_weight, 
            'has_stamps'        : has_stamps_weight * has_stamps_value, 
        }
        
        for key, value in private_metrics.iteritems():
            score += value
        
        if explain:
            explanations = {
                'friend_overlap'    : "%d friend%s in common" % \
                    (num_friend_overlap, '' if num_friend_overlap == 1 else 's'), 
                'stamp_overlap'     : "%d stamp%s in common" % \
                    (num_stamp_overlap, '' if num_stamp_overlap == 1 else 's'), 
                'category_overlap'  : "tends to stamp similar categories", 
                
                'proximity'         : "tends to stamp in similar areas", 
                'facebook_friend'   : "facebook friend", 
                'twitter_friend'    : "twitter Follower", # TODO: what to display here?
                'current_proximity' : "tends to stamp nearby", 
            }
            
            # naive conversion from lat/lng to closest large city (e.g., NYC or San Francisco)
            def _get_city(ll):
                ret = self.world_cities.query(ll, k=2)
                
                if ret:
                    if len(ret) >= 2 and ret[1][1]['population'] > 5 * ret[0][1]['population']:
                        return ret[1][1]['city']
                    else:
                        return ret[0][1]['city']
                
                return None
            
            try:
                if max_val[1][1] == 'proximity' or max_val[0][1] == 'proximity':
                    cities = []
                    lls = []
                    
                    if clusters[1][1] is not None:
                        lls.append(clusters[1][1])
                    
                    if clusters[0][1] is not None:
                        lls.append(clusters[0][1])
                    
                    for ll in lls:
                        city = _get_city(ll)
                        
                        if city is not None:
                            cities.append(city)
                    
                    if cities:
                        explanation = "tends to stamp in %s" % (" and ".join(cities), )
                        explanations['proximity'] = explanation
            except Exception:
                utils.printException()
            
            try:
                if coords is not None and (max_val[1][1] == 'current_proximity' or \
                                           max_val[0][1] == 'current_proximity'):
                    city = _get_city(coords)
                    
                    if city is not None:
                        explanation = "tends to stamp nearby (in %s)" % city
                        explanations['current_proximity'] = explanation
            except Exception:
                utils.printException()
            
            ret_explanations = []
            for val in reversed(max_val):
                name = val[1]
                
                if name is not None:
                    ret_explanations.append(explanations[name])
            
            return score, ret_explanations
        
        return score
    
    def _get_stamp_info(self, user_id):
        """
            Processes a single user, returning aggregate statistics about their 
            stamp behavior, including all entity_id's that the user's stamped, 
            a histogram of the categories those stamps fall into, a description 
            of their geographical stamp clusters, and the user object itself.
        """
        
        stampIds    = self.collection_collection.getUserStampIds(user_id)
        stamps      = self.stamp_collection.getStamps(stampIds, limit=1000, sort='modified')
        user        = self.user_collection.getUser(user_id)
        
        categories  = defaultdict(int)
        num_stamps  = len(stamps)
        entity_ids  = frozenset(s.entity_id for s in stamps)
        
        for stamp in stamps:
            categories[stamp.entity.category] = categories[stamp.entity.category] + 1.0 / num_stamps
        
        earthRadius = 3959.0 # miles
        clusters    = [ ]
        trivial     = True
        
        # find stamp clusters
        for stamp in stamps:
            if stamp.lat is not None and stamp.lng is not None:
                found_cluster = False
                ll = [ stamp.lat, stamp.lng ]
                #print "%s) %s" % (stamp.title, ll)
                
                for cluster in clusters:
                    dist = earthRadius * utils.get_spherical_distance(ll, cluster['avg'])
                    #print "%s) %s vs %s => %s (%s)" % (stamp.title, ll, cluster['avg'], dist, cluster['data'])
                    
                    if dist < 10:
                        cluster['data'].append(stamp.title)
                        
                        len_cluster   = len(cluster['data'])
                        found_cluster = True
                        trivial       = False
                        
                        cluster['sum'][0] = cluster['sum'][0] + ll[0]
                        cluster['sum'][1] = cluster['sum'][1] + ll[1]
                        
                        cluster['avg'][0] = cluster['sum'][0] / len_cluster
                        cluster['avg'][1] = cluster['sum'][1] / len_cluster
                        
                        #print "%s) %d %s" % (stamp.title, len_cluster, cluster)
                        break
                
                if not found_cluster:
                    clusters.append({
                        'avg'  : [ ll[0], ll[1] ], 
                        'sum'  : [ ll[0], ll[1] ], 
                        'data' : [ stamp.title ], 
                    })
        
        clusters2 = []
        if trivial:
            clusters2 = clusters
        else:
            # attempt to remove trivial clusters as outliers
            for cluster in clusters:
                if len(cluster['data']) > 1:
                    clusters2.append(cluster)
        
        return entity_ids, categories, clusters2, user

