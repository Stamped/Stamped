#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import copy, re

from errors             import *
from datetime           import datetime
from schema             import *
from utils              import lazyProperty
from pprint             import pformat

from api.SchemaValidation   import *

import libs.CountryData

city_state_re = re.compile('.*,\s*([a-zA-Z .-]+)\s*,\s*([a-zA-Z]+).*')

# ####### #
# General #
# ####### #

class Coordinates(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('lat',                              float, required=True)
        cls.addProperty('lng',                              float, required=True)

class Viewport(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('upper_left',                 Coordinates)
        cls.addNestedProperty('lower_right',                Coordinates)

class ImageSizeSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('url',                              basestring)
        cls.addProperty('width',                            int)
        cls.addProperty('height',                           int)

class ImageSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('sizes',                  ImageSizeSchema)
        cls.addProperty('caption',                          basestring)

class BasicTimestamp(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('created',                          datetime, required=True)
        cls.addProperty('modified',                         datetime)
        cls.addProperty('image_cache',                      datetime)

class UserTimestamp(BasicTimestamp):
    @classmethod
    def setSchema(cls):
        cls.addProperty('activity',                         datetime)

class StampTimestamp(BasicTimestamp):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamped',                          datetime)

class StatTimestamp(Schema):
    @classmethod 
    def setSchema(cls):
        cls.addProperty('generated',                        datetime)

class SettingsEmailAlertToken(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('token_id',                         basestring)
        cls.addNestedProperty('timestamp',                  BasicTimestamp)

class Client(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('client_id',                        basestring)
        cls.addProperty('client_class',                     basestring) # iphone, web
        cls.addProperty('api_version',                      int)
        cls.addProperty('is_mobile',                        bool)
        cls.addProperty('resolution',                       int) # 1, 2

class HoursSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('open',                             basestring)
        cls.addProperty('close',                            basestring)
        cls.addProperty('desc',                             basestring)

class TimesSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('sun',                    HoursSchema)
        cls.addNestedPropertyList('mon',                    HoursSchema)
        cls.addNestedPropertyList('tue',                    HoursSchema)
        cls.addNestedPropertyList('wed',                    HoursSchema)
        cls.addNestedPropertyList('thu',                    HoursSchema)
        cls.addNestedPropertyList('fri',                    HoursSchema)
        cls.addNestedPropertyList('sat',                    HoursSchema)


# ########## #
# ClientLogs #
# ########## #

class ClientLogsEntry(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entry_id',                         basestring)
        cls.addProperty('created',                          datetime)
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('key',                              basestring, required=True)
        cls.addProperty('value',                            basestring)

        # optional ids
        cls.addProperty('stamp_id',                         basestring)
        cls.addProperty('entity_id',                        basestring)
        cls.addProperty('todo_id',                          basestring)
        cls.addProperty('comment_id',                       basestring)
        cls.addProperty('activity_id',                      basestring)


# ##### #
# Stats #
# ##### #

class CategoryDistribution(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('category',                         basestring)
        cls.addProperty('count',                            int)

class UserStatsSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('num_stamps',                       int)
        cls.addProperty('num_stamps_left',                  int)
        cls.addProperty('num_stamps_total',                 int)
        cls.addProperty('num_friends',                      int)
        cls.addProperty('num_followers',                    int)
        cls.addProperty('num_todos',                        int)
        cls.addProperty('num_credits',                      int)
        cls.addProperty('num_credits_given',                int)
        cls.addProperty('num_likes',                        int)
        cls.addProperty('num_likes_given',                  int)
        cls.addProperty('num_unread_news',                  int)
        cls.addNestedPropertyList('distribution',           CategoryDistribution)

class StampStatsSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('num_comments',                     int) # DEPRECATED
        cls.addProperty('num_todos',                        int) # DEPRECATED
        cls.addProperty('num_credit',                       int) # DEPRECATED
        cls.addProperty('num_likes',                        int) # DEPRECATED
        cls.addProperty('like_threshold_hit',               bool)
        cls.addProperty('stamp_num',                        int)
        cls.addProperty('num_blurbs',                       int)
        cls.addProperty('quality',                          float)
        cls.addProperty('popularity',                       float)
        cls.addProperty('score',                            float)
        cls.addProperty('user_id',                          basestring)

class StampStats(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                         basestring, required=True)
        cls.addProperty('entity_id',                        basestring)
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('kind',                             basestring)
        cls.addPropertyList('types',                        basestring)
        cls.addProperty('lat',                              float)
        cls.addProperty('lng',                              float)
        cls.addProperty('last_stamped',                     datetime)

        cls.addProperty('quality',                          float)
        cls.addProperty('popularity',                       float)
        cls.addProperty('score',                            float)
        cls.addProperty('num_todos',                        int)
        cls.addProperty('num_likes',                        int)
        cls.addProperty('num_credits',                      int)
        cls.addProperty('num_comments',                     int)
        cls.addPropertyList('preview_todos',                basestring) # UserIds
        cls.addPropertyList('preview_likes',                basestring) # UserIds
        cls.addPropertyList('preview_credits',              basestring) # StampIds
        cls.addPropertyList('preview_comments',             basestring) # CommentIds
        cls.addNestedProperty('timestamp',                  StatTimestamp)

class EntityStats(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                        basestring, required=True)
        cls.addProperty('num_stamps',                       int)
        cls.addProperty('quality',                          float)
        cls.addProperty('popularity',                       float)
        cls.addProperty('score',                            float)
        cls.addProperty('kind',                             basestring)
        cls.addPropertyList('types',                        basestring)
        cls.addProperty('lat',                              float)
        cls.addProperty('lng',                              float)
        cls.addPropertyList('popular_users',                basestring)
        cls.addPropertyList('popular_stamps',               basestring)
        cls.addNestedProperty('timestamp',                  StatTimestamp)

    def isType(self, t):
        try:
            if t in self.types:
                return True
        except TypeError:
            logs.warning("Type field in stamp stat set to None")
        return False


# #### #
# Auth #
# #### #

class RefreshToken(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('token_id',                         basestring)
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('client_id',                        basestring)

        cls.addPropertyList('access_tokens',                basestring)

        cls.addNestedProperty('timestamp',                  BasicTimestamp, required=True)

    def __init__(self):
        Schema.__init__(self)
        self.timestamp  = BasicTimestamp()

class AccessToken(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('token_id',                         basestring)
        cls.addProperty('refresh_token',                    basestring)
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('client_id',                        basestring)
        cls.addProperty('expires',                          datetime)

        cls.addNestedProperty('timestamp',                  BasicTimestamp, required=True)

    def __init__(self):
        Schema.__init__(self)
        self.timestamp  = BasicTimestamp()

class PasswordResetToken(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('token_id',                         basestring)
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('expires',                          datetime)

        cls.addNestedProperty('timestamp',                  BasicTimestamp)


# ####### #
# Account #
# ####### #

class TwitterAccountSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('twitter_id',                       basestring)
        cls.addProperty('twitter_name',                     basestring)
        cls.addProperty('twitter_screen_name',              basestring)
        cls.addProperty('twitter_alerts_sent',              bool)

class TwitterAuthSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('twitter_key',                      basestring)
        cls.addProperty('twitter_secret',                   basestring)

class FacebookAccountSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('facebook_id',                      basestring)
        cls.addProperty('facebook_name',                    basestring)
        cls.addProperty('facebook_screen_name',             basestring)
        cls.addProperty('facebook_alerts_sent',             bool)

class FacebookAuthSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('facebook_token',                   basestring)

class NetflixAuthSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('netflix_user_id',                  basestring)
        cls.addProperty('netflix_token',                    basestring)
        cls.addProperty('netflix_secret',                   basestring)

class DevicesSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addPropertyList('ios_device_tokens',            basestring)

class AccountAlertSettings(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('alerts_credits_apns',              bool)
        cls.addProperty('alerts_credits_email',             bool)
        cls.addProperty('alerts_likes_apns',                bool)
        cls.addProperty('alerts_likes_email',               bool)
        cls.addProperty('alerts_todos_apns',                bool)
        cls.addProperty('alerts_todos_email',               bool)
        cls.addProperty('alerts_mentions_apns',             bool)
        cls.addProperty('alerts_mentions_email',            bool)
        cls.addProperty('alerts_comments_apns',             bool)
        cls.addProperty('alerts_comments_email',            bool)
        cls.addProperty('alerts_replies_apns',              bool)
        cls.addProperty('alerts_replies_email',             bool)
        cls.addProperty('alerts_followers_apns',            bool)
        cls.addProperty('alerts_followers_email',           bool)
        cls.addProperty('alerts_friends_apns',              bool)
        cls.addProperty('alerts_friends_email',             bool)
        cls.addProperty('alerts_actions_apns',              bool)
        cls.addProperty('alerts_actions_email',             bool)

class LinkedAccountShareSettings(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('share_stamps',                     bool)
        cls.addProperty('share_likes',                      bool)
        cls.addProperty('share_todos',                      bool)
        cls.addProperty('share_follows',                    bool)

class LinkedAccount(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('service_name',                     basestring, required=True)
        cls.addProperty('linked_user_id',                   basestring)
        cls.addProperty('linked_screen_name',               basestring)
        cls.addProperty('linked_name',                      basestring)
        cls.addProperty('token',                            basestring)
        cls.addProperty('secret',                           basestring)
        cls.addProperty('token_expiration',                 datetime)
        cls.addNestedProperty('share_settings',             LinkedAccountShareSettings)

class LinkedAccounts(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('twitter',                    LinkedAccount)
        cls.addNestedProperty('facebook',                   LinkedAccount)
        cls.addNestedProperty('netflix',                    LinkedAccount)
        cls.addNestedProperty('rdio',                       LinkedAccount)

class Account(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('auth_service',                     basestring, required=True)

        cls.addProperty('name_lower',                       basestring)
        cls.addProperty('email',                            basestring)
        cls.addProperty('password',                         basestring)
        cls.addProperty('screen_name',                      basestring, required=True, cast=validateScreenName)
        cls.addProperty('screen_name_lower',                basestring)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)
        cls.addProperty('phone',                            basestring, cast=parsePhoneNumber)
        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring)
        cls.addProperty('location',                         basestring)
        cls.addProperty('privacy',                          bool, required=True)
        cls.addNestedProperty('linked',                     LinkedAccounts)
        cls.addNestedProperty('devices',                    DevicesSchema)
        cls.addNestedProperty('stats',                      UserStatsSchema, required=True)
        cls.addNestedProperty('timestamp',                  UserTimestamp, required=True)
        cls.addNestedProperty('alert_settings',             AccountAlertSettings)

    def __init__(self):
        Schema.__init__(self)
        self.privacy        = False
        self.timestamp      = UserTimestamp()
        self.stats          = UserStatsSchema()
        self.auth_service   = 'stamped'

class FacebookAccountNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_token',                       basestring, required=True)

        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('email',                            basestring)#, required=True)
        cls.addProperty('screen_name',                      basestring, required=True, cast=validateScreenName)
        cls.addProperty('phone',                            int)

        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring)
        cls.addProperty('location',                         basestring)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)

class TwitterAccountNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_token',                       basestring, required=True)
        cls.addProperty('user_secret',                      basestring, required=True)

        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('email',                            basestring)#, required=True)
        cls.addProperty('screen_name',                      basestring, required=True, cast=validateScreenName)
        cls.addProperty('phone',                            int)

        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring)
        cls.addProperty('location',                         basestring)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)


class AccountUpdateForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                             basestring)
        cls.addProperty('screen_name',                      basestring, cast=validateScreenName)
        cls.addProperty('phone',                            basestring)

        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring)
        cls.addProperty('location',                         basestring)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)

        cls.addProperty('temp_image_url',                   basestring, cast=validateURL)


# ##### #
# Users #
# ##### #

class User(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('screen_name',                      basestring, required=True, cast=validateScreenName)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)
        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring)
        cls.addProperty('location',                         basestring)
        cls.addProperty('privacy',                          bool, required=True)
        cls.addNestedProperty('stats',                      UserStatsSchema, required=True)
        cls.addNestedProperty('timestamp',                  UserTimestamp, required=True)
        cls.addProperty('following',                        bool)

    def __init__(self):
        Schema.__init__(self)
        self.stats = UserStatsSchema()
        self.timestamp = UserTimestamp()

    def minimize(self):
        return UserMini().dataImport(self.dataExport(), overflow=True)

class UserMini(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring, required=True)
        cls.addProperty('name',                             basestring)
        cls.addProperty('screen_name',                      basestring, cast=validateScreenName)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)
        cls.addProperty('privacy',                          bool)
        cls.addNestedProperty('timestamp',                  UserTimestamp) 

    def __init__(self):
        Schema.__init__(self)

class UserTiny(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('screen_name',                      basestring)

class SuggestedUser(User):
    """
    This class is used for results within Friend Finder (e.g. fine by email, via Facebook, etc.).

    It includes three additional fields: 
    - search_identifier: The identifier used for the search query (if applicable), e.g. the facebook_id
    - explanation: An explanation for why the user is being returned
    """
    @classmethod
    def setSchema(cls):
        cls.addProperty('search_identifier',                basestring)
        cls.addProperty('relationship_explanation',         basestring)

    def __init__(self):
        User.__init__(self)

    def importUser(self, user):
        self.dataImport(user.dataExport())
        return self

class Invite(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('invite_id',                        basestring)
        cls.addProperty('recipient_email',                  basestring, required=True)
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('created',                          datetime)


# ######## #
# Comments #
# ######## #

class Comment(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('comment_id',                       basestring)
        cls.addNestedProperty('user',                       UserMini, required=True)
        cls.addProperty('stamp_id',                         basestring, required=True)
        cls.addProperty('blurb',                            basestring, required=True)
        cls.addNestedProperty('timestamp',                  BasicTimestamp)


# ########### #
# Friendships #
# ########### #

class Friendship(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring, required=True)
        cls.addProperty('friend_id',                        basestring, required=True)
        cls.addNestedProperty('timestamp',                  BasicTimestamp)


# ######## #
# Previews #
# ######## #

class StampPreview(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                         basestring)
        cls.addNestedProperty('user',                       UserMini)

class Previews(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('stamps',                 StampPreview)
        cls.addNestedPropertyList('credits',                StampPreview)
        cls.addNestedPropertyList('todos',                  UserMini)
        cls.addNestedPropertyList('likes',                  UserMini)
        cls.addNestedPropertyList('comments',               Comment)


# ######## #
# Entities #
# ######## #

class EntitySources(Schema):
    @classmethod
    def setSchema(cls):

        """
        Sources follow a generally consistent format:

        * id        The unique source-specific id.

        * url       A url pointing to the entity provided by the source.

        * source    The source of the id. This will usually be the source iteslf, but can be
                    a different third-party (e.g. TMDB provides IMDB ids).

        * timestamp The timestamp of when the source was last checked.

        Additional fields may also be stored by appending the key to the source name (e.g. opentable_nickname).

        Note: The tombstone is a stamped entity that points to a newer, "better" entity.
        """

        cls.addProperty('tombstone_id',                     basestring)
        cls.addProperty('tombstone_source',                 basestring)
        cls.addProperty('tombstone_timestamp',              datetime)

        cls.addProperty('user_generated_id',                basestring)
        cls.addProperty('user_generated_subtitle',          basestring)
        cls.addProperty('user_generated_timestamp',         datetime)

        cls.addProperty('spotify_id',                       basestring)
        cls.addProperty('spotify_url',                      basestring)
        cls.addProperty('spotify_source',                   basestring)
        cls.addProperty('spotify_timestamp',                datetime)

        cls.addProperty('itunes_id',                        basestring)
        cls.addProperty('itunes_url',                       basestring)
        cls.addProperty('itunes_source',                    basestring)
        cls.addProperty('itunes_preview',                   basestring)
        cls.addProperty('itunes_timestamp',                 datetime)

        cls.addProperty('rdio_id',                          basestring)
        cls.addProperty('rdio_url',                         basestring)
        cls.addProperty('rdio_source',                      basestring)
        cls.addProperty('rdio_timestamp',                   datetime)

        cls.addProperty('amazon_id',                        basestring)
        cls.addProperty('amazon_url',                       basestring)
        cls.addProperty('amazon_underlying',                basestring)
        cls.addProperty('amazon_source',                    basestring)
        cls.addProperty('amazon_timestamp',                 datetime)

        cls.addProperty('nytimes_id',                        basestring)
        cls.addProperty('nytimes_source',                    basestring)
        cls.addProperty('nytimes_timestamp',                 datetime)

        cls.addProperty('umdmusic_id',                        basestring)
        cls.addProperty('umdmusic_source',                    basestring)
        cls.addProperty('umdmusic_timestamp',                 datetime)

        cls.addProperty('opentable_id',                     basestring)
        cls.addProperty('opentable_url',                    basestring)
        cls.addProperty('opentable_source',                 basestring)
        cls.addProperty('opentable_nickname',               basestring)
        cls.addProperty('opentable_timestamp',              datetime)

        cls.addProperty('fandango_id',                      basestring)
        cls.addProperty('fandango_url',                     basestring)
        cls.addProperty('fandango_source',                  basestring)
        cls.addProperty('fandango_timestamp',               datetime)

        cls.addProperty('netflix_id',                       basestring)
        cls.addProperty('netflix_url',                      basestring)
        cls.addProperty('netflix_source',                   basestring)
        cls.addProperty('netflix_is_instant_available',     bool)
        cls.addProperty('netflix_instant_available_until',  datetime)
        cls.addProperty('netflix_timestamp',                datetime)

        cls.addProperty('singleplatform_id',                basestring)
        cls.addProperty('singleplatform_url',               basestring)
        cls.addProperty('singleplatform_source',            basestring)
        cls.addProperty('singleplatform_timestamp',         datetime)

        cls.addProperty('foursquare_id',                    basestring)
        cls.addProperty('foursquare_url',                   basestring)
        cls.addProperty('foursquare_source',                basestring)
        cls.addProperty('foursquare_timestamp',             datetime)

        cls.addProperty('instagram_id',                     basestring)
        cls.addProperty('instagram_source',                 basestring)
        cls.addProperty('instagram_timestamp',              datetime)

        cls.addProperty('factual_id',                       basestring)
        cls.addProperty('factual_url',                      basestring)
        cls.addProperty('factual_source',                   basestring)
        cls.addProperty('factual_crosswalk',                datetime)
        cls.addProperty('factual_timestamp',                datetime)

        cls.addProperty('tmdb_id',                          basestring)
        cls.addProperty('tmdb_url',                         basestring)
        cls.addProperty('tmdb_source',                      basestring)
        cls.addProperty('tmdb_timestamp',                   datetime)

        cls.addProperty('thetvdb_id',                       basestring)
        cls.addProperty('thetvdb_url',                      basestring)
        cls.addProperty('thetvdb_source',                   basestring)
        cls.addProperty('thetvdb_timestamp',                datetime)

        cls.addProperty('imdb_id',                          basestring)
        cls.addProperty('imdb_url',                         basestring)
        cls.addProperty('imdb_source',                      basestring)
        cls.addProperty('imdb_timestamp',                   datetime)

        cls.addProperty('googleplaces_id',                  basestring)
        cls.addProperty('googleplaces_reference',           basestring)
        cls.addProperty('googleplaces_url',                 basestring)
        cls.addProperty('googleplaces_source',              basestring)
        cls.addProperty('googleplaces_timestamp',           datetime)

class BasicEntityMini(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('schema_version',                   int, required=True)
        cls.addProperty('entity_id',                        basestring)
        cls.addProperty('title',                            basestring)
        cls.addProperty('subtitle',                         basestring)
        cls.addProperty('kind',                             basestring)
        cls.addPropertyList('types',                        basestring)
        cls.addNestedProperty('sources',                    EntitySources, required=True)
        cls.addNestedPropertyList('images',                 ImageSchema)

    def __init__(self):
        Schema.__init__(self)
        self.schema_version = 0
        self.kind = 'other'
        self.sources = EntitySources()

    def isType(self, t):
        try:
            if t in self.types:
                return True
        except Exception as e:
            logs.warning("isType error (%s): %s" % (self, e))
        return False

    @property
    def category(self):
        return 'other'

    @property
    def subcategory(self):
        return 'other'


class PlaceEntityMini(BasicEntityMini):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('coordinates',                Coordinates)

    def __init__(self):
        BasicEntityMini.__init__(self)
        self.kind = 'place'

    @property
    def category(self):
        return 'place'

    @property
    def subcategory(self):
        for t in self.types:
            return t
        return 'place'

class PersonEntityMini(BasicEntityMini):
    def __init__(self):
        BasicEntityMini.__init__(self)
        self.kind = 'person'

    @property
    def category(self):
        if self.isType('artist'):
            return 'music'
        return 'other'

    @property
    def subcategory(self):
        if self.isType('artist'):
            return 'artist'
        return 'other'

class MediaCollectionEntityMini(BasicEntityMini):
    def __init__(self):
        BasicEntityMini.__init__(self)
        self.kind = 'media_collection'

    @property
    def category(self):
        if self.isType('album'):
            return 'music'
        if self.isType('tv'):
            return 'film'
        return 'other'

    @property
    def subcategory(self):
        if self.isType('album'):
            return 'album'
        if self.isType('tv'):
            return 'tv'
        return 'other'

class MediaItemEntityMini(BasicEntityMini):
    @classmethod
    def setSchema(cls):
        cls.addProperty('length',                           int)

    def __init__(self):
        BasicEntityMini.__init__(self)
        self.kind = 'media_item'

    @property
    def category(self):
        if self.isType('movie'):
            return 'film'
        if self.isType('track'):
            return 'music'
        if self.isType('book'):
            return 'book'
        return 'other'

    @property
    def subcategory(self):
        if self.isType('movie'):
            return 'movie'
        if self.isType('track'):
            return 'song'
        if self.isType('book'):
            return 'book'
        return 'other'

class SoftwareEntityMini(BasicEntityMini):
    def __init__(self):
        BasicEntityMini.__init__(self)
        self.kind = 'software'

    @property
    def category(self):
        if self.isType('app'):
            return 'app'
        return 'other'

    @property
    def subcategory(self):
        if self.isType('app'):
            return 'app'
        elif 'video_game' in self.types:
            return 'video_game'

        return 'other'

class BasicEntity(BasicEntityMini):
    @classmethod
    def setSchema(cls):
        cls.addProperty('locale',                           basestring)

        cls.addProperty('desc',                             basestring)
        cls.addProperty('desc_source',                      basestring)
        cls.addProperty('desc_timestamp',                   datetime)

        cls.addProperty('types_source',                     basestring)
        cls.addProperty('types_timestamp',                  datetime)

        cls.addProperty('images_source',                    basestring)
        cls.addProperty('images_timestamp',                 datetime)

        cls.addProperty('site',                             basestring)
        cls.addProperty('site_source',                      basestring)
        cls.addProperty('site_timestamp',                   datetime)

        cls.addProperty('email',                            basestring)
        cls.addProperty('email_source',                     basestring)
        cls.addProperty('email_timestamp',                  datetime)

        cls.addProperty('fax',                              basestring)
        cls.addProperty('fax_source',                       basestring)
        cls.addProperty('fax_timestamp',                    datetime)

        cls.addProperty('phone',                            basestring)
        cls.addProperty('phone_source',                     basestring)
        cls.addProperty('phone_timestamp',                  datetime)

        cls.addNestedProperty('timestamp',                  BasicTimestamp, required=True)
        cls.addNestedProperty('previews',                   Previews)

        # The last date/time we got some input indicating that this is currently popular.
        cls.addProperty('last_popular',                     datetime)
        # Float indicating just how fucking popular this was. Rough guidelines:
        #
        #  MUSIC
        #  - In top 10 on the charts charts for three weeks ~ 100
        #  - Charted at spot 30 for a week ~ 10
        #  - Topped charts for two months straight ~ 500
        #
        #  FILM
        #  - Typical big-budget film with average performance ~100
        #  - Some crapass indie film ~10
        #  - Huge iconic hit (Star Wars, Jaws, etc.) ~ 500
        #
        #  BOOKS
        #  - Typical NYT best-seller ~100
        #  - Book that published but never made it anywhere ~10
        #  - Harry Potter ~500
        #  - Hamlet ~1000
        #
        #  Etc.
        cls.addProperty('total_popularity_measure',         float)
        cls.addProperty('last_popular_source',              basestring)
        cls.addProperty('last_popular_timestamp',           datetime)
        # Not to be exposed to users -- just some internal data letting us know what sort
        # of input we got indicating that this is currently popular.
        cls.addProperty('last_popular_info',                basestring)

        # A list of all third-party IDs (prefixed with the name of the third party in caps and an underscore) attached
        # to a cluster. Can include duplicates from one source. Put all in a repeated list for ease of searching.
        # Ordered for best matches first.
        cls.addPropertyList('third_party_ids',              basestring)


    def __init__(self):
        BasicEntityMini.__init__(self)
        self.schema_version = 0
        self.kind = 'other'
        self.types = []
        self.sources = EntitySources()
        self.timestamp = BasicTimestamp()

    @property
    def subtitle(self):
        return self._genericSubtitle()

    @property
    def search_subtitle(self):
        # There are some specific cases -- OK, currently one specific case -- where, for search, we prefer a different
        # subtitle to the one we would typically show.
        return self.subtitle

    @lazyProperty
    def search_id(self):
        if self.entity_id:
            return self.entity_id
        if self.sources.tombstone_id:
            return self.sources.tombstone_id
        self._maybeRegenerateThirdPartyIds()
        if not self.third_party_ids:
            raise SchemaKeyError("invalid search_id (no unique ids exist) (%s)" %
                                 pformat(self.dataExport()))

        return 'T_' + ('____'.join(self.third_party_ids))

    def dataExport(self):
        self._maybeRegenerateThirdPartyIds()
        return super(BasicEntity, self).dataExport()

    def addThirdPartyId(self, sourceName, sourceId):
        idString = '%s_%s' % (sourceName.upper(), sourceId)
        if not self.third_party_ids:
            self.third_party_ids = [idString]
        elif idString not in self.third_party_ids:
            self.third_party_ids = list(self.third_party_ids) + [idString]

    def _maybeRegenerateThirdPartyIds(self):
        if self.third_party_ids:
            return

        ids = [
            (self.sources.itunes_id,                'ITUNES'),
            (self.sources.rdio_id,                  'RDIO'),
            (self.sources.spotify_id,               'SPOTIFY'),
            (self.sources.opentable_id,             'OPENTABLE'),
            (self.sources.googleplaces_reference,   'GOOGLEPLACES'),
            (self.sources.factual_id,               'FACTUAL'),
            (self.sources.tmdb_id,                  'TMDB'),
            (self.sources.thetvdb_id,               'THETVDB'),
            (self.sources.amazon_id,                'AMAZON'),
            (self.sources.fandango_id,              'FANDANGO'),
            (self.sources.netflix_id,               'NETFLIX'),
        ]

        for sourceId, sourceName in ids:
            if sourceId:
                self.addThirdPartyId(sourceName, sourceId)

    def _genericSubtitle(self):
        if self.sources.user_generated_subtitle is not None and self.sources.user_generated_subtitle != '':
            return self.sources.user_generated_subtitle
        return unicode(self.subcategory).replace('_', ' ').title()

    def minimize(self, *args):
        mini = getEntityMiniObjectFromKind(self.kind)()
        attributes = set([
            'entity_id',
            'title',
            'types',
            'sources',
            'images',
        ])
        for arg in args:
            attributes.add(arg)

        for attribute in attributes:
            try:
                if getattr(self, attribute) is not None:
                    setattr(mini, attribute, getattr(self, attribute))
            except AttributeError:
                logs.warning('Unable to minimize attribute "%s"' % attribute)

        mini.subtitle = self.subtitle
        return mini

def getEntityObjectFromKind(kind):
    if kind == 'place':
        return PlaceEntity
    if kind == 'person':
        return PersonEntity
    if kind == 'media_collection':
        return MediaCollectionEntity
    if kind == 'media_item':
        return MediaItemEntity
    if kind == 'software':
        return SoftwareEntity
    return BasicEntity

def getEntityMiniObjectFromKind(kind):
    if kind == 'place':
        return PlaceEntityMini
    if kind == 'person':
        return PersonEntityMini
    if kind == 'media_collection':
        return MediaCollectionEntityMini
    if kind == 'media_item':
        return MediaItemEntityMini
    if kind == 'software':
        return SoftwareEntityMini
    return BasicEntityMini

class PlaceEntity(BasicEntity):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('coordinates',                Coordinates)
        cls.addProperty('coordinates_source',               basestring)
        cls.addProperty('coordinates_timestamp',            datetime)

        cls.addProperty('address_street',                   basestring)
        cls.addProperty('address_street_ext',               basestring)
        cls.addProperty('address_locality',                 basestring)
        cls.addProperty('address_region',                   basestring)
        cls.addProperty('address_postcode',                 basestring)
        cls.addProperty('address_country',                  basestring)
        cls.addProperty('address_source',                   basestring)
        cls.addProperty('address_timestamp',                datetime)

        cls.addProperty('formatted_address',                basestring)
        cls.addProperty('formatted_address_source',         basestring)
        cls.addProperty('formatted_address_timestamp',      datetime)

        cls.addProperty('neighborhood',                     basestring)
        cls.addProperty('neighborhood_source',              basestring)
        cls.addProperty('neighborhood_timestamp',           datetime)

        cls.addNestedPropertyList('gallery',                ImageSchema)
        cls.addProperty('gallery_source',                   basestring)
        cls.addProperty('gallery_timestamp',                datetime)

        cls.addNestedProperty('hours',                      TimesSchema)
        cls.addProperty('hours_source',                     basestring)
        cls.addProperty('hours_timestamp',                  datetime)

        cls.addPropertyList('cuisine',                      basestring)
        cls.addProperty('cuisine_source',                   basestring)
        cls.addProperty('cuisine_timestamp',                datetime)

        cls.addProperty('menu',                             bool)
        cls.addProperty('menu_source',                      basestring)
        cls.addProperty('menu_timestamp',                   datetime)

        cls.addProperty('price_range',                      int)
        cls.addProperty('price_range_source',               basestring)
        cls.addProperty('price_range_timestamp',            datetime)

        cls.addProperty('alcohol_flag',                     bool)
        cls.addProperty('alcohol_flag_source',              basestring)
        cls.addProperty('alcohol_flag_timestamp',           datetime)

    def __init__(self):
        BasicEntity.__init__(self)
        self.kind = 'place'

    def formatAddress(self, extendStreet=False, breakLines=False):
        street      = self.address_street
        street_ext  = self.address_street_ext
        locality    = self.address_locality
        region      = self.address_region
        postcode    = self.address_postcode
        country     = self.address_country

        if country is not None:
            country = country.upper()

        delimiter = '\n' if breakLines else ', '

        if street is not None and locality is not None and country is not None:
            # Expand street
            if extendStreet == True and street_ext is not None:
                street = '%s %s' % (street, street_ext)

            # Use state if in US
            if country == 'US':
                if region is not None and postcode is not None:
                    return '%s%s%s, %s %s' % (street, delimiter, locality, region, postcode)
                elif region is not None:
                    return '%s%s%s, %s' % (street, delimiter, locality, postcode)
                elif postcode is not None:
                    return '%s%s%s, %s' % (street, delimiter, locality, region)

            # Use country if outside US
            else:
                countries = libs.CountryData.countries
                if country in countries:
                    return '%s%s%s, %s' % (street, delimiter, locality, countries[country])
                else:
                    return '%s%s%s, %s' % (street, delimiter, locality, country)

        if self.formatted_address is not None:
            return self.formatted_address

        if self.neighborhood is not None:
            return self.neighborhood

        return None

    @property
    def subtitle(self):
        # Check if address components exist
        if self.address_country is not None and self.address_locality is not None:
            if self.address_country.upper() == 'US':
                if self.address_region is not None:
                    return "%s, %s" % (self.address_locality, self.address_region)
            else:
                countries = libs.CountryData.countries
                country = self.address_country
                if self.address_country.upper() in countries:
                    country = countries[self.address_country.upper()]
                return "%s, %s" % (self.address_locality, country)

        # Extract city / state with regex as fallback
        if self.formatted_address is not None:
            match = city_state_re.match(self.formatted_address)

            if match is not None:
                # city, state
                return "%s, %s" % match.groups()

        # Fallback to generic
        return self._genericSubtitle()

    @property
    def search_subtitle(self):
        # TODO: Make sure other places in the code (HTTPSchemas, EntitySearch) stop rolling their own versions of this!
        formattedAddress = self.formatAddress()
        return formattedAddress if formattedAddress else self.subtitle

    def minimize(self, *args):
        return BasicEntity.minimize(self, 'coordinates')

    @property
    def category(self):
        return 'place'

    @property
    def subcategory(self):
        for t in self.types:
            return t
        return 'place'

class PersonEntity(BasicEntity):
    @classmethod
    def setSchema(cls):
        cls.addPropertyList('genres',                       basestring)
        cls.addProperty('genres_source',                    basestring)
        cls.addProperty('genres_timestamp',                 datetime)

        cls.addNestedPropertyList('tracks',                 MediaItemEntityMini)
        cls.addProperty('tracks_source',                    basestring)
        cls.addProperty('tracks_timestamp',                 datetime)

        cls.addNestedPropertyList('albums',                 MediaCollectionEntityMini)
        cls.addProperty('albums_source',                    basestring)
        cls.addProperty('albums_timestamp',                 datetime)

        cls.addNestedPropertyList('movies',                 MediaItemEntityMini)
        cls.addProperty('movies_source',                    basestring)
        cls.addProperty('movies_timestamp',                 datetime)

        cls.addNestedPropertyList('books',                  MediaItemEntityMini)
        cls.addProperty('books_source',                     basestring)
        cls.addProperty('books_timestamp',                  datetime)

    def __init__(self):
        BasicEntity.__init__(self)
        self.kind = 'person'

    @property
    def subtitle(self):
        if self.isType('artist'):
            return 'Artist'
        return self._genericSubtitle()

    @property
    def category(self):
        if self.isType('artist'):
            return 'music'
        return 'other'

    @property
    def subcategory(self):
        if self.isType('artist'):
            return 'artist'
        return 'other'

class BasicMediaEntity(BasicEntity):
    @classmethod
    def setSchema(cls):
        cls.addProperty('release_date',                     datetime)
        cls.addProperty('release_date_source',              basestring)
        cls.addProperty('release_date_timestamp',           datetime)

        cls.addProperty('length',                           int)
        cls.addProperty('length_source',                    basestring)
        cls.addProperty('length_timestamp',                 datetime)

        cls.addPropertyList('genres',                       basestring)
        cls.addProperty('genres_source',                    basestring)
        cls.addProperty('genres_timestamp',                 datetime)

        cls.addNestedPropertyList('artists',                PersonEntityMini)
        cls.addProperty('artists_source',                   basestring)
        cls.addProperty('artists_timestamp',                datetime)

        cls.addNestedPropertyList('authors',                PersonEntityMini)
        cls.addProperty('authors_source',                   basestring)
        cls.addProperty('authors_timestamp',                datetime)

        cls.addNestedPropertyList('directors',              PersonEntityMini)
        cls.addProperty('directors_source',                 basestring)
        cls.addProperty('directors_timestamp',              datetime)

        cls.addNestedPropertyList('cast',                   PersonEntityMini)
        cls.addProperty('cast_source',                      basestring)
        cls.addProperty('cast_timestamp',                   datetime)

        cls.addNestedPropertyList('publishers',             BasicEntityMini)
        cls.addProperty('publishers_source',                basestring)
        cls.addProperty('publishers_timestamp',             datetime)

        cls.addNestedPropertyList('studios',                BasicEntityMini)
        cls.addProperty('studios_source',                   basestring)
        cls.addProperty('studios_timestamp',                datetime)

        cls.addNestedPropertyList('networks',               BasicEntityMini)
        cls.addProperty('networks_source',                  basestring)
        cls.addProperty('networks_timestamp',               datetime)

        cls.addProperty('mpaa_rating',                      basestring)
        cls.addProperty('mpaa_rating_source',               basestring)
        cls.addProperty('mpaa_rating_timestamp',            datetime)

        cls.addProperty('parental_advisory',                basestring)
        cls.addProperty('parental_advisory_source',         basestring)
        cls.addProperty('parental_advisory_timestamp',      datetime)

    def __init__(self):
        BasicEntity.__init__(self)

class MediaCollectionEntity(BasicMediaEntity):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('tracks',                 MediaItemEntityMini)
        cls.addProperty('tracks_source',                    basestring)
        cls.addProperty('tracks_timestamp',                 datetime)

    def __init__(self):
        BasicMediaEntity.__init__(self)
        self.kind = 'media_collection'
        ### TEMP: Set all lists to lists by default (not None)
        self.tracks = []

    @property
    def subtitle(self):
        if self.isType('album'):
            if self.artists is not None and len(self.artists) > 0:
                return 'Album by %s' % ', '.join(unicode(i.title) for i in self.artists)

            return 'Album'

        if self.isType('tv'):
            if self.networks is not None and len(self.networks) > 0:
                return 'TV Show (%s)' % ', '.join(unicode(i.title) for i in self.networks)

            return 'TV Show'

        return self._genericSubtitle()

    @property
    def category(self):
        if self.isType('album'):
            return 'music'
        if self.isType('tv'):
            return 'film'
        return 'other'

    @property
    def subcategory(self):
        if self.isType('album'):
            return 'album'
        if self.isType('tv'):
            return 'tv'
        return 'other'

class MediaItemEntity(BasicMediaEntity):
    @classmethod
    def setSchema(cls):
        # Tracks
        cls.addNestedPropertyList('albums',                 MediaCollectionEntityMini)
        cls.addProperty('albums_source',                    basestring)
        cls.addProperty('albums_timestamp',                 datetime)

        # Books
        cls.addProperty('isbn',                             basestring)
        cls.addProperty('isbn_source',                      basestring)
        cls.addProperty('isbn_timestamp',                   datetime)

        cls.addProperty('sku_number',                       basestring)
        cls.addProperty('sku_number_source',                basestring)
        cls.addProperty('sku_number_timestamp',             datetime)

    def __init__(self):
        BasicMediaEntity.__init__(self)
        self.kind = 'media_item'

    def minimize(self):
        return BasicEntity.minimize(self, 'length')

    @property
    def subtitle(self):
        if self.isType('movie'):
            if self.release_date is not None:
                return 'Movie (%s)' % self.release_date.year
            return 'Movie'

        if self.isType('track'):
            if self.artists is not None and len(self.artists) > 0:
                return 'Song by %s' % ', '.join(unicode(i.title) for i in self.artists)
            return 'Song'

        if self.isType('book'):
            if self.authors is not None and len(self.authors) > 0:
                return '%s' % ', '.join(unicode(i.title) for i in self.authors)
            return 'Book'

        return self._genericSubtitle()

    @property
    def category(self):
        if self.isType('movie'):
            return 'film'
        if self.isType('track'):
            return 'music'
        if self.isType('book'):
            return 'book'
        return 'other'

    @property
    def subcategory(self):
        if self.isType('movie'):
            return 'movie'
        if self.isType('track'):
            return 'song'
        if self.isType('book'):
            return 'book'
        return 'other'

class SoftwareEntity(BasicEntity):
    @classmethod
    def setSchema(cls):
        cls.addPropertyList('genres',                       basestring)
        cls.addProperty('genres_source',                    basestring)
        cls.addProperty('genres_timestamp',                 datetime)

        cls.addProperty('release_date',                     datetime)
        cls.addProperty('release_date_source',              basestring)
        cls.addProperty('release_date_timestamp',           datetime)

        cls.addNestedPropertyList('screenshots',            ImageSchema)
        cls.addProperty('screenshots_source',               basestring)
        cls.addProperty('screenshots_timestamp',            datetime)

        cls.addNestedPropertyList('authors',                PersonEntityMini)
        cls.addProperty('authors_source',                   basestring)
        cls.addProperty('authors_timestamp',                datetime)

        cls.addNestedPropertyList('publishers',             BasicEntityMini)
        cls.addProperty('publishers_source',                basestring)
        cls.addProperty('publishers_timestamp',             datetime)

        cls.addPropertyList('supported_devices',            basestring)
        cls.addProperty('supported_devices_source',         basestring)
        cls.addProperty('supported_devices_timestamp',      datetime)

        cls.addProperty('platform',                         basestring)
        cls.addProperty('platform_source',                  basestring)
        cls.addProperty('platform_timestamp',               datetime)

    def __init__(self):
        BasicEntity.__init__(self)
        self.kind = 'software'

    @property
    def subtitle(self):
        if self.isType('app'):
            if self.authors is not None and len(self.authors) > 0:
                return 'App (%s)' % ', '.join(unicode(i.title) for i in self.authors)
            return 'App'

        elif 'video_game' in self.types:
            if self.platform:
                return 'Video Game (%s)' % self.platform

            return 'Video Game'

        return self._genericSubtitle()

    @property
    def category(self):
        if self.isType('app'):
            return 'app'
        return 'other'

    @property
    def subcategory(self):
        if self.isType('app'):
            return 'app'
        elif 'video_game' in self.types:
            return 'video_game'

        return 'other'


# ##### #
# Menus #
# ##### #

class MenuPrice(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                            basestring)
        cls.addProperty('price',                            basestring)
        cls.addProperty('calories',                         int)
        cls.addProperty('unit',                             basestring)
        cls.addProperty('currency',                         basestring)

class MenuItem(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                            basestring)
        cls.addProperty('desc',                             basestring)
        cls.addPropertyList('categories',                   basestring)
        cls.addProperty('short_desc',                       basestring)
        cls.addProperty('spicy',                            int)
        cls.addPropertyList('allergens',                    basestring)
        cls.addPropertyList('allergen_free',                basestring)
        cls.addPropertyList('restrictions',                 basestring)
        cls.addNestedPropertyList('prices',                 MenuPrice)

class MenuSection(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                            basestring)
        cls.addProperty('desc',                             basestring)
        cls.addProperty('short_desc',                       basestring)
        cls.addNestedPropertyList('items',                  MenuItem)

class Submenu(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                            basestring)
        cls.addNestedPropertyList('times',                  TimesSchema)
        cls.addProperty('footnote',                         basestring)
        cls.addProperty('desc',                             basestring)
        cls.addProperty('short_desc',                       basestring)
        cls.addNestedPropertyList('sections',               MenuSection)

class Menu(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                        basestring)
        cls.addProperty('source',                           basestring)
        cls.addProperty('source_id',                        basestring)
        cls.addProperty('source_info',                      basestring)
        cls.addProperty('disclaimer',                       basestring)
        cls.addProperty('attribution_image',                basestring)
        cls.addProperty('attribution_image_link',           basestring)
        cls.addProperty('timestamp',                        datetime)
        cls.addProperty('quality',                          float)
        cls.addNestedPropertyList('menus',                  Submenu)


# ###### #
# Stamps #
# ###### #

class StampLinks(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('og_id',                            basestring)

class Badge(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring, required=True)
        cls.addProperty('genre',                            basestring, required=True)

class StampAttributesSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('is_liked',                         bool)
        cls.addProperty('is_todo',                          bool)

    def init(self):
        Schema.__init__(self)
        self.is_liked       = False
        self.is_todo        = False

class StampContent(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('content_id',                       basestring)
        cls.addProperty('blurb',                            basestring)
        cls.addNestedPropertyList('images',                 ImageSchema)
        cls.addNestedProperty('timestamp',                  BasicTimestamp, required=True)

    def __init__(self):
        Schema.__init__(self)
        self.timestamp = BasicTimestamp()

class StampMini(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                         basestring)
        cls.addNestedProperty('entity',                     BasicEntityMini, required=True)
        cls.addNestedProperty('user',                       UserMini, required=True)
        cls.addNestedPropertyList('credits',                StampPreview)
        cls.addNestedPropertyList('contents',               StampContent, required=True)
        cls.addNestedProperty('timestamp',                  StampTimestamp, required=True)
        cls.addNestedProperty('stats',                      StampStatsSchema, required=True)
        cls.addNestedProperty('attributes',                 StampAttributesSchema)
        cls.addNestedPropertyList('badges',                 Badge)
        cls.addProperty('via',                              basestring)

    def __init__(self):
        Schema.__init__(self)
        self.entity     = BasicEntity()
        self.user       = UserMini()
        self.timestamp  = StampTimestamp()
        self.stats      = StampStatsSchema()

class Stamp(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                         basestring)
        cls.addNestedProperty('entity',                     BasicEntityMini, required=True)
        cls.addNestedProperty('user',                       UserMini, required=True)
        cls.addNestedPropertyList('credits',                StampPreview)
        cls.addNestedPropertyList('contents',               StampContent, required=True)
        cls.addNestedProperty('timestamp',                  StampTimestamp, required=True)
        cls.addNestedProperty('stats',                      StampStatsSchema, required=True)
        cls.addNestedProperty('attributes',                 StampAttributesSchema)
        cls.addNestedPropertyList('badges',                 Badge)
        cls.addProperty('via',                              basestring)
        cls.addNestedProperty('previews',                   Previews)
        cls.addNestedProperty('links',                      StampLinks)
        cls.addProperty('og_action_id',                     basestring)

    def __init__(self):
        Schema.__init__(self)
        self.timestamp  = StampTimestamp()
        self.stats      = StampStatsSchema()

    def minimize(self):
        data = self.dataExport()
        if 'previews' in data:
            del(data['previews'])
        if 'entity' in data:
            del(data['entity'])
        mini = StampMini().dataImport(data, overflow=True)
        mini.entity = self.entity 
        return mini

class StampedByGroup(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('count',                            int)
        cls.addNestedPropertyList('stamps',                 StampPreview)

class StampedBy(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('friends',                    StampedByGroup)
        cls.addNestedProperty('all',                        StampedByGroup)


# #### #
# Todo #
# #### #

class RawTodo(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('todo_id',                          basestring)
        cls.addProperty('user_id',                          basestring, required=True)
        cls.addNestedProperty('entity',                     BasicEntityMini, required=True)
        cls.addPropertyList('source_stamp_ids',             basestring)
        cls.addProperty('stamp_id',                         basestring)
        cls.addNestedProperty('timestamp',                  BasicTimestamp)
        cls.addProperty('complete',                         bool)

    def enrich(self, user, entity, previews=None, sourceStamps=None, stamp=None):
        todo = Todo()
        todo.dataImport(self.dataExport(), overflow=True)
        todo.user   = user
        todo.entity = entity
        if sourceStamps is not None:
            todo.source_stamps = sourceStamps
        if stamp is not None:
            todo.stamp  = stamp
        if previews is not None:
            todo.previews = previews

        return todo

class Todo(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('todo_id',                          basestring)
        cls.addNestedProperty('user',                       UserMini, required=True)
        cls.addNestedProperty('entity',                     BasicEntityMini, required=True)
        cls.addNestedPropertyList('source_stamps',          Stamp)
        cls.addNestedProperty('stamp',                      Stamp)
        cls.addNestedProperty('timestamp',                  BasicTimestamp)
        cls.addProperty('complete',                         bool)
        cls.addProperty('previews',                         Previews)

    def __init__(self):
        Schema.__init__(self)
        self.entity = BasicEntity()
        self.complete = False


# ######## #
# Activity #
# ######## #

class ActivityObjects(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('users',                  UserMini)
        cls.addNestedPropertyList('stamps',                 Stamp)
        cls.addNestedPropertyList('entities',               BasicEntityMini)
        cls.addNestedPropertyList('comments',               Comment)

class ActivityObjectIds(Schema):
    @classmethod
    def setSchema(cls):
        cls.addPropertyList('user_ids',                     basestring)
        cls.addPropertyList('stamp_ids',                    basestring)
        cls.addPropertyList('entity_ids',                   basestring)
        cls.addPropertyList('comment_ids',                  basestring)

class ActivityLink(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('link_id',                          basestring)
        cls.addProperty('activity_id',                      basestring, required=True)
        cls.addProperty('user_id',                          basestring, required=True)
        cls.addNestedProperty('timestamp',                  BasicTimestamp)

class ActivityReference(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('stamp_id',                         basestring)
        cls.addProperty('entity_id',                        basestring)
        cls.addPropertyList('indices',                      int)

class Activity(Schema):
    @classmethod
    def setSchema(cls):
        # Metadata
        cls.addProperty('activity_id',                      basestring)
        cls.addProperty('benefit',                          int)
        cls.addNestedProperty('timestamp',                  BasicTimestamp, required=True)

        # Structure
        cls.addPropertyList('subjects',                     basestring)
        cls.addProperty('verb',                             basestring, required=True)
        cls.addNestedProperty('objects',                    ActivityObjectIds)
        cls.addProperty('source',                           basestring)

        # Text
        cls.addProperty('header',                           basestring)
        cls.addProperty('body',                             basestring)
        cls.addProperty('footer',                           basestring)

    def enrich(self, **kwargs):
        users               = kwargs.pop('users', {})
        stamps              = kwargs.pop('stamps', {})
        entities            = kwargs.pop('entities', {})
        comments            = kwargs.pop('comments', {})
        authUserId          = kwargs.pop('authUserId', None)
        personal            = kwargs.pop('personal', False)

        result              = EnrichedActivity()
        result.activity_id  = self.activity_id
        result.verb         = self.verb
        result.benefit      = self.benefit
        result.timestamp    = self.timestamp
        result.personal     = personal
        result.header       = self.header
        result.source       = self.source
        result.body         = self.body
        result.footer       = self.footer

        if self.subjects is not None:
            subjects = []
            for userId in self.subjects:
                if users[str(userId)] is None:
                    continue
                subjects.append(users[str(userId)])
            if len(subjects) == 0:
                logs.warning('All users missing from activity item subjects')
                raise StampedActivityMissingUsersError('All users missing from activity item subjects')
            result.subjects = subjects

        if self.objects is not None:
            result.objects = ActivityObjects()

            if self.objects.user_ids is not None:
                userobjects = []
                for userId in self.objects.user_ids:
                    if userId in users and users[userId] is not None:
                        userobjects.append(users[str(userId)])
                result.objects.users = userobjects

            if self.objects.stamp_ids is not None:
                stampobjects = []
                for stampId in self.objects.stamp_ids:
                    if stampId in stamps and stamps[stampId] is not None:
                        stampobjects.append(stamps[str(stampId)])
                result.objects.stamps = stampobjects

            if self.objects.entity_ids is not None:
                entityobjects = []
                for entityId in self.objects.entity_ids:
                    if entityId in entities and entities[entityId] is not None:
                        entityobjects.append(entities[str(entityId)])
                result.objects.entities = entityobjects

            if self.objects.comment_ids is not None:
                commentobjects = []
                for commentId in self.objects.comment_ids:
                    if commentId in comments and comments[commentId] is not None:
                        commentobjects.append(comments[str(commentId)])
                result.objects.comments = commentobjects

        logs.debug("ENRICHED ENTITY: %s" % result)
        return result

class EnrichedActivity(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('activity_id',                      basestring, required=True)
        cls.addProperty('benefit',                          int)
        cls.addNestedProperty('timestamp',                  BasicTimestamp, required=True)

        # Structure
        cls.addNestedPropertyList('subjects',               UserMini)
        cls.addProperty('verb',                             basestring, required=True)
        cls.addNestedProperty('objects',                    ActivityObjects)
        cls.addProperty('source',                           basestring)

        # Text
        cls.addProperty('personal',                         bool)
        cls.addProperty('header',                           basestring)
        cls.addProperty('body',                             basestring)
        cls.addProperty('footer',                           basestring)

class Alert(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('alert_id',                         basestring)
        cls.addProperty('activity_id',                      basestring, required=True)
        cls.addProperty('recipient_id',                     basestring, required=True)
        cls.addProperty('subject',                          basestring)
        cls.addProperty('verb',                             basestring)
        cls.addNestedProperty('objects',                    ActivityObjectIds)
        cls.addProperty('created',                          datetime)


# ####### #
# Slicing #
# ####### #

class TimeSlice(Schema):
    @classmethod
    def setSchema(cls):
        # Paging
        cls.addProperty('before',                           datetime)
        cls.addProperty('limit',                            int)
        cls.addProperty('offset',                           int)
        
        # Filtering
        cls.addPropertyList('kinds',                        basestring)
        cls.addPropertyList('types',                        basestring)
        cls.addNestedProperty('viewport',                   Viewport) 
        
        # Scope
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('scope',                            basestring) # me, friends, fof, popular, user

class SearchSlice(Schema):
    @classmethod
    def setSchema(cls):
        # Paging
        cls.addProperty('limit',                            int) # Max 50

        # Filtering
        cls.addPropertyList('kinds',                        basestring)
        cls.addPropertyList('types',                        basestring)
        cls.addNestedProperty('viewport',                   Viewport) 

        # Scope
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('scope',                            basestring) # me, friends, fof, popular
        cls.addProperty('query',                            basestring, required=True) 

class RelevanceSlice(Schema):
    @classmethod
    def setSchema(cls):
        # Filtering
        cls.addPropertyList('kinds',                        basestring)
        cls.addPropertyList('types',                        basestring)
        cls.addPropertyList('properties',                   basestring)
        cls.addNestedProperty('viewport',                   Viewport) 

        # Scope
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('scope',                            basestring) # me, friends, fof, popular

class GuideRequest(Schema):
    @classmethod
    def setSchema(cls):
        # Paging
        cls.addProperty('limit',                            int)
        cls.addProperty('offset',                           int)

        # Filtering
        cls.addProperty('section',                          basestring, required=True)
        cls.addProperty('subsection',                       basestring)
        cls.addNestedProperty('viewport',                   Viewport) 

        # Scope
        cls.addProperty('scope',                            basestring)

    def __init__(self):
        Schema.__init__(self)
        self.limit = 20
        self.offset = 0

class GuideSearchRequest(GuideRequest):
    @classmethod
    def setSchema(cls):
        cls.addProperty('query',                            basestring, required=True)

    def __init__(self):
        GuideRequest.__init__(self)

class GuideCacheItem(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                        basestring, required=True)
        cls.addNestedPropertyList('stamps',                 StampPreview)
        cls.addPropertyList('todo_user_ids',                basestring)
        cls.addPropertyList('tags',                         basestring)
        cls.addNestedProperty('coordinates',                Coordinates)
        cls.addProperty('score',                            float)

class GuideCache(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring, required=True)
        cls.addNestedPropertyList('music',                  GuideCacheItem)
        cls.addNestedPropertyList('film',                   GuideCacheItem)
        cls.addNestedPropertyList('book',                   GuideCacheItem)
        cls.addNestedPropertyList('food',                   GuideCacheItem)
        cls.addNestedPropertyList('app',                    GuideCacheItem)
        cls.addNestedPropertyList('other',                  GuideCacheItem)
        cls.addNestedProperty('timestamp',                  StatTimestamp)
