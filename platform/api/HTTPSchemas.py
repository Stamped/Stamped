#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import copy, urllib, urlparse, re, logs, string, time, utils

from errors             import *
from schema             import *
from api.Schemas        import *
from libs.LibUtils      import parseDateString
from libs.CountryData   import countries
from Entity             import *
from datetime           import datetime, date, timedelta

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
        url = 'http://static.stamped.com/users/default.jpg'
    elif cache + timedelta(days=1) <= datetime.utcnow():
        url = 'http://static.stamped.com/users/%s.jpg?%s' % \
            (str(screenName).lower(), int(time.mktime(cache.timetuple())))
    else:
        url = 'http://stamped.com.static.images.s3.amazonaws.com/users/%s.jpg?%s' % \
            (str(screenName).lower(), int(time.mktime(cache.timetuple())))
    return url

def _formatURL(url):
    try:
        return url.split('://')[-1].split('/')[0].split('www.')[-1]
    except:
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
    if raw_url is None:
        return None

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
        return raw_url

def _encodeFandangoURL(raw_url):
    return "http://www.qksrv.net/click-5348839-10576761?url=%s" % urllib.quote_plus(raw_url)

def _buildAmazonURL(amazonId):
    return "http://www.amazon.com/dp/%s?tag=%s" % (amazonId, AMAZON_TOKEN)

