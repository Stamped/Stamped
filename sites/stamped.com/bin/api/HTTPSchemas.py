#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import copy, urllib, urlparse, re
from datetime import datetime, date
from schema import *
from Schemas import *

# ####### #
# PRIVATE #
# ####### #

LINKSHARE_TOKEN = 'QaV3NQJNPRA'
FANDANGO_TOKEN  = '5348839'

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

def _encodeLinkShareDeepURL(raw_url):
    parsed_url  = urlparse.urlparse(raw_url)
    query       = "partnerId=30"
    new_query   = (parsed_url.query+'&'+query) if parsed_url.query else query
    url         = urlparse.urlunparse((
                        parsed_url.scheme,
                        parsed_url.netloc,
                        parsed_url.path,
                        parsed_url.params,
                        new_query,
                        parsed_url.fragment
                    ))
    deep_url    = urllib.quote_plus(urllib.quote_plus(url))
    return deep_url

def _encodeiTunesShortURL(raw_url):
    parsed_url  = urlparse.urlparse(raw_url)
    query       = "partnerId=30&siteID=%s" % LINKSHARE_TOKEN
    new_query   = (parsed_url.query+'&'+query) if parsed_url.query else query
    url         = urlparse.urlunparse((
                        parsed_url.scheme,
                        parsed_url.netloc,
                        parsed_url.path,
                        parsed_url.params,
                        new_query,
                        parsed_url.fragment
                    ))
    return url


# ######### #
# OAuth 2.0 #
# ######### #

class OAuthTokenRequest(Schema):
    def setSchema(self):
        self.refresh_token      = SchemaElement(basestring, required=True)
        self.grant_type         = SchemaElement(basestring, required=True)

class OAuthLogin(Schema):
    def setSchema(self):
        self.login              = SchemaElement(basestring, required=True)
        self.password           = SchemaElement(basestring, required=True)

# ####### #
# Account #
# ####### #

class HTTPAccount(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.name               = SchemaElement(basestring, required=True)
        self.email              = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.privacy            = SchemaElement(bool, required=True)
        self.phone              = SchemaElement(int)
        # self.language           = SchemaElement(basestring)
        # self.time_zone          = SchemaElement(basestring)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Account':
            self.importData(schema.exportSparse(), overflow=True)
        else:
            raise NotImplementedError
        return self

class HTTPAccountNew(Schema):
    def setSchema(self):
        self.name               = SchemaElement(basestring, required=True)
        self.email              = SchemaElement(basestring, required=True)
        self.password           = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.phone              = SchemaElement(int)
        self.profile_image      = SchemaElement(basestring, normalize=False)

    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'Account':
            schema.importData(self.exportSparse(), overflow=True)
        else:
            raise NotImplementedError
        return schema

class HTTPAccountSettings(Schema):
    def setSchema(self):
        self.email              = SchemaElement(basestring)
        self.password           = SchemaElement(basestring)
        self.screen_name        = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool)
        self.phone              = SchemaElement(int)
        # self.language           = SchemaElement(basestring)
        # self.time_zone          = SchemaElement(basestring)

class HTTPAccountProfile(Schema):
    def setSchema(self):
        self.name               = SchemaElement(basestring)
        self.color              = SchemaElement(basestring)
        self.bio                = SchemaElement(basestring)
        self.website            = SchemaElement(basestring)
        self.location           = SchemaElement(basestring)

class HTTPCustomizeStamp(Schema):
    def setSchema(self):
        self.color_primary      = SchemaElement(basestring, required=True)
        self.color_secondary    = SchemaElement(basestring, required=True)

class HTTPAccountProfileImage(Schema):
    def setSchema(self):
        self.profile_image      = SchemaElement(basestring, normalize=False)

class HTTPAccountCheck(Schema):
    def setSchema(self):
        self.login              = SchemaElement(basestring, required=True)

class HTTPLinkedAccounts(Schema):
    def setSchema(self):
        self.twitter_id         = SchemaElement(basestring)
        self.twitter_screen_name= SchemaElement(basestring)

    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'LinkedAccounts':
            schema.twitter_id           = self.twitter_id
            schema.twitter_screen_name  = self.twitter_screen_name
        else:
            raise NotImplementedError
        return schema

# ##### #
# Users #
# ##### #

