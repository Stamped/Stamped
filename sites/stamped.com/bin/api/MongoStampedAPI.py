#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import json, logs

from Entity                 import *
from Schemas                import *
from utils                  import lazyProperty
from StampedAPI             import StampedAPI
from S3ImageDB              import S3ImageDB
from StatsDSink             import StatsDSink
from match.EntityMatcher    import EntityMatcher
from libs.notify            import StampedNotificationHandler

from db.mongodb.MongoAccountCollection          import MongoAccountCollection
from db.mongodb.MongoEntityCollection           import MongoEntityCollection
from db.mongodb.MongoPlacesEntityCollection     import MongoPlacesEntityCollection
from db.mongodb.MongoUserCollection             import MongoUserCollection
from db.mongodb.MongoStampCollection            import MongoStampCollection
from db.mongodb.MongoCommentCollection          import MongoCommentCollection
from db.mongodb.MongoFavoriteCollection         import MongoFavoriteCollection
from db.mongodb.MongoCollectionCollection       import MongoCollectionCollection
from db.mongodb.MongoFriendshipCollection       import MongoFriendshipCollection
from db.mongodb.MongoActivityCollection         import MongoActivityCollection
from db.mongodb.MongoInvitationCollection       import MongoInvitationCollection
from db.mongodb.MongoEntitySearcher             import MongoEntitySearcher
from db.mongodb.MongoTempEntityCollection       import MongoTempEntityCollection
from db.mongodb.MongoSearchCacheCollection      import MongoSearchCacheCollection
from db.mongodb.MongoLogsCollection             import MongoLogsCollection
from db.mongodb.MongoStatsCollection            import MongoStatsCollection
from db.mongodb.MongoAuthAccessTokenCollection  import MongoAuthAccessTokenCollection
from db.mongodb.MongoAuthRefreshTokenCollection import MongoAuthRefreshTokenCollection
from db.mongodb.MongoAuthEmailAlertsCollection  import MongoAuthEmailAlertsCollection
from db.mongodb.MongoDeletedEntityCollection    import MongoDeletedEntityCollection

