#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import copy, urllib, urlparse, re, logs, string, time, utils

from datetime   import datetime, date, timedelta
from errors     import *
from schema     import *
from Schemas    import *

# ####### #
# PRIVATE #
# ####### #

LINKSHARE_TOKEN = 'QaV3NQJNPRA'
FANDANGO_TOKEN  = '5348839'
AMAZON_TOKEN    = 'stamped01-20'

amazon_image_re = re.compile('(.*)\.[^/.]+\.jpg')

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

def _profileImageURL(screenName, cache=None):
    if not cache:
        # url = 'http://stamped.com.static.images.s3.amazonaws.com/users/%s.jpg' % \
        #     str(screenName).lower()
        url = 'http://static.stamped.com/users/default.jpg'
    elif cache + timedelta(days=1) <= datetime.utcnow():
        url = 'http://static.stamped.com/users/%s.jpg?%s' % \
            (str(screenName).lower(), int(time.mktime(cache.timetuple())))
    else:
        url = 'http://stamped.com.static.images.s3.amazonaws.com/users/%s.jpg?%s' % \
            (str(screenName).lower(), int(time.mktime(cache.timetuple())))
    return url

def encodeStampTitle(title):
    stamp_title = title.replace(' ', '-').encode('ascii', 'ignore')
    stamp_title = re.sub('([^a-zA-Z0-9._-])', '', stamp_title)
    
    return stamp_title

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

def _encodeAmazonURL(raw_url):
    try:
        parsed_url  = urlparse.urlparse(raw_url)
        query       = "tag=%s" % AMAZON_TOKEN
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
    except:
        logs.warning('Unable to encode Amazon URL: %s' % raw_url)
        return None


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
        
        # for asynchronous image uploads
        self.temp_image_url     = SchemaElement(basestring)
        self.temp_image_width   = SchemaElement(int)
        self.temp_image_height  = SchemaElement(int)
    
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
        
        # for asynchronous image uploads
        self.temp_image_url     = SchemaElement(basestring)

class HTTPAccountCheck(Schema):
    def setSchema(self):
        self.login              = SchemaElement(basestring, required=True)

class HTTPLinkedAccounts(Schema):
    def setSchema(self):
        self.twitter_id             = SchemaElement(basestring)
        self.twitter_screen_name    = SchemaElement(basestring)
        self.twitter_key            = SchemaElement(basestring)
        self.twitter_secret         = SchemaElement(basestring)
        self.facebook_id            = SchemaElement(basestring)
        self.facebook_name          = SchemaElement(basestring)
        self.facebook_screen_name   = SchemaElement(basestring)
        self.facebook_token         = SchemaElement(basestring)

    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'LinkedAccounts':
            schema.twitter_id           = self.twitter_id
            schema.twitter_screen_name  = self.twitter_screen_name
            schema.facebook_id          = self.facebook_id
            schema.facebook_name        = self.facebook_name
            schema.facebook_screen_name = self.facebook_screen_name
        elif schema.__class__.__name__ == 'TwitterAuthSchema':
            schema.twitter_key          = self.twitter_key
            schema.twitter_secret       = self.twitter_secret
        elif schema.__class__.__name__ == 'FacebookAuthSchema':
            schema.facebook_token       = self.facebook_token
        else:
            raise NotImplementedError
        return schema

class HTTPAvailableLinkedAccounts(Schema):
    def setSchema(self):
        self.twitter                = SchemaElement(bool)
        self.facebook               = SchemaElement(bool)

class HTTPAccountChangePassword(Schema):
    def setSchema(self):
        self.old_password       = SchemaElement(basestring, required=True)
        self.new_password       = SchemaElement(basestring, required=True)