class HTTPUser(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.name               = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.color_primary      = SchemaElement(basestring)
        self.color_secondary    = SchemaElement(basestring)
        self.bio                = SchemaElement(basestring)
        self.website            = SchemaElement(basestring)
        self.location           = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool, required=True)
        self.identifier         = SchemaElement(basestring)
        self.num_stamps         = SchemaElement(int)
        self.num_stamps_left    = SchemaElement(int)
        self.num_friends        = SchemaElement(int)
        self.num_followers      = SchemaElement(int)
        self.num_faves          = SchemaElement(int)
        self.num_credits        = SchemaElement(int)
        self.num_credits_given  = SchemaElement(int)
        self.num_likes          = SchemaElement(int)
        self.num_likes_given    = SchemaElement(int)

    def importSchema(self, schema):
        if schema.__class__.__name__ in ('Account', 'User'):
            self.importData(schema.exportSparse(), overflow=True)
            
            stats = schema.stats.exportSparse()
            self.num_stamps         = stats.pop('num_stamps', 0)
            self.num_stamps_left    = stats.pop('num_stamps_left', 0)
            self.num_friends        = stats.pop('num_friends', 0)
            self.num_followers      = stats.pop('num_followers', 0)
            self.num_faves          = stats.pop('num_faves', 0)
            self.num_credits        = stats.pop('num_credits', 0)
            self.num_credits_given  = stats.pop('num_credits_given', 0)
            self.num_likes          = stats.pop('num_credits', 0)
            self.num_likes_given    = stats.pop('num_credits_given', 0)
        else:
            raise NotImplementedError
        return self

class HTTPUserMini(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.color_primary      = SchemaElement(basestring)
        self.color_secondary    = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool, required=True)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'UserMini':
            self.importData(schema.exportSparse(), overflow=True)
        else:
            raise NotImplementedError
        return self

class HTTPUserId(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring)
        self.screen_name        = SchemaElement(basestring)

class HTTPUserIds(Schema):
    def setSchema(self):
        self.user_ids           = SchemaList(SchemaElement(basestring), delimiter=',')
        self.screen_names       = SchemaList(SchemaElement(basestring), delimiter=',')

class HTTPUserSearch(Schema):
    def setSchema(self):
        self.q                  = SchemaElement(basestring)
        self.limit              = SchemaElement(int)

class HTTPUserRelationship(Schema):
    def setSchema(self):
        self.user_id_a          = SchemaElement(basestring)
        self.screen_name_a      = SchemaElement(basestring)
        self.user_id_b          = SchemaElement(basestring)
        self.screen_name_b      = SchemaElement(basestring)

class HTTPFindUser(Schema):
    def setSchema(self):
        self.q                  = SchemaList(SchemaElement(basestring), delimiter=',')

# ####### #
# Invites #
# ####### #

class HTTPInvitation(Schema):
    def setSchema(self):
        self.email              = SchemaElement(basestring)

# ######## #
# Entities #
# ######## #

