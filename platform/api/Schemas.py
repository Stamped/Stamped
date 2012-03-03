#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import copy
from datetime import datetime
from schema import *

# #### #
# Auth #
# #### #

class RefreshToken(Schema):
    def setSchema(self):
        self.token_id           = SchemaElement(basestring)
        self.client_id          = SchemaElement(basestring)
        self.user_id            = SchemaElement(basestring)
        self.access_tokens      = SchemaList(SchemaElement(basestring))
        self.timestamp          = TimestampSchema()

class AccessToken(Schema):
    def setSchema(self):
        self.token_id           = SchemaElement(basestring)
        self.client_id          = SchemaElement(basestring)
        self.refresh_token      = SchemaElement(basestring)
        self.user_id            = SchemaElement(basestring)
        self.expires            = SchemaElement(datetime)
        self.timestamp          = TimestampSchema()

class PasswordResetToken(Schema):
    def setSchema(self):
        self.token_id           = SchemaElement(basestring)
        self.user_id            = SchemaElement(basestring)
        self.expires            = SchemaElement(datetime)
        self.timestamp          = TimestampSchema()

class SettingsEmailAlertToken(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring)
        self.token_id           = SchemaElement(basestring)
        self.timestamp          = TimestampSchema()

# ####### #
# Account #
# ####### #

class Account(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring)
        
        # NOTE: account.name fails with a schema problem (always returning None), 
        # but account['name'] works as expected. not sure if 'name' is possibly 
        # being handled specially by python, but accessing it currently does *not* 
        # work properly unless you use the attribute indexing syntax.
        self.name               = SchemaElement(basestring, required=True)
        
        self.name_lower         = SchemaElement(basestring)
        self.email              = SchemaElement(basestring, required=True)
        self.password           = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.screen_name_lower  = SchemaElement(basestring)
        self.color_primary      = SchemaElement(basestring)
        self.color_secondary    = SchemaElement(basestring)
        self.phone              = SchemaElement(int)
        self.bio                = SchemaElement(basestring)
        self.website            = SchemaElement(basestring)
        self.location           = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool, required=True, default=False)
        self.locale             = LocaleSchema()
        self.linked_accounts    = LinkedAccounts()
        self.devices            = DevicesSchema()
        self.flags              = FlagsSchema()
        self.stats              = UserStatsSchema()
        self.timestamp          = TimestampSchema()
        self.alerts             = AccountAlerts()

class LinkedAccounts(Schema):
    def setSchema(self):
        self.itunes             = SchemaElement(basestring)
        self.twitter            = TwitterAccountSchema()
        self.facebook           = FacebookAccountSchema()

class TwitterAccountSchema(Schema):
    def setSchema(self):
        self.twitter_id             = SchemaElement(basestring)
        self.twitter_screen_name    = SchemaElement(basestring)
        self.twitter_alerts_sent    = SchemaElement(bool)

class TwitterAuthSchema(Schema):
    def setSchema(self):
        self.twitter_key            = SchemaElement(basestring)
        self.twitter_secret         = SchemaElement(basestring)

class FacebookAccountSchema(Schema):
    def setSchema(self):
        self.facebook_id            = SchemaElement(basestring)
        self.facebook_name          = SchemaElement(basestring)
        self.facebook_screen_name   = SchemaElement(basestring)
        self.facebook_alerts_sent   = SchemaElement(bool)

class FacebookAuthSchema(Schema):
    def setSchema(self):
        self.facebook_token         = SchemaElement(basestring)

class DevicesSchema(Schema):
    def setSchema(self):
        self.ios_device_tokens  = SchemaList(SchemaElement(basestring))

class LocaleSchema(Schema):
    def setSchema(self):
        self.language           = SchemaElement(basestring, default='en')
        self.time_zone          = SchemaElement(basestring)