class HTTPAccountAlerts(Schema):
    def setSchema(self):
        self.ios_alert_credit       = SchemaElement(bool, default=False)
        self.ios_alert_like         = SchemaElement(bool, default=False)
        self.ios_alert_fav          = SchemaElement(bool, default=False)
        self.ios_alert_mention      = SchemaElement(bool, default=False)
        self.ios_alert_comment      = SchemaElement(bool, default=False)
        self.ios_alert_reply        = SchemaElement(bool, default=False)
        self.ios_alert_follow       = SchemaElement(bool, default=False)
        self.email_alert_credit     = SchemaElement(bool, default=False)
        self.email_alert_like       = SchemaElement(bool, default=False)
        self.email_alert_fav        = SchemaElement(bool, default=False)
        self.email_alert_mention    = SchemaElement(bool, default=False)
        self.email_alert_comment    = SchemaElement(bool, default=False)
        self.email_alert_reply      = SchemaElement(bool, default=False)
        self.email_alert_follow     = SchemaElement(bool, default=False)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Account':
            data = schema.alerts.value
            self.importData(data, overflow=True)
        else:
            raise NotImplementedError
        return self

class HTTPAPNSToken(Schema):
    def setSchema(self):
        self.token              = SchemaElement(basestring, required=True)


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
        self.image_url          = SchemaElement(basestring)
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
            self.num_likes          = stats.pop('num_likes', 0)
            self.num_likes_given    = stats.pop('num_likes_given', 0)

            self.image_url = _profileImageURL(schema.screen_name, schema.image_cache)

        else:
            raise NotImplementedError
        return self

class HTTPSuggestedUser(HTTPUser):
    def setSchema(self):
        HTTPUser.setSchema(self)
        self.explanations       = SchemaList(SchemaElement(basestring))

class HTTPUserMini(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.color_primary      = SchemaElement(basestring)
        self.color_secondary    = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool, required=True)
        self.image_url          = SchemaElement(basestring)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'UserMini':
            self.importData(schema.exportSparse(), overflow=True)
            self.image_url = _profileImageURL(schema.screen_name, schema.image_cache)
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
        self.relationship       = SchemaElement(basestring)

class HTTPSuggestedUsers(Schema):
    def setSchema(self):
        # paging
        self.limit              = SchemaElement(int, default=10)
        self.offset             = SchemaElement(int, default=0)
        
        self.personalized       = SchemaElement(bool, default=False)
        self.coordinates        = SchemaElement(basestring)
        
        # third party keys for optionally augmenting friend suggestions with 
        # knowledge from other social networks
        self.twitter_key        = SchemaElement(basestring)
        self.twitter_secret     = SchemaElement(basestring)
        
        self.facebook_token     = SchemaElement(basestring)
    
    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'SuggestedUserRequest':
            data = self.exportSparse()
            coordinates         = data.pop('coordinates', None)
            schema.importData(data, overflow=True)
            
            if coordinates:
                schema.coordinates    = _coordinatesFlatToDict(coordinates)
        else:
            raise NotImplementedError
        
        return schema

class HTTPUserRelationship(Schema):
    def setSchema(self):
        self.user_id_a          = SchemaElement(basestring)
        self.screen_name_a      = SchemaElement(basestring)
        self.user_id_b          = SchemaElement(basestring)
        self.screen_name_b      = SchemaElement(basestring)

class HTTPFindUser(Schema):
    def setSchema(self):
        self.q                  = SchemaList(SchemaElement(basestring), delimiter=',')

class HTTPFindTwitterUser(Schema):
    def setSchema(self):
        self.q                  = SchemaList(SchemaElement(basestring), delimiter=',')
        self.twitter_key        = SchemaElement(basestring)
        self.twitter_secret     = SchemaElement(basestring)

class HTTPFindFacebookUser(Schema):
    def setSchema(self):
        self.q                  = SchemaList(SchemaElement(basestring), delimiter=',')
        self.facebook_token     = SchemaElement(basestring)
        

# ####### #
# Invites #
# ####### #

class HTTPEmail(Schema):
    def setSchema(self):
        self.email              = SchemaElement(basestring)


# ########## #
# ClientLogs #
# ########## #