def _buildOpenTableURL(opentable_id=None, opentable_nickname=None, client=None):
    if opentable_id is not None:
        if client is not None and isinstance(client, Client) and client.is_mobile == True:
            return 'http://m.opentable.com/Restaurant/Referral?RestID=%s&Ref=9166' % opentable_id
        else:
            return 'http://www.opentable.com/single.aspx?rid=%s&ref=9166' % opentable_id

    if opentable_nickname is not None:
        return 'http://www.opentable.com/reserve/%s&ref=9166' % opentable_nickname

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
        # Core
        self.entity_id          = SchemaElement(basestring, required=True)
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring, required=True)
        self.category           = SchemaElement(basestring, required=True)
        self.subcategory        = SchemaElement(basestring, required=True)
        self.caption            = SchemaElement(basestring)
        self.images             = SchemaList(ImageSchema())
        self.last_modified      = SchemaElement(basestring)
        
        # Location
        self.address            = SchemaElement(basestring)
        self.neighborhood       = SchemaElement(basestring)
        self.coordinates        = SchemaElement(basestring)
        
        # Components
        self.playlist           = HTTPEntityPlaylist()
        self.actions            = SchemaList(HTTPEntityAction())
        self.gallery            = HTTPEntityGallery()
        self.metadata           = SchemaList(HTTPEntityMetadataItem())
        self.stamped_by         = HTTPEntityStampedBy()
        self.related            = HTTPEntityRelated()


    def _addAction(self, actionType, name, sources, **kwargs):
        if len(sources) > 0:
            action          = HTTPAction()
            action.type     = actionType
            for i in xrange(len(sources)):
                if sources[i].link is None:
                    del(sources[i].link)
            action.sources  = sources
            action.name     = name

            item            = HTTPEntityAction()
            item.action     = action
            item.name       = name

            if 'icon' in kwargs:
                item.icon = kwargs['icon']

            self.actions.append(item)

    def _addMetadata(self, name, value, **kwargs):
        if value is not None and len(value) > 0:
            item = HTTPEntityMetadataItem()
            item.name = name

            if isinstance(value, list):
                value = ', '.join(i for i in value)
            item.value = value

            if 'key' in kwargs:
                item.key = kwargs['key']

            if 'icon' in kwargs:
                item.icon = kwargs['icon']

            if 'extended' in kwargs:
                item.extended = kwargs['extended']

            if 'optional' in kwargs:
                item.optional = kwargs['optional']

            if 'link' in kwargs:
                actionSource = HTTPActionSource()
                actionSource.link = kwargs['link']
                actionSource.name = 'View link'
                actionSource.source = 'link'

                action = HTTPAction()
                action.type = 'link'
                action.name = 'View link'
                action.sources.append(actionSource)

                item.action = action

            self.metadata.append(item)
    
    def _addImages(self, images):
        for image in images:
            if image.image is not None:
                url = image.image
                domain = urlparse.urlparse(url).netloc

                if 'amzstatic.com' in domain:
                    # try to return the maximum-resolution apple photo possible if we have 
                    # a lower-resolution version stored in our db
                    url = url.replace('100x100', '400x400').replace('170x170', '400x400')
                
                elif 'amazon.com' in domain:
                    # strip the 'look inside' image modifier
                    url = amazon_image_re.sub(r'\1.jpg', url)
            
                item = ImageSchema()
                item.image = url 
                self.images.append(item)

    def _getIconURL(self, filename, client=None):
        base_url = 'http://static.stamped.com/assets/icons'

        if client is None or not isinstance(client, Client):
            return '%s/default/%s.png' % (base_url, filename)

        if client.client_class == 'iphone':
            if client.resolution == 2:
                return '%s/iphone/2x/%s.png' % (base_url, filename)
            else:
                return '%s/iphone/1x/%s.png' % (base_url, filename)

        if client.client_class == 'web':
            return '%s/web/%s.png' % (base_url, filename)

        return '%s/default/%s.png' % (base_url, filename)


    def importEntity(self, entity, client=None):
        # General
        self.entity_id          = entity.entity_id
        self.title              = entity.title 
        self.subtitle           = entity.subtitle 
        self.category           = entity.category 
        self.subcategory        = entity.subcategory
        
        self.caption            = self.subtitle # Default
        self.last_modified      = entity.timestamp.created

        subcategory             = formatSubcategory(self.subcategory)
        
        # Restaurant / Bar
        if entity.kind == 'place' and entity.category == 'food':
            self.address        = entity.formatted_address
            self.coordinates    = _coordinatesDictToFlat(self.coordinates)

            address = formatAddress(entity, extendStreet=True, breakLines=True)
            if address is not None:
                self.caption = address 

            # Metadata
            self._addMetadata('Category', subcategory, icon=self._getIconURL('cat_food', client=client))
            self._addMetadata('Cuisine', entity.cuisine)
            self._addMetadata('Price', entity.price_range * '$' if entity.price_range is not None else None)
            self._addMetadata('Site', _formatURL(entity.site), link=entity.site)
            self._addMetadata('Description', entity.desc, key='desc', extended=True)

            # Actions: Reservation

            sources = []

            if entity.sources.opentable_id is not None or entity.sources.opentable_nickname is not None:
                source              = HTTPActionSource()
                source.name         = 'Reserve on OpenTable'
                source.source       = 'opentable'
                source.source_id    = entity.sources.opentable_id
                source.link         = _buildOpenTableURL(entity.opentable_id, entity.opentable_nickname, client)
                source.icon         = self._getIconURL('src_opentable', client=client)
                sources.append(source)

            actionIcon = self._getIconURL('act_reserve_primary', client=client)
            self._addAction('reserve', 'Reserve a table', sources, icon=actionIcon)

            # Actions: Call

            sources = []

            if entity.contact.phone is not None:
                source              = HTTPActionSource()
                source.source       = 'phone'
                source.source_id    = entity.contact.phone
                sources.append(source)

            actionIcon = self._getIconURL('act_call', client=client)
            self._addAction('phone', entity.contact.phone, sources, icon=actionIcon)

            # Actions: View Menu

            sources = []

            if entity.singleplatform_id is not None:
                source              = HTTPActionSource()
                source.name         = 'View menu'
                source.source       = 'menu'
                source.source_id    = entity.entity_id
                sources.append(source)

            actionIcon = self._getIconURL('act_menu', client=client)
            self._addAction('menu', 'View menu', sources, icon=actionIcon)

        # Generic Place
        elif entity.kind == 'place':
            self.address        = entity.formatted_address
            self.coordinates    = _coordinatesDictToFlat(self.coordinates)

            address = formatAddress(entity, extendStreet=True, breakLines=True)
            if address is not None:
                self.caption = address 

            # Metadata
            
            self._addMetadata('Category', subcategory, icon=self._getIconURL('cat_place', client=client))
            self._addMetadata('Description', entity.desc, key='desc')
            self._addMetadata('Site', _formatURL(entity.site), link=entity.site)

            # Actions: Call

            sources = []

            if entity.contact.phone is not None:
                source              = HTTPActionSource()
                source.source       = 'phone'
                source.source_id    = entity.contact.phone
                sources.append(source)

            actionIcon = self._getIconURL('act_call', client=client)
            self._addAction('phone', entity.contact.phone, sources, icon=actionIcon)

        # Book
        elif entity.kind == 'media_item' and 'book' in entity.types.value:

            if entity.authors is not None:
                self.caption = 'by %s' % ', '.join(str(i.title) for i in entity.authors)

            # Metadata

            self._addMetadata('Category', entity.subcategory, icon=self._getIconURL('cat_book', client=client))
            self._addMetadata('Publish Date', entity.release_date)
            self._addMetadata('Description', entity.desc, key='desc', extended=True)
            self._addMetadata('Publisher', entity.publishers)

            # Actions: Buy

            sources = []

            if entity.sources.amazon_underlying is not None:
                source              = HTTPActionSource()
                source.name         = 'Buy from Amazon'
                source.source       = 'amazon'
                source.source_id    = entity.sources.amazon_underlying
                source.icon         = self._getIconURL('src_amazon', client=client)
                source.link         = _buildAmazonURL(entity.sources.amazon_underlying)
                sources.append(source)

            actionIcon = self._getIconURL('act_buy_primary', client=client)
            self._addAction('buy', 'Buy now', sources, icon=actionIcon)

        # Movie
        elif entity.kind == 'media_item' and 'movie' in entity.types.value:

            if entity.subcategory == 'movie' and entity.length is not None:
                length = formatFilmLength(entity.length)
                if length is not None:
                    self.caption = length

            if entity.subcategory == 'tv' and entity.network_name is not None:
                self.caption = entity.network_name

            # Metadata

            self._addMetadata('Category', entity.subcategory, icon=self._getIconURL('cat_film', client=client))
            self._addMetadata('Overview', entity.desc, key='desc', extended=True)
            self._addMetadata('Release Date', formatReleaseDate(entity.release_date))
            self._addMetadata('Cast', entity.cast, extended=True, optional=True)
            self._addMetadata('Director', entity.directors, optional=True)
            self._addMetadata('Genres', entity.genres, optional=True)
            if entity.subcategory == 'movie':
                self._addMetadata('Rating', entity.mpaa_rating, key='rating', optional=True)

            # Actions: Watch Now

            sources = []

            if entity.sources.itunes_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Watch on iTunes'
                source.source       = 'itunes'
                source.source_id    = entity.sources.itunes_id
                source.link         = _encodeiTunesShortURL(entity.itunes_url)
                source.icon         = self._getIconURL('src_itunes', client=client)
                sources.append(source)

            actionIcon = self._getIconURL('act_play_primary', client=client)
            self._addAction('watch', 'Watch now', sources, icon=actionIcon)

            # Actions: Find Tickets

            sources = []

            if entity.sources.fandango_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Buy from Fandango'
                source.source       = 'fandango'
                source.source_id    = entity.sources.fandango_id
                source.link         = entity.sources.fandango_url 
                # Only add icon if no "watch now"
                if len(self.actions) == 0:
                    source.icon   = self._getIconURL('src_fandango', client=client)
                sources.append(source)

            actionIcon = self._getIconURL('act_ticket_primary', client=client)
            if len(self.actions) == 0:
                actionIcon = self._getIconURL('act_ticket', client=client)
            self._addAction('tickets', 'Find tickets', sources, icon=actionIcon)

            # Actions: Add to Queue

            ### TODO: Add Netflix

            # Actions: Watch Trailer

            ### TODO: Add source

            # Actions: Download

            sources = []

            if entity.sources.amazon_underlying is not None:
                source              = HTTPActionSource()
                source.name         = 'Buy from Amazon'
                source.source       = 'amazon'
                source.source_id    = entity.sources.amazon_underlying
                source.link         = _buildAmazonURL(entity.sources.amazon_underlying)
                sources.append(source)

            actionIcon = self._getIconURL('act_buy', client=client)
            self._addAction('buy', 'Buy', sources, icon=actionIcon)

        # Music
        elif entity.category == 'music':

            if entity.subcategory == 'artist':
                self.caption = 'Artist'

            elif entity.subcategory == 'album' and entity.artists is not None:
                self.caption = 'by %s' % ', '.join(str(i.title) for i in entity.artists)

            elif entity.subcategory == 'song' and entity.artists is not None:
                self.caption = 'by %s' % ', '.join(str(i.title) for i in entity.artists)

            # Metadata

            self._addMetadata('Category', subcategory, icon=self._getIconURL('cat_music', client=client))
            if entity.subcategory == 'artist':
                self._addMetadata('Biography', entity.desc, key='desc')
                self._addMetadata('Genre', entity.genres, optional=True)

            elif entity.subcategory == 'album':
                self._addMetadata('Genre', entity.genres)
                self._addMetadata('Release Date', formatReleaseDate(entity.release_date))
                self._addMetadata('Album Details', entity.desc, key='desc', optional=True)

            elif entity.subcategory == 'song':
                self._addMetadata('Genre', entity.genres)
                self._addMetadata('Release Date', formatReleaseDate(entity.release_date))
                self._addMetadata('Song Details', entity.desc, key='desc', optional=True)

            # Actions: Listen

            sources = []

            if entity.sources.itunes_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Listen on iTunes'
                source.source       = 'itunes'
                source.source_id    = entity.sources.itunes_id
                source.icon         = self._getIconURL('src_itunes', client=client)
                source.link         = _encodeiTunesShortURL(entity.itunes_url)
                sources.append(source)

            if entity.sources.rdio_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Listen on Rdio'
                source.source       = 'rdio'
                source.source_id    = entity.sources.rdio_id
                source.icon         = self._getIconURL('src_rdio', client=client)
                source.link         = entity.rdio_url
                sources.append(source)

            if entity.sources.spotify_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Listen on Spotify'
                source.source       = 'spotify'
                source.source_id    = entity.sources.spotify_id
                source.icon         = self._getIconURL('src_spotify', client=client)
                sources.append(source)

            actionTitle = 'Listen'
            if entity.subcategory == 'artist':
                actionTitle = 'Listen to top songs'
            elif entity.subcategory == 'album':
                actionTitle = 'Listen to album'
            elif entity.subcategory == 'song':
                actionTitle = 'Listen to song'
                    
            actionIcon = self._getIconURL('act_play_primary', client=client)
            self._addAction('listen', actionTitle, sources, icon=actionIcon)

            # Actions: Add to Playlist

            sources = []

            if entity.sources.rdio_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Add to playlist on Rdio'
                source.source       = 'rdio'
                source.source_id    = entity.sources.rdio_id
                sources.append(source)

            if entity.sources.spotify_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Add to playlist on Spotify'
                source.source       = 'spotify'
                source.source_id    = entity.sources.spotify_id
                sources.append(source)

            actionTitle = 'Add to playlist'
            if entity.subcategory == 'artist':
                actionTitle = 'Add artist to playlist'
            
            actionIcon = self._getIconURL('act_playlist_music', client=client)
            self._addAction('playlist', actionTitle, sources, icon=actionIcon)

            # Actions: Download

            sources = []

            if entity.sources.itunes_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Download from iTunes'
                source.source       = 'itunes'
                source.source_id    = entity.sources.itunes_id
                source.link         = _encodeiTunesShortURL(entity.itunes_url)
                sources.append(source)

            actionTitle = 'Download %s' % entity.subcategory
            actionIcon  = self._getIconURL('act_download', client=client)
            self._addAction('download', actionTitle, sources, icon=actionIcon)

            # Playlist
        
            if entity.subcategory in ["album", "artist"] and entity.tracks is not None:
                playlist = HTTPEntityPlaylist()

                if entity.subcategory == 'album':
                    playlist.name = 'Tracks'
                else:
                    playlist.name = 'Top songs'

                for i in range(len(entity.tracks))[:50]:
                    try:
                        song = entity.tracks[i]
                        item = HTTPEntityPlaylistItem()
                        # item.length = song.length
                        item.num = i + 1
                        item.icon = None ### TODO

                        sources = []

                        if song.sources.itunes_id is not None:
                            source              = HTTPActionSource()
                            source.name         = 'Listen on iTunes'
                            source.source       = 'itunes'
                            source.source_id    = song.sources.itunes_id
                            source.icon         = self._getIconURL('src_itunes', client=client)
                            sources.append(source)

                        if song.sources.rdio_id is not None:
                            source              = HTTPActionSource()
                            source.name         = 'Listen on Rdio'
                            source.source       = 'rdio'
                            source.source_id    = song.sources.rdio_id
                            source.icon         = self._getIconURL('src_rdio', client=client)
                            sources.append(source)

                        if song.sources.spotify_id is not None:
                            source              = HTTPActionSource()
                            source.name         = 'Listen on Spotify'
                            source.source       = 'spotify'
                            source.source_id    = song.sources.spotify_id
                            source.icon         = self._getIconURL('src_spotify', client=client)
                            sources.append(source)

                        if len(sources) > 0:
                            action = HTTPAction()
                            action.type = 'listen'
                            action.name = 'Listen to song'
                            action.sources = sources

                            item.action = action

                        playlist.data.append(item)

                    except Exception:
                        pass

                if len(playlist.data) > 0:
                    self.playlist = playlist

        elif entity.kind == 'software' and 'app' in entity.types.value:

            if entity.authors is not None:
                self.caption = 'by %s' % ', '.join(str(i.title) for i in entity.authors)

            # Metadata

            self._addMetadata('Category', subcategory, icon=self._getIconURL('cat_app', client=client))
            self._addMetadata('Genre', entity.genres)
            self._addMetadata('Description', entity.desc, key='desc', extended=True)

            # Actions: Download

            sources = []

            if entity.sources.itunes_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Download from iTunes'
                source.source       = 'itunes'
                source.source_id    = entity.sources.itunes_id
                source.icon         = self._getIconURL('src_itunes', client=client)
                source.link         = _encodeiTunesShortURL(entity.itunes_url)
                sources.append(source)

            actionIcon = self._getIconURL('act_download_primary', client=client)
            self._addAction('download', 'Download', sources, icon=actionIcon)

            # Gallery

            if entity.screenshots is not None:

                for screenshot in entity.screenshots:
                    item = HTTPEntityGalleryItem()
                    item.image = screenshot.image
                    self.gallery.data.append(item)


        # Generic item
        else:

            # Metadata

            self._addMetadata('Category', subcategory, icon=self._getIconURL('cat_other', client=client))
            self._addMetadata('Description', entity.desc, key='desc')
            self._addMetadata('Site', _formatURL(entity.site), link=entity.site)

        
        # Image

        if entity.kind == 'place':
            # Don't add an image if coordinates exist
            del(self.images)
        elif len(entity.images) > 0:
            self._addImages(entity.images)

        return self
            
    def importSchema(self, schema, client=None):
        if schema.__class__.__name__ == 'EntityMini':
            data                = schema.value
            coordinates         = data.pop('coordinates', None)
            self.importData(data, overflow=True)
            self.coordinates    = _coordinatesDictToFlat(coordinates)
        else:
            raise NotImplementedError
        return self