class AccountAlerts(Schema):
    def setSchema(self):
        self.ios_alert_credit       = SchemaElement(bool)
        self.ios_alert_like         = SchemaElement(bool)
        self.ios_alert_fav          = SchemaElement(bool)
        self.ios_alert_mention      = SchemaElement(bool)
        self.ios_alert_comment      = SchemaElement(bool)
        self.ios_alert_reply        = SchemaElement(bool)
        self.ios_alert_follow       = SchemaElement(bool)
        self.email_alert_credit     = SchemaElement(bool)
        self.email_alert_like       = SchemaElement(bool)
        self.email_alert_fav        = SchemaElement(bool)
        self.email_alert_mention    = SchemaElement(bool)
        self.email_alert_comment    = SchemaElement(bool)
        self.email_alert_reply      = SchemaElement(bool)
        self.email_alert_follow     = SchemaElement(bool)


# ##### #
# Users #
# ##### #

class User(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring)
        self.name               = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.color_primary      = SchemaElement(basestring)
        self.color_secondary    = SchemaElement(basestring)
        self.bio                = SchemaElement(basestring)
        self.website            = SchemaElement(basestring)
        self.location           = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool, required=True)
        self.flags              = FlagsSchema()
        self.stats              = UserStatsSchema()
        self.timestamp          = TimestampSchema(required=True)
        self.identifier         = SchemaElement(basestring)
    
    def exportSchema(self, schema):
        if schema.__class__.__name__ in ('UserMini', 'UserTiny'):
            schema.importData(self.value, overflow=True)
        else:
            raise NotImplementedError
        return schema

class UserMini(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring)
        self.color_primary      = SchemaElement(basestring)
        self.color_secondary    = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool)
        self.timestamp          = TimestampSchema()

class UserTiny(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring)
        self.screen_name        = SchemaElement(basestring)

class SuggestedUserRequest(Schema):
    def setSchema(self):
        # paging
        self.limit              = SchemaElement(int, default=10)
        self.offset             = SchemaElement(int, default=0)
        
        self.personalized       = SchemaElement(bool, default=False)
        self.coordinates        = CoordinatesSchema()
        
        # third party keys for optionally augmenting friend suggestions with 
        # knowledge from other social networks
        self.twitter_key        = SchemaElement(basestring)
        self.twitter_secret     = SchemaElement(basestring)
        
        self.facebook_token     = SchemaElement(basestring)

class Invite(Schema):
    def setSchema(self):
        self.invite_id          = SchemaElement(basestring)
        self.recipient_email    = SchemaElement(basestring, required=True)
        self.user_id            = SchemaElement(basestring)
        self.created            = SchemaElement(datetime)


# ##### #
# Flags #
# ##### #

class FlagsSchema(Schema):
    def setSchema(self):
        self.flagged            = SchemaElement(bool)
        self.locked             = SchemaElement(bool)


# ##### #
# Stats #
# ##### #

class UserStatsSchema(Schema):
    def setSchema(self):
        self.num_stamps         = SchemaElement(int)
        self.num_stamps_left    = SchemaElement(int)
        self.num_stamps_total   = SchemaElement(int)
        self.num_friends        = SchemaElement(int)
        self.num_followers      = SchemaElement(int)
        self.num_faves          = SchemaElement(int)
        self.num_credits        = SchemaElement(int)
        self.num_credits_given  = SchemaElement(int)
        self.num_likes          = SchemaElement(int)
        self.num_likes_given    = SchemaElement(int)
        self.num_unread_news    = SchemaElement(int)

class StampStatsSchema(Schema):
    def setSchema(self):
        self.num_comments       = SchemaElement(int)
        self.num_todos          = SchemaElement(int)
        self.num_credit         = SchemaElement(int)
        self.num_likes          = SchemaElement(int)
        self.like_threshold_hit = SchemaElement(bool)
        self.stamp_num          = SchemaElement(int)


# ########## #
# Timestamps #
# ########## #

class TimestampSchema(Schema):
    def setSchema(self):
        self.created            = SchemaElement(datetime, required=True)
        self.modified           = SchemaElement(datetime)
        self.image_cache        = SchemaElement(datetime)


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
        self.entity             = EntityMini(required=True)
        self.stamp              = Stamp()
        self.timestamp          = TimestampSchema()
        self.complete           = SchemaElement(bool)


# ###### #
# Stamps #
# ###### #

