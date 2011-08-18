#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import copy
from datetime import datetime
from schema import *

# ####### #
# PRIVATE #
# ####### #

def _coordinatesDictToFlat(coordinates):
    try:
        if not isinstance(coordinates['lat'], float) or \
            not isinstance(coordinates['lng'], float):
            raise
        return '%s,%s' % (coordinates['lat'], coordinates['lng'])
    except:
        return None

def _coordinatesFlatToDict(coordinates):
    try:
        coordinates = coordinates.split(',')
        lat = float(coordinates[0])
        lng = float(coordinates[1])
        return {
            'lat': lat,
            'lng': lng
        }
    except:
        return None

# ####### #
# Account #
# ####### #

class AccountSchema(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring)
        self.first_name         = SchemaElement(basestring, required=True)
        self.last_name          = SchemaElement(basestring, required=True)
        self.email              = SchemaElement(basestring, required=True)
        self.password           = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.display_name       = SchemaElement(basestring, required=True)
        self.profile_image      = SchemaElement(basestring)
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

class UserSchema(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring)
        self.first_name         = SchemaElement(basestring, required=True)
        self.last_name          = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.display_name       = SchemaElement(basestring, required=True)
        self.profile_image      = SchemaElement(basestring)
        self.color_primary      = SchemaElement(basestring)
        self.color_secondary    = SchemaElement(basestring)
        self.bio                = SchemaElement(basestring)
        self.website            = SchemaElement(basestring)
        self.location           = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool, required=True)
        self.flags              = FlagsSchema()
        self.stats              = UserStatsSchema()
        self.timestamp          = TimestampSchema(required=True)

class UserMiniSchema(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.display_name       = SchemaElement(basestring, required=True)
        self.profile_image      = SchemaElement(basestring)
        self.color_primary      = SchemaElement(basestring)
        self.color_secondary    = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool, required=True)