# HTTPEntity Components

class HTTPAction(Schema):
    def setSchema(self):
        self.type               = SchemaElement(basestring, required=True)
        self.name               = SchemaElement(basestring, required=True)
        self.sources            = SchemaList(HTTPActionSource(), required=True)

class HTTPActionSource(Schema):
    def setSchema(self):
        self.name               = SchemaElement(basestring, required=True)
        self.source             = SchemaElement(basestring, required=True)
        self.source_id          = SchemaElement(basestring)
        self.endpoint           = SchemaElement(basestring)
        self.link               = SchemaElement(basestring)
        self.icon               = SchemaElement(basestring)

class HTTPEntityAction(Schema):
    def setSchema(self):
        self.action             = HTTPAction(required=True)
        self.name               = SchemaElement(basestring, required=True)
        self.icon               = SchemaElement(basestring)

class HTTPEntityMetadataItem(Schema):
    def setSchema(self):
        self.name               = SchemaElement(basestring, required=True)
        self.value              = SchemaElement(basestring, required=True)
        self.key                = SchemaElement(basestring)
        self.action             = HTTPAction()
        self.icon               = SchemaElement(basestring)
        self.extended           = SchemaElement(bool)
        self.optional           = SchemaElement(bool)

class HTTPEntityGallery(Schema):
    def setSchema(self):
        self.data               = SchemaList(HTTPEntityGalleryItem(), required=True)
        self.name               = SchemaElement(basestring)