class HTTPClientLogsEntry(Schema):
    def setSchema(self):
        self.key                = SchemaElement(basestring, required=True)
        self.value              = SchemaElement(basestring)
        
        # optional ids
        self.stamp_id           = SchemaElement(basestring)
        self.entity_id          = SchemaElement(basestring)
        self.favorite_id        = SchemaElement(basestring)
        self.comment_id         = SchemaElement(basestring)
        self.activity_id        = SchemaElement(basestring)


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
        self.release_date       = SchemaElement(basestring)
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
        self.opentable_m_url    = SchemaElement(basestring)
        self.itunes_url         = SchemaElement(basestring)
        self.itunes_short_url   = SchemaElement(basestring)
        self.netflix_url        = SchemaElement(basestring)
        self.fandango_url       = SchemaElement(basestring)
        self.barnesnoble_url    = SchemaElement(basestring)
        self.amazon_url         = SchemaElement(basestring)

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
            ### TEMP: Remove this until we get good neighborhood data
            # self.neighborhood   = schema.neighborhood
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
                    cleanDate = schema.release_date
                    if cleanDate is not None:
                        self.release_date = str(cleanDate)[:10]
                    else:
                        dateString = schema.original_release_date
                        if len(dateString) == 10:
                            release_date = datetime(int(dateString[0:4]), \
                                                int(dateString[5:7]), \
                                                int(dateString[8:10]))
                            self.release_date   = str(release_date)[:10]
                        elif len(dateString) == 4:
                            self.release_date = dateString
                        else:
                            self.release_date = None
                except:
                    self.release_date   = None
                
                self.length         = schema.track_length
                self.rating         = schema.mpaa_rating
                
                if schema.genre is not None:
                    self.genre = schema.genre
                elif schema.ngenres is not None:
                    self.genre = string.join((str(i) for i in schema.ngenres), '; ')
                
                if schema.short_description != None:
                    new_desc = schema.short_description
                    if new_desc != '' and new_desc != None  and ( self.desc == None or self.desc == '' ):
                        self.desc = new_desc
            
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
            if schema.rid is not None:
                self.opentable_url = "http://www.opentable.com/single.aspx?rid=%s&ref=9166" % \
                                      schema.rid
                self.opentable_m_url = "http://m.opentable.com/Restaurant/Referral?RestID=%s&Ref=9166" % \
                                      schema.rid
            if schema.reserveURL is not None:
                self.opentable_url = "http://www.opentable.com/reserve/%s&ref=9166" % \
                                      schema.reserveURL
            
            if schema.sources.fandango.f_url is not None:
                self.fandango_url = schema.f_url
            
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
            
            if schema.amazon_link != None:
                self.amazon_url = _encodeAmazonURL(schema.amazon_link)
            
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
            
            if schema.subcategory == "album" and schema.tracks is not None:
                self.songs = schema.tracks
            
            if (schema.subcategory == "album" or schema.subcategory == "artist") and schema.albums is not None:
                try:
                    albums = list(album.album_name for album in schema.albums)
                    self.albums = albums
                except:
                    utils.printException()
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
        
        if 'amazon.com' in url:
            # strip the 'look inside' image modifier
            return amazon_image_re.sub(r'\1.jpg', url)
        
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
        self.distance           = SchemaElement(float)
    
    def importSchema(self, schema, distance):
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
            if isinstance(distance, float) and distance >= 0:
                self.distance = distance
            
            if self.subtitle is None:
                entity.subtitle = str(entity.subcategory).replace('_', ' ').title()
        else:
            raise NotImplementedError
        return self

class HTTPEntityId(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring, required=True)

class HTTPEntityIdSearchId(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring)
        self.search_id          = SchemaElement(basestring)

class HTTPEntitySearch(Schema):
    def setSchema(self):
        self.q                  = SchemaElement(basestring, required=True)
        self.coordinates        = SchemaElement(basestring)
        self.category           = SchemaElement(basestring)
        self.subcategory        = SchemaElement(basestring)
        self.local              = SchemaElement(bool)
        self.page               = SchemaElement(int, default=0)
    
    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'EntitySearch':
            schema.importData({'q': self.q})
            schema.coordinates = _coordinatesFlatToDict(self.coordinates)
            schema.importData({'category': self.category})
            schema.importData({'subcategory': self.subcategory})
            schema.importData({'local': self.local})
            schema.importData({'page': self.page})
        else:
            raise NotImplementedError
        return schema