class MongoStampedAPI(StampedAPI):
    """
        Implementation of Stamped API atop MongoDB.
    """
    
    def __init__(self, db=None, **kwargs):
        self.__statsSink = None
        StampedAPI.__init__(self, "MongoStampedAPI", **kwargs)
        self.lite_mode = kwargs.pop('lite_mode', False)
        
        if db:
            utils.init_db_config(db)
        
        self._entityDB       = MongoEntityCollection()
        self._placesEntityDB = MongoPlacesEntityCollection()
    
    @property
    def _statsSink(self):
        if self.__statsSink is None:
            self.__statsSink = StatsDSink(self)
        
        return self.__statsSink
    
    @lazyProperty
    def _accountDB(self):
        return MongoAccountCollection()
    
    @lazyProperty
    def _userDB(self):
        return MongoUserCollection()
    
    @lazyProperty
    def _stampDB(self):
        return MongoStampCollection()
    
    @lazyProperty
    def _commentDB(self):
        return MongoCommentCollection()
    
    @lazyProperty
    def _favoriteDB(self):
        return MongoFavoriteCollection()
    
    @lazyProperty
    def _collectionDB(self):
        return MongoCollectionCollection()
    
    @lazyProperty
    def _friendshipDB(self):
        return MongoFriendshipCollection()
    
    @lazyProperty
    def _activityDB(self):
        return MongoActivityCollection()
    
    @lazyProperty
    def _inviteDB(self):
        return MongoInvitationCollection()
    
    @lazyProperty
    def _entitySearcher(self):
        return MongoEntitySearcher(self)
    
    @lazyProperty
    def _imageDB(self):
        return S3ImageDB()
    
    @lazyProperty
    def _entityMatcher(self):
        return EntityMatcher(self)
    
    @lazyProperty
    def _logsDB(self):
        return MongoLogsCollection()
    
    @lazyProperty
    def _statsDB(self):
        return MongoStatsCollection()
    
    @lazyProperty
    def _tempEntityDB(self):
        return MongoTempEntityCollection()
    
    @lazyProperty
    def _searchCacheDB(self):
        return MongoSearchCacheCollection()
    
    @lazyProperty
    def _notificationHandler(self):
        return StampedNotificationHandler()
    
    @lazyProperty
    def _accessTokenDB(self):
        return MongoAuthAccessTokenCollection()

    @lazyProperty
    def _refreshTokenDB(self):
        return MongoAuthRefreshTokenCollection()

    @lazyProperty
    def _emailAlertDB(self):
        return MongoAuthEmailAlertsCollection()
    
    @lazyProperty
    def _deletedEntityDB(self):
        return MongoDeletedEntityCollection()
    
    def getStats(self, store=False):
        unique_user_stats = {}
        #subcategory_stats = { }
        #source_stats = { }
        
        # find the number of unique, active users from the past day / week / month
        cmd   = 'db.logstats.group({ reduce: function(obj,prev) { prev.users[obj.uid] = 1; }, cond:{uid: {$exists: true}, %s}, initial: {users:{}, }, key:{}, })'
        
        times = [
            ('one_day',   24  * 60 * 60000), # 24 hours in milliseconds
            ('one_week',  168 * 60 * 60000), # 7  days  in milliseconds
            ('one_month', 720 * 60 * 60000), # 30 days  in milliseconds
            ('total'    , None), 
        ]
        
        for k, v in times:
            try:
                if v is not None:
                    mongo_cmd = cmd % ("bgn: {$gte: new Date(new Date() - %s)}, " % v)
                else:
                    mongo_cmd = cmd % ""
                
                ret = utils.runMongoCommand(mongo_cmd)
                num_users = len(ret[0]['users'])
                
                #print "%s) %d" % (k, num_users)
                unique_user_stats[k] = num_users
            except:
                utils.printException()
        
        # evaluate distribution of comments per stamp
        cmd = 'db.comments.group({ reduce: function(obj,prev) { prev.count += 1 }, initial: {count: 0, }, key:{stamp_id:1}, })'
        ret = utils.runMongoCommand(cmd)
        num_comments_per_stamp = utils.get_basic_stats(ret, 'count')
        
        # evaluate distribution of comments per user
        cmd = 'db.comments.group({ reduce: function(obj,prev) { prev.count += 1 }, initial: {count: 0, }, key:{user:1}, })'
        ret = utils.runMongoCommand(cmd)
        num_comments_per_user = utils.get_basic_stats(ret, 'count')
        
        custom_stats = {}
        cmds = {
            # num stamps per user
            'num_stamps_per_user' : ('db.stamps.group({ reduce: function(obj,prev) { prev.count += 1 }, %sinitial: {count: 0, }, key:{user:1}, })', 1), 
            
            # num stamps left per user
            'num_stamps_left_per_user' : ('db.users.group({ reduce: function(obj,prev) { prev.count = obj.stats.num_stamps_left }, %sinitial: {count: 0, }, key:{_id:1}, finalize: function(obj) { return { "count" : obj.count }}})', 0, ), 
            
            # num likes per stamp
            'num_likes_per_stamp' : ('db.stamps.group({ reduce: function(obj,prev) { if (obj.stats.hasOwnProperty("num_likes")) { prev.count = obj.stats.num_likes; } else { prev.count = 0; } }, %sinitial: {count: 0, }, key:{_id:1}, finalize: function(obj) { return { "count" : obj.count }}})', 2), 
            
            # num likes per user
            'num_likes_per_user' : ('db.users.group({ reduce: function(obj,prev) { if (obj.stats.hasOwnProperty("num_likes")) { prev.count = obj.stats.num_likes; } else { prev.count = 0; } }, %sinitial: {count: 0, }, key:{_id:1}, finalize: function(obj) { return { "count" : obj.count }}})', 0), 
            
            # num followers per user
            'num_followers_per_user' : ('db.users.group({ reduce: function(obj,prev) { if (obj.stats.hasOwnProperty("num_followers")) { prev.count = obj.stats.num_followers; } else { prev.count = 0; } }, %sinitial: {count: 0, }, key:{_id:1}, finalize: function(obj) { return { "count" : obj.count }}})', 0), 
        }
        
        for cmd_key, cmd in cmds.iteritems():
            custom_stats[cmd_key] = {}
            
            for k, v in times:
                if v is not None:
                    if cmd[1] == 0:
                        continue
                    elif cmd[1] == 1:
                        field = 'timestamp.created'
                    else:
                        field = 'timestamp.modified'
                    
                    mongo_cmd = cmd[0] % ('cond: { "%s": {$gte: new Date(new Date() - %s)} }, ' % (field, v))
                else:
                    mongo_cmd = cmd[0] % ""
                
                ret   = utils.runMongoCommand(mongo_cmd)
                stats = utils.get_basic_stats(ret, 'count')
                
                custom_stats[cmd_key][k] = stats
        
        # TODO: incorporate more metrics
        # https://docs.google.com/a/stamped.com/spreadsheet/ccc?key=0AmEQSQLwlDtTdHoweWRZSjhXTm5Xb3NvSFBCQ0szWlE&hl=en_US#gid=0
        
        """
        for source in EntitySourcesSchema()._elements:
            count = self._entityDB._collection.find({"sources.%s" % source : { "$exists" : True }}).count()
            source_stats[source] = count
        
        for subcategory in subcategories:
            count = self._entityDB._collection.find({"subcategory" : subcategory}).count()
            subcategory_stats[subcategory] = count
        """
        
        stats = {
            'entities' : {
                'count' : self._entityDB._collection.count(), 
                'places' : {
                    'count' : self._placesEntityDB._collection.count(), 
                }, 
            }, 
            'users' : {
                'count'  : self._userDB._collection.count(), 
                'active' : unique_user_stats, 
            }, 
            'comments' : {
                'count' : self._commentDB._collection.count(), 
                'per_stamp' : num_comments_per_stamp, 
                'per_user'  : num_comments_per_user, 
            }, 
            'likes' : {
                'per_stamp' : custom_stats['num_likes_per_stamp'], 
                'per_user'  : custom_stats['num_likes_per_user'], 
            }, 
            'stamps' : {
                'count' : self._stampDB._collection.count(), 
                'per_user' : custom_stats['num_stamps_per_user'], 
                'left_per_user' : custom_stats['num_stamps_left_per_user'], 
            }, 
        }
        
        # optionally store stats
        def _store(prefix, stats):
            for k, v in stats.iteritems():
                key = "%s.%s" % (prefix, k)
                
                if isinstance(v, dict):
                    _store(key, v)
                else:
                    if isinstance(v, basestring):
                        try:
                            v = float(v)
                        except:
                            continue
                    
                    self._statsSink.time(key, v)
        
        if store:
            _store('stamped.stats', stats)
        
        return stats