class Stamp(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring)
        self.entity             = EntityMini(required=True)
        self.user               = UserMini(required=True)
        self.blurb              = SchemaElement(basestring)
        self.mentions           = SchemaList(MentionSchema())
        self.credit             = SchemaList(CreditSchema())
        self.comment_preview    = SchemaList(Comment())
        self.image_dimensions   = SchemaElement(basestring)
        self.timestamp          = TimestampSchema()
        self.flags              = FlagsSchema()
        self.stats              = StampStatsSchema()
        self.via                = SchemaElement(basestring)
        self.attributes         = StampAttributesSchema()

class MentionSchema(Schema):
    def setSchema(self):
        self.screen_name        = SchemaElement(basestring, required=True)
        self.user_id            = SchemaElement(basestring)
        self.indices            = SchemaList(SchemaElement(int))

class CreditSchema(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.stamp_id           = SchemaElement(basestring)
        ### TEMP?
        self.color_primary      = SchemaElement(basestring)
        self.color_secondary    = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool)

class StampAttributesSchema(Schema):
    def setSchema(self):
        self.is_liked           = SchemaElement(bool)
        self.is_fav             = SchemaElement(bool)

class DeletedStamp(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring)
        self.timestamp          = ModifiedTimestampSchema()
        self.deleted            = SchemaElement(bool)

class ModifiedTimestampSchema(Schema):
    def setSchema(self):
        self.modified           = SchemaElement(datetime)


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
        self.mentions           = SchemaList(MentionSchema())
        self.timestamp          = TimestampSchema()


# ######## #
# Activity #
# ######## #

class Activity(Schema):
    def setSchema(self):
        # Metadata
        self.activity_id        = SchemaElement(basestring)
        self.recipient_id       = SchemaElement(basestring)
        self.genre              = SchemaElement(basestring, required=True)
        self.user               = UserMini()
        self.timestamp          = TimestampSchema()
        self.benefit            = SchemaElement(int)

        # Image
        self.image              = SchemaElement(basestring)
        self.icon               = SchemaElement(basestring)

        # Text
        self.subject            = SchemaElement(basestring)
        self.subject_objects    = SchemaList(ActivityObjectSchema())
        self.blurb              = SchemaElement(basestring)
        self.blurb_format       = ActivityFormatSchema()
        self.blurb_objects      = SchemaList(ActivityObjectSchema())

        # Links
        self.link               = ActivityLink()

class ActivityLink(Schema):
    def setSchema(self):
        self.linked_user        = UserMini()
        self.linked_user_id     = SchemaElement(basestring)
        self.linked_stamp       = Stamp()
        self.linked_stamp_id    = SchemaElement(basestring)
        self.linked_entity      = Entity()
        self.linked_entity_id   = SchemaElement(basestring)
        self.linked_comment     = Comment()
        self.linked_comment_id  = SchemaElement(basestring)
        self.linked_url         = LinkedURL()

class ActivityObjectSchema(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring)
        self.stamp_id           = SchemaElement(basestring)
        self.entity_id          = SchemaElement(basestring)
        self.indices            = SchemaList(SchemaElement(int))

class ActivityFormatSchema(Schema):
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

class LinkedURL(Schema):
    def setSchema(self):
        self.url                = SchemaElement(basestring, required=True)
        self.chrome             = SchemaElement(bool)


# ########## #
# ClientLogs #
# ########## #

class ClientLogsEntry(Schema):
    def setSchema(self):
        self.entry_id           = SchemaElement(basestring)
        self.created            = SchemaElement(datetime)
        self.user_id            = SchemaElement(basestring)
        self.key                = SchemaElement(basestring, required=True)
        self.value              = SchemaElement(basestring)
        
        # optional ids
        self.stamp_id           = SchemaElement(basestring)
        self.entity_id          = SchemaElement(basestring)
        self.favorite_id        = SchemaElement(basestring)
        self.comment_id         = SchemaElement(basestring)
        self.activity_id        = SchemaElement(basestring)


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

class ViewportSchema(Schema):
    def setSchema(self):
        self.upperLeft          = CoordinatesSchema()
        self.lowerRight         = CoordinatesSchema()


