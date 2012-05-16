#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import copy, re

from datetime   import datetime
from schema     import *
from utils      import lazyProperty
from pprint     import pformat

import libs.CountryData

city_state_re = re.compile('.*,\s*([a-zA-Z .-]+)\s*,\s*([a-zA-Z]+).*')

# ####### #
# General #
# ####### #

class CoordinatesSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('lat',                             float, required=True)
        cls.addProperty('lng',                             float, required=True)

class ImageSizeSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('url',                             basestring)
        cls.addProperty('width',                           int)
        cls.addProperty('height',                          int)

class ImageSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('sizes',                           ImageSizeSchema)
        cls.addProperty('caption',                         basestring)

class TimestampSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('created',              datetime, required=True)
        cls.addProperty('modified',             datetime)
        cls.addProperty('image_cache',          datetime)

class UserTimestampSchema(TimestampSchema):
    @classmethod
    def setSchema(cls):
        # TimestampSchema.setSchema()
        ### TODO: Right now inheritance happens automatically. Landon is fixing. 
        cls.addProperty('activity',                     datetime)

class StampTimestampSchema(TimestampSchema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamped',              datetime)

class ModifiedTimestampSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('modified',             datetime)

class SettingsEmailAlertToken(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',            basestring)
        cls.addProperty('token_id',           basestring)
        cls.addNestedProperty('timestamp',      TimestampSchema)

class Client(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('client_id',          basestring)
        cls.addProperty('client_class',       basestring) # iphone, web
        cls.addProperty('api_version',        int)
        cls.addProperty('is_mobile',          bool)
        cls.addProperty('resolution',         int) # 1, 2


# ########## #
# ClientLogs #
# ########## #

class ClientLogsEntry(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entry_id',            basestring)
        cls.addProperty('created',             datetime)
        cls.addProperty('user_id',             basestring)
        cls.addProperty('key',                 basestring, required=True)
        cls.addProperty('value',               basestring)
        
        # optional ids
        cls.addProperty('stamp_id',            basestring)
        cls.addProperty('entity_id',           basestring)
        cls.addProperty('favorite_id',         basestring)
        cls.addProperty('comment_id',          basestring)
        cls.addProperty('activity_id',         basestring)


# ##### #
# Stats #
# ##### #

class CategoryDistributionSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('category',             basestring)
        cls.addProperty('count',                int)

class UserStatsSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('num_stamps',           int)
        cls.addProperty('num_stamps_left',      int)
        cls.addProperty('num_stamps_total',     int)
        cls.addProperty('num_friends',          int)
        cls.addProperty('num_followers',        int)
        cls.addProperty('num_faves',            int)
        cls.addProperty('num_credits',          int)
        cls.addProperty('num_credits_given',    int)
        cls.addProperty('num_likes',            int)
        cls.addProperty('num_likes_given',      int)
        cls.addProperty('num_unread_news',      int)
        cls.addNestedPropertyList('distribution', CategoryDistributionSchema)


class StampStatsSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('num_comments       ',  int)
        cls.addProperty('num_todos          ',  int)
        cls.addProperty('num_credit         ',  int)
        cls.addProperty('num_likes          ',  int)
        cls.addProperty('like_threshold_hit ',  bool)
        cls.addProperty('stamp_num          ',  int)
        cls.addProperty('num_blurbs         ',  int)

class StampStats(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id           ',  basestring, required=True)
        cls.addProperty('num_todos          ',  int)
        cls.addProperty('num_likes          ',  int)
        cls.addProperty('num_credits        ',  int)
        cls.addProperty('num_comments       ',  int)
        cls.addPropertyList('preview_todos',      basestring) # UserIds
        cls.addPropertyList('preview_likes',      basestring) # UserIds
        cls.addPropertyList('preview_credits',    basestring) # StampIds
        cls.addPropertyList('preview_comments',   basestring) # CommentIds

class EntityStats(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id          ',  basestring, required=True)
        cls.addProperty('num_stamps         ',  int)
        cls.addPropertyList('popular_users',      basestring)




# #### #
# Auth #
# #### #

class RefreshToken(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('token_id',             basestring)
        cls.addProperty('user_id',              basestring)
        cls.addProperty('client_id',            basestring)

        cls.addPropertyList('access_tokens',    basestring)

        cls.addNestedProperty('timestamp',      TimestampSchema, required=True)

    def __init__(self):
        Schema.__init__(self)
        self.timestamp  = UserTimestampSchema()

class AccessToken(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('token_id',             basestring)
        cls.addProperty('refresh_token',        basestring)
        cls.addProperty('user_id',              basestring)
        cls.addProperty('client_id',            basestring)
        cls.addProperty('expires',              datetime)

        cls.addNestedProperty('timestamp',      TimestampSchema, required=True)

    def __init__(self):
        Schema.__init__(self)
        self.timestamp  = UserTimestampSchema()

class PasswordResetToken(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('token_id',             basestring)
        cls.addProperty('user_id',              basestring)
        cls.addProperty('expires',              datetime)

        cls.addNestedProperty('timestamp',      TimestampSchema)


# ####### #
# Account #
# ####### #

class TwitterAccountSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('twitter_id',               basestring)
        cls.addProperty('twitter_screen_name',      basestring)
        cls.addProperty('twitter_alerts_sent',      bool)

class TwitterAuthSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('twitter_key',              basestring)
        cls.addProperty('twitter_secret',           basestring)

class FacebookAccountSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('facebook_id',              basestring)
        cls.addProperty('facebook_name',            basestring)
        cls.addProperty('facebook_screen_name',     basestring)
        cls.addProperty('facebook_alerts_sent',     bool)

class FacebookAuthSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('facebook_token',           basestring)

class NetflixAuthSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('netflix_user_id',          basestring)
        cls.addProperty('netflix_token',            basestring)
        cls.addProperty('netflix_secret',           basestring)

class DevicesSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addPropertyList('ios_device_tokens',    basestring)

class AccountAlerts(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('ios_alert_credit',         bool)
        cls.addProperty('ios_alert_like',           bool)
        cls.addProperty('ios_alert_fav',            bool)
        cls.addProperty('ios_alert_mention',        bool)
        cls.addProperty('ios_alert_comment',        bool)
        cls.addProperty('ios_alert_reply',          bool)
        cls.addProperty('ios_alert_follow',         bool)
        cls.addProperty('email_alert_credit',       bool)
        cls.addProperty('email_alert_like',         bool)
        cls.addProperty('email_alert_fav',          bool)
        cls.addProperty('email_alert_mention',      bool)
        cls.addProperty('email_alert_comment',      bool)
        cls.addProperty('email_alert_reply',        bool)
        cls.addProperty('email_alert_follow',       bool)

class LinkedAccounts(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('itunes',                   basestring)
        cls.addNestedProperty('twitter',            TwitterAccountSchema)
        cls.addNestedProperty('facebook',           FacebookAccountSchema)
        cls.addNestedProperty('netflix',            NetflixAuthSchema)       # netflix is the first where we keep auth tokens in db

class Account(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                  basestring)
        cls.addProperty('name',                     basestring, required=True)
        
        cls.addProperty('name_lower',               basestring)
        cls.addProperty('email',                    basestring, required=True)
        cls.addProperty('password',                 basestring, required=True)
        cls.addProperty('screen_name',              basestring, required=True)
        cls.addProperty('screen_name_lower',        basestring)
        cls.addProperty('color_primary',            basestring)
        cls.addProperty('color_secondary',          basestring)
        cls.addProperty('phone',                    int)
        cls.addProperty('bio',                      basestring)
        cls.addProperty('website',                  basestring)
        cls.addProperty('location',                 basestring)
        cls.addProperty('privacy',                  bool, required=True)
        cls.addNestedProperty('linked_accounts',    LinkedAccounts)
        cls.addNestedProperty('devices',            DevicesSchema)
        cls.addNestedProperty('stats',              UserStatsSchema, required=True)
        cls.addNestedProperty('timestamp',          UserTimestampSchema, required=True)
        cls.addNestedProperty('alerts',             AccountAlerts)

    def __init__(self):
        Schema.__init__(self)
        self.privacy    = False 
        self.timestamp  = UserTimestampSchema()
        self.stats      = UserStatsSchema()



# ##### #
# Users #
# ##### #

class User(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',              basestring)
        cls.addProperty('name',                 basestring, required=True)
        cls.addProperty('screen_name',          basestring, required=True)
        cls.addProperty('color_primary',        basestring)
        cls.addProperty('color_secondary',      basestring)
        cls.addProperty('bio',                  basestring)
        cls.addProperty('website',              basestring)
        cls.addProperty('location',             basestring)
        cls.addProperty('privacy',              bool, required=True)
        cls.addNestedProperty('stats',          UserStatsSchema)
        cls.addNestedProperty('timestamp',      UserTimestampSchema, required=True)
        cls.addProperty('identifier',           basestring)
    
    # def exportSchema(self, schema):
    #     if schema.__class__.__name__ in ('UserMini', 'UserTiny'):
    #         schema.importData(self.value, overflow=True)
    #     else:
    #         raise NotImplementedError
    #     return schema

class UserMini(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',              basestring, required=True)
        cls.addProperty('screen_name',          basestring)
        cls.addProperty('color_primary',        basestring)
        cls.addProperty('color_secondary',      basestring)
        cls.addProperty('privacy',              bool)
        cls.addProperty('timestamp',            UserTimestampSchema)

class UserTiny(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',              basestring)
        cls.addProperty('screen_name',          basestring)

class SuggestedUserRequest(Schema):
    @classmethod
    def setSchema(cls):
        # paging
        cls.addProperty('limit',                int)
        cls.addProperty('offset',               int)
        
        cls.addProperty('personalized',         bool)
        cls.addProperty('coordinates',          CoordinatesSchema)
        
        # third party keys for optionally augmenting friend suggestions with 
        # knowledge from other social networks
        cls.addProperty('twitter_key',          basestring)
        cls.addProperty('twitter_secret',       basestring)
        cls.addProperty('facebook_token',       basestring)

    def __init__(self):
        Schema.__init__(self)
        self.limit          = 10 
        self.offset         = 0
        self.personalized   = False

class Invite(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('invite_id',            basestring)
        cls.addProperty('recipient_email',      basestring, required=True)
        cls.addProperty('user_id',              basestring)
        cls.addProperty('created',              datetime)


# ######## #
# Entities #
# ######## #


class EntityStatsSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('titlev',                          float)
        cls.addProperty('subcatv',                         float)
        cls.addProperty('sourcev',                         float)
        cls.addProperty('qualityv',                        float)
        cls.addProperty('distancev',                       float)
        cls.addProperty('totalv',                          float)

class EntityContactSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('site',                            basestring)
        cls.addProperty('site_source',                     basestring)
        cls.addProperty('site_timestamp',                  datetime)

        cls.addProperty('email',                           basestring)
        cls.addProperty('email_source',                    basestring)
        cls.addProperty('email_timestamp',                 datetime)

        cls.addProperty('fax',                             basestring)
        cls.addProperty('fax_source',                      basestring)
        cls.addProperty('fax_timestamp',                   datetime)

        cls.addProperty('phone',                           basestring)
        cls.addProperty('phone_source',                    basestring)
        cls.addProperty('phone_timestamp',                 datetime)

class EntitySourcesSchema(Schema):
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

        cls.addProperty('tombstone_id',                    basestring)
        cls.addProperty('tombstone_source',                basestring)
        cls.addProperty('tombstone_timestamp',             datetime)

        cls.addProperty('user_generated_id',               basestring)
        cls.addProperty('user_generated_subtitle',         basestring)
        cls.addProperty('user_generated_timestamp',        datetime)

        cls.addProperty('spotify_id',                      basestring)
        cls.addProperty('spotify_url',                     basestring)
        cls.addProperty('spotify_source',                  basestring)
        cls.addProperty('spotify_timestamp',               datetime)

        cls.addProperty('itunes_id',                       basestring)
        cls.addProperty('itunes_url',                      basestring)
        cls.addProperty('itunes_source',                   basestring)
        cls.addProperty('itunes_preview',                  basestring)
        cls.addProperty('itunes_timestamp',                datetime)

        cls.addProperty('rdio_id',                         basestring)
        cls.addProperty('rdio_url',                        basestring)
        cls.addProperty('rdio_source',                     basestring)
        cls.addProperty('rdio_timestamp',                  datetime)
        
        cls.addProperty('amazon_id',                       basestring)
        cls.addProperty('amazon_url',                      basestring)
        cls.addProperty('amazon_underlying',               basestring)
        cls.addProperty('amazon_source',                   basestring)
        cls.addProperty('amazon_timestamp',                datetime)
        
        cls.addProperty('opentable_id',                    basestring)
        cls.addProperty('opentable_url',                   basestring)
        cls.addProperty('opentable_source',                basestring)
        cls.addProperty('opentable_nickname',              basestring)
        cls.addProperty('opentable_timestamp',             datetime)
        
        cls.addProperty('fandango_id',                     basestring)
        cls.addProperty('fandango_url',                    basestring)
        cls.addProperty('fandango_source',                 basestring)
        cls.addProperty('fandango_timestamp',              datetime)

        cls.addProperty('netflix_id',                      basestring)
        cls.addProperty('netflix_url',                     basestring)
        cls.addProperty('netflix_source',                  basestring)
        cls.addProperty('netflix_is_instant_available',    bool)
        cls.addProperty('netflix_instant_available_until', datetime)
        cls.addProperty('netflix_timestamp',               datetime)

        cls.addProperty('singleplatform_id',               basestring)
        cls.addProperty('singleplatform_url',              basestring)
        cls.addProperty('singleplatform_source',           basestring)
        cls.addProperty('singleplatform_timestamp',        datetime)

        cls.addProperty('foursquare_id',                   basestring)
        cls.addProperty('foursquare_url',                  basestring)
        cls.addProperty('foursquare_source',               basestring)
        cls.addProperty('foursquare_timestamp',            datetime)

        cls.addProperty('instagram_id',                    basestring)
        cls.addProperty('instagram_source',                basestring)
        cls.addProperty('instagram_timestamp',             datetime)

        cls.addProperty('factual_id',                      basestring)
        cls.addProperty('factual_url',                     basestring)
        cls.addProperty('factual_source',                  basestring)
        cls.addProperty('factual_crosswalk',               datetime)
        cls.addProperty('factual_timestamp',               datetime)

        cls.addProperty('tmdb_id',                         basestring)
        cls.addProperty('tmdb_url',                        basestring)
        cls.addProperty('tmdb_source',                     basestring)
        cls.addProperty('tmdb_timestamp',                  datetime)
        
        cls.addProperty('thetvdb_id',                      basestring)
        cls.addProperty('thetvdb_url',                     basestring)
        cls.addProperty('thetvdb_source',                  basestring)
        cls.addProperty('thetvdb_timestamp',               datetime)
        
        cls.addProperty('imdb_id',                         basestring)
        cls.addProperty('imdb_url',                        basestring)
        cls.addProperty('imdb_source',                     basestring)
        cls.addProperty('imdb_timestamp',                  datetime)
        
        cls.addProperty('googleplaces_id',                 basestring)
        cls.addProperty('googleplaces_reference',          basestring)
        cls.addProperty('googleplaces_url',                basestring)
        cls.addProperty('googleplaces_source',             basestring)
        cls.addProperty('googleplaces_timestamp',          datetime)


class BasicEntity(Schema):

    @classmethod
    def setSchema(cls):
        cls.addProperty('schema_version',         int, required=True) ### TO-DO: DEFAULT = 0

        cls.addProperty('entity_id',              basestring)
        cls.addProperty('title',                  basestring)
        cls.addProperty('kind',                   basestring, required=True) ### TO-DO: DEFAULT = 'other'
        cls.addProperty('locale',                 basestring)

        cls.addProperty('desc',                            basestring)
        cls.addProperty('desc_source',                     basestring)
        cls.addProperty('desc_timestamp',                  datetime)
        
        cls.addPropertyList('types',                        basestring)
        cls.addProperty('types_source',                    basestring)
        cls.addProperty('types_timestamp',                 datetime)
        
        cls.addNestedPropertyList('images',                 ImageSchema)
        cls.addProperty('images_source',                   basestring)
        cls.addProperty('images_timestamp',                datetime)
        
        cls.addNestedProperty('contact',                         EntityContactSchema)
        cls.addNestedProperty('stats',                           EntityStatsSchema)
        cls.addNestedProperty('sources',                         EntitySourcesSchema)
        cls.addNestedProperty('timestamp',                 TimestampSchema)
    
    @property 
    def subtitle(self):
        return self._genericSubtitle()
    
    @property 
    def category(self):
        return 'other'
    
    @property 
    def subcategory(self):
        return 'other'
    
    @lazyProperty
    def search_id(self):
        _is_valid_id = lambda x: x is not None and len(x) > 0
        
        ids = [
            (self.sources.tombstone_id, ''), 
            (self.entity_id,            ''), 
            (self.itunes_id,            'T_ITUNES_'), 
            (self.rdio_id,              'T_RDIO_'), 
            (self.spotify_id,           'T_SPOTIFY_'), 
            (self.opentable_id,         'T_OPENTABLE_'), 
            (self.googleplaces_reference,'T_GOOGLEPLACES_'),
            (self.factual_id,           'T_FACTUAL_'), 
            (self.tmdb_id,              'T_TMDB_'), 
            (self.thetvdb_id,           'T_THETVDB_'), 
            (self.amazon_id,            'T_AMAZON_'), 
            (self.fandango_id,          'T_FANDANGO_'),
            (self.netflix_id,           'T_NETFLIX_'),
        ]
        
        for (id, prefix) in ids:
            if _is_valid_id(id):
                return "%s%s" % (prefix, id)
        
        raise SchemaKeyError("invalid search_id (no unique ids exist) (%s)" % 
                             pformat(self.exportSparse()))
    
    def _genericSubtitle(self):
        if self.user_generated_subtitle is not None:
            return self.user_generated_subtitle
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
                if self[attribute] is not None:
                    mini[attribute] = self[attribute]
            except:
                pass

        return mini

    def isType(self, t):
        try:
            if t in self.types.value:
                return True
        except:
            pass
        return False
    
    # def __str__(self):
    #     t = list(self.types)
    #     # if len(t) == 1: t = t[0]
        
    #     return "%s: %s (%s)" % (self.__class__.__name__, self.title, '; '.join(unicode(i) for i in t))
    
    def __repr__(self):
        return "%s (%s)" % (self.__class__.__name__, pformat(self.value))





# ##### #
# Menus #
# ##### #

class HoursSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('open',                            basestring)
        cls.addProperty('close',                           basestring)
        cls.addProperty('desc',                            basestring)

class TimesSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('sun',                 HoursSchema)
        cls.addNestedPropertyList('mon',                 HoursSchema)
        cls.addNestedPropertyList('tue',                 HoursSchema)
        cls.addNestedPropertyList('wed',                 HoursSchema)
        cls.addNestedPropertyList('thu',                 HoursSchema)
        cls.addNestedPropertyList('fri',                 HoursSchema)
        cls.addNestedPropertyList('sat',                 HoursSchema)

class MenuPriceSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                           basestring)
        cls.addProperty('price',                           basestring)
        cls.addProperty('calories',                        int)
        cls.addProperty('unit',                            basestring)
        cls.addProperty('currency',                        basestring)

class MenuItemSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                           basestring)
        cls.addProperty('desc',                            basestring)
        cls.addPropertyList('categories',               basestring)
        cls.addProperty('short_desc',                      basestring)
        cls.addProperty('spicy',                           int)
        cls.addPropertyList('allergens',                      basestring)
        cls.addPropertyList('allergen_free',                  basestring)
        cls.addPropertyList('restrictions',                   basestring)
        cls.addNestedPropertyList('prices',                 MenuPriceSchema)

class MenuSectionSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                           basestring)
        cls.addProperty('desc',                            basestring)
        cls.addProperty('short_desc',                      basestring)
        cls.addNestedPropertyList('items'               , MenuItemSchema)

class SubmenuSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                           basestring)
        cls.addNestedPropertyList('times'                          , TimesSchema)
        cls.addProperty('footnote',                        basestring)
        cls.addProperty('desc',                            basestring)
        cls.addProperty('short_desc',                      basestring)
        cls.addNestedPropertyList('sections'            , MenuSectionSchema)

class MenuSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                       basestring)
        cls.addProperty('source',                          basestring)
        cls.addProperty('source_id',                       basestring)
        cls.addProperty('source_info',                     basestring)
        cls.addProperty('disclaimer',                      basestring)
        cls.addProperty('attribution_image',               basestring)
        cls.addProperty('attribution_image_link',          basestring)
        cls.addProperty('timestamp',                       datetime)
        cls.addProperty('quality',                         float)
        cls.addNestedPropertyList('menus',              SubmenuSchema)


class PlaceEntity(Schema):
    pass


# ###### #
# Stamps #
# ###### #

class Badge(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',              basestring, required=True)
        cls.addProperty('genre',                basestring, required=True)

class MentionSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('screen_name',          basestring, required=True)
        cls.addProperty('user_id',              basestring)
        cls.addPropertyList('indices',      int)

class CreditSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',              basestring, required=True)
        cls.addProperty('screen_name',          basestring, required=True)
        cls.addProperty('stamp_id',             basestring)
        ### TEMP?
        cls.addProperty('color_primary',        basestring)
        cls.addProperty('color_secondary',      basestring)
        cls.addProperty('privacy',              bool)

class StampAttributesSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('is_liked',             bool)
        cls.addProperty('is_fav',               bool)

# class DeletedStamp(Schema):
#     @classmethod
#     def setSchema(cls):
#         cls.addProperty('stamp_id',             basestring)
#         cls.addNestedProperty('timestamp',          TimestampSchema)
#         cls.addProperty('deleted',              bool)

class StampContent(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('blurb',                basestring)
        cls.addNestedPropertyList('images',             ImageSchema)
        cls.addNestedProperty('timestamp',          TimestampSchema)
        cls.addNestedPropertyList('mentions',           MentionSchema)

class StampMini(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                 basestring)
        cls.addNestedProperty('entity',             BasicEntity, required=True)
        cls.addNestedProperty('user',               UserMini, required=True)
        cls.addNestedPropertyList('credit',         CreditSchema)
        cls.addNestedPropertyList('contents',       StampContent)
        cls.addProperty('via',                      basestring)
        cls.addNestedProperty('timestamp',          StampTimestampSchema)
        cls.addNestedProperty('stats',              StampStatsSchema)
        cls.addNestedProperty('attributes',         StampAttributesSchema)
        cls.addNestedPropertyList('badges',         Badge)

class StampPreviews(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('likes',              UserMini)
        cls.addNestedPropertyList('todos',              UserMini)
        cls.addNestedPropertyList('credits',            StampMini)
        cls.addNestedPropertyList('comments',           Comment)

class Stamp(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                 basestring)
        cls.addNestedProperty('entity',             BasicEntity, required=True)
        cls.addNestedProperty('user',               UserMini, required=True)
        cls.addNestedPropertyList('credit',         CreditSchema)
        cls.addNestedPropertyList('contents',       StampContent)
        cls.addProperty('via',                      basestring)
        cls.addNestedProperty('timestamp',          StampTimestampSchema)
        cls.addNestedProperty('stats',              StampStatsSchema)
        cls.addNestedProperty('attributes',         StampAttributesSchema)
        cls.addNestedPropertyList('badges',         Badge)
        cls.addNestedProperty('previews',           StampPreviews)

    def minimize(self):
        return StampMini().dataImport(self.dataExport(), overflow=True)





if 1 == 0:







    # ########### #
    # Friendships #
    # ########### #

    class Friendship(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring, required=True)
            self.friend_id          = SchemaElement(basestring, required=True)
            self.timestamp          = TimestampSchema()


    # ######## #
    # Favorite #
    # ######## #

    class Favorite(Schema):
        def setSchema(self):
            self.favorite_id        = SchemaElement(basestring)
            self.user_id            = SchemaElement(basestring, required=True)
            self.entity             = BasicEntity(required=True)
            self.stamp              = Stamp()
            self.timestamp          = TimestampSchema()
            self.complete           = SchemaElement(bool)



    # ######## #
    # Comments #
    # ######## #

    class Comment(Schema):
        def setSchema(self):
            self.comment_id         = SchemaElement(basestring)
            self.user               = UserMini(required=True)
            self.stamp_id           = SchemaElement(basestring, required=True)
            self.restamp_id         = SchemaElement(basestring)
            self.blurb              = SchemaElement(basestring, required=True)
            self.blurb_formatted    = SchemaElement(basestring)
            self.mentions           = SchemaList(MentionSchema())
            self.timestamp          = TimestampSchema()


    # ######## #
    # Activity #
    # ######## #

    class Activity(Schema):
        def setSchema(self):
            # Metadata
            self.activity_id        = SchemaElement(basestring)
            self.benefit            = SchemaElement(int)
            self.timestamp          = TimestampSchema()

            # Structure
            self.subjects           = SchemaList(SchemaElement(basestring))
            self.verb               = SchemaElement(basestring, required=True)
            self.objects            = ActivityObjectIds()

            # Text
            self.header             = SchemaElement(basestring)
            self.body               = SchemaElement(basestring)
            self.footer             = SchemaElement(basestring)

        def enrich(self, **kwargs):
            users       = kwargs.pop('users', {})
            stamps      = kwargs.pop('stamps', {})
            entities    = kwargs.pop('entities', {})
            comments    = kwargs.pop('comments', {})
            authUserId  = kwargs.pop('authUserId', None)
            personal    = kwargs.pop('personal', False)

            result              = EnrichedActivity()
            result.activity_id  = self.activity_id
            result.verb         = self.verb 
            result.benefit      = self.benefit
            result.timestamp    = self.timestamp 
            result.personal     = personal

            for userId in self.subjects:
                result.subjects.append(users[str(userId)])

            for userId in self.objects.user_ids:
                result.objects.users.append(users[str(userId)])

            for stampId in self.objects.stamp_ids:
                result.objects.stamps.append(stamps[str(stampId)])

            for entityId in self.objects.entity_ids:
                result.objects.entities.append(entities[str(entityId)])

            for commentId in self.objects.comment_ids:
                result.objects.comments.append(comments[str(commentId)])

            return result


    class EnrichedActivity(Schema):
        def setSchema(self):
            self.activity_id        = SchemaElement(basestring, required=True)
            self.benefit            = SchemaElement(int)
            self.timestamp          = TimestampSchema()

            # Structure
            self.subjects           = SchemaList(UserMini())
            self.verb               = SchemaElement(basestring, required=True)
            self.objects            = ActivityObjects()

            # Text
            self.personal           = SchemaElement(bool)
            self.header             = SchemaElement(basestring)
            self.body               = SchemaElement(basestring)
            self.footer             = SchemaElement(basestring)


    class ActivityObjects(Schema):
        def setSchema(self):
            self.users              = SchemaList(UserMini())
            self.stamps             = SchemaList(Stamp())
            self.entities           = SchemaList(BasicEntityMini())
            self.comments           = SchemaList(Comment())

    class ActivityObjectIds(Schema):
        def setSchema(self):
            self.user_ids           = SchemaList(SchemaElement(basestring))
            self.stamp_ids          = SchemaList(SchemaElement(basestring))
            self.entity_ids         = SchemaList(SchemaElement(basestring))
            self.comment_ids        = SchemaList(SchemaElement(basestring))

    class ActivityLink(Schema):
        def setSchema(self):
            self.link_id            = SchemaElement(basestring)
            self.activity_id        = SchemaElement(basestring, required=True)
            self.user_id            = SchemaElement(basestring, required=True)
            self.timestamp          = TimestampSchema()

    class ActivityReference(Schema):
        def setSchema(self):
            self.user_id            = SchemaElement(basestring)
            self.stamp_id           = SchemaElement(basestring)
            self.entity_id          = SchemaElement(basestring)
            self.indices            = SchemaList(SchemaElement(int))

    class ActivityFormat(Schema):
        def setSchema(self):
            self.title              = SchemaElement(bool)

    class Alert(Schema):
        def setSchema(self):
            self.alert_id           = SchemaElement(basestring)
            self.activity_id        = SchemaElement(basestring, required=True)
            self.recipient_id       = SchemaElement(basestring, required=True)
            self.user_id            = SchemaElement(basestring)
            self.genre              = SchemaElement(basestring)
            self.created            = SchemaElement(datetime)




    # ####### #
    # Slicing #
    # ####### #

    class GenericSlice(Schema):
        def setSchema(self):
            # paging
            self.limit              = SchemaElement(int)
            self.offset             = SchemaElement(int, default=0)
            
            # sorting
            self.sort               = SchemaElement(basestring, default='modified')
            self.reverse            = SchemaElement(bool,       default=False)
            self.coordinates        = CoordinatesSchema()
            
            # filtering
            self.since              = SchemaElement(datetime)
            self.before             = SchemaElement(datetime)

    class GenericCollectionSlice(GenericSlice):
        def setSchema(self):
            GenericSlice.setSchema(self)
            
            # sorting
            # (relevance, popularity, proximity, created, modified, alphabetical)

            # filtering
            self.query              = SchemaElement(basestring)
            self.category           = SchemaElement(basestring)
            self.subcategory        = SchemaElement(basestring)
            self.viewport           = ViewportSchema()
            
            # misc options
            self.quality            = SchemaElement(int,  default=1)
            self.deleted            = SchemaElement(bool, default=False)
            self.comments           = SchemaElement(bool, default=True)
            self.unique             = SchemaElement(bool, default=False)

    class UserCollectionSlice(GenericCollectionSlice):
        def setSchema(self):
            GenericCollectionSlice.setSchema(self)
            
            self.user_id            = SchemaElement(basestring)
            self.screen_name        = SchemaElement(basestring)

    class FriendsSlice(GenericCollectionSlice):
        def setSchema(self):
            GenericCollectionSlice.setSchema(self)
            
            self.distance           = SchemaElement(int,  default=2)
            self.inclusive          = SchemaElement(bool, default=True)

    class ConsumptionSlice(GenericCollectionSlice):
        def setSchema(self):
            GenericCollectionSlice.setSchema(self)

            self.scope              = SchemaElement(basestring)
            self.filter             = SchemaElement(basestring)


    class ViewportSchema(Schema):
        def setSchema(self):
            self.upperLeft          = CoordinatesSchema()
            self.lowerRight         = CoordinatesSchema()










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

        def setSchema(self):
            BasicEntity.setSchema(self)
            self.kind                           = SchemaElement(basestring, required=True, default='place')
            
            self.coordinates                    = CoordinatesSchema()
            self.coordinates_source             = SchemaElement(basestring)
            self.coordinates_timestamp          = SchemaElement(datetime) 
            
            self.address_street                 = SchemaElement(basestring)
            self.address_street_ext             = SchemaElement(basestring)
            self.address_locality               = SchemaElement(basestring)
            self.address_region                 = SchemaElement(basestring)
            self.address_postcode               = SchemaElement(basestring)
            self.address_country                = SchemaElement(basestring)
            self.address_source                 = SchemaElement(basestring)
            self.address_timestamp              = SchemaElement(datetime)
            
            self.formatted_address              = SchemaElement(basestring)
            self.formatted_address_source       = SchemaElement(basestring)
            self.formatted_address_timestamp    = SchemaElement(datetime)
            
            self.neighborhood                   = SchemaElement(basestring)
            self.neighborhood_source            = SchemaElement(basestring)
            self.neighborhood_timestamp         = SchemaElement(datetime)

            self.gallery                        = SchemaList(ImageSchema())
            self.gallery_source                 = SchemaElement(basestring)
            self.gallery_timestamp              = SchemaElement(datetime)
            
            self.hours                          = TimesSchema()
            self.hours_source                   = SchemaElement(basestring)
            self.hours_timestamp                = SchemaElement(datetime)
            
            self.cuisine                        = SchemaList(SchemaElement(basestring))
            self.cuisine_source                 = SchemaElement(basestring)
            self.cuisine_timestamp              = SchemaElement(datetime)
            
            self.menu                           = SchemaElement(bool)
            self.menu_source                    = SchemaElement(basestring)
            self.menu_timestamp                 = SchemaElement(datetime)
            
            self.price_range                    = SchemaElement(int)
            self.price_range_source             = SchemaElement(basestring)
            self.price_range_timestamp          = SchemaElement(datetime)
            
            self.alcohol_flag                   = SchemaElement(bool)
            self.alcohol_flag_source            = SchemaElement(basestring)
            self.alcohol_flag_timestamp         = SchemaElement(datetime)

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
        def category(self):
            food = set(['restaurant', 'bar', 'bakery', 'cafe', 'market', 'food', 'night_club'])
            if len(food.intersection(self.types.value)) > 0:
                return 'food'
            return 'other'

        @property 
        def subcategory(self):
            for t in self.types.value:
                return t
            return 'other'


    class PersonEntity(BasicEntity):
        def setSchema(self):
            BasicEntity.setSchema(self)
            self.kind                           = SchemaElement(basestring, required=True, default='person')

            self.genres                         = SchemaList(SchemaElement(basestring))
            self.genres_source                  = SchemaElement(basestring)
            self.genres_timestamp               = SchemaElement(datetime)

            self.tracks                         = SchemaList(MediaItemEntityMini())
            self.tracks_source                  = SchemaElement(basestring)
            self.tracks_timestamp               = SchemaElement(datetime)
            
            self.albums                         = SchemaList(MediaCollectionEntityMini())
            self.albums_source                  = SchemaElement(basestring)
            self.albums_timestamp               = SchemaElement(datetime)
            
            self.movies                         = SchemaList(MediaItemEntityMini())
            self.movies_source                  = SchemaElement(basestring)
            self.movies_timestamp               = SchemaElement(datetime)
            
            self.books                          = SchemaList(MediaItemEntityMini())
            self.books_source                   = SchemaElement(basestring)
            self.books_timestamp                = SchemaElement(datetime)

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
        def setSchema(self):
            BasicEntity.setSchema(self)
            
            self.release_date                   = SchemaElement(datetime)
            self.release_date_source            = SchemaElement(basestring)
            self.release_date_timestamp         = SchemaElement(datetime)
            
            self.length                         = SchemaElement(int)
            self.length_source                  = SchemaElement(basestring)
            self.length_timestamp               = SchemaElement(datetime)
            
            self.genres                         = SchemaList(SchemaElement(basestring))
            self.genres_source                  = SchemaElement(basestring)
            self.genres_timestamp               = SchemaElement(datetime)
            
            self.artists                        = SchemaList(PersonEntityMini())
            self.artists_source                 = SchemaElement(basestring)
            self.artists_timestamp              = SchemaElement(datetime)
            
            self.authors                        = SchemaList(PersonEntityMini())
            self.authors_source                 = SchemaElement(basestring)
            self.authors_timestamp              = SchemaElement(datetime)
            
            self.directors                      = SchemaList(PersonEntityMini())
            self.directors_source               = SchemaElement(basestring)
            self.directors_timestamp            = SchemaElement(datetime)
            
            self.cast                           = SchemaList(PersonEntityMini())
            self.cast_source                    = SchemaElement(basestring)
            self.cast_timestamp                 = SchemaElement(datetime)
            
            self.publishers                     = SchemaList(BasicEntityMini())
            self.publishers_source              = SchemaElement(basestring)
            self.publishers_timestamp           = SchemaElement(datetime)
            
            self.studios                        = SchemaList(BasicEntityMini())
            self.studios_source                 = SchemaElement(basestring)
            self.studios_timestamp              = SchemaElement(datetime)
            
            self.networks                       = SchemaList(BasicEntityMini())
            self.networks_source                = SchemaElement(basestring)
            self.networks_timestamp             = SchemaElement(datetime)
            
            self.mpaa_rating                    = SchemaElement(basestring)
            self.mpaa_rating_source             = SchemaElement(basestring)
            self.mpaa_rating_timestamp          = SchemaElement(datetime)
            
            self.parental_advisory              = SchemaElement(basestring)
            self.parental_advisory_source       = SchemaElement(basestring)
            self.parental_advisory_timestamp    = SchemaElement(datetime)

    class MediaCollectionEntity(BasicMediaEntity):
        def setSchema(self):
            BasicMediaEntity.setSchema(self)
            self.kind                           = SchemaElement(basestring, required=True, default='media_collection')
            
            self.tracks                         = SchemaList(MediaItemEntityMini())
            self.tracks_source                  = SchemaElement(basestring)
            self.tracks_timestamp               = SchemaElement(datetime)
            
            #self.seasons                        = SchemaList(SeasonSchema())
            #self.status                         = SchemaElement(basestring)
        
        @property 
        def subtitle(self):
            if self.isType('album'):
                if len(self.artists) > 0:
                    return 'Album by %s' % ', '.join(unicode(i['title']) for i in self.artists)
                
                return 'Album'
            
            if self.isType('tv'):
                if len(self.networks) > 0:
                    return 'TV Show (%s)' % ', '.join(unicode(i['title']) for i in self.networks)
                
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
        def setSchema(self):
            BasicMediaEntity.setSchema(self)
            self.kind                           = SchemaElement(basestring, required=True, default='media_item')
            
            # Tracks
            self.albums                         = SchemaList(MediaCollectionEntityMini())
            self.albums_source                  = SchemaElement(basestring)
            self.albums_timestamp               = SchemaElement(datetime)
            
            # Books
            self.isbn                           = SchemaElement(basestring)
            self.isbn_source                    = SchemaElement(basestring)
            self.isbn_timestamp                 = SchemaElement(datetime)
            
            self.sku_number                     = SchemaElement(basestring)
            self.sku_number_source              = SchemaElement(basestring)
            self.sku_number_timestamp           = SchemaElement(datetime)

        def minimize(self):
            return BasicEntity.minimize(self, 'length')
        
        @property 
        def subtitle(self):
            if self.isType('movie'):
                if self.release_date is not None:
                    return 'Movie (%s)' % self.release_date.year
                return 'Movie'

            if self.isType('track'):
                if len(self.artists) > 0:
                    return 'Song by %s' % ', '.join(unicode(i['title']) for i in self.artists)
                return 'Song'

            if self.isType('book'):
                if len(self.authors) > 0:
                    return '%s' % ', '.join(unicode(i['title']) for i in self.authors)
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
        def setSchema(self):
            BasicEntity.setSchema(self)
            self.kind                           = SchemaElement(basestring, required=True, default='software')

            self.genres                         = SchemaList(SchemaElement(basestring))
            self.genres_source                  = SchemaElement(basestring)
            self.genres_timestamp               = SchemaElement(datetime)

            self.release_date                   = SchemaElement(datetime)
            self.release_date_source            = SchemaElement(basestring)
            self.release_date_timestamp         = SchemaElement(datetime)

            self.screenshots                    = SchemaList(ImageSchema())
            self.screenshots_source             = SchemaElement(basestring)
            self.screenshots_timestamp          = SchemaElement(datetime)

            self.authors                        = SchemaList(PersonEntityMini())
            self.authors_source                 = SchemaElement(basestring)
            self.authors_timestamp              = SchemaElement(datetime)
            
            self.publishers                     = SchemaList(BasicEntityMini())
            self.publishers_source              = SchemaElement(basestring)
            self.publishers_timestamp           = SchemaElement(datetime)

            self.supported_devices              = SchemaList(SchemaElement(basestring))
            self.supported_devices_source       = SchemaElement(basestring)
            self.supported_devices_timestamp    = SchemaElement(datetime)
            
            self.platform                       = SchemaElement(basestring)
            self.platform_source                = SchemaElement(basestring)
            self.platform_timestamp             = SchemaElement(datetime)
        
        @property 
        def subtitle(self):
            if self.isType('app'):
                suffix = ''
                if len(self.authors) > 0:
                    suffix = ' (%s)' % ', '.join(unicode(i['title']) for i in self.authors)
                
                return 'App%s' % suffix
            elif 'video_game' in self.types.value:
                suffix = ''
                if self.platform:
                    suffix = ' (%s)' % self.platform
                
                return 'Video Game%s' % suffix
            
            return self._genericSubtitle()
        
        @property 
        def category(self):
            return 'other'
        
        @property 
        def subcategory(self):
            if self.isType('app'):
                return 'app'
            elif 'video_game' in self.types.value:
                return 'video_game'
            
            return 'other'

    class EntitySuggested(Schema):
        def setSchema(self):
            self.coordinates                    = CoordinatesSchema()
            self.category                       = SchemaElement(basestring)
            self.subcategory                    = SchemaElement(basestring)
            self.limit                          = SchemaElement(int, default=10)
     

    # ############# #
    # Mini Entities #
    # ############# #

    class BasicEntityMini(BasicEntity):
        def setSchema(self):
            self.schema_version                 = SchemaElement(int, default=0)
            self.entity_id                      = SchemaElement(basestring)
            self.title                          = SchemaElement(basestring)
            self.kind                           = SchemaElement(basestring, default='other')
            self.types                          = SchemaList(SchemaElement(basestring))
            self.sources                        = EntitySourcesSchema()
            self.coordinates                    = CoordinatesSchema()
            self.images                         = SchemaList(ImageSchema())

    class PlaceEntityMini(BasicEntityMini):
        def setSchema(self):
            BasicEntityMini.setSchema(self)
            self.kind                           = SchemaElement(basestring, default='place')

    class PersonEntityMini(BasicEntityMini, PersonEntity):
        def setSchema(self):
            BasicEntityMini.setSchema(self)
            self.kind                           = SchemaElement(basestring, default='person')

    class MediaCollectionEntityMini(BasicEntityMini, MediaCollectionEntity):
        def setSchema(self):
            BasicEntityMini.setSchema(self)
            self.kind                           = SchemaElement(basestring, default='media_collection')

    class MediaItemEntityMini(BasicEntityMini, MediaItemEntity):
        def setSchema(self):
            BasicEntityMini.setSchema(self)
            self.kind                           = SchemaElement(basestring, default='media_item')
            self.length                         = SchemaElement(int)

    class SoftwareEntityMini(BasicEntityMini, SoftwareEntity):
        def setSchema(self):
            BasicEntityMini.setSchema(self)
            self.kind                           = SchemaElement(basestring, default='software')


    # #################### #
    # DEPRECATED: Entities #
    # #################### #

    class EntityPlace(Schema):
        def setSchema(self):
            self.entity_id          = SchemaElement(basestring, required=True)
            self.coordinates        = CoordinatesSchema(required=True)

    class EntitySearch(Schema):
        def setSchema(self):
            self.q                  = SchemaElement(basestring, required=True)
            self.coordinates        = CoordinatesSchema()
            self.category           = SchemaElement(basestring)
            self.subcategory        = SchemaElement(basestring)
            self.local              = SchemaElement(bool)
            self.page               = SchemaElement(int, default=0)

    class EntityNearby(Schema):
        def setSchema(self):
            self.coordinates        = CoordinatesSchema()
            self.category           = SchemaElement(basestring)
            self.subcategory        = SchemaElement(basestring)
            self.page               = SchemaElement(int, default=0)


    """
    class Entity(Schema):
        def setSchema(self):
            self.schema_version     = SchemaElement(int)

            self.entity_id          = SchemaElement(basestring)
            self.search_id          = SchemaElement(basestring)
            self.title              = SchemaElement(basestring, required=True)
            self.titlel             = SchemaElement(basestring)
            
            self.mangled_title              = SchemaElement(basestring)
            self.mangled_title_source       = SchemaElement(basestring)
            self.mangled_title_timestamp    = SchemaElement(datetime) 
            
            self.subtitle           = SchemaElement(basestring)
            self.subtitle_source    = SchemaElement(basestring)
            self.subtitle_timestamp = SchemaElement(datetime)
            
            self.type               = SchemaElement(basestring, required=True)
            self.category           = SchemaElement(basestring, derivedFrom='subcategory', derivedFn=self.set_category)
            self.subcategory        = SchemaElement(basestring, required=True)
            self.subcategory_source = SchemaElement(basestring)
            self.subcategory_timestamp = SchemaElement(datetime)
            # Not present in existing database
            self.locale             = SchemaElement(basestring)
            
            self.desc               = SchemaElement(basestring)
            self.desc_source        = SchemaElement(basestring)
            self.desc_timestamp     = SchemaElement(datetime)
            
            self.image              = SchemaElement(basestring)
            self.popularity         = SchemaElement(int)
            self.timestamp          = TimestampSchema()
            self.coordinates        = CoordinatesSchema()
            self.coordinates_source         = SchemaElement(basestring)
            self.coordinates_timestamp      = SchemaElement(datetime) 
            self.details            = EntityDetailsSchema()
            self.sources            = EntitySourcesSchema()
            self.stats              = StatsSchema()
        
        def exportSchema(self, schema):
            if schema.__class__.__name__ in ('EntityMini', 'EntityPlace'):
                from Entity import setFields
                setFields(self)
                schema.importData(self.value, overflow=True)
            else:
                raise NotImplementedError
            return schema
        
        def set_category(self, subcategory):
            from Entity import subcategories
            
            try:
                return subcategories[subcategory]
            except KeyError:
                # default to 'other' category
                return "other"

    class GenericSourceSchema(Schema):
        def setSchema(self):
            self.source             = SchemaElement(basestring)
            self.source_id          = SchemaElement(basestring)
            self.link               = SchemaElement(basestring)
            self.icon               = SchemaElement(basestring)

    class StatsSchema(Schema):
        def setSchema(self):
            self.simplified_title   = SchemaElement(basestring)
            self.titlev             = SchemaElement(float)
            self.subcatv            = SchemaElement(float)
            self.sourcev            = SchemaElement(float)
            self.qualityv           = SchemaElement(float)
            self.distancev          = SchemaElement(float)
            self.totalv             = SchemaElement(float)

    class EntityMini(Schema):
        def setSchema(self):
            self.entity_id          = SchemaElement(basestring, required=True)
            self.title              = SchemaElement(basestring)
            self.subtitle           = SchemaElement(basestring)
            self.type               = SchemaElement(basestring)
            self.category           = SchemaElement(basestring)
            self.subcategory        = SchemaElement(basestring)
            self.coordinates        = CoordinatesSchema()

    class EntityPlace(Schema):
        def setSchema(self):
            self.entity_id          = SchemaElement(basestring, required=True)
            self.coordinates        = CoordinatesSchema(required=True)

    class EntitySearch(Schema):
        def setSchema(self):
            self.q                  = SchemaElement(basestring, required=True)
            self.coordinates        = CoordinatesSchema()
            self.category           = SchemaElement(basestring)
            self.subcategory        = SchemaElement(basestring)
            self.local              = SchemaElement(bool)
            self.page               = SchemaElement(int, default=0)

    class EntityNearby(Schema):
        def setSchema(self):
            self.coordinates        = CoordinatesSchema()
            self.category           = SchemaElement(basestring)
            self.subcategory        = SchemaElement(basestring)
            self.page               = SchemaElement(int, default=0)

    class CoordinatesSchema(Schema):
        def setSchema(self):
            self.lat                = SchemaElement(float, required=True)
            self.lng                = SchemaElement(float, required=True)

    class EntityDetailsSchema(Schema):
        def setSchema(self):
            self.place              = PlaceSchema()
            self.contact            = ContactSchema()
            self.restaurant         = RestaurantSchema()
            # self.app                = AppSchema()
            self.book               = BookSchema()
            self.video              = VideoSchema()
            self.artist             = ArtistSchema()
            # self.song               = SongSchema()
            # self.album              = AlbumSchema()
            self.media              = MediaSchema()
            # self.product            = ProductSchema()

    class PlaceSchema(Schema):
        def setSchema(self):
            #
            # The new core address set
            #
            self.address_street     = SchemaElement(basestring)
            self.address_street_ext = SchemaElement(basestring)
            self.address_locality   = SchemaElement(basestring)
            self.address_region     = SchemaElement(basestring)
            self.address_postcode   = SchemaElement(basestring)
            self.address_country    = SchemaElement(basestring)
            self.address_source     = SchemaElement(basestring)
            self.address_timestamp  = SchemaElement(datetime)
            
            self.neighborhood               = SchemaElement(basestring)
            self.neighborhood_source        = SchemaElement(basestring)
            self.neighborhood_timestamp     = SchemaElement(datetime)
            
            self.hours              = TimesSchema()
            self.hours_source       = SchemaElement(basestring)
            self.hours_timestamp    = SchemaElement(datetime)
            
            self.address            = SchemaElement(basestring)
            self.address_components = SchemaList(AddressComponentSchema())
            self.types              = SchemaList(SchemaElement(basestring))
            self.vicinity           = SchemaElement(basestring)
            self.crossStreet        = SchemaElement(basestring)
            self.publicTransit      = SchemaElement(basestring)
            self.parking            = SchemaElement(basestring)
            self.parkingDetails     = SchemaElement(basestring)
            self.wheelchairAccess   = SchemaElement(basestring) 

    class AddressComponentSchema(Schema):
        def setSchema(self):
            self.long_name          = SchemaElement(basestring)
            self.short_name         = SchemaElement(basestring)
            self.types              = SchemaList(SchemaElement(basestring))

    class ContactSchema(Schema):
        def setSchema(self):
            self.phone              = SchemaElement(basestring)
            self.phone_source       = SchemaElement(basestring)
            self.phone_timestamp    = SchemaElement(datetime)

            self.site               = SchemaElement(basestring)
            self.site_source        = SchemaElement(basestring)
            self.site_timestamp     = SchemaElement(datetime)

            self.fax                = SchemaElement(basestring)
            self.email              = SchemaElement(basestring)
            self.hoursOfOperation   = SchemaElement(basestring)

    class RestaurantSchema(Schema):
        def setSchema(self):
            self.diningStyle        = SchemaElement(basestring)
            self.cuisine            = SchemaElement(basestring)
            self.cuisine_source     = SchemaElement(basestring)
            self.cuisine_timestamp  = SchemaElement(datetime)
            
            self.menu               = SchemaElement(bool)
            self.menu_source        = SchemaElement(basestring)
            self.menu_timestamp     = SchemaElement(datetime)
            
            self.price_range        = SchemaElement(int)
            self.price_range_source = SchemaElement(basestring)
            self.price_range_timestamp = SchemaElement(datetime)
            
            self.alcohol_flag       = SchemaElement(bool)
            self.alcohol_flag_source        = SchemaElement(basestring)
            self.alcohol_flag_timestamp     = SchemaElement(datetime)
            
            self.payment            = SchemaElement(basestring)
            self.dressCode          = SchemaElement(basestring)
            self.acceptsReservations        = SchemaElement(basestring)
            self.acceptsWalkins     = SchemaElement(basestring)
            self.offers             = SchemaElement(basestring)
            self.privatePartyFacilities     = SchemaElement(basestring)
            self.privatePartyContact        = SchemaElement(basestring)
            self.entertainment      = SchemaElement(basestring)
            self.specialEvents      = SchemaElement(basestring)
            self.catering           = SchemaElement(basestring)
            self.takeout            = SchemaElement(basestring)
            self.delivery           = SchemaElement(basestring)
            self.kosher             = SchemaElement(basestring)
            self.bar                = SchemaElement(basestring)
            self.alcohol            = SchemaElement(basestring)
            self.menuLink           = SchemaElement(basestring)
            self.chef               = SchemaElement(basestring)
            self.owner              = SchemaElement(basestring)
            self.reviewLinks        = SchemaElement(basestring)
            self.priceScale         = SchemaElement(basestring)


    class BookSchema(Schema):
        def setSchema(self):
            self.isbn               = SchemaElement(basestring)
            self.isbn_source        = SchemaElement(basestring)
            self.isbn_timestamp     = SchemaElement(datetime)

            self.author             = SchemaElement(basestring)
            self.author_source      = SchemaElement(basestring)
            self.author_timestamp   = SchemaElement(datetime)

            self.sku_number         = SchemaElement(basestring)
            self.sku_number_source  = SchemaElement(basestring)
            self.sku_number_timestamp = SchemaElement(datetime)
            
            self.publisher          = SchemaElement(basestring)
            self.publisher_source   = SchemaElement(basestring)
            self.publisher_timestamp= SchemaElement(datetime)

            self.publish_date       = SchemaElement(basestring)
            self.language           = SchemaElement(basestring)
            self.book_format        = SchemaElement(basestring)
            self.edition            = SchemaElement(basestring)

            self.num_pages          = SchemaElement(int)
            self.num_pages_source   = SchemaElement(basestring)
            self.num_pages_timestamp= SchemaElement(datetime)

    class VideoSchema(Schema):
        def setSchema(self):
            self.studio_name        = SchemaElement(basestring)
            self.studio_url         = SchemaElement(basestring)
            self.network_name       = SchemaElement(basestring)
            
            self.short_description  = SchemaElement(basestring)
            self.short_description_source = SchemaElement(basestring)
            self.short_description_timestamp = SchemaElement(datetime)

            self.long_description   = SchemaElement(basestring)
            self.episode_production_number  = SchemaElement(basestring)
            ### TODO: modify these based on crawler logic (only for custom entities currently)
            self.cast               = SchemaElement(basestring)
            self.cast_source        = SchemaElement(basestring)
            self.cast_timestamp     = SchemaElement(datetime)
            self.cast_list                  = SchemaList(CastEntrySchema())
            self.cast_list_source           = SchemaElement(basestring)
            self.cast_list_timestamp        = SchemaElement(datetime)
            
            self.director           = SchemaElement(basestring)
            self.director_source    = SchemaElement(basestring)
            self.director_timestamp = SchemaElement(datetime)

            self.in_theaters        = SchemaElement(bool)
            
            self.v_retail_price     = SchemaElement(basestring)
            self.v_currency_code    = SchemaElement(basestring)
            self.v_availability_date        = SchemaElement(basestring)
            self.v_sd_price         = SchemaElement(basestring)
            self.v_hq_price         = SchemaElement(basestring)
            self.v_lc_rental_price  = SchemaElement(basestring)
            self.v_sd_rental_price  = SchemaElement(basestring)
            self.v_hd_rental_price  = SchemaElement(basestring)
            
            self.imdb_id            = SchemaElement(basestring)
            self.imdb_source        = SchemaElement(basestring)
            self.imdb_timestamp     = SchemaElement(datetime)

    class CastEntrySchema(Schema):
        def setSchema(self):
            self.name       = SchemaElement(basestring)
            self.role       = SchemaElement(basestring)

    class ArtistSchema(Schema):
        def setSchema(self):
            self.artist_type        = SchemaElement(basestring)
            self.albums             = SchemaList(ArtistAlbumsSchema())
            self.albums_source      = SchemaElement(basestring)
            self.albums_timestamp   = SchemaElement(datetime)
            self.songs              = SchemaList(ArtistSongsSchema())
            self.songs_source       = SchemaElement(basestring)
            self.songs_timestamp    = SchemaElement(datetime)

    class ArtistAlbumsSchema(Schema):
        def setSchema(self):
            self.album_id           = SchemaElement(int)            # Deprecated
            self.rank               = SchemaElement(int)            # Deprecated
            self.genre_id           = SchemaElement(int)            # Deprecated
            self.album_name         = SchemaElement(basestring)
            self.album_mangled      = SchemaElement(basestring)
            self.source             = SchemaElement(basestring)
            self.id                 = SchemaElement(basestring)     # Rename to album_id?
            self.timestamp          = SchemaElement(datetime)
            self.entity_id          = SchemaElement(basestring)     # Move to sources?
            self.sources            = SchemaList(GenericSourceSchema())

    class ArtistSongsSchema(Schema):
        def setSchema(self):
            self.song_id            = SchemaElement(int)            # Deprecated
            self.song_name          = SchemaElement(basestring)
            self.song_mangled       = SchemaElement(basestring)
            self.source             = SchemaElement(basestring)
            self.id                 = SchemaElement(basestring)     # Rename to song_id?
            self.timestamp          = SchemaElement(datetime)
            self.entity_id          = SchemaElement(basestring)     # Move to sources?
            self.sources            = SchemaList(GenericSourceSchema())

    # class AlbumSchema(Schema):
    #     def setSchema(self):
    #         self.label_studio       = SchemaElement(basestring)
    #         self.is_compilation     = SchemaElement(bool)
    #         self.a_retail_price             = SchemaElement(basestring)
    #         self.a_hq_price                 = SchemaElement(basestring)
    #         self.a_currency_code            = SchemaElement(basestring)
    #         self.a_availability_date        = SchemaElement(basestring)
    #         self.track_count                = SchemaElement(int)
    #         self.tracks                     = SchemaList(SchemaElement(basestring))
    #         self.tracks_source              = SchemaElement(basestring)
    #         self.tracks_timestamp           = SchemaElement(datetime)

    # class ProductSchema(Schema):
    #     def setSchema(self):
    #         self.manufacturer               = SchemaElement(basestring)
    #         self.brand                      = SchemaElement(basestring)
    #         self.salesRank                  = SchemaElement(int)
    #         self.price                      = PriceSchema()

    # class PriceSchema(Schema):
    #     def setSchema(self):
    #         self.amount                     = SchemaElement(int)
    #         self.currency_code              = SchemaElement(basestring)
    #         self.formatted_price            = SchemaElement(basestring)

    class MediaSchema(Schema):
        def setSchema(self):
            self.release_date               = SchemaElement(datetime)
            self.release_date_source        = SchemaElement(basestring)
            self.release_date_timestamp     = SchemaElement(datetime)

            self.track_length               = SchemaElement(basestring)
            self.track_length_source        = SchemaElement(basestring)
            self.track_length_timestamp     = SchemaElement(datetime)

            self.title_version              = SchemaElement(basestring)     # Deprecated
            self.search_terms               = SchemaElement(basestring)     # Deprecated
            self.parental_advisory_id       = SchemaElement(basestring)     # Deprecated
            self.collection_display_name    = SchemaElement(basestring)     # Deprecated
            self.original_release_date      = SchemaElement(basestring)     # Deprecated
            self.itunes_release_date        = SchemaElement(basestring)     # Deprecated
            self.copyright                  = SchemaElement(basestring)     # Deprecated
            self.p_line                     = SchemaElement(basestring)     # Deprecated
            self.content_provider_name      = SchemaElement(basestring)     # Deprecated
            self.media_type_id              = SchemaElement(basestring)     # Deprecated
            self.artwork_url                = SchemaElement(basestring)     # Deprecated

            self.mpaa_rating                = SchemaElement(basestring)
            self.mpaa_rating_source         = SchemaElement(basestring)
            self.mpaa_rating_timestamp      = SchemaElement(datetime)

            self.artist_display_name        = SchemaElement(basestring)
            self.artist_display_name_source = SchemaElement(basestring)
            self.artist_display_name_timestamp = SchemaElement(datetime)

            self.album_name                 = SchemaElement(basestring)
            self.album_name_source          = SchemaElement(basestring)
            self.album_name_timestamp       = SchemaElement(datetime)

            self.genre                      = SchemaElement(basestring)
            self.genre_source               = SchemaElement(basestring)
            self.genre_timestamp            = SchemaElement(datetime)

            self.artist_id                  = SchemaElement(basestring)

            self.screenshots                = SchemaList(SchemaElement(basestring))
            self.screenshots_source         = SchemaElement(basestring)                     # TODO: Populate
            self.screenshots_timestamp      = SchemaElement(datetime)                       # TODO: Populate

            self.track_list                 = SchemaList(MediaItemSchema())                 # TODO: Populate
            self.track_list_source          = SchemaElement(basestring)                     # TODO: Populate
            self.track_list_timestamp       = SchemaElement(basestring)                     # TODO: Populate

            self.album_list                 = SchemaList(MediaItemSchema())                 # TODO: Populate
            self.album_list_source          = SchemaElement(basestring)                     # TODO: Populate
            self.album_list_timestamp       = SchemaElement(basestring)                     # TODO: Populate

    class MediaItemSchema(Schema):
        def setSchema(self):
            self.title              = SchemaElement(basestring)
            self.mangled_title      = SchemaElement(basestring)
            self.entity_id          = SchemaElement(basestring)     # Move to sources?
            self.sources            = SchemaList(GenericSourceSchema())

    class SongSchema(Schema):
        def setSchema(self):
            self.preview_url        = SchemaElement(basestring)
            self.preview_length     = SchemaElement(basestring)
            
            ### TODO: modify this based on crawler logic (only for custom entities currently)
            self.album_name         = SchemaElement(basestring) 
            self.album_name_source  = SchemaElement(basestring)
            self.album_name_timestamp = SchemaElement(datetime)
            self.song_album_id      = SchemaElement(basestring) 

    class TMDBSchema(Schema):
        def setSchema(self):
            self.tmdb_id            = SchemaElement(basestring)
            self.tmdb_source        = SchemaElement(basestring)
            self.tmdb_timestamp     = SchemaElement(datetime)

    class EntitySourcesSchema(Schema):
        def setSchema(self):
            #new resolve fields
            self.singleplatform         = SinglePlatformSchema()
            self.factual                = FactualSchema()
            self.tmdb                   = TMDBSchema()

            self.stamped_id             = SchemaElement(basestring)
            self.stamped_url            = SchemaElement(basestring)
            self.stamped_timestamp      = SchemaElement(datetime)
            self.stamped_source         = SchemaElement(basestring)

            self.spotify_id             = SchemaElement(basestring)
            self.spotify_url            = SchemaElement(basestring)
            self.spotify_timestamp      = SchemaElement(datetime)
            self.spotify_source         = SchemaElement(basestring)

            self.itunes_id              = SchemaElement(basestring)
            self.itunes_url             = SchemaElement(basestring)
            self.itunes_timestamp       = SchemaElement(datetime)
            self.itunes_source          = SchemaElement(basestring)

            self.rdio_id                = SchemaElement(basestring)
            self.rdio_url               = SchemaElement(basestring)
            self.rdio_timestamp         = SchemaElement(datetime)
            self.rdio_source            = SchemaElement(basestring)
            
            self.amazon_id              = SchemaElement(basestring)
            self.amazon_url             = SchemaElement(basestring)
            self.amazon_source          = SchemaElement(basestring)
            self.amazon_timestamp       = SchemaElement(datetime)
            
            self.opentable_id           = SchemaElement(basestring)
            self.opentable_url          = SchemaElement(basestring)
            self.opentable_source       = SchemaElement(basestring)
            self.opentable_timestamp    = SchemaElement(datetime)

            self.opentable_nickname         = SchemaElement(basestring)
            self.opentable_nickname_source  = SchemaElement(basestring)
            self.opentable_nickname_timestamp= SchemaElement(datetime)
            
            self.fandango_id            = SchemaElement(basestring)
            self.fandango_url           = SchemaElement(basestring)
            self.fandango_source        = SchemaElement(basestring)
            self.fandango_timestamp     = SchemaElement(datetime)

            
            self.googlePlaces       = GooglePlacesSchema()
            self.googleLocal        = GoogleLocalSchema()
            self.openTable          = OpenTableSchema()
            self.apple              = AppleSchema()
            self.zagat              = ZagatSchema()
            self.yelp               = YelpSchema()
            self.urbanspoon         = UrbanSpoonSchema()
            self.nymag              = NYMagSchema()
            self.nytimes            = NYTimesSchema()
            self.sfmag              = SFMagSchema()
            self.latimes            = LATimesSchema()
            self.bostonmag          = BostonMagSchema()
            self.fandango           = FandangoSchema()
            self.chicagomag         = ChicagoMagSchema()
            self.phillymag          = PhillyMagSchema()
            self.washmag            = WashMagSchema()
            self.netflix            = NetflixSchema()
            self.thetvdb            = TheTVDBSchema()
            self.amazon             = AmazonSchema()
            self.awardAnnals        = AwardAnnalsSchema()
            self.userGenerated      = UserGeneratedSchema()
            self.barnesAndNoble     = BarnesAndNobleSchema()
            self.sfweekly           = SFWeeklySchema()
            self.seattletimes       = SeattleTimesSchema()
            self.sfgate             = SFGateSchema()
            self.timeout_chi        = TimeOutChiSchema()
            self.timeout_la         = TimeOutLASchema()
            self.timeout_lv         = TimeOutLVSchema()
            self.timeout_mia        = TimeOutMIASchema()
            self.timeout_sf         = TimeOutSFSchema()

    class GooglePlacesSchema(Schema):
        def setSchema(self):
            self.gid                = SchemaElement(basestring)
            self.gurl               = SchemaElement(basestring)
            self.reference          = SchemaElement(basestring)
            self.googleplaces_id         = SchemaElement(basestring)
            self.googleplaces_timestamp  = SchemaElement(datetime)
            self.googleplaces_source     = SchemaElement(basestring)

    class TMDBSchema(Schema):
        def setSchema(self):
            self.tmdb_id            = SchemaElement(basestring)
            self.tmdb_url           = SchemaElement(basestring)
            self.tmdb_source        = SchemaElement(basestring)
            self.tmdb_timestamp     = SchemaElement(datetime)

    class GoogleLocalSchema(Schema):
        def setSchema(self):
            pass

    class OpenTableSchema(Schema):
        def setSchema(self):
            self.rid                = SchemaElement(basestring)
            self.reserveURL         = SchemaElement(basestring)
            self.countryID          = SchemaElement(basestring)
            self.metroName          = SchemaElement(basestring)
            self.neighborhoodName   = SchemaElement(basestring)

    class FactualSchema(Schema):
        def setSchema(self):
            self.faid               = SchemaElement(basestring)
            self.table              = SchemaElement(basestring)
            self.factual_id         = SchemaElement(basestring)
            self.factual_url        = SchemaElement(basestring)
            self.factual_timestamp  = SchemaElement(datetime)
            self.factual_source     = SchemaElement(basestring)
            self.factual_crosswalk  = SchemaElement(datetime)

    class SinglePlatformSchema(Schema):
        def setSchema(self):
            self.singleplatform_id  = SchemaElement(basestring)
            self.singleplatform_url = SchemaElement(basestring)
            self.singleplatform_timestamp  = SchemaElement(datetime)
            self.singleplatform_source = SchemaElement(basestring)

    class AppleSchema(Schema):
        def setSchema(self):
            self.aid                = SchemaElement(basestring)
            self.export_date        = SchemaElement(basestring)
            self.is_actual_artist   = SchemaElement(bool)
            self.view_url           = SchemaElement(basestring)
            self.a_popular          = SchemaElement(bool)
            self.match              = AppleMatchSchema()

    class AppleMatchSchema(Schema):
        def setSchema(self):
            self.upc                = SchemaElement(basestring)
            self.isrc               = SchemaElement(basestring)
            self.grid               = SchemaElement(basestring)
            self.amg_video_id       = SchemaElement(basestring)
            self.amg_track_id       = SchemaElement(basestring)
            self.isan               = SchemaElement(basestring)

    class ZagatSchema(Schema):
        def setSchema(self):
            self.zurl               = SchemaElement(basestring)

    class UrbanSpoonSchema(Schema):
        def setSchema(self):
            self.uurl               = SchemaElement(basestring)

    class NYMagSchema(Schema):
        def setSchema(self):
            pass

    class NYTimesSchema(Schema):
        def setSchema(self):
            pass

    class YelpSchema(Schema):
        def setSchema(self):
            self.yurl               = SchemaElement(basestring)
            self.yrating            = SchemaElement(float)
            self.yreviews           = SchemaElement(int)

    class SFMagSchema(Schema):
        def setSchema(self):
            pass

    class SFWeeklySchema(Schema):
        def setSchema(self):
            pass

    class SeattleTimesSchema(Schema):
        def setSchema(self):
            pass

    class LATimesSchema(Schema):
        def setSchema(self):
            pass

    class BostonMagSchema(Schema):
        def setSchema(self):
            pass

    class AwardAnnalsSchema(Schema):
        def setSchema(self):
            pass

    class FandangoSchema(Schema):
        def setSchema(self):
            self.fid                = SchemaElement(basestring)
            self.f_url              = SchemaElement(basestring)

    class AmazonSchema(Schema):
        def setSchema(self):
            self.asin               = SchemaElement(basestring)
            self.amazon_link        = SchemaElement(basestring)
            self.amazon_link_source = SchemaElement(basestring)
            self.amazon_link_timestamp = SchemaElement(datetime)
            self.amazon_underlying  = SchemaElement(basestring)
            self.amazon_underlying_source = SchemaElement(basestring)
            self.amazon_underlying_timestamp = SchemaElement(datetime)

    class ChicagoMagSchema(Schema):
        def setSchema(self):
            pass

    class PhillyMagSchema(Schema):
        def setSchema(self):
            pass

    class TimeOutChiSchema(Schema):
        def setSchema(self):
            pass

    class TimeOutLASchema(Schema):
        def setSchema(self):
            pass

    class TimeOutLVSchema(Schema):
        def setSchema(self):
            pass

    class TimeOutMIASchema(Schema):
        def setSchema(self):
            pass

    class TimeOutSFSchema(Schema):
        def setSchema(self):
            pass

    class SFGateSchema(Schema):
        def setSchema(self):
            pass

    class WashMagSchema(Schema):
        def setSchema(self):
            pass

    class TheTVDBSchema(Schema):
        def setSchema(self):
            self.thetvdb_id         = SchemaElement(basestring)
            self.num_seasons        = SchemaElement(int)
            self.earliest_air_date  = SchemaElement(datetime)
            self.latest_air_date    = SchemaElement(datetime)
            self.air_time           = SchemaElement(basestring)

    class NetflixSchema(Schema):
        def setSchema(self):
            self.nid                = SchemaElement(int)
            self.nrating            = SchemaElement(float)
            self.ngenres            = SchemaList(SchemaElement(basestring))
            self.nurl               = SchemaElement(basestring)
            self.images             = NetflixImageSchema()
            self.images_source      = SchemaElement(basestring)
            self.images_timestamp   = SchemaElement(datetime)

    class NetflixImageSchema(Schema):
        def setSchema(self):
            self.tiny               = SchemaElement(basestring)
            self.small              = SchemaElement(basestring)
            self.large              = SchemaElement(basestring)
            self.hd                 = SchemaElement(basestring)

    class UserGeneratedSchema(Schema):
        def setSchema(self):
            # TODO (tfischer) adding user_id in temporarily for koopa s.t. entities will 
            # validate for search, and removing required=True from generated_by for the 
            # same reason; this can be switched back after we migrate to boo.
            self.generated_by       = SchemaElement(basestring)
            self.user_id            = SchemaElement(basestring)

    class BarnesAndNobleSchema(Schema):
        def setSchema(self):
            self.bid                = SchemaElement(int)
    """