class UserTinySchema(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.display_name       = SchemaElement(basestring, required=True)


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
        self.num_following      = SchemaElement(int)
        self.num_followers      = SchemaElement(int)
        self.num_todos          = SchemaElement(int)
        self.num_credit         = SchemaElement(int)
        self.num_credit_given   = SchemaElement(int)

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

class FriendshipSchema(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.friend_id          = SchemaElement(basestring, required=True)
        self.timestamp          = TimestampSchema()


# ######## #
# Activity #
# ######## #

class ActivitySchema(Schema):
    def setSchema(self):
        self.activity_id        = SchemaElement(basestring)
        self.genre              = SchemaElement(basestring, required=True)
        self.user               = UserMiniSchema(required=True)
        self.comment            = CommentSchema()
        self.stamp              = StampSchema()
        self.favorite           = FavoriteSchema()
        self.timestamp          = TimestampSchema()


# ######## #
# Favorite #
# ######## #

class FavoriteSchema(Schema):
    def setSchema(self):
        self.favorite_id        = SchemaElement(basestring)
        self.entity             = EntityMini(required=True)
        self.user_id            = SchemaElement(basestring, required=True)
        self.stamp              = StampSchema()
        self.timestamp          = TimestampSchema()
        self.complete           = SchemaElement(bool)

# class FavoriteStampSchema(Schema):
#     def setSchema(self):
#         self.stamp_id           = SchemaElement(basestring, required=True)
#         self.display_name       = SchemaElement(basestring, required=True)
#         self.user_id            = SchemaElement(basestring, required=True)
#         self.blurb              = SchemaElement(basestring)


# ###### #
# Stamps #
# ###### #

class StampSchema(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring)
        self.entity             = EntityMini(required=True)
        self.user               = UserMiniSchema(required=True)
        self.blurb              = SchemaElement(basestring)
        self.image              = SchemaElement(basestring)
        self.mentions           = SchemaList(MentionSchema())
        self.credit             = SchemaList(UserTinySchema())
        self.comment_preview    = SchemaList(CommentSchema())
        self.timestamp          = TimestampSchema()
        self.flags              = FlagsSchema()
        self.stats              = StampStatsSchema()

class MentionSchema(Schema):
    def setSchema(self):
        self.screen_name        = SchemaElement(basestring, required=True)
        self.display_name       = SchemaElement(basestring)
        self.user_id            = SchemaElement(basestring)
        self.indices            = SchemaList(SchemaElement(int))


# ######## #
# Comments #
# ######## #

class CommentSchema(Schema):
    def setSchema(self):
        self.comment_id         = SchemaElement(basestring)
        self.user               = UserMiniSchema(required=True)
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.restamp_id         = SchemaElement(basestring)
        self.blurb              = SchemaElement(basestring, required=True)
        self.mentions           = SchemaList(MentionSchema())
        self.timestamp          = TimestampSchema()


# ######## #
# Entities #
# ######## #

class Entity(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring)
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring, required=True)
        self.category           = SchemaElement(basestring, required=True)
        self.subcategory        = SchemaElement(basestring, required=True)
        self.locale             = SchemaElement(basestring)
        self.desc               = SchemaElement(basestring)
        self.image              = SchemaElement(basestring)

        self.timestamp          = TimestampSchema()
        self.coordinates        = CoordinatesSchema()
        self.details            = EntityDetailsSchema()
        self.sources            = EntitySourcesSchema()

    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'HTTPEntity':
            data                = self.value
            coordinates         = data.pop('coordinates', None)

            schema.importData(data, overflow=True)

            schema.address      = self.details.place.address
            schema.neighborhood = self.details.place.neighborhood
            schema.phone        = self.details.contact.phone
            schema.site         = self.details.contact.site
            schema.hours        = self.details.contact.hoursOfOperation
            schema.cuisine      = self.details.restaurant.cuisine

            schema.coordinates  = _coordinatesDictToFlat(coordinates)

            if self.sources.openTable.reserveURL != None:
                schema.opentable_url = "http://www.opentable.com/reserve/%s&ref=9166" % \
                                        (self.sources.openTable.reserveURL)
        
        elif schema.__class__.__name__ in ('EntityMini', 'EntityPlace', \
                                            'HTTPEntityAutosuggest'):
            schema.importData(self.exportSparse(), overflow=True)

        else:
            raise NotImplementedError

        return schema

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

class HTTPEntity(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring, required=True)
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring, required=True)
        self.category           = SchemaElement(basestring, required=True)
        self.subcategory        = SchemaElement(basestring, required=True)
        self.desc               = SchemaElement(basestring)
        self.address            = SchemaElement(basestring)
        self.neighborhood       = SchemaElement(basestring)
        self.coordinates        = SchemaElement(basestring)
        self.image              = SchemaElement(basestring)
        self.phone              = SchemaElement(int)
        self.site               = SchemaElement(basestring)
        self.hours              = SchemaElement(basestring)
        self.cuisine            = SchemaElement(basestring)
        self.opentable_url      = SchemaElement(basestring)
        self.last_modified      = SchemaElement(basestring)

class HTTPAddEntity(Schema):
    def setSchema(self):
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring, required=True)
        self.category           = SchemaElement(basestring, required=True)
        self.subcategory        = SchemaElement(basestring, required=True)
        self.desc               = SchemaElement(basestring)
        self.address            = SchemaElement(basestring)
        self.coordinates        = SchemaElement(basestring)

    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'Entity':

            schema.importData({
                'title':        self.title,
                'subtitle':     self.subtitle,
                'category':     self.category,
                'subcategory':  self.subcategory,
                'desc':         self.desc
            })

            schema.details.place.address = self.address 

            schema.coordinates = _coordinatesFlatToDict(self.coordinates)

        else:
            raise NotImplementedError

        return schema