# ######## #
# Entities #
# ######## #

class Entity(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring)
        self.search_id          = SchemaElement(basestring)
        self.title              = SchemaElement(basestring, required=True)
        self.titlel             = SchemaElement(basestring)
        self.mangled_title              = SchemaElement(basestring)
        self.mangled_title_source       = SchemaElement(basestring)
        self.mangled_title_timestamp    = SchemaElement(datetime) 
        #self.titles             = SchemaList(SchemaElement(basestring))
        self.subtitle           = SchemaElement(basestring)
        self.subtitle_source    = SchemaElement(basestring)
        self.subtitle_timestamp = SchemaElement(datetime)

        self.category           = SchemaElement(basestring, derivedFrom='subcategory', derivedFn=self.set_category)
        self.subcategory        = SchemaElement(basestring, required=True)
        # Not present in existing database
        self.locale             = SchemaElement(basestring)
        
        self.desc               = SchemaElement(basestring)
        self.desc_source        = SchemaElement(basestring)
        self.desc_timestamp     = SchemaElement(datetime)

        self.image              = SchemaElement(basestring)
        self.popularity         = SchemaElement(int)
        self.timestamp          = TimestampSchema()
        self.coordinates        = CoordinatesSchema()
        self.details            = EntityDetailsSchema()
        self.sources            = EntitySourcesSchema()
        self.stats              = StatsSchema()
        self.successor          = SchemaElement(basestring)
        self.successor_source   = SchemaElement(basestring)
        self.successor_timestamp= SchemaElement(datetime)
    
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
        self.app                = AppSchema()
        self.book               = BookSchema()
        self.video              = VideoSchema()
        self.artist             = ArtistSchema()
        self.song               = SongSchema()
        self.album              = AlbumSchema()
        self.media              = MediaSchema()
        self.product            = ProductSchema()

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

        self.menu_source        = SchemaElement(basestring)
        self.menu_timestamp     = SchemaElement(datetime)

        self.price_range        = SchemaElement(int)
        self.price_range_source = SchemaElement(basestring)
        self.price_range_timestamp = SchemaElement(datetime)

        self.alcohol_flag       = SchemaElement(bool)
        self.alcohol_flag_source        = SchemaElement(basestring)
        self.alcohol_flag_timestamp     = SchemaElement(datetime)


        #self.price              = SchemaElement(basestring)
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

class AppSchema(Schema):
    def setSchema(self):
        
        pass
        #self.developer          = SchemaElement(basestring)
        #self.developerURL       = SchemaElement(basestring)
        #self.developerSupportURL= SchemaElement(basestring)
        #self.publisher          = SchemaElement(basestring)
        #self.releaseDate        = SchemaElement(basestring)
        #self.appCategory        = SchemaElement(basestring)
        #self.language           = SchemaElement(basestring)
        #self.rating             = SchemaElement(basestring)
        #self.popularity         = SchemaElement(basestring)
        #self.parentalRating     = SchemaElement(basestring)
        #self.platform           = SchemaElement(basestring)
        #self.requirements       = SchemaElement(basestring)
        #self.size               = SchemaElement(basestring)
        #self.version            = SchemaElement(basestring)
        #self.downloadURL        = SchemaElement(basestring)
        #self.thumbnailURL       = SchemaElement(basestring)
        #self.screenshotURL      = SchemaElement(basestring)
        #self.videoURL           = SchemaElement(basestring)

class BookSchema(Schema):
    def setSchema(self):
        self.isbn               = SchemaElement(basestring)
        self.author             = SchemaElement(basestring)
        self.sku_number         = SchemaElement(basestring)
        self.publisher          = SchemaElement(basestring)
        self.publish_date       = SchemaElement(basestring)
        self.language           = SchemaElement(basestring)
        self.book_format        = SchemaElement(basestring)
        self.edition            = SchemaElement(basestring)
        self.num_pages          = SchemaElement(int)

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