class HTTPEntity(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring, required=True)
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring, required=True)
        self.category           = SchemaElement(basestring, required=True)
        self.subcategory        = SchemaElement(basestring, required=True)
        self.desc               = SchemaElement(basestring)
        self.image              = SchemaElement(basestring)
        self.last_modified      = SchemaElement(basestring)
        
        # Address
        self.address            = SchemaElement(basestring)
        self.address_street     = SchemaElement(basestring)
        self.address_city       = SchemaElement(basestring)
        self.address_state      = SchemaElement(basestring)
        self.address_country    = SchemaElement(basestring)
        self.address_zip        = SchemaElement(basestring)
        
        self.neighborhood       = SchemaElement(basestring)
        self.coordinates        = SchemaElement(basestring)
        
        # Contact
        self.phone              = SchemaElement(basestring)
        self.site               = SchemaElement(basestring)
        self.hours              = SchemaElement(basestring)
        
        # Cross-Category
        self.release_date       = SchemaElement(datetime)
        self.length             = SchemaElement(basestring)
        self.rating             = SchemaElement(basestring)
        
        # Food
        self.cuisine            = SchemaElement(basestring)
        self.price_scale        = SchemaElement(basestring)
        
        # Book
        self.author             = SchemaElement(basestring)
        self.isbn               = SchemaElement(basestring)
        self.publisher          = SchemaElement(basestring)
        self.format             = SchemaElement(basestring)
        self.language           = SchemaElement(basestring)
        self.edition            = SchemaElement(basestring)
        
        # Film
        self.genre              = SchemaElement(basestring)
        self.cast               = SchemaElement(basestring)
        self.director           = SchemaElement(basestring)
        self.network            = SchemaElement(basestring)
        self.in_theaters        = SchemaElement(basestring)
        self.run_dates          = SchemaElement(basestring)
        
        # Music
        self.artist_name        = SchemaElement(basestring)
        self.album_name         = SchemaElement(basestring)
        self.label              = SchemaElement(basestring)
        self.albums             = SchemaList(SchemaElement(basestring))
        self.songs              = SchemaList(SchemaElement(basestring))
        self.preview_url        = SchemaElement(basestring)
        
        # Affiliates
        self.opentable_url      = SchemaElement(basestring)
        self.itunes_url         = SchemaElement(basestring)
        self.itunes_short_url   = SchemaElement(basestring)
        self.netflix_url        = SchemaElement(basestring)
        self.fandango_url       = SchemaElement(basestring)
        self.barnesnoble_url    = SchemaElement(basestring)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Entity':
            from Entity import setFields
            setFields(schema)
            
            data                = schema.value
            coordinates         = data.pop('coordinates', None)
            
            self.importData(data, overflow=True)
            
            self.last_modified  = schema.timestamp.created
            
            # Place
            self.address        = schema.address
            self.neighborhood   = schema.neighborhood
            self.coordinates    = _coordinatesDictToFlat(coordinates)
            
            if len(schema.address_components) > 0:
                address = {}
                for component in schema.address_components:
                    for i in component['types']:
                        address[str(i)] = component['short_name']
                    
                if 'street_address' in address:
                    self.address_street = address['street_address']
                elif 'street_number' in address and 'route' in address:
                    self.address_street = "%s %s" % \
                        (address['street_number'], address['route'])
                
                if 'locality' in address:
                    self.address_city = address['locality']
                
                if 'administrative_area_level_1' in address:
                    self.address_state = address['administrative_area_level_1']
                
                if 'country' in address:
                    self.address_country = address['country']
                
                if 'postal_code' in address:
                    self.address_zip = address['postal_code']
            
            # Contact
            self.phone          = schema.phone
            self.site           = schema.site
            self.hours          = schema.hoursOfOperation
            
            # Cross-Category
            
            ### TODO: Unify these within Schemas.py where possible
            if self.category == 'book':
                self.release_date   = schema.publish_date
                self.length         = schema.num_pages
            
            elif self.category == 'film':
                try:
                    dateString = schema.original_release_date
                    release_date = date(int(dateString[0:4]), \
                                        int(dateString[5:7]), \
                                        int(dateString[8:10]))
                    self.release_date   = release_date
                except:
                    self.release_date   = None
                
                self.length         = schema.track_length
                self.rating         = schema.mpaa_rating
                
                if schema.ngenres is not None:
                    self.genre = strings.joinfields(schema.ngenres, '; ')
                
                if schema.short_description != None:
                    self.desc = schema.short_description
            
            elif self.category == 'music':
                try:
                    dateString = schema.original_release_date
                    release_date = date(int(dateString[0:4]), \
                                        int(dateString[5:7]), \
                                        int(dateString[8:10]))
                    self.release_date   = release_date
                except:
                    self.release_date   = None
                
                self.length         = schema.track_length
                if schema.parental_advisory_id == 1:
                    self.rating     = "Parental Advisory"
            
            # Food
            self.cuisine        = schema.cuisine
            self.price_scale    = schema.priceScale

            # Book
            self.author         = schema.author
            self.isbn           = schema.isbn
            self.publisher      = schema.publisher
            self.format         = schema.book_format
            self.language       = schema.language
            self.edition        = schema.edition

            # Film
            self.cast           = schema.cast
            self.director       = schema.director
            self.network        = schema.network_name
            self.in_theaters    = schema.in_theaters
            
            # Music
            self.artist_name    = schema.artist_display_name
            self.album_name     = schema.album_name
            self.label          = schema.label_studio
            
            if 'preview_url' in schema:
                self.preview_url = schema.preview_url
            
            # Affiliates
            if schema.sources.openTable.reserveURL != None:
                url = "http://www.opentable.com/reserve/%s&ref=9166" % \
                        (schema.sources.openTable.reserveURL, )
                self.opentable_url = url
            
            if schema.sources.apple.view_url != None:
                itunes_url  = schema.sources.apple.view_url
                base_url    = "http://click.linksynergy.com/fs-bin/stat"
                params      = "id=%s&offerid=146261&type=3&subid=0&tmpid=1826" \
                               % (LINKSHARE_TOKEN)
                deep_url    = "%s?%s&RD_PARM1=%s" % (base_url, params, \
                                    _encodeLinkShareDeepURL(itunes_url))
                short_url   = _encodeiTunesShortURL(itunes_url)
                
                self.itunes_url       = deep_url
                self.itunes_short_url = short_url
            
            is_apple = 'apple' in schema
            
            # Image
            if schema.image is not None:
                self.image = self._handle_image(schema.image, is_apple)
            elif schema.large is not None:
                self.image = self._handle_image(schema.large, is_apple)
            elif schema.small is not None:
                self.image = self._handle_image(schema.small, is_apple)
            elif schema.tiny is not None:
                self.image = self._handle_image(schema.tiny, is_apple)
            elif schema.artwork_url is not None:
                self.image = self._handle_image(schema.artwork_url, is_apple)
            
            if (schema.subcategory == "album" or schema.subcategory == "artist") and schema.songs is not None:
                songs = schema.songs
                
                # for an artist, only return up to 10 songs
                if schema.subcategory == "artist":
                    songs = songs[0: min(10, len(songs))]
                
                songs = list(song.song_name for song in songs)
                self.songs = songs
            
            if (schema.subcategory == "album" or schema.subcategory == "artist") and schema.albums is not None:
                try:
                    albums = list(album.album_name for album in schema.albums)
                    self.albums = albums
                except:
                    pass
        elif schema.__class__.__name__ == 'EntityMini':
            data                = schema.value
            coordinates         = data.pop('coordinates', None)
            self.importData(data, overflow=True)
            self.coordinates    = _coordinatesDictToFlat(coordinates)
        else:
            raise NotImplementedError
        return self
    
    def _handle_image(self, url, is_apple):
        if is_apple:
            # try to return the maximum-resolution apple photo possible if we have 
            # a lower-resolution version stored in our db
            return url.replace('100x100', '200x200').replace('170x170', '200x200')
        
        return url