class HTTPEntityGalleryItem(Schema):
    def setSchema(self):
        self.image              = SchemaElement(basestring, required=True)
        self.action             = HTTPAction()
        self.caption            = SchemaElement(basestring)
        self.height             = SchemaElement(int)
        self.width              = SchemaElement(int)

class HTTPEntityPlaylist(Schema):
    def setSchema(self):
        self.data               = SchemaList(HTTPEntityPlaylistItem(), required=True)
        self.name               = SchemaElement(basestring)

class HTTPEntityPlaylistItem(Schema):
    def setSchema(self):
        self.name               = SchemaElement(basestring, required=True)
        self.action             = HTTPAction()
        self.num                = SchemaElement(int)
        self.length             = SchemaElement(int)
        self.icon               = SchemaElement(basestring)

class HTTPEntityStampedBy(Schema):
    def setSchema(self):
        self.friends            = SchemaElement(int, required=True)
        self.friends_of_friends = SchemaElement(int)
        self.everyone           = SchemaElement(int)

class HTTPEntityRelated(Schema):
    def setSchema(self):
        self.data               = SchemaList(HTTPEntityMini(), required=True)
        self.title              = SchemaElement(basestring)

# Related

class HTTPEntityMini(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring, required=True)
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring, required=True)
        self.category           = SchemaElement(basestring, required=True)
        self.subcategory        = SchemaElement(basestring, required=True)
        self.coordinates        = SchemaElement(basestring)

    def importSchema(self, schema):
        if isinstance(schema, BasicEntity):
            self.entity_id      = schema.entity_id
            self.title          = schema.title 
            self.subtitle       = schema.subtitle
            self.category       = schema.category
            self.subcategory    = schema.subcategory 

            try:
                self.coordinates    = _coordinatesDictToFlat(schema.coordinates)
            except:
                pass
        else:
            raise NotImplementedError
        return self


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

    def exportEntity(self, authUserId):

        kind    = deriveKindFromSubcategory(self.subcategory)
        entity  = buildEntity(kind=kind)

        entity.schema_version   = 0
        entity.types            = list(deriveTypesFromSubcategories([self.subcategory]))
        entity.title            = self.title 
        # TODO: Add subtitle

        def addField(entity, field, value, timestamp):
            if value is not None:
                try:
                    entity[field] = value
                    entity['%s_source' % field] = 'seed'
                    entity['%s_timestamp' % field] = timestamp
                except:
                    pass

        def addListField(entity, field, value, entityMini=None, timestamp=None):
            if value is not None:
                try:
                    if entityMini is not None:
                        item = entityMini()
                        entityMini.title = value
                    else:
                        item = value
                    entity[field].append(item)
                    entity['%s_source' % field] = 'seed'
                    entity['%s_timestamp' % field] = timestamp
                except:
                    pass

        now = datetime.utcnow()

        addField(entity, 'desc', self.desc, now)
        addField(entity, 'formatted_address', self.address, now)
        addField(entity, 'release_date', self.release_date, now)

        if _coordinatesFlatToDict(self.coordinates) is not None:
            addField(entity, 'coordinates', _coordinatesFlatToDict(self.coordinates), now)

        entity.user_generated_id            = authUserId
        entity.user_generated_subtitle      = self.subtitle
        entity.user_generated_timestamp     = now

        addListField(entity, 'directors', self.director, PersonEntityMini, now)
        addListField(entity, 'cast', self.cast, PersonEntityMini, now)
        addListField(entity, 'authors', self.author, PersonEntityMini, now)
        addListField(entity, 'artists', self.artist, PersonEntityMini, now)
        addListField(entity, 'collections', self.album, MediaCollectionEntityMini, now)

        return entity

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
                'type':         deriveTypesFromSubcategories([self.subcategory])[-1],
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
        if isinstance(schema, BasicEntity):

            self.search_id = schema.entity_id
            assert self.search_id is not None

            self.title          = schema.title 
            self.subtitle       = schema.subtitle
            self.category       = schema.category 

            if isinstance(distance, float) and distance >= 0:
                self.distance   = distance    

        elif schema.__class__.__name__ == 'Entity':
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