class ArtistAlbumsSchema(Schema):
    def setSchema(self):
        self.album_id           = SchemaElement(int)
        self.rank               = SchemaElement(int)
        self.genre_id           = SchemaElement(int)
        self.album_name         = SchemaElement(basestring)
        self.album_mangled      = SchemaElement(basestring)
        self.source             = SchemaElement(basestring)
        self.id                 = SchemaElement(basestring)
        self.timestamp          = SchemaElement(datetime)

class ArtistSongsSchema(Schema):
    def setSchema(self):
        self.song_id            = SchemaElement(int)
        self.song_name          = SchemaElement(basestring)
        self.song_mangled       = SchemaElement(basestring)
        self.source             = SchemaElement(basestring)
        self.id                 = SchemaElement(basestring)
        self.timestamp          = SchemaElement(datetime)

class SongSchema(Schema):
    def setSchema(self):
        self.preview_url        = SchemaElement(basestring)
        self.preview_length     = SchemaElement(basestring)
        
        ### TODO: modify this based on crawler logic (only for custom entities currently)
        self.album_name         = SchemaElement(basestring) 
        self.album_name_source  = SchemaElement(basestring)
        self.album_name_timestamp = SchemaElement(datetime)
        self.song_album_id      = SchemaElement(basestring) 

class AlbumSchema(Schema):
    def setSchema(self):
        self.label_studio       = SchemaElement(basestring)
        self.is_compilation     = SchemaElement(bool)
        
        self.a_retail_price             = SchemaElement(basestring)
        self.a_hq_price                 = SchemaElement(basestring)
        self.a_currency_code            = SchemaElement(basestring)
        self.a_availability_date        = SchemaElement(basestring)
        
        self.track_count                = SchemaElement(int)

        self.tracks                     = SchemaList(SchemaElement(basestring))
        self.tracks_source              = SchemaElement(basestring)
        self.tracks_timestamp           = SchemaElement(datetime)

class ProductSchema(Schema):
    def setSchema(self):
        self.manufacturer               = SchemaElement(basestring)
        self.brand                      = SchemaElement(basestring)
        self.salesRank                  = SchemaElement(int)
        self.price                      = PriceSchema()

class PriceSchema(Schema):
    def setSchema(self):
        self.amount                     = SchemaElement(int)
        self.currency_code              = SchemaElement(basestring)
        self.formatted_price            = SchemaElement(basestring)

class MediaSchema(Schema):
    def setSchema(self):
        self.release_date               = SchemaElement(datetime)
        self.release_date_source        = SchemaElement(basestring)
        self.release_date_timestamp     = SchemaElement(datetime)
        self.track_length               = SchemaElement(basestring)
        self.track_length_source        = SchemaElement(basestring)
        self.track_length_timestamp     = SchemaElement(datetime)

        self.title_version              = SchemaElement(basestring)
        self.search_terms               = SchemaElement(basestring)
        self.parental_advisory_id       = SchemaElement(basestring)
        self.collection_display_name    = SchemaElement(basestring)
        self.original_release_date      = SchemaElement(basestring)
        self.itunes_release_date        = SchemaElement(basestring)
        self.copyright                  = SchemaElement(basestring)
        self.p_line                     = SchemaElement(basestring)
        self.content_provider_name      = SchemaElement(basestring)
        self.media_type_id              = SchemaElement(basestring)
        self.artwork_url                = SchemaElement(basestring)

        self.mpaa_rating                = SchemaElement(basestring)
        self.mpaa_rating_source         = SchemaElement(basestring)
        self.mpaa_rating_timestamp      = SchemaElement(datetime)

        self.artist_display_name        = SchemaElement(basestring)
        self.artist_display_name_source = SchemaElement(basestring)
        self.artist_display_name_timestamp = SchemaElement(datetime)

        self.genre                      = SchemaElement(basestring)
        self.genre_source               = SchemaElement(basestring)
        self.genre_timestamp            = SchemaElement(datetime)

        self.artist_id                  = SchemaElement(basestring)
        self.screenshots                = SchemaList(SchemaElement(basestring))

class TMDBSchema(Schema):
    def setSchema(self):
        self.tmdb_id            = SchemaElement(basestring)
        self.tmdb_source        = SchemaElement(basestring)
        self.tmdb_timestamp     = SchemaElement(datetime)

