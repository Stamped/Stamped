#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from api_old import Blacklist
from api_old.Schemas                    import *
from api_old.auth                       import convertPasswordForStorage
from api_old                            import SchemaValidation
from api_old.S3ImageDB                  import S3ImageDB

import utils
import datetime
import logs
import libs.ec2_utils
import libs.Facebook
import libs.Twitter

from api.module import APIObject

from db.mongodb.MongoAccountCollection import MongoAccountCollection

from utils import lazyProperty, LoggingThreadPool

class LinkedAccountAPI(APIObject):

    def __init__(self):
        APIObject.__init__(self)

    @lazyProperty
    def _account_db(self):
        return MongoAccountCollection()

    @lazyProperty
    def _facebook(self):
        return libs.Facebook.Facebook()
    
    @lazyProperty
    def _twitter(self):
        return libs.Twitter.Twitter()


    def map_kind_types_to_og_type(self, kind, types):
        if kind == 'place':
            if 'bar' in types:
                return 'bar'
            elif 'restaurant' in types:
                return 'restaurant'
            # place type is broken for some reason. We'll use establishment for now
            return 'establishment'
            #return 'place'

        elif kind == 'person':
            if 'artist' in types:
                return 'artist'
            return 'person'

        elif kind == 'media_collection':
            if 'tv' in types:
                return 'tv_show'
            elif 'album' in types:
                return 'album'

        elif kind == 'media_item':
            if 'track' in types:
                return 'song'
            elif 'movie' in types:
                return 'movie'
            elif 'book' in types:
                return 'book'
            elif 'song' in types:
                return 'song'

        elif kind == 'software':
            if 'app' in types:
                return 'app'
            elif 'video_game' in types:
                return 'video_game'
        return 'other'

    def get_og_url(self, stamp=None, user=None):
        if stamp is not None:
            return stamp.url
        if user is not None:
            return "http://www.stamped.com/%s" % user.screen_name

    def remove_og_async(self, auth_user_id, og_action_id):
        account = self._account_db.getAccount(auth_user_id)
        if account.linked is not None and account.linked.facebook is not None\
           and account.linked.facebook.token is not None:
            token = account.linked.facebook.token
            result = self._facebook.deleteFromOpenGraph(og_action_id, token)


    def post_og_async(self, auth_user_id, stamp_id=None, like_stamp_id=None, todo_stamp_id=None, follow_user_id=None, image_url=None):
        # Only post to open graph if we're on prod (or we're Mike)
        ### RESTRUCTURE TODO: self.__is_prod
        if not self.__is_prod and auth_user_id != '4ecab825112dea0cfe000293':
            return

        account = self._account_db.getAccount(auth_user_id)

        token = account.linked.facebook.token
        if token is None:
            return
        fb_user_id = account.linked.facebook.linked_user_id
        action = None
        ogType = None
        url = None

        kwargs = {}
        stamp = None
        user = None
        if image_url is not None:
            kwargs['image_url'] = image_url
        if stamp_id is not None:
            action = 'stamp'
            stamp = self.getStamp(stamp_id)
            kind = stamp.entity.kind
            types = stamp.entity.types
            ogType = self.map_kind_types_to_og_type(kind, types)
            url = self.get_og_url(stamp = stamp)
            kwargs['message'] = stamp.contents[-1].blurb
        elif like_stamp_id is not None:
            action = 'like'
            stamp = self.getStamp(like_stamp_id)
            kind = stamp.entity.kind
            types = stamp.entity.types
            ogType = self.map_kind_types_to_og_type(kind, types)
            url = self.get_og_url(stamp = stamp)
        elif todo_stamp_id is not None:
            action = 'todo'
            stamp = self.getStamp(todo_stamp_id)
            kind = stamp.entity.kind
            types = stamp.entity.types
            ogType = self.map_kind_types_to_og_type(kind, types)
            url = self.get_og_url(stamp = stamp)
        elif follow_user_id is not None:
            action = 'follow'
            user = self.getUser({'user_id' : follow_user_id})
            ogType = 'profile'
            url = self.get_og_url(user = user)

        if action is None or ogType is None or url is None:
            return

        delay = 5
        while True:
            try:
                uniqueUrl = '%s?ts=%s' % (url, time.time()) if delay > 5 else url
                logs.info('### calling postToOpenGraph with action: %s  token: %s  ogType: %s  url: %s' % (action, token, ogType, uniqueUrl))
                result = self._facebook.postToOpenGraph(fb_user_id, action, token, ogType, uniqueUrl, **kwargs)
                break
            except StampedFacebookPermissionsError as e:
                account.linked.facebook.have_share_permissions = False
                self._accountDB.updateLinkedAccount(auth_user_id, account.linked.facebook)
                return
            except StampedFacebookTokenError as e:
                account.linked.facebook.token = None
                self._accountDB.updateLinkedAccount(auth_user_id, account.linked.facebook)
                return
            except StampedFacebookUniqueActionAlreadyTakenOnObject as e:
                logs.info('Unique action already taken on OG object')
                return
            except StampedFacebookOGImageSizeError as e:
                logs.info('OG Image size error')
                try:
                    del(kwargs['image_url'])
                except KeyError:
                    pass
                if delay > 60*10:
                    raise e
                time.sleep(delay)
                delay *= 2
                continue
            except StampedThirdPartyError as e:
                logs.info('### delay is at: %s' % delay)
                if delay > 60*10:
                    raise e
                time.sleep(delay)
                delay *= 2
                continue



        if stamp_id is not None and 'id' in result:
            og_action_id = result['id']
            self._stampDB.updateStampOGActionId(stamp_id, og_action_id)
        if account.linked.facebook.have_share_permissions is None:
            account.linked.facebook.have_share_permissions = True
            self._accountDB.updateLinkedAccount(auth_user_id, account.linked.facebook)