class HTTPEntityNearby(Schema):
    def setSchema(self):
        self.coordinates        = SchemaElement(basestring, required=True)
        self.category           = SchemaElement(basestring)
        self.subcategory        = SchemaElement(basestring)
        self.page               = SchemaElement(int, default=0)
    
    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'EntityNearby':
            schema.coordinates = _coordinatesFlatToDict(self.coordinates)
            schema.importData({'category': self.category})
            schema.importData({'subcategory': self.subcategory})
            schema.importData({'page': self.page})
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
        self.modified           = SchemaElement(basestring)
        self.num_comments       = SchemaElement(int)
        self.num_likes          = SchemaElement(int)
        self.like_threshold_hit = SchemaElement(bool)
        self.is_liked           = SchemaElement(bool)
        self.is_fav             = SchemaElement(bool)
        self.via                = SchemaElement(basestring)
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
            self.user                   = HTTPUserMini().importSchema(schema.user).exportSparse()
            self.entity.coordinates     = _coordinatesDictToFlat(coordinates)
            self.like_threshold_hit     = schema.like_threshold_hit
            self.created                = schema.timestamp.created
            self.modified               = schema.timestamp.modified

            self.num_comments = 0
            if schema.num_comments > 0:
                self.num_comments       = schema.num_comments
            
            self.num_likes = 0
            if schema.num_likes > 0:
                self.num_likes          = schema.num_likes

            self.is_liked = False
            if schema.is_liked:
                self.is_liked = True

            self.is_fav = False
            if schema.is_fav:
                self.is_fav = True

            if self.image_dimensions != None:
                self.image_url = 'http://static.stamped.com/stamps/%s.jpg' % self.stamp_id

            stamp_title = encodeStampTitle(schema.entity.title)
            self.url = 'http://www.stamped.com/%s/stamps/%s/%s' % \
                (schema.user.screen_name, schema.stamp_num, stamp_title)
        
        else:
            logs.error("unknown import class '%s'; expected 'Stamp'" % schema.__class__.__name__)
            raise NotImplementedError
        
        return self

class HTTPImageUpload(Schema):
    def setSchema(self):
        self.image              = SchemaElement(basestring, normalize=False)
        
        # for asynchronous image uploads
        self.temp_image_url     = SchemaElement(basestring)
        self.temp_image_width   = SchemaElement(int)
        self.temp_image_height  = SchemaElement(int)

class HTTPStampNew(HTTPImageUpload):
    def setSchema(self):
        HTTPImageUpload.setSchema(self)
        
        self.entity_id          = SchemaElement(basestring)
        self.search_id          = SchemaElement(basestring)
        self.blurb              = SchemaElement(basestring)
        self.credit             = SchemaList(SchemaElement(basestring), delimiter=',')

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
        # paging
        self.limit              = SchemaElement(int)
        self.offset             = SchemaElement(int)
        
        # sorting
        # (relevance, popularity, proximity, created, modified, alphabetical)
        self.sort               = SchemaElement(basestring, default='modified')
        self.reverse            = SchemaElement(bool,       default=False)
        self.coordinates        = SchemaElement(basestring) # "lat,lng"
        
        # filtering
        self.since              = SchemaElement(int)
        self.before             = SchemaElement(int)
    
    def _convertData(self, data):
        if 'coordinates' in data:
            try:
                lat, lng = data['coordinates'].split(',')
                data['coordinates'] = {
                    'lat' : float(lat), 
                    'lng' : float(lng)
                }
            except:
                raise StampedInputError("invalid coordinates parameter; format \"lat,lng\"")
        
        if 'since' in data:
            try: 
                data['since'] = datetime.utcfromtimestamp(int(data['since']) - 2)
            except:
                raise StampedInputError("invalid since parameter; must be a valid UNIX timestamp")
        
        if 'before' in data:
            try: 
                data['before'] = datetime.utcfromtimestamp(int(data['before']) + 2)
            except:
                raise StampedInputError("invalid since parameter; must be a valid UNIX timestamp")
        
        # TODO: validate since <= before
        
        if 'offset' not in data:
            data['offset'] = 0
        
        return data
    
    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'GenericSlice':
            data = self._convertData(self.exportSparse())
            schema.importData(data)
        else:
            raise NotImplementedError
        
        return schema

