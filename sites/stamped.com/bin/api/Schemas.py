#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

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

# ####### #
# Account #
# ####### #

class Account(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring)
        self.name               = SchemaElement(basestring, required=True)
        self.email              = SchemaElement(basestring, required=True)
        self.password           = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.color_primary      = SchemaElement(basestring)
        self.color_secondary    = SchemaElement(basestring)
        self.bio                = SchemaElement(basestring)
        self.website            = SchemaElement(basestring)
        self.location           = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool, required=True, default=False)
        self.locale             = LocaleSchema()
        self.linked_accounts    = LinkedAccountSchema()
        self.devices            = DevicesSchema()
        self.flags              = FlagsSchema()
        self.stats              = UserStatsSchema()
        self.timestamp          = TimestampSchema()

class LinkedAccountSchema(Schema):
    def setSchema(self):
        self.itunes             = SchemaElement(basestring)
        
class DevicesSchema(Schema):
    def setSchema(self):
        self.ios_device_tokens  = SchemaElement(basestring)
        
class LocaleSchema(Schema):
    def setSchema(self):
        self.language           = SchemaElement(basestring, default='en')
        self.time_zone          = SchemaElement(basestring)

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

    def exportSchema(self, schema):
        if schema.__class__.__name__ in ('UserMini', 'UserTiny'):
            schema.importData(self.value, overflow=True)
        else:
            raise NotImplementedError

        return schema

class UserMini(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.color_primary      = SchemaElement(basestring)
        self.color_secondary    = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool, required=True)

class UserTiny(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)


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
        self.num_friends        = SchemaElement(int)
        self.num_followers      = SchemaElement(int)
        self.num_faves          = SchemaElement(int)
        self.num_credits        = SchemaElement(int)
        self.num_credits_given  = SchemaElement(int)

class StampStatsSchema(Schema):
    def setSchema(self):
        self.num_comments       = SchemaElement(int)
        self.num_todos          = SchemaElement(int)
        self.num_credit         = SchemaElement(int)


# ########## #
# Timestamps #
# ########## #

class TimestampSchema(Schema):
    def setSchema(self):
        self.created            = SchemaElement(datetime, required=True)
        self.modified           = SchemaElement(datetime)


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
        self.image              = SchemaElement(basestring)
        self.mentions           = SchemaList(MentionSchema())
        self.credit             = SchemaList(CreditSchema())
        self.comment_preview    = SchemaList(Comment())
        self.timestamp          = TimestampSchema()
        self.flags              = FlagsSchema()
        self.stats              = StampStatsSchema()

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
        self.activity_id        = SchemaElement(basestring)
        self.genre              = SchemaElement(basestring, required=True)
        self.user               = UserMini(required=True)
        self.image              = SchemaElement(basestring)
        self.subject            = SchemaElement(basestring)
        self.blurb              = SchemaElement(basestring)
        self.link               = ActivityLink()
        self.timestamp          = TimestampSchema()

class ActivityLink(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring)
        self.stamp_id           = SchemaElement(basestring)
        self.entity_id          = SchemaElement(basestring)
        self.comment_id         = SchemaElement(basestring)
        self.url                = SchemaElement(basestring)

# ######## #
# Entities #
# ######## #

class Entity(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring)
        self.title              = SchemaElement(basestring, required=True)
        #self.titles             = SchemaList(SchemaElement(basestring))
        self.subtitle           = SchemaElement(basestring)
        self.category           = SchemaElement(basestring, derivedFrom='subcategory', derivedFn=self.set_category)
        self.subcategory        = SchemaElement(basestring, required=True)
        self.locale             = SchemaElement(basestring)
        self.desc               = SchemaElement(basestring)
        self.image              = SchemaElement(basestring)
        self.popularity         = SchemaElement(int)
        self.timestamp          = TimestampSchema()
        self.coordinates        = CoordinatesSchema()
        self.details            = EntityDetailsSchema()
        self.sources            = EntitySourcesSchema()
    
    def exportSchema(self, schema):
        if schema.__class__.__name__ in ('EntityMini', 'EntityPlace'):
            if self.subtitle is None:
                if 'address' in self:
                    self.subtitle = self.address
                else:
                    self.subtitle = self.subcategory
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

class EntityMini(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring, required=True)
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring, required=True)
        self.category           = SchemaElement(basestring, required=True)
        self.subcategory        = SchemaElement(basestring, required=True)
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

class CoordinatesSchema(Schema):
    def setSchema(self):
        self.lat                = SchemaElement(float, required=True)
        self.lng                = SchemaElement(float, required=True)