class HTTPEntityAutosuggest(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring, required=True)
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring, required=True)
        self.category           = SchemaElement(basestring, required=True)






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
        self.price              = SchemaElement(basestring) 
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
        self.developer          = SchemaElement(basestring) 
        self.developerURL       = SchemaElement(basestring) 
        self.developerSupportURL        = SchemaElement(basestring) 
        self.publisher          = SchemaElement(basestring) 
        self.releaseDate        = SchemaElement(basestring) 
        self.appCategory        = SchemaElement(basestring) 
        self.language           = SchemaElement(basestring) 
        self.rating             = SchemaElement(basestring) 
        self.popularity         = SchemaElement(basestring) 
        self.parentalRating     = SchemaElement(basestring) 
        self.platform           = SchemaElement(basestring) 
        self.requirements       = SchemaElement(basestring) 
        self.size               = SchemaElement(basestring) 
        self.version            = SchemaElement(basestring) 
        self.downloadURL        = SchemaElement(basestring) 
        self.thumbnailURL       = SchemaElement(basestring) 
        self.screenshotURL      = SchemaElement(basestring) 
        self.videoURL           = SchemaElement(basestring) 

class BookSchema(Schema):
    def setSchema(self):
        # TODO
        pass

class VideoSchema(Schema):
    def setSchema(self):
        # TODO: modify types
        self.studio_name        = SchemaElement(basestring) 
        self.network_name       = SchemaElement(basestring) 
        self.short_description  = SchemaElement(basestring) 
        self.long_description   = SchemaElement(basestring) 
        self.episode_production_number  = SchemaElement(basestring) 
        
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
        self.albums             = SchemaList(SchemaElement(basestring))

class SongSchema(Schema):
    def setSchema(self):
        self.preview_url        = SchemaElement(basestring) 
        self.preview_length     = SchemaElement(basestring) 

class AlbumSchema(Schema):
    def setSchema(self):
        self.label_studio       = SchemaElement(basestring) 
        self.is_compilation     = SchemaElement(bool)
        
        self.a_retail_price     = SchemaElement(basestring) 
        self.a_hq_price         = SchemaElement(basestring) 
        self.a_currency_code    = SchemaElement(basestring) 
        self.a_availability_date        = SchemaElement(basestring) 

class MediaSchema(Schema):
    def setSchema(self):
        self.title_version      = SchemaElement(basestring) 
        self.search_terms       = SchemaElement(basestring) 
        self.parental_advisory_id       = SchemaElement(basestring) 
        self.artist_display_name        = SchemaElement(basestring) 
        self.collection_display_name    = SchemaElement(basestring) 
        self.original_release_date      = SchemaElement(basestring) 
        self.itunes_release_date        = SchemaElement(basestring) 
        self.track_length       = SchemaElement(basestring) 
        self.copyright          = SchemaElement(basestring) 
        self.p_line             = SchemaElement(basestring) 
        self.content_provider_name      = SchemaElement(basestring) 
        self.media_type_id      = SchemaElement(basestring) 
        self.artwork_url        = SchemaElement(basestring) 

class EntitySourcesSchema(Schema):
    def setSchema(self):
        self.googlePlaces       = GooglePlacesSchema()
        self.openTable          = OpenTableSchema()
        self.factual            = FactualSchema()
        self.apple              = AppleSchema()
        self.zagat              = ZagatSchema()
        self.urbanspoon         = UrbanSpoonSchema()
        self.nymag              = NYMagSchema()
        self.sfmag              = SFMagSchema()
        self.latimes            = LATimesSchema()
        self.bostonmag          = BostonMagSchema()
        self.fandango           = FandangoSchema()
        self.chimag             = ChicagoMagSchema()
        self.userGenerated      = UserGeneratedSchema()

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
        self.popularity         = SchemaElement(int)
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

class SFMagSchema(Schema):
    def setSchema(self):
        pass

class LATimesSchema(Schema):
    def setSchema(self):
        pass

class BostonMagSchema(Schema):
    def setSchema(self):
        pass

class FandangoSchema(Schema):
    def setSchema(self):
        self.fid                = SchemaElement(basestring)

class ChicagoMagSchema(Schema):
    def setSchema(self):
        pass

class UserGeneratedSchema(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)