class HTTPGenericCollectionSlice(HTTPGenericSlice):
    def setSchema(self):
        HTTPGenericSlice.setSchema(self)
        
        # filtering
        self.query              = SchemaElement(basestring)
        self.category           = SchemaElement(basestring)
        self.subcategory        = SchemaElement(basestring)
        self.viewport           = SchemaElement(basestring) # "lat0,lng0,lat1,lng1"
        
        # misc options
        self.quality            = SchemaElement(int,  default=1)
        self.deleted            = SchemaElement(bool, default=False)
        self.comments           = SchemaElement(bool, default=True)
        self.unique             = SchemaElement(bool, default=False)
    
    def _convertData(self, data):
        data = super(HTTPGenericCollectionSlice, self)._convertData(data)
        
        if 'viewport' in data:
            try:
                lat0, lng0, lat1, lng1 = data['viewport'].split(',')
                
                data['viewport'] = {
                    'upperLeft' : {
                        'lat' : float(lat0), 
                        'lng' : float(lng0), 
                    }, 
                    'lowerRight' : {
                        'lat' : float(lat1), 
                        'lng' : float(lng1), 
                    }
                }
                
                # TODO: validate viewport
            except:
                raise StampedInputError("invalid viewport parameter; format \"lat0,lng0,lat1,lng1\"")
        
        return data
    
    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'GenericCollectionSlice':
            data = self._convertData(self.exportSparse())
            schema.importData(data)
        else:
            raise NotImplementedError
        
        return schema

class HTTPUserCollectionSlice(HTTPGenericCollectionSlice):
    def setSchema(self):
        HTTPGenericCollectionSlice.setSchema(self)
        
        self.user_id            = SchemaElement(basestring)
        self.screen_name        = SchemaElement(basestring)
    
    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'UserCollectionSlice':
            data = self._convertData(self.exportSparse())
            schema.importData(data)
        else:
            raise NotImplementedError
        
        return schema

class HTTPFriendsSlice(HTTPGenericCollectionSlice):
    def setSchema(self):
        HTTPGenericCollectionSlice.setSchema(self)
        
        self.distance           = SchemaElement(int)
        self.inclusive          = SchemaElement(bool)
    
    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'FriendsSlice':
            data = self._convertData(self.exportSparse())
            schema.importData(data)
        else:
            raise NotImplementedError
        
        return schema