class EntityDetailsSchema(Schema):
    def setSchema(self):
        self.place              = PlaceSchema()
        self.contact            = ContactSchema()
        self.restaurant         = RestaurantSchema()
        self.iPhoneApp          = AppSchema()
        self.book               = BookSchema()
        self.video              = VideoSchema()
        self.artist             = ArtistSchema()
        self.song               = SongSchema()
        self.album              = AlbumSchema()
        self.media              = MediaSchema()
        self.product            = ProductSchema()

class PlaceSchema(Schema):
    def setSchema(self):
        self.address            = SchemaElement(basestring)
        self.types              = SchemaList(SchemaElement(basestring))
        self.vicinity           = SchemaElement(basestring)
        self.neighborhood       = SchemaElement(basestring)
        self.crossStreet        = SchemaElement(basestring)
        self.publicTransit      = SchemaElement(basestring)
        self.parking            = SchemaElement(basestring)
        self.parkingDetails     = SchemaElement(basestring)
        self.wheelchairAccess   = SchemaElement(basestring)

class ContactSchema(Schema):
    def setSchema(self):
        self.phone              = SchemaElement(basestring)
        self.fax                = SchemaElement(basestring)
        self.site               = SchemaElement(basestring)
        self.email              = SchemaElement(basestring)
        self.hoursOfOperation   = SchemaElement(basestring)

class RestaurantSchema(Schema):
    def setSchema(self):
        self.diningStyle        = SchemaElement(basestring)
        self.cuisine            = SchemaElement(basestring)
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
        self.num_pages          = SchemaElement(int)

class VideoSchema(Schema):
    def setSchema(self):
        self.studio_name        = SchemaElement(basestring)
        self.network_name       = SchemaElement(basestring)
        self.short_description  = SchemaElement(basestring)
        self.long_description   = SchemaElement(basestring)
        self.episode_production_number  = SchemaElement(basestring)
        ### TODO: populate cast / director from crawler
        self.cast               = SchemaElement(basestring)
        self.director           = SchemaElement(basestring)
        
        self.v_retail_price     = SchemaElement(basestring)
        self.v_currency_code    = SchemaElement(basestring)
        self.v_availability_date        = SchemaElement(basestring)
        self.v_sd_price         = SchemaElement(basestring)
        self.v_hq_price         = SchemaElement(basestring)
        self.v_lc_rental_price  = SchemaElement(basestring)
        self.v_sd_rental_price  = SchemaElement(basestring)
        self.v_hd_rental_price  = SchemaElement(basestring)

class ArtistSchema(Schema):
    def setSchema(self):
        self.albums             = SchemaList(ArtistAlbumsSchema())

class ArtistAlbumsSchema(Schema):
    def setSchema(self):
        self.album_id           = SchemaElement(int)
        self.rank               = SchemaElement(int)
        self.genre_id           = SchemaElement(int)

class SongSchema(Schema):
    def setSchema(self):
        self.preview_url        = SchemaElement(basestring)
        self.preview_length     = SchemaElement(basestring)
        ### TODO: modify this based on crawler logic (only for custom entities currently)
        self.album_name         = SchemaElement(basestring) 

class AlbumSchema(Schema):
    def setSchema(self):
        self.label_studio       = SchemaElement(basestring)
        self.is_compilation     = SchemaElement(bool)
        
        self.a_retail_price             = SchemaElement(basestring)
        self.a_hq_price                 = SchemaElement(basestring)
        self.a_currency_code            = SchemaElement(basestring)
        self.a_availability_date        = SchemaElement(basestring)
        
        self.tracks                     = SchemaList(SchemaElement(basestring))

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
        self.title_version              = SchemaElement(basestring)
        self.search_terms               = SchemaElement(basestring)
        self.parental_advisory_id       = SchemaElement(basestring)
        self.artist_display_name        = SchemaElement(basestring)
        self.collection_display_name    = SchemaElement(basestring)
        self.original_release_date      = SchemaElement(basestring)
        self.itunes_release_date        = SchemaElement(basestring)
        self.track_length               = SchemaElement(basestring)
        self.copyright                  = SchemaElement(basestring)
        self.p_line                     = SchemaElement(basestring)
        self.content_provider_name      = SchemaElement(basestring)
        self.media_type_id              = SchemaElement(basestring)
        self.artwork_url                = SchemaElement(basestring)
        self.mpaa_rating                = SchemaElement(basestring)

class EntitySourcesSchema(Schema):
    def setSchema(self):
        self.googlePlaces       = GooglePlacesSchema()
        self.openTable          = OpenTableSchema()
        self.factual            = FactualSchema()
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

class AppleSchema(Schema):
    def setSchema(self):
        self.aid                = SchemaElement(basestring)
        self.export_date        = SchemaElement(basestring)
        self.is_actual_artist   = SchemaElement(bool)
        self.view_url           = SchemaElement(basestring)
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
        self.user_id            = SchemaElement(basestring, required=True)

class BarnesAndNobleSchema(Schema):
    def setSchema(self):
        self.bid                = SchemaElement(int)

