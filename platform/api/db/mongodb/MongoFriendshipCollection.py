#!/usr/bin/python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals, logs, utils
import heapq, math, operator

from collections                import defaultdict
from utils                      import lazyProperty
from pprint                     import pprint

from AMongoCollection           import AMongoCollection
from MongoUserCollection        import MongoUserCollection
from MongoFriendsCollection     import MongoFriendsCollection
from MongoFollowersCollection   import MongoFollowersCollection
from MongoStampCollection       import MongoStampCollection
from MongoBlockCollection       import MongoBlockCollection

from api.AFriendshipDB          import AFriendshipDB

class MongoFriendshipCollection(AFriendshipDB):
    
    ### PUBLIC
    
    @lazyProperty
    def block_collection(self):
        return MongoBlockCollection()
    
    @lazyProperty
    def user_collection(self):
        return MongoUserCollection()
    
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
    
    def getSuggestedUserIds(self, userId, limit=20):
        friends_of_friends  = {}
        visited_users       = set()
        todo                = []
        max_distance        = 2
        friends             = None
        
        def visit_user(user_id, distance):
            if user_id in visited_users:
                return
            
            if distance == max_distance:
                try:
                    count = friends_of_friends[user_id]
                    friends_of_friends[user_id] = count + 1
                except:
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
        
        for user_id, friend_overlap in friends_of_friends.iteritems():
            if friend_overlap > 1:
                potential_friends[user_id]['friend_overlap'] = friend_overlap
        
        user_entity_ids, user_categories, user_clusters = self._get_stamp_info(userId)
        
        #for cluster in user_clusters:
        #    print "%s) %d" % (cluster['avg'], len(cluster['data']))
        
        for entity_id in user_entity_ids:
            stamps = self.stamp_collection.getStampsFromEntity(entity_id, limit=200)
            
            for stamp in stamps:
                user_id = stamp.user.user_id
                
                if user_id not in friends:
                    try:
                        potential_friends[user_id]['stamp_overlap'] = potential_friends[user_id]['stamp_overlap'] + 1
                    except:
                        potential_friends[user_id]['stamp_overlap'] = 1
        
        count = 0
        prune = 0
        
        for user_id, values in potential_friends.iteritems():
            try:
                if 'friend_overlap' not in values and values['stamp_overlap'] <= 1:
                    prune = prune + 1
                    continue
            except:
                prune = prune + 1
                continue
            
            count = count + 1
            entity_ids, categories, clusters = self._get_stamp_info(user_id)
            
            #common_entity_ids = user_entity_ids & entity_ids
            #values['stamp_overlap'] = len(common_entity_ids)
            
            summation = 0.0
            for category in [ 'food', 'music', 'film', 'book', 'other' ]:
                diff = user_categories[category] - categories[category]
                summation += diff * diff
            
            category_dist = 1.0 - math.sqrt(summation)
            values['category_overlap'] = category_dist
            
            earthRadius = 3959.0 # miles
            sum0  = len(user_entity_ids)
            sum1  = len(entity_ids)
            sum0  = 1.0 / sum0 if sum0 > 0 else 0.0
            sum1  = 1.0 / sum1 if sum1 > 0 else 0.0
            score = -1
            
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
                
                if min_len >= 0:
                    score = score + len0 * min_len * min_dist
            
            if score >= 0 and len(user_clusters) > 0:
                score = score / len(user_clusters)
            
            if score < 0:
                score = None
            elif score > 0:
                score = -math.log(score)
            
            values['proximity'] = score
        
        utils.log("potential friends:  %d" % len(potential_friends))
        utils.log("friends of friends: %d" % len(friends_of_friends))
        utils.log("processed: %d; pruned: %d" % (count, prune))
        
        """
        #for k, v in potential_friends.iteritems():
        #    utils.log("%s) %s" % (k, v))
        
        def print_top(key, reverse=True, default=-1):
            print("-" * 40)
            users = sorted(potential_friends.iteritems(), key=lambda kv: kv[1][key] if key in kv[1] else default, reverse=True)[:10]
            for user in users:
                pprint(user)
        
        print_top('friend_overlap')
        print_top('stamp_overlap')
        print_top('category_overlap')
        print_top('proximity')
        
        return []
        """
        # TODO: integrate other signals into ranking function
        # TODO: support ignoring a friend suggestion
        
        # SIGNALS:
        #    * (DONE) friend overlap
        #    * stamped entity overlap
        #       * would need fast entity_id => list(stamp_id) lookups
        #    * stamp category overlap
        #    * quality signals for potential friends
        #    * geographical proximity
        #    * small boost if other user is following you
        
        # friends of friends sorted by overlap
        # TODO: optimize this sorted loop to only retain the top n results
        users = sorted(potential_friends.iteritems(), key=self._get_potential_friend_score, reverse=True)
        if limit is not None:
            users = users[:limit]
        
        return map(lambda kv: (kv[0], self._get_potential_friend_score(kv, explain=True)[1]), users)
    
    def _get_potential_friend_score(self, kv, explain=False):
        values = kv[1]
        
        try:
            friend_overlap_value    = values['friend_overlap']
        except:
            friend_overlap_value    = 0
        
        try:
            stamp_overlap_value     = values['stamp_overlap']
        except:
            stamp_overlap_value     = 0
        
        try:
            category_overlap_value  = values['category_overlap']
        except:
            category_overlap_value  = 0
        
        try:
            proximity_value         = float(values['proximity'])
        except:
            proximity_value         = 0
        
        friend_overlap_weight       = 1.0
        stamp_overlap_weight        = 2.0
        category_overlap_weight     = 1.0
        proximity_weight            = 3.0
        
        max_val = [ (0, None), (0, None) ]
        score   = 0.0
        
        metrics = {
            'friend_overlap'    : friend_overlap_value    * friend_overlap_weight, 
            'stamp_overlap'     : stamp_overlap_value     * stamp_overlap_weight, 
            'category_overlap'  : category_overlap_value  * category_overlap_weight, 
            'proximity'         : proximity_value         * proximity_weight, 
        }
        
        #if explain:
        #    pprint(metrics)
        
        for key, value in metrics.iteritems():
            score += value
            
            if explain:
                if max_val[0][1] is None or value > max_val[0][0]:
                    if max_val[1][1] is None or value > max_val[1][0]:
                        max_val[0] = max_val[1]
                        max_val[1] = (value, key)
                    else:
                        max_val[0] = (value, key)
        
        if explain:
            explanations = {
                'friend_overlap'    : "%d friend%s in common" % \
                    (friend_overlap_value, '' if friend_overlap_value == 1 else 's'), 
                'stamp_overlap'     : "%d stamps in common" % \
                    (stamp_overlap_value, '' if stamp_overlap_value == 1 else 's'), 
                'category_overlap'  : "tend to stamp similar categories", 
                
                # TODO: naive lookup to convert cluster lat/lng => high level region (e.g., NYC or San Francisco)
                'proximity'         : "tend to stamp in similar areas", 
            }
            
            return score, (explanations[max_val[1][1]], explanations[max_val[0][1]])
        
        return score
    
    def _get_stamp_info(self, user_id):
        stampIds    = self.collection_collection.getUserStampIds(user_id)
        stamps      = self.stamp_collection.getStamps(stampIds, limit=1000, sort='modified')
        
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
        
        return entity_ids, categories, clusters2

