#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals, utils
import logs

from Entity                 import *
from Schemas                import *
from utils                  import lazyProperty
from StampedAPI             import StampedAPI
from S3ImageDB              import S3ImageDB
from StatsDSink             import StatsDSink
from match.EntityMatcher    import EntityMatcher
from libs.notify            import StampedNotificationHandler
from libs.EC2Utils          import EC2Utils

from db.mongodb.MongoAccountCollection      import MongoAccountCollection
from db.mongodb.MongoEntityCollection       import MongoEntityCollection
from db.mongodb.MongoPlacesEntityCollection import MongoPlacesEntityCollection
from db.mongodb.MongoUserCollection         import MongoUserCollection
from db.mongodb.MongoStampCollection        import MongoStampCollection
from db.mongodb.MongoCommentCollection      import MongoCommentCollection
from db.mongodb.MongoFavoriteCollection     import MongoFavoriteCollection
from db.mongodb.MongoCollectionCollection   import MongoCollectionCollection
from db.mongodb.MongoFriendshipCollection   import MongoFriendshipCollection
from db.mongodb.MongoActivityCollection     import MongoActivityCollection
from db.mongodb.MongoInvitationCollection   import MongoInvitationCollection
from db.mongodb.MongoEntitySearcher         import MongoEntitySearcher
from db.mongodb.MongoTempEntityCollection   import MongoTempEntityCollection
from db.mongodb.MongoLogsCollection         import MongoLogsCollection
from db.mongodb.MongoAuthAccessTokenCollection  import MongoAuthAccessTokenCollection
from db.mongodb.MongoAuthRefreshTokenCollection import MongoAuthRefreshTokenCollection

class MongoStampedAPI(StampedAPI):
    """
        Implementation of Stamped API atop MongoDB.
    """
    
    def __init__(self, db=None, **kwargs):
        StampedAPI.__init__(self, "MongoStampedAPI", **kwargs)
        
        if db:
            utils.init_db_config(db)
        
        self._entityDB       = MongoEntityCollection()
        self._placesEntityDB = MongoPlacesEntityCollection()
        self._statsSink      = self._getStatsSink()
        
        self.ec2_utils  = EC2Utils()
    
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
    def _tempEntityDB(self):
        return MongoTempEntityCollection()
    
    @lazyProperty
    def _notificationHandler(self):
        return StampedNotificationHandler()
    
    @lazyProperty
    def _accessTokenDB(self):
        return MongoAuthAccessTokenCollection()

    @lazyProperty
    def _refreshTokenDB(self):
        return MongoAuthRefreshTokenCollection()
    
    def _getStatsSink(self):
        host, port = "localhost", 8125
        
        if utils.is_ec2():
            try:
                logs.info("initializing stats sink")
                self.stack_info = self.ec2_utils.get_stack_info()
                
                for node in stack_info.nodes:
                    if 'monitor' in node.roles:
                        host, port = node.private_dns, 8125
                        break
            except:
                pass
        
        logs.info("initializing stats sink to %s:%d" % (host, port))
        return StatsDSink(host, port)
    
    def getStats(self):
        subcategory_stats = { }
        source_stats = { }
        
        # TODO: incorporate more metrics
        # https://docs.google.com/a/stamped.com/spreadsheet/ccc?key=0AmEQSQLwlDtTdHoweWRZSjhXTm5Xb3NvSFBCQ0szWlE&hl=en_US#gid=0
        
        for source in EntitySourcesSchema()._elements:
            count = self._entityDB._collection.find({"sources.%s" % source : { "$exists" : True }}).count()
            source_stats[source] = count
        
        for subcategory in subcategories:
            count = self._entityDB._collection.find({"subcategory" : subcategory}).count()
            subcategory_stats[subcategory] = count
        
        stats = {
            'entities' : {
                'count' : self._entityDB._collection.count(), 
                'sources' : source_stats, 
                'subcategory' : subcategory_stats, 
                'places' : {
                    'count' : self._placesEntityDB._collection.count(), 
                }, 
            }, 
            'users' : {
                'count' : self._userDB._collection.count(), 
            }, 
            'comments' : {
                'count' : self._commentDB._collection.count(), 
            }, 
            'stamps' : {
                'count' : self._stampDB._collection.count(), 
            }, 
        }
        
        return stats