class HTTPEntityActionEndpoint(Schema):
    def setSchema(self):
        self.status             = SchemaElement(basestring)
        self.message            = SchemaElement(basestring)
        self.redirect           = SchemaElement(basestring)


# ###### #
# Stamps #
# ###### #

class HTTPStamp(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.entity             = HTTPEntityMini(required=True)
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

            data['entity'] = HTTPEntityMini().importSchema(schema.entity).exportSparse()

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

class HTTPStampedBySlice(HTTPGenericCollectionSlice):
    def setSchema(self):
        HTTPGenericCollectionSlice.setSchema(self)
        
        self.entity_id          = SchemaElement(basestring, required=True)
        self.group              = SchemaElement(basestring)
    
    def exportSchema(self, schema):
        if schema.__class__.__name__ in ['FriendsSlice', 'GenericCollectionSlice']:
            data = self._convertData(self.exportSparse())
            schema.importData(data, overflow=True)
        else:
            raise NotImplementedError
        
        return schema

class HTTPStampedBy(Schema):
    def setSchema(self):
        self.friends            = HTTPStampedByGroup()
        self.fof                = HTTPStampedByGroup()
        self.all                = HTTPStampedByGroup()

class HTTPStampedByGroup(Schema):
    def setSchema(self):
        self.count              = SchemaElement(int)
        self.stamps             = SchemaList(HTTPStamp())

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
        self.entity             = HTTPEntityMini(required=True)
        self.stamp              = HTTPStamp()
        self.created            = SchemaElement(basestring)
        self.complete           = SchemaElement(bool)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Favorite':
            self.favorite_id    = schema.favorite_id 
            self.user_id        = schema.user_id
            self.entity         = HTTPEntityMini().importSchema(schema.entity).exportSparse()
            self.created        = schema.timestamp.created
            self.complete       = schema.complete 

            if schema.stamp.isSet:
                self.stamp      = HTTPStamp().importSchema(schema.stamp).exportSparse()

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


# ########## #
# Deprecated #
# ########## #

class HTTPEntity_stampedtest(Schema):
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
        self.genre              = SchemaElement(basestring)
        
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

        if 'ntity' not in schema.__class__.__name__:
            raise NotImplementedError

        validEntities = set([
            'BasicEntity',
            'PlaceEntity',
            'PersonEntity',
            'MediaCollectionEntity',
            'MediaItemEntity',
            'SoftwareEntity',
        ])

        if schema.__class__.__name__ in validEntities:
            # setFields(schema)
            
            self.entity_id          = schema.entity_id
            self.title              = schema.title 
            self.subtitle           = schema.subtitle 
            self.category           = schema.category
            self.subcategory        = schema.subcategory
            self.desc               = schema.desc 
            self.last_modified      = schema.timestamp.created 

            self.phone              = schema.phone
            self.site               = schema.site 

            # TODO: Image
            if len(schema.images) > 0:
                self.image = self._handle_image(schema.images[0]['image'])

            # Affiliates

            if schema.sources.fandango_url is not None:
                self.fandango_url   = schema.sources.fandango_url

            if schema.sources.itunes_url is not None:
                base        = "http://click.linksynergy.com/fs-bin/stat"
                params      = "id=%s&offerid=146261&type=3&subid=0&tmpid=1826" % LINKSHARE_TOKEN
                deep_url    = "%s?%s&RD_PARM1=%s" % (base, params, _encodeLinkShareDeepURL(schema.sources.itunes_url))
                short_url   = _encodeiTunesShortURL(schema.sources.itunes_url)
                self.itunes_url       = deep_url
                self.itunes_short_url = short_url

            if schema.sources.amazon_url is not None:
                self.amazon_url     = _encodeAmazonURL(schema.sources.amazon_url)

            if schema.sources.opentable_id is not None:
                opentable_id = schema.sources.opentable_id
                self.opentable_url = "http://www.opentable.com/single.aspx?rid=%s&ref=9166" % opentable_id
                self.opentable_m_url = "http://m.opentable.com/Restaurant/Referral?RestID=%s&Ref=9166" % opentable_id

        if schema.__class__.__name__ == 'PlaceEntity':

            self.address            = schema.formatted_address
            self.coordinates        = _coordinatesDictToFlat(schema.coordinates)

            if schema.cuisine is not None:
                self.cuisine        = ', '.join(str(i) for i in schema.cuisine)

            if schema.price_range is not None:
                self.price_scale    = '$' * schema.price_range

        if schema.__class__.__name__ == 'PersonEntity':

            if schema.genres is not None:
                self.genre          = ', '.join(str(i) for i in schema.genres)

            if schema.tracks is not None:
                tracks = schema.tracks[:10]
                for track in tracks:
                    self.songs.append(track['title'])

            for album in schema.albums:
                self.albums.append(album['title'])

        if schema.__class__.__name__ in ['MediaCollectionEntity', 'MediaItemEntity']:

            self.length             = schema.length 
            self.rating             = schema.mpaa_rating

            if schema.release_date is not None:
                self.release_date   = schema.release_date.strftime("%h %d, %Y")

            if schema.genres is not None:
                self.genre          = ', '.join(str(i) for i in schema.genres)


            if schema.authors is not None:
                self.author         = ', '.join(str(i) for i in schema.authors)

            if schema.artists is not None:
                self.artist_name    = ', '.join(str(i) for i in schema.artists)

            if schema.publishers is not None:
                self.publisher      = ', '.join(str(i) for i in schema.publishers)

            if schema.cast is not None:
                self.cast           = ', '.join(str(i) for i in schema.cast)

            if schema.directors is not None:
                self.director       = ', '.join(str(i) for i in schema.directors)

            if schema.networks is not None:
                self.network        = ', '.join(str(i) for i in schema.networks)

        if schema.__class__.__name__ == 'MediaItemEntity':

            self.isbn               = schema.isbn

        if schema.__class__.__name__ == 'SoftwareEntity':

            pass

        if schema.__class__.__name__ == 'EntityMini':
            data                = schema.value
            coordinates         = data.pop('coordinates', None)
            self.importData(data, overflow=True)
            self.coordinates    = _coordinatesDictToFlat(coordinates)

        return self
    
    def _handle_image(self, url):
        if url is not None:
            domain = urlparse.urlparse(url).netloc

            if 'amzstatic.com' in domain:
                # try to return the maximum-resolution apple photo possible if we have 
                # a lower-resolution version stored in our db
                url = url.replace('100x100', '200x200').replace('170x170', '200x200')
            
            elif 'amazon.com' in domain:
                # strip the 'look inside' image modifier
                url = amazon_image_re.sub(r'\1.jpg', url)
            
        return url