class HTTPStampImage(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.image              = SchemaElement(basestring, required=True, normalize=False)

class HTTPDeletedStamp(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.modified           = SchemaElement(basestring)
        self.deleted            = SchemaElement(bool)
    
    def importSchema(self, schema):
        if schema.__class__.__name__ == 'DeletedStamp':
            self.importData(schema.exportSparse(), overflow=True)
            self.modified       = schema.timestamp.modified
        else:
            raise NotImplementedError
        
        return self

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
            self.user = HTTPUserMini().importSchema(schema.user).exportSparse()

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

class HTTPCommentSlice(HTTPGenericSlice):
    def setSchema(self):
        HTTPGenericSlice.setSchema(self)
        
        self.stamp_id           = SchemaElement(basestring, required=True)

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
        self.entity_id          = SchemaElement(basestring)
        self.search_id          = SchemaElement(basestring)
        self.stamp_id           = SchemaElement(basestring)


# ######## #
# Activity #
# ######## #

class HTTPActivity(Schema):
    def setSchema(self):
        # Metadata
        self.activity_id        = SchemaElement(basestring, required=True)
        self.genre              = SchemaElement(basestring, required=True)
        self.user               = HTTPUserMini()
        self.created            = SchemaElement(basestring)
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
        self.linked_user        = HTTPUserMini()
        self.linked_stamp       = HTTPStamp()
        self.linked_entity      = HTTPEntity()
        self.linked_url         = HTTPLinkedURL()

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Activity':
            data                = schema.value
            link                = data.pop('link', {})
            linked_entity       = link.pop('linked_entity', None)
            linked_stamp        = link.pop('linked_stamp', None)
            linked_user         = link.pop('linked_user', None)
            linked_url          = link.pop('linked_url', None)
            user                = data.pop('user', None)

            self.importData(data, overflow=True)

            if user is not None:
                self.user = HTTPUserMini().importSchema(UserMini(user)).value 
            
            if linked_stamp is not None:
                self.linked_stamp = HTTPStamp().importSchema(Stamp(linked_stamp)).value
            elif linked_user is not None:
                self.linked_user = HTTPUserMini().importSchema(UserMini(linked_user)).value
            elif linked_entity is not None:
                self.linked_entity = HTTPEntity().importSchema(Entity(linked_entity)).value
            elif linked_url is not None:
                self.linked_url = HTTPLinkedURL().importSchema(LinkedURL(linked_url)).value

            self.created = schema.timestamp.created
        else:
            raise NotImplementedError
        return self

class HTTPActivitySlice(HTTPGenericSlice):
    def setSchema(self):
        HTTPGenericSlice.setSchema(self)

class HTTPLinkedURL(Schema):
    def setSchema(self):
        self.url                = SchemaElement(basestring, required=True)
        self.chrome             = SchemaElement(bool)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'LinkedURL':
            self.importData(schema.exportSparse(), overflow=True)
        else:
            raise NotImplementedError
        return self


# #### #
# Menu #
# #### #

class HTTPMenu(Schema):
    def setSchema(self):
        self.disclaimer = SchemaElement(basestring)
        self.attribution_image = SchemaElement(basestring)
        self.attribution_image_link = SchemaElement(basestring)
        self.menus = SchemaList(HTTPSubmenu())

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'MenuSchema':
            self.disclaimer = schema.disclaimer
            self.attribution_image = schema.attribution_image
            self.attribution_image_link = schema.attribution_image_link
            self.menus = schema.menus.value
        else:
            raise NotImplementedError
        return self

class HTTPSubmenu(Schema):
    def setSchema(self):
        self.title = SchemaElement(basestring)
        self.times = HTTPTimes()
        self.footnote = SchemaElement(basestring)
        self.desc = SchemaElement(basestring)
        self.short_desc = SchemaElement(basestring)
        self.sections = SchemaList(HTTPMenuSection())

class HTTPMenuSection(Schema):
    def setSchema(self):
        self.title = SchemaElement(basestring)
        self.desc = SchemaElement(basestring)
        self.short_desc = SchemaElement(basestring)
        self.items = SchemaList(HTTPMenuItem())

class HTTPMenuItem(Schema):
    def setSchema(self):
        self.title = SchemaElement(basestring)
        self.desc = SchemaElement(basestring)
        self.categories = SchemaList(SchemaElement(basestring))
        self.short_desc = SchemaElement(basestring)
        self.spicy = SchemaElement(int)
        self.allergens = SchemaList(SchemaElement(basestring))
        self.allergen_free = SchemaList(SchemaElement(basestring))
        self.restrictions = SchemaList(SchemaElement(basestring))
        self.prices = SchemaList(HTTPMenuPrice())

class HTTPMenuPrice(Schema):
    def setSchema(self):
        self.title = SchemaElement(basestring)
        self.price = SchemaElement(basestring)
        self.calories = SchemaElement(int)
        self.unit = SchemaElement(basestring)
        self.currency = SchemaElement(basestring)

class HTTPTimes(Schema):
    def setSchema(self):
        self.sun = SchemaList(HTTPHours())
        self.mon = SchemaList(HTTPHours())
        self.tue = SchemaList(HTTPHours())
        self.wed = SchemaList(HTTPHours())
        self.thu = SchemaList(HTTPHours())
        self.fri = SchemaList(HTTPHours())
        self.sat = SchemaList(HTTPHours())

class HTTPHours(Schema):
    def setSchema(self):
        self.open = SchemaElement(basestring)
        self.close = SchemaElement(basestring)
        self.desc = SchemaElement(basestring)