class EntitySourcesSchema(Schema):
    def setSchema(self):
        #new resolve fields
        self.singleplatform     = SinglePlatformSchema()
        self.factual            = FactualSchema()
        self.tmdb               = TMDBSchema()

        self.spotify_id         = SchemaElement(basestring)
        self.spotify_timestamp  = SchemaElement(datetime)
        self.spotify_source     = SchemaElement(basestring)

        self.itunes_id          = SchemaElement(basestring)
        self.itunes_timestamp   = SchemaElement(datetime)
        self.itunes_source      = SchemaElement(basestring)

        self.rdio_id            = SchemaElement(basestring)
        self.rdio_timestamp     = SchemaElement(datetime)
        self.rdio_source        = SchemaElement(basestring)
        
        self.amazon_id          = SchemaElement(basestring)
        self.amazon_source      = SchemaElement(basestring)
        self.amazon_timestamp   = SchemaElement(datetime)
        
        # TODO: remove these three lines -- temporary workaround!
        # (and the TMDBSchema and RdioSchema above)
        self.tmdb               = TMDBSchema()
        self.factual            = FactualSchema()
        # TODO: remove these three lines -- temporary workaround!
        # (and the TMDBSchema and RdioSchema above)
        
        
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
        self.factual_timestamp  = SchemaElement(datetime)
        self.factual_source     = SchemaElement(basestring)
        self.factual_crosswalk  = SchemaElement(datetime)

class SinglePlatformSchema(Schema):
    def setSchema(self):
        self.singleplatform_id  = SchemaElement(basestring)
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

class MenuSchema(Schema):
    def setSchema(self):
        self.entity_id = SchemaElement(basestring)
        self.source = SchemaElement(basestring)
        self.source_id = SchemaElement(basestring)
        self.source_info = SchemaElement(basestring)
        self.disclaimer = SchemaElement(basestring)
        self.attribution_image = SchemaElement(basestring)
        self.attribution_image_link = SchemaElement(basestring)
        self.timestamp = SchemaElement(datetime)
        self.quality = SchemaElement(float)
        self.menus = SchemaList(SubmenuSchema())

class SubmenuSchema(Schema):
    def setSchema(self):
        self.title = SchemaElement(basestring)
        self.times = TimesSchema()
        self.footnote = SchemaElement(basestring)
        self.desc = SchemaElement(basestring)
        self.short_desc = SchemaElement(basestring)
        self.sections = SchemaList(MenuSectionSchema())

class MenuSectionSchema(Schema):
    def setSchema(self):
        self.title = SchemaElement(basestring)
        self.desc = SchemaElement(basestring)
        self.short_desc = SchemaElement(basestring)
        self.items = SchemaList(MenuItemSchema())

class MenuItemSchema(Schema):
    def setSchema(self):
        self.title = SchemaElement(basestring)
        self.desc = SchemaElement(basestring)
        self.categories = SchemaList(SchemaElement(basestring))
        self.short_desc = SchemaElement(basestring)
        self.spicy = SchemaElement(int)
        self.allergens = SchemaList(SchemaElement(basestring))
        self.allergen_free = SchemaList(SchemaElement(basestring))
        self.restrictions = SchemaList(SchemaElement(basestring))
        self.prices = SchemaList(MenuPriceSchema())

class MenuPriceSchema(Schema):
    def setSchema(self):
        self.title = SchemaElement(basestring)
        self.price = SchemaElement(basestring)
        self.calories = SchemaElement(int)
        self.unit = SchemaElement(basestring)
        self.currency = SchemaElement(basestring)

class TimesSchema(Schema):
    def setSchema(self):
        self.sun = SchemaList(HoursSchema())
        self.mon = SchemaList(HoursSchema())
        self.tue = SchemaList(HoursSchema())
        self.wed = SchemaList(HoursSchema())
        self.thu = SchemaList(HoursSchema())
        self.fri = SchemaList(HoursSchema())
        self.sat = SchemaList(HoursSchema())

class HoursSchema(Schema):
    def setSchema(self):
        self.open = SchemaElement(basestring)
        self.close = SchemaElement(basestring)
        self.desc = SchemaElement(basestring)



