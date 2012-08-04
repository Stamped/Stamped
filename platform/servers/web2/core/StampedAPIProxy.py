#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import copy, json, logs, urllib2, utils
import libs.ec2_utils

from api.HTTPSchemas            import *
from api.MongoStampedAPI        import globalMongoStampedAPI
from libs.Memcache              import globalMemcache, generateKeyFromDictionary
from django.utils.functional    import wraps

# initialize several useful globals
CLIENT_ID       = 'web-1.0.0'
CLIENT_SECRET   = '9lm4520o4m3718m3nmpn10h71nlbmui5'

IS_PROD         = libs.ec2_utils.is_prod_stack()

if IS_PROD:
    _baseurl    = "https://api.stamped.com/v1"
else:
    _baseurl    = "https://dev.stamped.com/v1"

class StampedAPIProxy(object):
    
    def __init__(self):
        self._prod = IS_PROD
        self._ec2  = utils.is_ec2()
        
        self.api    = globalMongoStampedAPI()
        self._cache = globalMemcache()
    
    def CACHED(no_cache=False, ttl=600):
        def decorator(fn):
            # NOTE (travis): if you hit this assertion, you're likely using the 
            # handleHTTPRequest decorator incorrectly.
            assert callable(fn)
            
            @wraps(fn)
            def _wrapper(*args, **kwargs):
                if not no_cache:
                    args2 = copy.copy(args)
                    args2[0] = None
                    
                    key = fn(*args2, **kwargs)
                    ret = self._try_get_cache(key)
                    
                    if ret is not None:
                        return ret
                
                ret = fn(*args, **kwargs)
                
                if not no_cache:
                    return self._try_set_cache(key, ret, ttl)
                else:
                    return ret
            
            return _wrapper
        return decorator
    
    def _try_get_cache(self, key):
        try:
            return self._cache[key]
        except KeyError:
            pass
        
        return None
    
    def _try_set_cache(self, key, value, ttl=600):
        try:
            self._cache.set(key, value, time=ttl)
        except Exception as e:
            logs.warning("Unable to set cache: %s" % e)
        
        return value
    
    def _export(self, d):
        for k, v in d.iteritems():
            if isinstance(v, datetime):
                d[k] = v.isoformat()
            elif isinstance(v, dict):
                d[k] = self._export(v)
        
        return d
    
    def checkAccount(self, email):
        if self._ec2:
            user = self.api.checkAccount(email)
            
            return HTTPUser().importUser(user).dataExport()
        else:
            return self._handle_post("account/check.json", {
                'login'         : email, 
                'client_id'     : CLIENT_ID, 
                'client_secret' : CLIENT_SECRET, 
            })
    
    @CACHED(no_cache=True)
    def getAccountByScreenName(self, screen_name):
        if self is None:
            return str("web::getAccountByScreenName::%s" % screen_name)
        
        if self._ec2:
            return self._export(self.api.getAccountByScreenName(screen_name).dataExport())
        else:
            return self._handle_get("users/show.json", { 'screen_name' : screen_name })
    
    @CACHED(no_cache=True)
    def getAccount(self, user_id, no_cache=False):
        if self is None:
            return str("web::getAccount::%s" % user_id)
        
        if self._ec2:
            return self._export(self.api.getAccount(user_id).dataExport())
        else:
            return self._handle_get("users/show.json", { 'user_id' : user_id })
    
    def updateAlerts(self, user_id, on, off):
        if self._ec2:
            return self.api.updateAlerts(user_id, on, off)
        else:
            raise NotImplementedError
    
    def getUser(self, params, no_cache=False):
        if self._ec2:
            key = str("web::getUser::%s" % generateKeyFromDictionary(params))
            
            if not no_cache:
                ret = self._try_get_cache(key)
                
                if ret is not None:
                    return ret
            
            user = self.api.getUser(HTTPUserId().dataImport(params), None)
            ret  = HTTPUser().importUser(user).dataExport()
            
            return self._try_set_cache(key, ret)
        else:
            return self._handle_get("users/show.json", params)
    
    def getUserStamps(self, params):
        params['scope'] = 'user'
        
        if self._ec2:
            key = str("web::getUserStamps::%s" % generateKeyFromDictionary(params))
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            ts  = HTTPTimeSlice.exportTimeSlice(HTTPTimeSlice().dataImport(params))
            ret = self._transform_stamps(self.api.getStampCollection(ts, None))
            
            return self._try_set_cache(key, ret)
        else:
            return self._handle_get("stamps/collection.json", params)
    
    def _transform_stamps(self, stamps):
        if stamps is None:
            stamps = []
        
        ret = []
        
        for stamp in stamps:
            try:
                ret.append(HTTPStamp().importStamp(stamp).dataExport())
            except Exception:
                logs.warn(utils.getFormattedException())
        
        return ret
    
    def _transform_users(self, users):
        output = []
        
        for user in users:
            output.append(HTTPUser().importUser(user).dataExport())
        
        return output
    
    def getFriends(self, user_id, limit=None):
        if self._ec2:
            key = str("web::getFriends::user_id=%s" % user_id)
            if limit is not None:
                key = str("%s,%s" % (key, limit))
            
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            ret = self._transform_users(self.api.getEnrichedFriends(user_id, limit))
            return self._try_set_cache(key, ret)
        else:
            params = { 'user_id' : user_id }
            
            return self._get_users("friendships/friends.json", params, limit)
    
    def getFollowers(self, user_id, limit=None):
        if self._ec2:
            key = str("web::getFollowers::user_id=%s" % user_id)
            if limit is not None:
                key = str("%s,%s" % (key, limit))
            
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            ret = self._transform_users(self.api.getEnrichedFollowers(user_id, limit))
            return self._try_set_cache(key, ret)
        else:
            params = { 'user_id' : user_id }
            
            return self._get_users("friendships/followers.json", params, limit)
    
    def getLikes(self, stamp_id, limit=None):
        if self._ec2:
            key = str("web::getLikes::stamp_id=%s" % stamp_id)
            if limit is not None:
                key = str("%s,%s" % (key, limit))
            
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            user_ids = self.api.getLikes(None, stamp_id)
            ret = self._transform_users(self.api.getUsers(user_ids, None, None))
            
            return self._try_set_cache(key, ret)
        else:
            params = { 'stamp_id' : stamp_id }
            
            return self._get_users("stamps/likes/show.json", params, limit)
    
    def getTodos(self, stamp_id, limit=None):
        if self._ec2:
            key = str("web::getTodos::stamp_id=%s" % stamp_id)
            if limit is not None:
                key = str("%s,%s" % (key, limit))
            
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            user_ids = self.api.getStampTodos(None, stamp_id)
            ret = self._transform_users(self.api.getUsers(user_ids, None, None))
            
            return self._try_set_cache(key, ret)
        else:
            params = { 'stamp_id' : stamp_id }
            
            return self._get_users("stamps/todos/show.json", params, limit)
    
    def _get_users(self, path, params, limit=None):
        response = self._handle_get(path, params)
        
        if 'user_ids' in response and len(response['user_ids']) > 0:
            if limit is not None:
                response['user_ids'] = response['user_ids'][:limit]
            
            # TODO: PAGING -- this only returns max 100 at a time
            return self._handle_post("users/lookup.json", {
                'user_ids' : ",".join(response['user_ids']), 
            })
        else:
            return []
    
    def getStampFromUser(self, user_id, stamp_num):
        if self._ec2:
            key = str("web::getStampFromUser::user_id=%s,stamp_num=%s" % (user_id, stamp_num))
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            stamp = self.api.getStampFromUser(userId=user_id, stampNumber=stamp_num)
            ret   = HTTPStamp().importStamp(stamp).dataExport()
            
            return self._try_set_cache(key, ret)
        else:
            return self._handle_get("stamps/show.json", {
                'user_id'   : user_id, 
                'stamp_num' : stamp_num, 
            })
    
    def getEntity(self, entity_id):
        if self._ec2:
            key = str("web::getEntity::entity_id=%s" % entity_id)
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            entity = self.api.getEntity(HTTPEntityIdSearchId().dataImport({'entity_id' : entity_id}), None)
            ret = HTTPEntity().importEntity(entity, None).dataExport()
            
            return self._try_set_cache(key, ret)
        else:
            return self._handle_get("entities/show.json", {
                'entity_id' : entity_id
            })
    
    def getEntityMenu(self, entity_id):
        if self._ec2:
            key = str("web::getEntityMenu::entity_id=%s" % entity_id)
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            menu = self.api.getMenu(entity_id)
            ret  = HTTPMenu().importMenu(menu).dataExport()
            
            return self._try_set_cache(key, ret)
        else:
            return self._handle_get("entities/menu.json", {
                'entity_id' : entity_id
            })
    
    def _handle_get(self, path, data):
        params = urllib.urlencode(data)
        url    = "%s/%s?%s" % (_baseurl, path, params)
        
        if not IS_PROD:
            utils.log("GET:  %s" % url)
        
        raw = urllib2.urlopen(url).read()
        return json.loads(raw)
    
    def _handle_post(self, path, data):
        params = urllib.urlencode(data)
        url    = "%s/%s" % (_baseurl, path)
        
        if not IS_PROD:
            utils.log("POST: %s" % url)
            utils.log(pformat(params))
        
        raw = urllib2.urlopen(url, params).read()
        return json.loads(raw)

__globalStampedAPIProxy = None

def globalStampedAPIProxy():
    global __globalStampedAPIProxy
    
    if __globalStampedAPIProxy is None:
        __globalStampedAPIProxy = StampedAPIProxy()
    
    return __globalStampedAPIProxy