class HTTPEntityNew(Schema):
    def setSchema(self):
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring, required=True)
        self.category           = SchemaElement(basestring, required=True)
        self.subcategory        = SchemaElement(basestring, required=True)
        self.desc               = SchemaElement(basestring)
        self.address            = SchemaElement(basestring)
        self.coordinates        = SchemaElement(basestring)
        self.cast               = SchemaElement(basestring)
        self.director           = SchemaElement(basestring)
        self.release_date       = SchemaElement(basestring)
        self.artist             = SchemaElement(basestring)
        self.album              = SchemaElement(basestring)
        self.author             = SchemaElement(basestring)

    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'Entity':
            schema.importData({
                'title':        self.title,
                'subtitle':     self.subtitle,
                'category':     self.category,
                'subcategory':  self.subcategory,
                'desc':         self.desc
            })
            schema.address      = self.address 
            schema.director     = self.director
            schema.cast         = self.cast
            schema.album_name   = self.album
            schema.author       = self.author
            schema.artist_display_name = self.artist
            schema.original_release_date = self.release_date

            if _coordinatesFlatToDict(self.coordinates) != None:
                schema.coordinates = _coordinatesFlatToDict(self.coordinates)
        else:
            raise NotImplementedError
        return schema

class HTTPEntityEdit(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring, required=True)
        self.title              = SchemaElement(basestring)
        self.subtitle           = SchemaElement(basestring)
        self.category           = SchemaElement(basestring)
        self.subcategory        = SchemaElement(basestring)
        self.desc               = SchemaElement(basestring)
        self.address            = SchemaElement(basestring)
        self.coordinates        = SchemaElement(basestring)

    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'Entity':
            schema.importData({
                'entity_id':    self.entity_id,
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
        self.search_id          = SchemaElement(basestring, required=True)
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring)
        self.category           = SchemaElement(basestring, required=True)
    
    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Entity':
            from Entity import setFields
            setFields(schema, detailed=True)

            if schema.search_id is not None:
                self.search_id = schema.search_id

            else:
                self.search_id = schema.entity_id
            assert self.search_id is not None

            self.title = schema.title
            self.subtitle = schema.subtitle
            self.category = schema.category

            if self.subtitle is None:
                entity.subtitle = str(entity.subcategory).replace('_', ' ').title()
        else:
            raise NotImplementedError
        return self

class HTTPEntityId(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring, required=True)

class HTTPEntitySearch(Schema):
    def setSchema(self):
        self.q                  = SchemaElement(basestring, required=True)
        self.coordinates        = SchemaElement(basestring)
        self.category           = SchemaElement(basestring)
        self.subcategory        = SchemaElement(basestring)
    
    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'EntitySearch':
            schema.importData({'q': self.q})
            schema.coordinates = _coordinatesFlatToDict(self.coordinates)
            schema.importData({'category': self.category})
            schema.importData({'subcategory': self.subcategory})
        else:
            raise NotImplementedError
        return schema

# ###### #
# Stamps #
# ###### #

class HTTPStamp(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.entity             = HTTPEntity(required=True)
        self.user               = HTTPUserMini(required=True)
        self.blurb              = SchemaElement(basestring)
        self.mentions           = SchemaList(MentionSchema())
        self.credit             = SchemaList(CreditSchema())
        self.comment_preview    = SchemaList(HTTPComment())
        self.image_dimensions   = SchemaElement(basestring)
        self.image_url          = SchemaElement(basestring)
        self.created            = SchemaElement(basestring)
        self.num_comments       = SchemaElement(int)
        self.num_likes          = SchemaElement(int)
        self.like_threshold_hit = SchemaElement(bool)
        self.is_liked           = SchemaElement(bool)
        self.is_fav             = SchemaElement(bool)
        self.url                = SchemaElement(basestring)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Stamp':
            data                = schema.exportSparse()
            coordinates         = data['entity'].pop('coordinates', None)
            comments            = data.pop('comment_preview', [])
            mentions            = data.pop('mentions', [])
            credit              = data.pop('credit', [])

            comment_preview = []
            for comment in comments:
                comment = Comment(comment)
                comment = HTTPComment().importSchema(comment).exportSparse()
                comment_preview.append(comment)
            data['comment_preview'] = comment_preview

            if len(mentions) > 0:
                data['mentions'] = mentions

            if len(credit) > 0:
                data['credit'] = credit

            self.importData(data, overflow=True)
            self.entity.coordinates     = _coordinatesDictToFlat(coordinates)
            self.num_comments           = schema.num_comments
            self.num_likes              = schema.num_likes
            self.like_threshold_hit     = schema.like_threshold_hit
            self.created                = schema.timestamp.created
            self.is_liked               = schema.is_liked
            self.is_fav                 = schema.is_fav

            if self.image_dimensions != None:
                self.image_url = 'http://static.stamped.com/stamps/%s.jpg' % self.stamp_id

            stamp_title = schema.entity.title.replace(' ', '-').encode('ascii', 'ignore')
            stamp_title = re.sub('([^a-zA-Z0-9._-])', '', stamp_title)
            self.url = 'http://www.stamped.com/%s/stamps/%s/%s' % \
                (schema.user.screen_name, schema.stamp_num, stamp_title)

        else:
            raise NotImplementedError
        return self

class HTTPStampNew(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring)
        self.search_id          = SchemaElement(basestring)
        self.blurb              = SchemaElement(basestring)
        self.credit             = SchemaList(SchemaElement(basestring), delimiter=',')
        self.image              = SchemaElement(basestring, normalize=False)

class HTTPStampEdit(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.blurb              = SchemaElement(basestring)
        self.credit             = SchemaList(SchemaElement(basestring), delimiter=',')

class HTTPStampId(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)

class HTTPGenericSlice(Schema):
    def setSchema(self):
        self.limit              = SchemaElement(int)
        self.since              = SchemaElement(int)
        self.before             = SchemaElement(int)
        self.quality            = SchemaElement(int)

class HTTPUserCollectionSlice(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring)
        self.screen_name        = SchemaElement(basestring)
        self.limit              = SchemaElement(int)
        self.since              = SchemaElement(int)
        self.before             = SchemaElement(int)
        self.quality            = SchemaElement(int)

class HTTPStampImage(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.image              = SchemaElement(basestring, required=True, normalize=False)

# ######## #
# Comments #
# ######## #

class HTTPComment(Schema):
    def setSchema(self):
        self.comment_id         = SchemaElement(basestring, required=True)
        self.user               = HTTPUserMini(required=True)
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.restamp_id         = SchemaElement(basestring)
        self.blurb              = SchemaElement(basestring, required=True)
        self.mentions           = SchemaList(MentionSchema())
        self.created            = SchemaElement(basestring)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Comment':
            self.importData(schema.exportSparse(), overflow=True)
            self.created = schema.timestamp.created

        else:
            raise NotImplementedError

        return self

class HTTPCommentNew(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.blurb              = SchemaElement(basestring, required=True)

class HTTPCommentId(Schema):
    def setSchema(self):
        self.comment_id         = SchemaElement(basestring, required=True)

class HTTPCommentSlice(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.limit              = SchemaElement(int)
        self.since              = SchemaElement(int)
        self.before             = SchemaElement(int)

# ######## #
# Favorite #
# ######## #

class HTTPFavorite(Schema):
    def setSchema(self):
        self.favorite_id        = SchemaElement(basestring, required=True)
        self.user_id            = SchemaElement(basestring, required=True)
        self.entity             = HTTPEntity(required=True)
        self.stamp              = HTTPStamp()
        self.created            = SchemaElement(basestring)
        self.complete           = SchemaElement(bool)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Favorite':
            data                = schema.exportSparse()
            entity              = EntityMini(data.pop('entity', None))
            stamp               = Stamp(data.pop('stamp', None))
            data['entity']      = HTTPEntity().importSchema(entity).exportSparse()

            if stamp.stamp_id != None:
                data['stamp']   = HTTPStamp().importSchema(stamp).exportSparse()

            self.importData(data, overflow=True)
            self.created = schema.timestamp.created
        else:
            raise NotImplementedError
        return self

class HTTPFavoriteNew(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring, required=True)
        self.stamp_id           = SchemaElement(basestring)


# ######## #
# Activity #
# ######## #

class HTTPActivity(Schema):
    def setSchema(self):
        self.activity_id        = SchemaElement(basestring, required=True)
        self.genre              = SchemaElement(basestring, required=True)
        self.user               = HTTPUserMini(required=True)
        self.image              = SchemaElement(basestring)
        self.subject            = SchemaElement(basestring)
        self.blurb              = SchemaElement(basestring)
        self.link_user_id       = SchemaElement(basestring)
        self.link_stamp_id      = SchemaElement(basestring)
        self.link_entity_id     = SchemaElement(basestring)
        self.link_url           = SchemaElement(basestring)
        self.created            = SchemaElement(basestring)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Activity':
            data                = schema.value
            user                = UserMini(data.pop('user', None))
            data['user']        = HTTPUserMini().importSchema(user).value

            self.importData(data, overflow=True)
            
            if schema.link_stamp_id != None:
                self.link_stamp_id = schema.link_stamp_id
            elif schema.link_user_id != None:
                self.link_user_id = schema.link_user_id
            elif schema.link_entity_id != None:
                self.link_entity_id = schema.link_entity_id
            elif schema.link_url != None:
                self.link_url = schema.link_url

            self.created = schema.timestamp.created
        else:
            raise NotImplementedError
        return self


### TEMPORARY
class HTTPActivityOld(Schema):
    def setSchema(self):
        self.activity_id        = SchemaElement(basestring, required=True)
        self.genre              = SchemaElement(basestring, required=True)
        self.user               = HTTPUserMini(required=True)
        self.comment            = HTTPComment()
        self.stamp              = HTTPStamp()
        self.favorite           = HTTPFavorite()
        self.created            = SchemaElement(basestring)

    def importSchema(self, schema, stamp=None, comment=None, favorite=None):
        if schema.__class__.__name__ == 'Activity':
            data                = schema.exportSparse()
            user                = UserMini(data.pop('user', None))

            data['user']        = HTTPUserMini().importSchema(user).exportSparse()

            if stamp != None and stamp.stamp_id != None:
                data['stamp']   = HTTPStamp().importSchema(stamp).exportSparse()
                if 'num_comments' in data['stamp']:
                    del(data['stamp']['num_comments'])
            if comment != None and comment.comment_id != None:
                data['comment'] = HTTPComment().importSchema(comment).exportSparse()
            if favorite != None and favorite.favorite_id != None:
                data['favorite']= HTTPFavorite().importSchema(favorite).exportSparse()
 
            self.importData(data, overflow=True)

            self.created = schema.timestamp.created
        else:
            raise NotImplementedError
        return self
