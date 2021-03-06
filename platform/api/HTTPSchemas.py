#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import copy, urllib, urlparse, re, logs, string, time, utils
import libs.ec2_utils
from api import Entity

from errors             import *
from schema             import *
from api.Schemas        import *
from api.Entity             import *
from api.SchemaValidation   import *

from libs.LibUtils      import parseDateString
from libs.CountryData   import countries
from datetime           import datetime, date, timedelta


# ####### #
# PRIVATE #
# ####### #

COMPLETION_ENDPOINT = 'actions/complete.json'

LINKSHARE_TOKEN = 'QaV3NQJNPRA'
FANDANGO_TOKEN  = '5348839'
AMAZON_TOKEN    = 'stamped01-20'

amazon_image_re = re.compile('(.*)\.[^/.]+\.jpg')
non_numeric_re  = re.compile('\D')
mention_re      = re.compile(r'(?<![a-zA-Z0-9_])@([a-zA-Z0-9+_]{1,20})(?![a-zA-Z0-9_])', re.IGNORECASE)
# URL regex taken from http://daringfireball.net/2010/07/improved_regex_for_matching_urls (via http://stackoverflow.com/questions/520031/whats-the-cleanest-way-to-extract-urls-from-a-string-using-python)
url_re          = re.compile(r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(‌​([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))""", re.DOTALL)

def generateStampUrl(stamp):
    #url_title = encodeStampTitle(stamp.entity.title)
    
    # NOTE (travis): as of June 2012, we've shortened our sdetail URLs.
    # Also note that the v1 URL format will continue to be supported by the web client.
    # Going forward (after v2 launch), we'd like to support both verbose and shortened 
    # versions, with the shortened version being an actual hash instead of the short-ish 
    # version we're using today.
    
    # v1: http://www.stamped.com/{{screen_name}}/stamps/{{stamp_num}}/{{entity_title}}
    # v2: http://www.stamped.com/{{screen_name}}/s/{{stamp_num}}
    
    # TODO: remove the implicit http:// prefix here?
    return 'http://www.stamped.com/%s/s/%s' % (stamp.user.screen_name, stamp.stats.stamp_num)

def _coordinatesDictToFlat(coordinates):
    try:
        if isinstance(coordinates, Schema):
            coordinates = coordinates.dataExport()

        if not isinstance(coordinates['lat'], float) or not isinstance(coordinates['lng'], float):
            raise

        return '%s,%s' % (coordinates['lat'], coordinates['lng'])
    except Exception as e:
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
    except Exception:
        return None

def _profileImageURL(screenName, cache=None, size=None):
    image = "%s.jpg" % (str(screenName).lower())
    if size is not None:
        image = "%s-%dx%d.jpg" % (str(screenName).lower(), size, size)
    
    if not cache:
        url = 'http://static.stamped.com/users/default.jpg'
    elif cache + timedelta(days=1) <= datetime.utcnow():
        url = 'http://static.stamped.com/users/%s?%s' % \
              (image, int(time.mktime(cache.timetuple())))
    else:
        url = 'http://stamped.com.static.images.s3.amazonaws.com/users/%s?%s' % \
              (image, int(time.mktime(cache.timetuple())))

    return url

def _formatURL(url):
    try:
        return url.split('://')[-1].split('/')[0].split('www.')[-1]
    except Exception:
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
    except Exception:
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

def _getIconURL(filename, client=None):
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

def _cleanImageURL(url):
    domain = urlparse.urlparse(url).netloc

    if 'mzstatic.com' in domain:
        # try to return the maximum-resolution apple photo possible if we have 
        # a lower-resolution version stored in our db
        url = url.replace('100x100', '200x200').replace('170x170', '200x200')

    elif 'amazon.com' in domain:
        # strip the 'look inside' image modifier
        url = amazon_image_re.sub(r'\1.jpg', url)
    elif 'nflximg.com' in domain:
        # replace the large boxart with hd
        url = url.replace('/large/', '/ghd/')

    return url

def _phoneToInt(string):
    if string is None:
        return None 

    try:
        return int(string)
    except ValueError:
        pass 

    try:
        digits = re.findall(r'\d+', string)
        return int("".join(digits))
    except Exception as e:
        logs.warning("Unable to convert phone number to int (%s): %s" % (string, e))
        return None

def _convertViewport(string):
    try:
        viewportData            = string.split(',')

        coordinates0            = Coordinates()
        coordinates0.lat        = viewportData[0]
        coordinates0.lng        = viewportData[1]

        coordinates1            = Coordinates()
        coordinates1.lat        = viewportData[2]
        coordinates1.lng        = viewportData[3]

        viewport                = Viewport()
        viewport.upper_left     = coordinates0
        viewport.lower_right    = coordinates1

        return viewport
    except Exception as e:
        logs.warning("Unable to convert viewport (%s): %s" % (string, e))
        raise StampedInputError("Invalid viewport: %s" % string)

def _buildTextReferences(text):
    """
    Extract @mention and URL references from a blurb (e.g. stamp blurb or comment blurb)

    This creates a "view" action for any user mentions extracted. It also creates a "link" action
    for any URLs it can parse. Additionally, it attempts to replace the full URL with a "prettified"
    URL that's shorter. This is the only complex part of this section, since the indices of any 
    after a shortened URL need to be updated.
    """
    refs = []
    offsets = {}

    if text is None:
        return None, []

    # Mentions
    mentions = mention_re.finditer(text)
    for item in mentions:
        source = HTTPActionSource()
        source.name = 'View profile'
        source.source = 'stamped'
        source.source_id = item.groups()[0]

        action = HTTPAction()
        action.type = 'stamped_view_screen_name'
        action.name = 'View profile'
        action.sources = [ source ]

        reference = HTTPTextReference()
        reference.indices = [ item.start(), item.end() ]
        reference.action = action

        refs.append(reference)

    # URL
    urls = url_re.finditer(text)
    for item in url_re.finditer(text):
        url = item.groups()[0]
        formatted = url.split('://')[-1].split('?')[0]
        if '/' in formatted:
            truncated = "%s..." % formatted[:formatted.index('/')+4]
            if len(truncated) < len(formatted):
                formatted = truncated
        offsets[item.end()] = len(formatted) - len(url)
        text = string.replace(text, url, formatted)

        source = HTTPActionSource()
        source.link = url
        source.name = 'Go to %s' % formatted
        source.source = 'link'

        action = HTTPAction()
        action.type = 'link'
        action.name = 'Go to %s' % formatted
        action.sources = [ source ]

        reference = HTTPTextReference()
        reference.indices = [ item.start(), item.end() ]
        reference.action = action

        refs.append(reference)

    # Update any references affected by changing the URL text
    for ref in refs:
        indices = ref.indices
        for position, offset in offsets.items():
            if position <= ref.indices[0]:
                indices = (indices[0] + offset, indices[1] + offset)
            elif position <= ref.indices[1]:
                indices = (indices[0], indices[1] + offset)
        ref.indices = indices

    # Sort by index
    refs.sort(key=lambda x: x.indices[0])

    return text, refs


# ######### #
# OAuth 2.0 #
# ######### #

class OAuthTokenRequest(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('refresh_token',                    basestring, required=True)
        cls.addProperty('grant_type',                       basestring, required=True)

class OAuthLogin(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('login',                            basestring, required=True)
        cls.addProperty('password',                         basestring, required=True, cast=validateString)

# TODO: Consolidate OAuthFacebookLogin and OAuthTwitterLogin after linked account generification?

class OAuthFacebookLogin(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_token',                       basestring, required=True)

class OAuthTwitterLogin(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_token',                       basestring, required=True)
        cls.addProperty('user_secret',                      basestring, required=True)


# ####### #
# Actions #
# ####### #

class HTTPActionCompletionData(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('action',                           basestring)
        cls.addProperty('source',                           basestring)
        cls.addProperty('source_id',                        basestring)
        cls.addProperty('entity_id',                        basestring)
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('stamp_id',                         basestring)

class HTTPActionSource(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('source',                           basestring, required=True)
        cls.addProperty('source_id',                        basestring)
        cls.addProperty('source_data',                      dict)
        cls.addProperty('endpoint',                         basestring)
        cls.addProperty('endpoint_data',                    dict)
        cls.addProperty('link',                             basestring)
        cls.addProperty('icon',                             basestring)
        cls.addProperty('completion_endpoint',              basestring)
        cls.addProperty('completion_data',                  dict) # dictionary?

    def setCompletion(self, **kwargs):
        self.completion_endpoint    = COMPLETION_ENDPOINT
        self.completion_data        = HTTPActionCompletionData().dataImport(kwargs, overflow=True).dataExport()

    def setIcon(self, filename, client=None):
        self.source_data['icon'] = _getIconURL(filename, client)

class HTTPAction(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('type',                             basestring, required=True)
        cls.addProperty('name',                             basestring, required=True)
        cls.addNestedPropertyList('sources',                HTTPActionSource, required=True)


# ####### #
# General #
# ####### #

class HTTPImageSize(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('url',                              basestring)
        cls.addProperty('width',                            int)
        cls.addProperty('height',                           int)

class HTTPImage(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('sizes',                  HTTPImageSize)
        cls.addProperty('caption',                          basestring)
        cls.addNestedProperty('action',                     HTTPAction)

class HTTPTextReference(Schema):
    @classmethod
    def setSchema(cls):
        cls.addPropertyList('indices',                      int, required=True)
        cls.addNestedProperty('action',                     HTTPAction)


# ####### #
# Account #
# ####### #

class HTTPAccount(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring, required=True, cast=validateUserId)
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('auth_service',                     basestring, required=True)
        cls.addProperty('email',                            basestring, required=True)
        cls.addProperty('screen_name',                      basestring, required=True, cast=validateScreenName)
        cls.addProperty('privacy',                          bool, required=True)
        cls.addProperty('phone',                            basestring, cast=parsePhoneNumber)

    def importAccount(self, account, client=None):
        self.dataImport(account.dataExport(), overflow=True)
        return self

class HTTPAccountNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('email',                            basestring, required=True, cast=validateEmail)
        cls.addProperty('password',                         basestring, required=True, cast=validateString)
        cls.addProperty('screen_name',                      basestring, required=True, cast=validateScreenName)
        cls.addProperty('phone',                            basestring, cast=parsePhoneNumber)

        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring, cast=validateURL)
        cls.addProperty('location',                         basestring)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)

        # for asynchronous image uploads
        cls.addProperty('temp_image_url',                   basestring)

    def convertToAccount(self):
        data = self.dataExport()
        phone = _phoneToInt(data.pop('phone', None))
        if phone is not None:
            data['phone'] = phone

        return Account().dataImport(data, overflow=True)

class HTTPAccountUpgradeForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('email',                            basestring, required=True)
        cls.addProperty('password',                         basestring, required=True, cast=validateString)


class HTTPFacebookAccountNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('screen_name',                      basestring, required=True, cast=validateScreenName)
        cls.addProperty('user_token',                       basestring, required=True)
        cls.addProperty('email',                            basestring, cast=validateEmail)
        cls.addProperty('phone',                            basestring, cast=parsePhoneNumber)

        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring, cast=validateURL)
        cls.addProperty('location',                         basestring)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)

        cls.addProperty('temp_image_url',                   basestring)

    def convertToFacebookAccountNew(self):
        data = self.dataExport()
        phone = _phoneToInt(data.pop('phone', None))
        if phone is not None:
            data['phone'] = phone

        return FacebookAccountNew().dataImport(data, overflow=True)

class HTTPTwitterAccountNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('screen_name',                      basestring, required=True, cast=validateScreenName)
        cls.addProperty('user_token',                       basestring, required=True)
        cls.addProperty('user_secret',                      basestring, required=True)
        cls.addProperty('email',                            basestring, cast=validateEmail)
        cls.addProperty('phone',                            basestring, cast=parsePhoneNumber)

        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring, cast=validateURL)
        cls.addProperty('location',                         basestring)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)

        cls.addProperty('temp_image_url',                   basestring)

    def convertToTwitterAccountNew(self):
        data = self.dataExport()
        if 'phone' in data:
            data['phone'] = _phoneToInt(data['phone'])

        return TwitterAccountNew().dataImport(data, overflow=True)

class HTTPAccountUpdateForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                             basestring)
        cls.addProperty('screen_name',                      basestring, cast=validateScreenName)
        cls.addProperty('phone',                            basestring, cast=parsePhoneNumber)

        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring, cast=validateURL)
        cls.addProperty('location',                         basestring)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)

        cls.addProperty('temp_image_url',                   basestring, cast=validateURL)

    def convertToAccountUpdateForm(self):
        data = self.dataExport()
        if 'phone' in data:
            data['phone'] = _phoneToInt(data['phone'])

        return AccountUpdateForm().dataImport(data, overflow=True)

class HTTPCustomizeStamp(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('color_primary',                    basestring, required=True, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, required=True, cast=validateHexColor)

class HTTPAccountProfileImage(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('temp_image_url',                   basestring, cast=validateURL)

class HTTPAccountCheck(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('login',                            basestring, required=True)

class HTTPServiceNameForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('service_name',                     basestring)

class HTTPUpdateLinkedAccountShareSettingsForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('service_name',                     basestring, required=True)
        cls.addProperty('share_stamps',                     bool)
        cls.addProperty('share_likes',                      bool)
        cls.addProperty('share_todos',                      bool)
        cls.addProperty('share_follows',                    bool)

    def exportLinkedAccountShareSettings(self):
        shareSettings = LinkedAccountShareSettings().dataImport(self.dataExport(), overflow=True)
        return shareSettings

class HTTPLinkedAccountShareSettings(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('share_stamps',                     bool)
        cls.addProperty('share_likes',                      bool)
        cls.addProperty('share_todos',                      bool)
        cls.addProperty('share_follows',                    bool)

class HTTPLinkedAccount(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('service_name',                     basestring)
        cls.addProperty('linked_user_id',                   basestring)
        cls.addProperty('linked_screen_name',               basestring)
        cls.addProperty('linked_name',                      basestring)
        cls.addProperty('token',                            basestring)
        cls.addProperty('secret',                           basestring)
        cls.addProperty('token_expiration',                 basestring)
        cls.addNestedProperty('share_settings',             HTTPLinkedAccountShareSettings)

    def importLinkedAccount(self, linked):
        self.dataImport(linked.dataExport(), overflow=True)
        return self

    def exportLinkedAccount(self):
        linkedAccount = LinkedAccount().dataImport(self.dataExport(), overflow=True)
        return linkedAccount

class HTTPLinkedAccounts(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('twitter',                    HTTPLinkedAccount)
        cls.addNestedProperty('facebook',                   HTTPLinkedAccount)
        cls.addNestedProperty('netflix',                    HTTPLinkedAccount)
        cls.addNestedProperty('rdio',                       HTTPLinkedAccount)

    def importLinkedAccounts(self, linked):
        if linked.twitter is not None:
            self.twitter = HTTPLinkedAccount().importLinkedAccount(linked.twitter)
        if linked.facebook is not None:
            self.facebook = HTTPLinkedAccount().importLinkedAccount(linked.facebook)
        if linked.netflix is not None:
            self.netflix = HTTPLinkedAccount().importLinkedAccount(linked.netflix)
        if linked.rdio is not None:
            self.rdio = HTTPLinkedAccount().importLinkedAccount(linked.rdio)
        return self

    def exportLinkedAccounts(self):
        schema = LinkedAccounts()

        if self.twitter is not None:
            schema.twitter = LinkedAccount().dataImport(self.twitter.dataExport(), overflow=True)
        if self.facebook is not None:
            schema.facebook = LinkedAccount().dataImport(self.facebook.dataExport(), overflow=True)
        if self.twitter is not None:
            schema.netflix = LinkedAccount().dataImport(self.netflix.dataExport(), overflow=True)
        if self.rdio is not None:
            schema.rdio = LinkedAccount().dataImport(self.rdio.dataExport(), overflow=True)
        return schema 

class HTTPAvailableLinkedAccounts(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('twitter',                          bool)
        cls.addProperty('facebook',                         bool)
        cls.addProperty('netflix',                          bool)

class HTTPAccountChangePassword(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('old_password',                     basestring, required=True, cast=validateString)
        cls.addProperty('new_password',                     basestring, required=True, cast=validateString)

class HTTPAPNSToken(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('token',                            basestring, required=True)

class HTTPSettingsToggle(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('toggle_id',                        basestring, required=True)
        cls.addProperty('type',                             basestring, required=True)
        cls.addProperty('value',                            bool, required=True)

class HTTPSettingsGroup(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('group_id',                         basestring, required=True)
        cls.addProperty('name',                             basestring, required=True) # Used for display
        cls.addProperty('desc',                             basestring) # Used for display
        cls.addNestedPropertyList('toggles',                HTTPSettingsToggle)

class HTTPSettingsToggleRequest(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('on',                               basestring)
        cls.addProperty('off',                              basestring)

class HTTPShareSettingsToggleRequest(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('service_name',                     basestring)
        cls.addProperty('on',                               basestring)
        cls.addProperty('off',                              basestring)


# ##### #
# Users #
# ##### #

class HTTPUserId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring, cast=validateUserId)
        cls.addProperty('screen_name',                      basestring, cast=validateScreenName)

class HTTPUserIds(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_ids',                         basestring) # Comma delimited
        cls.addProperty('screen_names',                     basestring) # Comma delimited

class HTTPUserSearch(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('query',                            basestring)
        cls.addProperty('limit',                            int)
        cls.addProperty('relationship',                     basestring)

class HTTPUserRelationship(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id_a',                        basestring, cast=validateUserId)
        cls.addProperty('screen_name_a',                    basestring, cast=validateScreenName)
        cls.addProperty('user_id_b',                        basestring, cast=validateUserId)
        cls.addProperty('screen_name_b',                    basestring, cast=validateScreenName)

class HTTPFindUser(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('query',                            basestring, required=True) # Comma delimited

class HTTPFriendsCollectionForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('limit',                            int)
        cls.addProperty('offset',                           int)

class HTTPFacebookLoginResponse(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('state',                            basestring) # passed back state value to prevent csrf attacks
        cls.addProperty('code',                             basestring) # code we'll exchange for a user token

class HTTPFacebookAuthResponse(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('access_token',                     basestring)
        cls.addProperty('expires',                          int)        # seconds until token expires

class HTTPNetflixId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('netflix_id',                       basestring)

class HTTPNetflixAuthResponse(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('state',                            basestring)
        cls.addProperty('netflix_add_id',                   basestring)
        cls.addProperty('thirdparty_oauth_token',           basestring)
        cls.addProperty('thirdparty_oauth_verifier',        basestring)
        cls.addProperty('secret',                           basestring)

class HTTPFacebookAuthResponse(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('state',                            basestring)
        cls.addProperty('code',                             basestring)
        cls.addProperty('error',                            basestring)
        cls.addProperty('error_reason',                     basestring)
        cls.addProperty('error_description',                basestring)

class HTTPCategoryDistribution(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('category',                         basestring, required=True)
        cls.addProperty('name',                             basestring)
        cls.addProperty('icon',                             basestring)
        cls.addProperty('count',                            int)

class HTTPUser(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring, required=True, cast=validateUserId)
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('screen_name',                      basestring, required=True, cast=validateScreenName)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)
        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring, cast=validateURL)
        cls.addProperty('location',                         basestring)
        cls.addProperty('privacy',                          bool, required=True)
        cls.addProperty('image_url',                        basestring)
        cls.addNestedPropertyList('distribution',           HTTPCategoryDistribution)

        cls.addProperty('following',                        bool)

        cls.addProperty('num_stamps',                       int)
        cls.addProperty('num_stamps_left',                  int)
        cls.addProperty('num_friends',                      int)
        cls.addProperty('num_followers',                    int)
        cls.addProperty('num_faves',                        int)
        cls.addProperty('num_credits',                      int)
        cls.addProperty('num_credits_given',                int)
        cls.addProperty('num_likes',                        int)
        cls.addProperty('num_likes_given',                  int)

    def importAccount(self, account, client=None):
        return self.importUser(account, client)

    def importUser(self, user, client=None):
        self.dataImport(user.dataExport(), overflow=True)

        stats = user.stats.dataExport()
        self.num_stamps         = stats.pop('num_stamps', 0)
        self.num_stamps_left    = stats.pop('num_stamps_left', 0)
        self.num_friends        = stats.pop('num_friends', 0)
        self.num_followers      = stats.pop('num_followers', 0)
        self.num_faves          = stats.pop('num_faves', 0)
        self.num_credits        = stats.pop('num_credits', 0)
        self.num_credits_given  = stats.pop('num_credits_given', 0)
        self.num_likes          = stats.pop('num_likes', 0)
        self.num_likes_given    = stats.pop('num_likes_given', 0)

        self.image_url = _profileImageURL(user.screen_name, user.timestamp.image_cache)

        distributionData = {}
        if 'distribution' in stats:
            for item in stats['distribution']:
                distributionData[item['category']] = item['count']

        distribution = []
        order = [
            'place',
            'book',
            'film', 
            'music',
            'app',
            'other',
        ]
        for i in order:
            d           = HTTPCategoryDistribution()
            d.category  = i
            d.name      = i.title()
            d.count     = distributionData.pop(i, 0)
            d.icon      = _getIconURL('cat_%s' % i, client=client)
            distribution.append(d)
        self.distribution = distribution

        return self

class HTTPSuggestedUser(HTTPUser):
    @classmethod
    def setSchema(cls):
        cls.addProperty('search_identifier',                basestring)
        cls.addProperty('relationship_explanation',         basestring)

    def __init__(self):
        HTTPUser.__init__(self)

    def importUser(self, user, client=None):
        HTTPUser.importUser(self, user, client)
        return self

class HTTPUserMini(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring, required=True, cast=validateUserId)
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('screen_name',                      basestring, required=True, cast=validateScreenName)
        cls.addProperty('color_primary',                    basestring, cast=validateHexColor)
        cls.addProperty('color_secondary',                  basestring, cast=validateHexColor)
        cls.addProperty('privacy',                          bool, required=True)
        cls.addProperty('image_url',                        basestring)

    def importUserMini(self, mini):
        self.dataImport(mini.dataExport(), overflow=True)
        self.image_url = _profileImageURL(mini.screen_name, mini.timestamp.image_cache)

        return self

class HTTPSuggestedUserRequest(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('limit',                            int)
        cls.addProperty('offset',                           int)

    def __init__(self):
        Schema.__init__(self)
        self.limit          = 10
        self.offset         = 0

class HTTPUserImages(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('sizes',                  HTTPImageSize)

    def importUser(self, user):
        sizes = [ 24, 48, 60, 96, 144 ]
        imageSizes = []

        for size in sizes:
            image           = HTTPImageSize()
            image.url       = _profileImageURL(user.screen_name, cache=user.timestamp.image_cache, size=size)
            image.width     = size 
            image.height    = size
            imageSizes.append(image)

        self.sizes = imageSizes

        return self


# ####### #
# Invites #
# ####### #

class HTTPEmail(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('email',                            basestring, cast=validateEmail)

class HTTPEmails(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('emails',                           basestring, cast=validateEmails)


# ######## #
# Comments #
# ######## #

class HTTPComment(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('comment_id',                       basestring, required=True)
        cls.addNestedProperty('user',                       HTTPUserMini, required=True)
        cls.addProperty('stamp_id',                         basestring, required=True)
        cls.addProperty('blurb',                            basestring, required=True)
        cls.addNestedPropertyList('blurb_references',       HTTPTextReference)
        cls.addProperty('created',                          basestring)

    def importComment(self, comment):
        self.dataImport(comment.dataExport(), overflow=True)
        self.created = comment.timestamp.created
        self.user = HTTPUserMini().importUserMini(comment.user)
        blurb, references = _buildTextReferences(self.blurb)
        if len(references) > 0:
            self.blurb = blurb
            self.blurb_references = references
        return self

class HTTPCommentNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                         basestring, required=True, cast=validateStampId)
        cls.addProperty('blurb',                            basestring, required=True)

class HTTPCommentId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('comment_id',                       basestring, required=True)


# ######## #
# Previews #
# ######## #

class HTTPStampPreview(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                         basestring)
        cls.addNestedProperty('user',                       HTTPUserMini)

    def importStamp(self, stamp):
        return self.importStampPreview(stamp)


    def importStampPreview(self, stampPreview):
        self.stamp_id = stampPreview.stamp_id
        self.user = HTTPUserMini().importUserMini(stampPreview.user)
        return self 

class HTTPPreviews(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('stamps',                 HTTPStampPreview)
        cls.addNestedPropertyList('credits',                HTTPStampPreview)
        cls.addNestedPropertyList('todos',                  HTTPUserMini)
        cls.addNestedPropertyList('likes',                  HTTPUserMini)
        cls.addNestedPropertyList('comments',               HTTPComment)


# ################# #
# Endpoint Response #
# ################# #

class HTTPActionResponse(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('action',                     HTTPAction)

    def setAction(self, actionType, name, sources):
        if len(sources) > 0:
            action          = HTTPAction()
            action.type     = actionType
            action.name     = name
            action.sources  = sources

            self.action = action


# ######## #
# Entities #
# ######## #

def _addImages(dest, images):
    newImages = []
    if images is not None:
        for image in images:
            if len(image.sizes) == 0:
                continue
            newimg = HTTPImage()
            sizes = []
            for size in image.sizes:
                if size.url is not None:
                    newsize = HTTPImageSize()
                    newsize.url = _cleanImageURL(size.url)
                    sizes.append(newsize)
            newimg.sizes = sizes
            newImages.append(newimg)

    dest.images = newImages

class HTTPEntityAction(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('action',                     HTTPAction, required=True)
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('icon',                             basestring)

class HTTPEntityMetadataItem(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('value',                            basestring, required=True)
        cls.addProperty('key',                              basestring)
        cls.addNestedProperty('action',                     HTTPAction)
        cls.addProperty('icon',                             basestring)
        cls.addProperty('extended',                         bool)
        cls.addProperty('optional',                         bool)

class HTTPEntityGallery(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('images',                 HTTPImage, required=True)
        cls.addProperty('name',                             basestring)
        cls.addProperty('layout',                           basestring) # 'list' or None

class HTTPEntityPlaylistItem(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                        basestring)
        cls.addProperty('name',                             basestring, required=True)
        cls.addNestedProperty('action',                     HTTPAction)
        cls.addProperty('length',                           int)
        cls.addProperty('icon',                             basestring)

class HTTPEntityPlaylist(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('data',                   HTTPEntityPlaylistItem, required=True)
        cls.addProperty('name',                             basestring)

class HTTPEntityMini(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                        basestring, required=True)
        cls.addProperty('title',                            basestring, required=True)
        cls.addProperty('subtitle',                         basestring, required=True)
        cls.addProperty('category',                         basestring, required=True)
        cls.addProperty('subcategory',                      basestring, required=True)
        cls.addProperty('coordinates',                      basestring)
        cls.addNestedPropertyList('images',                 HTTPImage)

    def importEntity(self, entity):
        self.entity_id              = entity.entity_id
        self.title                  = entity.title
        self.subtitle               = entity.subtitle
        self.category               = entity.category
        self.subcategory            = entity.subcategory
        _addImages(self, entity.images)

        try:
            self.coordinates    = _coordinatesDictToFlat(entity.coordinates)
        except AttributeError:
            pass

        return self

class HTTPEntityRelated(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('data',                   HTTPEntityMini, required=True)
        cls.addProperty('title',                            basestring)


class HTTPEntity(Schema):
    @classmethod
    def setSchema(cls):
        # Core
        cls.addProperty('entity_id',                        basestring, required=True)
        cls.addProperty('title',                            basestring, required=True)
        cls.addProperty('subtitle',                         basestring, required=True)
        cls.addProperty('category',                         basestring, required=True)
        cls.addProperty('subcategory',                      basestring, required=True)
        cls.addProperty('caption',                          basestring)
        cls.addProperty('desc',                             basestring)
        cls.addNestedPropertyList('images',                 HTTPImage)
        cls.addProperty('last_modified',                    basestring)
        cls.addNestedProperty('previews',                   HTTPPreviews)
        
        # Location
        cls.addProperty('address',                          basestring)
        cls.addProperty('neighborhood',                     basestring)
        cls.addProperty('coordinates',                      basestring)
        
        # Components
        cls.addNestedProperty('playlist',                   HTTPEntityPlaylist)
        cls.addNestedPropertyList('actions',                HTTPEntityAction)
        cls.addNestedPropertyList('galleries',              HTTPEntityGallery)
        cls.addNestedPropertyList('metadata',               HTTPEntityMetadataItem)
        cls.addNestedProperty('related',                    HTTPEntityRelated)

    def __init__(self):
        Schema.__init__(self)
        self.actions = []

    def _addAction(self, actionType, name, sources, **kwargs):
        if len(sources) > 0:
            action          = HTTPAction()
            action.type     = actionType
            action.name     = name
            action.sources  = sources

            item            = HTTPEntityAction()
            item.action     = action
            item.name       = name

            if 'icon' in kwargs:
                item.icon = kwargs['icon']

            self.actions += (item,)

    def _addMetadata(self, name, value, **kwargs):
        if value is not None and len(value) > 0:
            item        = HTTPEntityMetadataItem()
            item.name   = name
            item.value  = value

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
                actionSource.name = 'Go to URL'
                actionSource.source = 'link'

                action = HTTPAction()
                action.type = 'link'
                action.name = 'Go to URL'
                action.sources = [actionSource]

                item.action = action

            if 'action' in kwargs:
                item.action = kwargs['action']

            metadata = self.metadata
            if metadata is None:
                metadata = tuple()
            metadata = metadata + (item,)

            self.metadata = metadata

    def _formatMetadataList(self, data, attribute=None):
        if data is None or len(data) == 0:
            return None
        if attribute is not None:
            return ', '.join(unicode(getattr(i, attribute)) for i in data)
        else:
            return ', '.join(unicode(i) for i in data)

    def _formatReleaseDate(self, date):
        try:
            return date.strftime("%h %d, %Y")
        except Exception:
            return None

    def _formatFilmLength(self, seconds):
        try:
            seconds = int(seconds)
            m = (seconds % 3600) / 60
            h = (seconds - (seconds % 3600)) / 3600
            if h > 0:
                return '%s hr %s min' % (h, m)
            else:
                return '%s min' % m
        except Exception:
            return None

    def _formatSubcategory(self, subcategory):
        if subcategory == 'tv':
            return 'TV'
        return subcategory.replace('_', ' ').title()

    def importEntity(self, entity, client=None):
        # General
        self.entity_id          = entity.entity_id
        self.title              = entity.title
        self.subtitle           = entity.subtitle
        self.category           = entity.category
        self.subcategory        = entity.subcategory

        self.caption            = self.subtitle # Default
        self.desc               = entity.desc
        self.last_modified      = entity.timestamp.created

        # Temporary hack to fix bug in 2.0.1 that displays "an place"
        if self.subcategory == 'establishment':
            self.subcategory = 'place'
            
        subcategory             = self._formatSubcategory(self.subcategory)

        # Place
        if entity.kind == 'place':
            self.address        = entity.formatAddress(extendStreet=True)
            self.coordinates    = _coordinatesDictToFlat(entity.coordinates)

            address = entity.formatAddress(extendStreet=True, breakLines=True)
            if address is not None:
                self.caption = address

            # Metadata
            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_place', client=client))
            self._addMetadata('Cuisine', self._formatMetadataList(entity.cuisine))
            self._addMetadata('Price', entity.price_range * '$' if entity.price_range is not None else None)
            self._addMetadata('Site', _formatURL(entity.site), link=entity.site)
            self._addMetadata('Description', entity.desc, key='desc', extended=True)

            # Image Gallery

            if entity.gallery is not None and len(entity.gallery) > 0:
                gallery = HTTPEntityGallery()
                images = []
                for image in entity.gallery:
                    item                = HTTPImage().dataImport(image.dataExport())
                    source              = HTTPActionSource()
                    source.source_id    = item.sizes[0].url
                    source.source       = 'stamped'
                    source.link         = item.sizes[0].url
                    action              = HTTPAction()
                    action.type         = 'stamped_view_image'
                    action.sources      = [ source ]
                    item.action         = action
                    images.append(item)
                gallery.images = images
                self.galleries = [gallery]

            # Actions: Reservation

            actionType  = 'reserve'
            actionIcon  = _getIconURL('act_reserve_primary', client=client)
            sources     = []

            if entity.sources.opentable_id is not None or entity.sources.opentable_nickname is not None:
                source              = HTTPActionSource()
                source.name         = 'Reserve on OpenTable'
                source.source       = 'opentable'
                source.source_id    = entity.sources.opentable_id
                source.link         = _buildOpenTableURL(entity.sources.opentable_id, entity.sources.opentable_nickname, client)
                source.icon         = _getIconURL('src_opentable', client=client)
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            self._addAction(actionType, 'Reserve a table', sources, icon=actionIcon)

            # Actions: Call

            actionType  = 'phone'
            actionIcon  = _getIconURL('act_call', client=client)
            sources     = []

            if entity.phone is not None:
                source              = HTTPActionSource()
                source.source       = 'phone'
                source.source_id    = entity.phone
                source.link         = 'tel:%s' % non_numeric_re.sub('', entity.phone)
                sources.append(source)

            self._addAction(actionType, entity.phone, sources, icon=actionIcon)

            # Actions: View Menu

            actionType  = 'menu'
            actionIcon  = _getIconURL('act_menu', client=client)
            sources     = []

            if entity.menu is not None and entity.menu:
                source              = HTTPActionSource()
                source.name         = 'View menu'
                source.source       = 'stamped'
                source.source_id    = entity.entity_id
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            self._addAction(actionType, 'View menu', sources, icon=actionIcon)

            # Image gallery

            if entity.gallery is not None and len(entity.gallery) > 0:
                gallery = HTTPEntityGallery()
                images = []
                for image in entity.gallery:
                    item = HTTPImage().dataImport(image.dataExport(), overflow=True)
                    source              = HTTPActionSource()
                    source.source_id    = item.sizes[0].url
                    source.source       = 'stamped'
                    source.link         = item.sizes[0].url
                    action              = HTTPAction()
                    action.type         = 'stamped_view_image'
                    action.sources      = [ source ]
                    item.action         = action
                    images.append(item)
                gallery.images = images
                self.galleries = [gallery]

        # Book
        elif entity.kind == 'media_item' and entity.isType('book'):

            if entity.authors is not None and len(entity.authors) > 0:
                self.caption = 'by %s' % self._formatMetadataList(entity.authors, 'title')

            # Metadata

            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_book', client=client))
            self._addMetadata('Publish Date', self._formatReleaseDate(entity.release_date))
            self._addMetadata('Description', entity.desc, key='desc', extended=True)
            self._addMetadata('Publisher', self._formatMetadataList(entity.publishers, 'title'))

            # Actions: Buy

            actionType  = 'buy'
            actionIcon  = _getIconURL('act_buy_primary', client=client)
            sources     = []

            source              = HTTPActionSource()
            source.name         = 'Buy from Amazon'
            source.source       = 'amazon'
            source.icon         = _getIconURL('src_amazon', client=client)
            source.setCompletion(
                action      = actionType,
                entity_id   = entity.entity_id,
                source      = source.source,
                source_id   = source.source_id,
            )
            if entity.sources.amazon_underlying is not None:
                source.source_id    = entity.sources.amazon_underlying
                source.link         = _buildAmazonURL(entity.sources.amazon_underlying)
                sources.append(source)
            elif entity.sources.amazon_id is not None:
                source.source_id    = entity.sources.amazon_id
                source.link         = _buildAmazonURL(entity.sources.amazon_id)
                sources.append(source)

            self._addAction(actionType, 'Buy now', sources, icon=actionIcon)

        # TV
        elif entity.kind == 'media_collection' and entity.isType('tv'):

            if entity.networks is not None and len(entity.networks) > 0:
                self.caption = self._formatMetadataList(entity.networks, 'title')

            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_film', client=client))
            self._addMetadata('Overview', entity.desc, key='desc', extended=True)
            self._addMetadata('Release Date', self._formatReleaseDate(entity.release_date))
            self._addMetadata('Cast', self._formatMetadataList(entity.cast, 'title'), extended=True, optional=True)
            self._addMetadata('Director', self._formatMetadataList(entity.directors, 'title'), optional=True)
            self._addMetadata('Genres', self._formatMetadataList(entity.genres), optional=True)

            if entity.subcategory == 'movie':
                self._addMetadata('Rating', entity.mpaa_rating, key='rating', optional=True)

            # Actions: Watch Now

            actionType  = 'watch'
            actionIcon  = _getIconURL('act_play_primary', client=client)
            sources     = []

            if entity.sources.itunes_id is not None and entity.sources.itunes_preview is not None:
                source              = HTTPActionSource()
                source.name         = 'Watch Trailer on iTunes'
                source.source       = 'itunes'
                source.source_id    = entity.sources.itunes_id
                source.source_data  = { 'preview_url': entity.sources.itunes_preview }
                source.icon         = _getIconURL('src_itunes', client=client)
                if getattr(entity.sources, 'itunes_url', None) is not None:
                    source.link     = _encodeiTunesShortURL(entity.sources.itunes_url)
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            self._addAction(actionType, 'Watch trailer', sources, icon=actionIcon)

            # Actions: Add to Netflix Instant Queue
            actionType  = 'queue'
            actionIcon  = _getIconURL('act_play_primary', client=client)
            sources     = []

            if entity.sources.netflix_id is not None and entity.sources.netflix_is_instant_available:
                source                  = HTTPActionSource()
                source.name             = 'Add to Netflix Instant Queue'
                source.source           = 'netflix'
                source.source_id        = entity.sources.netflix_id
                source.endpoint         = 'account/linked/netflix/add_instant.json'
                source.endpoint_data    = {'netflix_id': entity.sources.netflix_id}
                source.icon             = _getIconURL('src_netflix', client=client)
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            self._addAction(actionType, 'Add to Netflix Instant Queue', sources, icon=actionIcon)

            # Actions: Download

            actionType  = 'buy'
            actionIcon  = _getIconURL('act_buy', client=client)
            sources     = []

            if entity.sources.amazon_underlying is not None:
                source              = HTTPActionSource()
                source.name         = 'Buy from Amazon'
                source.source       = 'amazon'
                source.source_id    = entity.sources.amazon_underlying
                source.link         = _buildAmazonURL(entity.sources.amazon_underlying)
                sources.append(source)

            self._addAction(actionType, 'Buy', sources, icon=actionIcon)

        # Movie
        elif entity.kind == 'media_item' and entity.isType('movie'):
            if entity.length is not None:
                length = self._formatFilmLength(entity.length)
                if length is not None:
                    self.caption = length

            # Metadata

            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_film', client=client))
            self._addMetadata('Overview', entity.desc, key='desc', extended=True)
            self._addMetadata('Release Date', self._formatReleaseDate(entity.release_date))
            self._addMetadata('Cast', self._formatMetadataList(entity.cast, 'title'), extended=True, optional=True)
            self._addMetadata('Director', self._formatMetadataList(entity.directors, 'title'), optional=True)
            self._addMetadata('Genres', self._formatMetadataList(entity.genres), optional=True)
            self._addMetadata('Rating', entity.mpaa_rating, key='rating', optional=True)

            # Actions: Preview

            actionType  = 'watch'
            actionIcon  = _getIconURL('act_play_primary', client=client)
            sources     = []

            if entity.sources.itunes_id is not None and entity.sources.itunes_preview is not None:
                source              = HTTPActionSource()
                source.name         = 'Watch Trailer on iTunes'
                source.source       = 'itunes'
                source.source_id    = entity.sources.itunes_id
                source.source_data  = { 'preview_url': entity.sources.itunes_preview }
                source.icon         = _getIconURL('src_itunes', client=client)

                if getattr(entity.sources, 'itunes_url', None) is not None:
                    source.link     = _encodeiTunesShortURL(entity.sources.itunes_url)

                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            self._addAction(actionType, 'Watch trailer', sources, icon=actionIcon)

            # Actions: Find Tickets

            actionType  = 'tickets'
            actionIcon  = _getIconURL('act_ticket_primary', client=client)
            if len(self.actions) == 0:
                actionIcon = _getIconURL('act_ticket', client=client)

            sources     = []
            if getattr(entity.sources, 'fandango_id', None) is not None:
                source              = HTTPActionSource()
                source.name         = 'Buy from Fandango'
                source.source       = 'fandango'
                source.source_id    = entity.sources.fandango_id

                if getattr(entity.sources, 'fandango_url', None) is not None:
                    source.link     = entity.sources.fandango_url

                # Only add icon if no "watch now"
                if len(self.actions) == 0:
                    source.icon   = _getIconURL('src_fandango', client=client)

                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            self._addAction(actionType, 'Find tickets', sources, icon=actionIcon)

            # Actions: Add to Netflix Instant Queue
            actionType  = 'queue'
            actionIcon  = _getIconURL('act_play_primary', client=client)
            sources     = []

            if entity.sources.netflix_id is not None and entity.sources.netflix_is_instant_available:
                source                  = HTTPActionSource()
                source.name             = 'Add to Netflix Instant Queue'
                source.source           = 'netflix'
                source.source_id        = entity.sources.netflix_id
                source.endpoint         = 'account/linked/netflix/add_instant.json'
                source.endpoint_data    = { 'netflix_id': entity.sources.netflix_id }
                source.icon             = _getIconURL('src_netflix', client=client)
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            self._addAction(actionType, 'Add to Netflix Instant Queue', sources, icon=actionIcon)

            # Actions: Download

            actionType  = 'buy'
            actionIcon  = _getIconURL('act_buy', client=client)
            sources     = []

            if entity.sources.amazon_underlying is not None:
                source              = HTTPActionSource()
                source.name         = 'Buy from Amazon'
                source.source       = 'amazon'
                source.source_id    = entity.sources.amazon_underlying
                source.link         = _buildAmazonURL(entity.sources.amazon_underlying)
                sources.append(source)

            self._addAction(actionType, 'Buy', sources, icon=actionIcon)

        # Music
        elif entity.category == 'music':

            if entity.isType('artist'):
                self.caption = 'Artist'

            elif entity.isType('album') and entity.artists is not None and len(entity.artists) > 0:
                self.caption = 'by %s' % self._formatMetadataList(entity.artists, 'title')

            elif entity.isType('track') and entity.artists is not None and len(entity.artists) > 0:
                self.caption = 'by %s' % self._formatMetadataList(entity.artists, 'title')

            # Metadata

            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_music', client=client))
            if entity.isType('artist'):
                self._addMetadata('Biography', entity.desc, key='desc')
                self._addMetadata('Genre', self._formatMetadataList(entity.genres), optional=True)

            elif entity.isType('album'):
                if entity.artists is not None and len(entity.artists) > 0:
                    artist = entity.artists[0]
                    if artist.entity_id is not None:
                        source              = HTTPActionSource()
                        source.name         = 'View Artist'
                        source.source       = 'stamped'
                        source.source_id    = artist.entity_id
                        action              = HTTPAction()
                        action.type         = 'stamped_view_entity'
                        action.name         = 'View Artist'
                        action.sources      = [source]
                        self._addMetadata('Artist', entity.artists[0].title, action=action, optional=True, key='artist')
                self._addMetadata('Genre', self._formatMetadataList(entity.genres))
                self._addMetadata('Release Date', self._formatReleaseDate(entity.release_date))
                self._addMetadata('Album Details', entity.desc, key='desc', optional=True)

            elif entity.isType('track'):
                if entity.artists is not None and len(entity.artists) > 0:
                    artist = entity.artists[0]
                    if artist.entity_id is not None:
                        source              = HTTPActionSource()
                        source.name         = 'View Artist'
                        source.source       = 'stamped'
                        source.source_id    = artist.entity_id
                        action              = HTTPAction()
                        action.type         = 'stamped_view_entity'
                        action.name         = 'View Artist'
                        action.sources      = [source]
                        self._addMetadata('Artist', entity.artists[0].title, action=action, optional=True, key='artist')
                    ### TODO: Add album
                self._addMetadata('Genre', self._formatMetadataList(entity.genres))
                self._addMetadata('Release Date', self._formatReleaseDate(entity.release_date))
                self._addMetadata('Song Details', entity.desc, key='desc', optional=True)

            # Actions: Listen

            actionType  = 'listen'
            actionTitle = 'Listen'
            if entity.isType('artist'):
                actionTitle = 'Listen to top songs'
            elif entity.isType('album'):
                actionTitle = 'Listen to album'
            elif entity.isType('track'):
                actionTitle = 'Listen to song'
            actionIcon  = _getIconURL('act_play_primary', client=client)
            sources     = []
            if getattr(entity.sources, 'itunes_id', None) is not None \
               and getattr(entity.sources, 'itunes_preview', None) is not None:
                source              = HTTPActionSource()
                source.name         = 'Listen on iTunes'
                source.source       = 'itunes'
                source.source_id    = entity.sources.itunes_id
                source.source_data  = { 'preview_url': entity.sources.itunes_preview }
                source.icon         = _getIconURL('src_itunes', client=client)
                if getattr(entity.sources, 'itunes_url', None) is not None:
                    source.link     = _encodeiTunesShortURL(entity.sources.itunes_url)
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            if getattr(entity.sources, 'rdio_id', None) is not None:
                if entity.sources.rdio_available_stream == True or entity.isType('artist'):
                    source              = HTTPActionSource()
                    source.name         = 'Listen on Rdio'
                    source.source       = 'rdio'
                    source.source_id    = entity.sources.rdio_id
                    source.icon         = _getIconURL('src_rdio', client=client)
                    if getattr(entity.sources, 'rdio_url', None) is not None:
                        source.link     = entity.sources.rdio_url
                    source.setCompletion(
                        action      = actionType,
                        entity_id   = entity.entity_id,
                        source      = source.source,
                        source_id   = source.source_id,
                    )
                    sources.append(source)

            if getattr(entity.sources, 'spotify_id', None) is not None:
                source              = HTTPActionSource()
                source.name         = 'Listen on Spotify'
                source.source       = 'spotify'
                source.source_id    = entity.sources.spotify_id
                source.icon         = _getIconURL('src_spotify', client=client)
                if getattr(entity.sources, 'spotify_url', None) is not None:
                    source.link     = entity.sources.spotify_url
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            self._addAction(actionType, actionTitle, sources, icon=actionIcon)

            # Actions: Add to Playlist

            actionType  = 'playlist'
            actionTitle = 'Add to playlist'
            if entity.isType('artist'):
                actionTitle = 'Add artist to playlist'
            actionIcon  = _getIconURL('act_playlist_music', client=client)
            sources     = []

            if getattr(entity.sources, 'rdio_id', None) is not None:
                source              = HTTPActionSource()
                source.name         = 'Add to playlist on Rdio'
                source.source       = 'rdio'
                source.source_id    = entity.sources.rdio_id
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            if getattr(entity.sources, 'spotify_id', None) is not None:
                source              = HTTPActionSource()
                source.name         = 'Add to playlist on Spotify'
                source.source       = 'spotify'
                source.source_id    = entity.sources.spotify_id
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            # Landon only implemented this for tracks. WTF man.
            if entity.isType('track'):
                self._addAction(actionType, actionTitle, sources, icon=actionIcon)

            # Actions: Download

            actionType  = 'download'
            actionTitle = 'Download %s' % entity.subcategory
            actionIcon  = _getIconURL('act_download', client=client)
            sources     = []

            if getattr(entity.sources, 'itunes_id', None) is not None:
                source              = HTTPActionSource()
                source.name         = 'Download from iTunes'
                source.source       = 'itunes'
                source.source_id    = entity.sources.itunes_id
                if entity.sources.itunes_url is not None:
                    source.link     = _encodeiTunesShortURL(entity.sources.itunes_url)
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            self._addAction(actionType, actionTitle, sources, icon=actionIcon)

            # Playlist

            if (entity.isType('album') or entity.isType('artist')) and entity.tracks is not None:
                playlist = HTTPEntityPlaylist()
                data = []

                if entity.isType('album'):
                    playlist.name = 'Tracks'
                else:
                    playlist.name = 'Top songs'

                for i in range(len(entity.tracks))[:20]:
                    try:
                        song = entity.tracks[i]
                        item = HTTPEntityPlaylistItem()
                        item.name   = song.title
                        if song.length is not None:
                            item.length = song.length
                        # if song.entity_id is not None:
                        #     item.entity_id = song.entity_id
                        # item.icon   = None ### TODO

                        sources = []

                        if getattr(song.sources, 'itunes_id', None) is not None     \
                           and getattr(song.sources, 'itunes_preview', None) is not None:
                            source                      = HTTPActionSource()
                            source.name                 = 'Listen on iTunes'
                            source.source               = 'itunes'
                            source.source_id            = song.sources.itunes_id
                            source.source_data          = { 'preview_url': song.sources.itunes_preview }
                            source.icon                 = _getIconURL('src_itunes', client=client)
                            sources.append(source)

                            if item.entity_id is None:
                                item.entity_id = 'T_ITUNES_%s' % song.sources.itunes_id

                        if getattr(song.sources, 'rdio_id', None) is not None:
                            source                      = HTTPActionSource()
                            source.name                 = 'Listen on Rdio'
                            source.source               = 'rdio'
                            source.source_id            = song.sources.rdio_id
                            source.icon                 = _getIconURL('src_rdio', client=client)
                            sources.append(source)

                            if item.entity_id is None:
                                item.entity_id = 'T_RDIO_%s' % song.sources.rdio_id

                        if getattr(song.sources, 'spotify_id', None) is not None:
                            source                      = HTTPActionSource()
                            source.name                 = 'Listen on Spotify'
                            source.source               = 'spotify'
                            source.source_id            = song.sources.spotify_id
                            source.icon                 = _getIconURL('src_spotify', client=client)
                            sources.append(source)

                            if item.entity_id is None:
                                item.entity_id = 'T_SPOTIFY_%s' % song.sources.spotify_id

                        if len(sources) > 0:
                            action = HTTPAction()
                            action.type = 'listen'
                            action.name = 'Listen to song'

                            for source in sources:
                                source.setCompletion(
                                    action      = 'listen',
                                    entity_id   = entity.entity_id,
                                    source      = source.source,
                                    source_id   = source.source_id,
                                )

                            action.sources = sources

                            item.action = action

                        data.append(item)

                    except Exception as e:
                        print "\n\nEXCEPTION %s\n\n" % e

                if len(data) > 0:
                    playlist.data = data
                    self.playlist = playlist

            # Albums

            if entity.isType('artist') and entity.albums is not None and len(entity.albums) > 0:
                gallery = HTTPEntityGallery()
                gallery.layout = 'list'
                images = []
                for album in entity.albums[:10]:
                    try:
                        item            = HTTPImage()
                        size            = HTTPImageSize()
                        ### TODO: Add placeholder if image doesn't exist?
                        size.url        = _cleanImageURL(album.images[0].sizes[0].url)
                        item.caption    = album.title
                        item.sizes      = [size]

                        if album.entity_id is not None:
                            source              = HTTPActionSource()
                            source.name         = 'View Album'
                            source.source       = 'stamped'
                            source.source_id    = album.entity_id

                            action              = HTTPAction()
                            action.type         = 'stamped_view_entity'
                            action.name         = 'View Album'
                            action.sources      = [source]

                            item.action         = action

                        images.append(item)
                    except Exception as e:
                        logs.warning("Artist album-gallery item failed: %s (%s)" % (e, album))
                        pass

                gallery.images = images
                if len(gallery.images) > 0:
                    if self.galleries is None:
                        self.galleries = [gallery]
                    else:
                        self.galleries += (gallery,)

        elif entity.kind == 'software' and entity.isType('app'):

            if entity.authors is not None and len(entity.authors) > 0:
                self.caption = 'by %s' % self._formatMetadataList(entity.authors, 'title')

            # Metadata

            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_app', client=client))
            self._addMetadata('Genre', self._formatMetadataList(entity.genres))
            self._addMetadata('Description', entity.desc, key='desc', extended=True)

            # Actions: Download

            actionType  = 'download'
            actionIcon  = _getIconURL('act_download_primary', client=client)
            sources     = []

            if getattr(entity.sources, 'itunes_id', None) is not None:
                source              = HTTPActionSource()
                source.name         = 'Download from the App Store'
                source.source       = 'appstore'
                source.source_id    = entity.sources.itunes_id
                source.icon         = _getIconURL('src_itunes', client=client)
                if getattr(entity.sources, 'itunes_url', None) is not None:
                    source.link     = _encodeiTunesShortURL(entity.sources.itunes_url)
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            self._addAction(actionType, 'Download', sources, icon=actionIcon)

            # Screenshots

            if entity.screenshots is not None and len(entity.screenshots) > 0:
                gallery = HTTPEntityGallery()
                images = []
                for screenshot in entity.screenshots:
                    item = HTTPImage().dataImport(screenshot.dataExport())
                    images.append(item)
                gallery.images = images
                if self.galleries is None:
                    self.galleries = [gallery]
                else:
                    self.galleries += (gallery,)


        # Generic item
        else:

            # Metadata

            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_other', client=client))
            self._addMetadata('Description', entity.desc, key='desc')
            self._addMetadata('Site', _formatURL(entity.site), link=entity.site)


        # Image

        if entity.kind == 'place':
            # Don't add an image if coordinates exist
            del(self.images)
        elif entity.images is not None and len(entity.images) > 0:
            _addImages(self, entity.images)

        # Previews

        if entity.previews is not None:
            previews = HTTPPreviews()

            if entity.previews.todos is not None:
                users = []
                for user in entity.previews.todos:
                    users.append(HTTPUserMini().importUserMini(user))
                previews.todos = users

            if entity.previews.stamps is not None:
                stampPreviews = []
                for item in entity.previews.stamps:
                    stampPreviews.append(HTTPStampPreview().importStampPreview(item))
                previews.stamps = stampPreviews

            self.previews = previews

        return self

    def importEntityMini(self, mini, client=None):
        self.dataImport(mini.dataExport(), overflow=True)
        if mini.coordinates is not None:
            self.coordinates = _coordinatesDictToFlat(mini.coordinates)

        return self

class HTTPEntityNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                            basestring, required=True, cast=validateString)
        cls.addProperty('category',                         basestring, required=True, cast=validateCategory)
        cls.addProperty('subcategory',                      basestring, required=True, cast=validateSubcategory)
        cls.addProperty('subtitle',                         basestring, cast=validateString)
        cls.addProperty('desc',                             basestring, cast=validateString)

        cls.addProperty('address_street',                   basestring)
        cls.addProperty('address_street_ext',               basestring)
        cls.addProperty('address_locality',                 basestring)
        cls.addProperty('address_region',                   basestring)
        cls.addProperty('address_postcode',                 basestring)
        cls.addProperty('address_country',                  basestring) ### TODO: Add cast to check ISO code

        cls.addProperty('coordinates',                      basestring, cast=validateCoordinates)
        cls.addProperty('year',                             int) 
        cls.addProperty('artist',                           basestring)
        cls.addProperty('album',                            basestring)
        cls.addProperty('author',                           basestring)
        cls.addProperty('network',                          basestring)
        cls.addProperty('director',                         basestring)
        cls.addProperty('genre',                            basestring)

    def exportEntity(self, authUserId):

        kind    = list(Entity.mapSubcategoryToKinds(self.subcategory))[0]
        entity  = buildEntity(kind=kind)

        entity.schema_version   = 0
        entity.types            = list(Entity.mapSubcategoryToTypes(self.subcategory))
        entity.title            = self.title

        def addField(entity, field, value, timestamp):
            if value is not None and value != '':
                try:
                    setattr(entity, field, value)
                    setattr(entity, '%s_source' % field, 'seed')
                    setattr(entity, '%s_timestamp' % field, timestamp)
                except AttributeError:
                    pass

        def addListField(entity, field, value, entityMini=None, timestamp=None):
            if value is not None and value != '':
                try:
                    if entityMini is not None:
                        item = entityMini()
                        item.title = value
                    else:
                        item = value
                    getattr(entity, field).append(item)
                    setattr(entity, '%s_source' % field, 'seed')
                    setattr(entity, '%s_timestamp' % field, timestamp)
                except AttributeError:
                    pass

        now = datetime.utcnow()

        addField(entity, 'desc', self.desc, now)

        if self.year is not None:
            addField(entity, 'release_date', datetime(int(self.year), 1, 1), timestamp=now)

        addField(entity, 'address_street', self.address_street, timestamp=now)
        addField(entity, 'address_street_ext', self.address_street_ext, timestamp=now)
        addField(entity, 'address_locality', self.address_locality, timestamp=now)
        addField(entity, 'address_region', self.address_region, timestamp=now)
        addField(entity, 'address_postcode', self.address_postcode, timestamp=now)
        # Only add country if other fields are set, too
        if self.address_street is not None \
            or self.address_locality is not None \
            or self.address_region is not None \
            or self.address_postcode is not None:
            addField(entity, 'address_country', self.address_country, timestamp=now)

        addListField(entity, 'artists', self.artist, PersonEntityMini, timestamp=now)
        addListField(entity, 'collections', self.album, MediaCollectionEntityMini, timestamp=now)
        addListField(entity, 'authors', self.author, PersonEntityMini, timestamp=now)
        addListField(entity, 'networks', self.network, BasicEntityMini, timestamp=now)
        addListField(entity, 'directors', self.director, PersonEntityMini, timestamp=now)
        addListField(entity, 'genres', self.genre, timestamp=now)

        if _coordinatesFlatToDict(self.coordinates) is not None:
            coords = Coordinates().dataImport(_coordinatesFlatToDict(self.coordinates))
            addField(entity, 'coordinates', coords, now)

        entity.sources.user_generated_id = authUserId
        entity.sources.user_generated_timestamp = now
        if self.subtitle is not None and self.subtitle != '':
            entity.sources.user_generated_subtitle = self.subtitle

        return entity

class HTTPEntityId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                        basestring, required=True)

class HTTPEntityEdit(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                        basestring, required=True)
        cls.addProperty('secret',                           basestring, required=True)

class HTTPEntityUpdate(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                        basestring, required=True)
        cls.addProperty('secret',                           basestring, required=True)          
        cls.addProperty('title',                            basestring)
        cls.addProperty('desc',                             basestring)
        cls.addProperty('image_url',                        basestring)
        
        # sources
        cls.addProperty('rdio_url',                         basestring)
        cls.addProperty('itunes_url',                       basestring)
        cls.addProperty('imdb_url',                         basestring)
        cls.addProperty('fandango_url',                     basestring)
        cls.addProperty('amazon_url',                       basestring)
        cls.addProperty('netflix_url',                      basestring)
        cls.addProperty('singleplatform_url',               basestring)
        cls.addProperty('spotify_id',                       basestring)
        cls.addProperty('opentable_url',                    basestring)
        cls.addProperty('tombstone_id',                     basestring)
        # Comma-separated list of nemesis ids.
        cls.addProperty('nemesis_ids',                      basestring)

        cls.addProperty('break_cluster',                    basestring)
        cls.addProperty('purge_tombstone',                  basestring)
        cls.addProperty('purge_tracks',                     basestring)
        cls.addProperty('purge_image',                      basestring)

        # place
        cls.addProperty('address_street',                   basestring)
        cls.addProperty('address_street_ext',               basestring)
        cls.addProperty('address_locality',                 basestring)
        cls.addProperty('address_region',                   basestring)
        cls.addProperty('address_postcode',                 basestring)
        cls.addProperty('address_country',                  basestring)

        cls.addProperty('phone',                            basestring)



class HTTPEntityIdSearchId(Schema): ### TODO: Remove?
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                        basestring)
        cls.addProperty('search_id',                        basestring)

class HTTPEntitySearchRequest(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('query',                            basestring, required=True) 
        cls.addProperty('category',                         basestring, required=True, cast=validateCategory)
        cls.addProperty('coordinates',                      basestring)

    def exportCoordinates(self):
        if self.coordinates is not None:
            return Coordinates().dataImport(_coordinatesFlatToDict(self.coordinates))
        return None

class HTTPEntitySuggestionRequest(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('category',                         basestring, required=True, cast=validateCategory)
        cls.addProperty('subcategory',                      basestring)
        cls.addProperty('coordinates',                      basestring)

    def exportCoordinates(self):
        if self.coordinates is not None:
            return Coordinates().dataImport(_coordinatesFlatToDict(self.coordinates))
        return None

class HTTPEntitySearchResultsItem(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('search_id',                        basestring, required=True)
        cls.addProperty('title',                            basestring, required=True)
        cls.addProperty('subtitle',                         basestring)
        cls.addProperty('category',                         basestring, required=True)
        cls.addProperty('icon',                             basestring)
        cls.addProperty('distance',                         float)

    def importEntity(self, entity, distance=None):
        self.search_id          = entity.search_id
        self.title              = entity.title
        self.subtitle           = entity.subtitle
        self.category           = entity.category

        if entity.kind == 'place':
            address = entity.formatAddress()
            if address is not None:
                self.subtitle = address

        # Build icon
        if entity.isType('restaurant'):
            self.icon = _getIconURL('search_restaurant')
        elif entity.isType('bar'):
            self.icon = _getIconURL('search_bar')
        elif entity.isType('cafe'):
            self.icon = _getIconURL('search_cafe')
        elif entity.kind == 'place':
            self.icon = _getIconURL('search_place')
        elif entity.isType('tv'):
            self.icon = _getIconURL('search_tv')
        elif entity.isType('movie'):
            self.icon = _getIconURL('search_movie')
        elif entity.isType('artist'):
            self.icon = _getIconURL('search_artist')
        elif entity.isType('album'):
            self.icon = _getIconURL('search_album')
        elif entity.isType('track'):
            self.icon = _getIconURL('search_track')
        elif entity.isType('app'):
            self.icon = _getIconURL('search_app')
        elif entity.isType('book'):
            self.icon = _getIconURL('search_book')
        else:
            self.icon = _getIconURL('search_other')

        if isinstance(distance, float) and distance >= 0:
            self.distance = distance

        assert self.search_id is not None

        return self

class HTTPEntitySearchResultsGroup(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('entities',               HTTPEntitySearchResultsItem)
        cls.addProperty('title',                            basestring)
        cls.addProperty('subtitle',                         basestring)
        cls.addProperty('image_url',                        basestring)

class HTTPEntityActionEndpoint(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('status',                           basestring)
        cls.addProperty('message',                          basestring)
        cls.addProperty('redirect',                         basestring)

class HTTPActionComplete(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('action',                           basestring)
        cls.addProperty('source',                           basestring)
        cls.addProperty('source_id',                        basestring)
        cls.addProperty('entity_id',                        basestring)
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('stamp_id',                         basestring)


# ###### #
# Slices #
# ###### #

class HTTPTimeSlice(Schema):
    @classmethod
    def setSchema(cls):

        def validateScope(scope):
            if scope is None:
                return None
            scope = scope.lower()
            ### TEMP
            if scope == 'everyone':
                scope = 'popular'
            if scope in set(['me', 'inbox', 'friends', 'popular', 'todo', 'user', 'credit']):
                return scope 
            raise StampedInputError("Invalid scope: %s" % scope)

        # Paging
        cls.addProperty('before',                           int)
        cls.addProperty('limit',                            int)
        cls.addProperty('offset',                           int)

        # Filtering
        cls.addProperty('category',                         basestring, cast=validateCategory)
        cls.addProperty('subcategory',                      basestring, cast=validateSubcategory)
        cls.addProperty('viewport',                         basestring, cast=validateViewport)

        # Scope
        cls.addProperty('user_id',                          basestring, cast=validateUserId)
        cls.addProperty('scope',                            basestring, cast=validateScope, required=True) 

    def exportTimeSlice(self):
        data                = self.dataExport()
        beforeData          = data.pop('before', None)
        viewportData        = data.pop('viewport', None)
        categoryData        = data.pop('category', None)
        subcategoryData     = data.pop('subcategory', None)

        slc                 = TimeSlice()
        slc.dataImport(data)

        if self.before is not None:
            slc.before          = datetime.utcfromtimestamp(int(self.before))

        if self.subcategory is not None:
            slc.kinds = list(Entity.mapSubcategoryToKinds(self.subcategory))
            slc.types = list(Entity.mapSubcategoryToTypes(self.subcategory))
        elif self.category is not None:
            slc.kinds = list(Entity.mapCategoryToKinds(self.category))
            slc.types = list(Entity.mapCategoryToTypes(self.category))

        if self.viewport is not None:
            slc.viewport = _convertViewport(self.viewport)

        return slc

class HTTPTodoTimeSlice(HTTPTimeSlice):
    def __init__(self):
        HTTPTimeSlice.__init__(self)
        self.scope = 'todo'

class HTTPSearchSlice(Schema):
    @classmethod
    def setSchema(cls):

        def validateScope(scope):
            if scope is None:
                return None
            scope = scope.lower()
            ### TEMP
            if scope == 'everyone':
                scope = 'popular'
            if scope in set(['me', 'inbox', 'friends', 'popular', 'todo', 'user', 'credit']):
                return scope 
            raise StampedInputError("Invalid scope: %s" % scope)

        # Paging
        cls.addProperty('limit',                            int) # Max 50

        # Filtering
        cls.addProperty('category',                         basestring, cast=validateCategory)
        cls.addProperty('subcategory',                      basestring, cast=validateSubcategory)
        cls.addProperty('viewport',                         basestring, cast=validateViewport)

        # Scope
        cls.addProperty('user_id',                          basestring, cast=validateUserId)
        cls.addProperty('scope',                            basestring, cast=validateScope)
        cls.addProperty('query',                            basestring, required=True)

    def exportSearchSlice(self):
        data                = self.dataExport()
        beforeData          = data.pop('before', None)
        viewportData        = data.pop('viewport', None)
        categoryData        = data.pop('category', None)
        subcategoryData     = data.pop('subcategory', None)

        slc                 = SearchSlice()
        slc.dataImport(data)

        if self.subcategory is not None:
            slc.kinds = list(Entity.mapSubcategoryToKinds(self.subcategory))
            slc.types = list(Entity.mapSubcategoryToTypes(self.subcategory))
        elif self.category is not None:
            slc.kinds = list(Entity.mapCategoryToKinds(self.category))
            slc.types = list(Entity.mapCategoryToTypes(self.category))

        if self.viewport is not None:
            slc.viewport = _convertViewport(self.viewport)

        return slc

class HTTPRelevanceSlice(Schema):
    @classmethod
    def setSchema(cls):

        def validateScope(scope):
            if scope is None:
                return None
            scope = scope.lower()
            ### TEMP
            if scope == 'everyone':
                scope = 'popular'
            if scope in set(['me', 'inbox', 'friends', 'popular', 'todo', 'user', 'credit']):
                return scope 
            raise StampedInputError("Invalid scope: %s" % scope)

        # Filtering
        cls.addProperty('category',                         basestring, cast=validateCategory)
        cls.addProperty('subcategory',                      basestring, cast=validateSubcategory)
        cls.addProperty('viewport',                         basestring, cast=validateViewport)

        # Scope
        cls.addProperty('user_id',                          basestring, cast=validateUserId)
        cls.addProperty('scope',                            basestring, cast=validateScope)

    def exportRelevanceSlice(self):
        data                = self.dataExport()
        beforeData          = data.pop('before', None)
        viewportData        = data.pop('viewport', None)
        categoryData        = data.pop('category', None)
        subcategoryData     = data.pop('subcategory', None)

        slc                 = RelevanceSlice()
        slc.dataImport(data)

        if self.subcategory is not None:
            slc.kinds = list(Entity.mapSubcategoryToKinds(self.subcategory))
            slc.types = list(Entity.mapSubcategoryToTypes(self.subcategory))
        elif self.category is not None:
            slc.kinds = list(Entity.mapCategoryToKinds(self.category))
            slc.types = list(Entity.mapCategoryToTypes(self.category))

        if self.viewport is not None:
            slc.viewport = _convertViewport(self.viewport)

        return slc

class HTTPCommentSlice(Schema):
    @classmethod
    def setSchema(cls):
        # Paging
        cls.addProperty('before',                           int)
        cls.addProperty('limit',                            int)
        cls.addProperty('offset',                           int)

        # Scope
        cls.addProperty('stamp_id',                         basestring, cast=validateStampId)

    def exportBefore(self):
        if self.before is not None:
            return datetime.utcfromtimestamp(int(self.before))
        return None

class HTTPActivitySlice(Schema):
    @classmethod
    def setSchema(cls):
        # Paging
        cls.addProperty('limit',                            int)
        cls.addProperty('offset',                           int)

        # Scope
        cls.addProperty('scope',                            basestring) # me, friends

    def __init__(self):
        Schema.__init__(self)
        self.limit = 20
        self.offset = 0

class HTTPGuideRequest(Schema):
    @classmethod
    def setSchema(cls):
        def validateSection(section):
            if section is None:
                return None
            section = section.lower()
            if section in set(['food', 'music', 'film', 'book', 'app']):
                return section 
            raise StampedInputError("Invalid section: %s" % section)

        def validateSubsection(subsection):
            if subsection is None:
                return None
            subsection = subsection.lower()
            if subsection in set(['restaurant', 'bar', 'cafe', 'artist', 'album', 'track', 'movie', 'tv']):
                return subsection
            raise StampedInputError("Invalid subsection: %s" % subsection)

        def validateScope(scope):
            if scope is None:
                return None
            scope = scope.lower()
            ### TEMP
            if scope == 'everyone':
                scope = 'popular'
            if scope in set(['me', 'inbox', 'popular']):
                return scope 
            raise StampedInputError("Invalid scope: %s" % scope)


        cls.addProperty('limit',                            int)
        cls.addProperty('offset',                           int)
        cls.addProperty('section',                          basestring, required=True, cast=validateSection)
        cls.addProperty('subsection',                       basestring, cast=validateSubsection)
        cls.addProperty('viewport',                         basestring, cast=validateViewport)
        cls.addProperty('scope',                            basestring, required=True, cast=validateScope)

    def exportGuideRequest(self):
        data = self.dataExport()
        if 'viewport' in data:
            del(data['viewport'])
        guideRequest = GuideRequest()
        guideRequest.dataImport(data)

        if self.viewport is not None:
            guideRequest.viewport = _convertViewport(self.viewport)

        return guideRequest

class HTTPGuideSearchRequest(HTTPGuideRequest):
    @classmethod
    def setSchema(cls):
        cls.addProperty('query',                            basestring, required=True)

    def __init__(self):
        HTTPGuideRequest.__init__(self)

    def exportGuideSearchRequest(self):
        data = self.dataExport()
        if 'viewport' in data:
            del(data['viewport'])
        guideSearchRequest = GuideSearchRequest()
        guideSearchRequest.dataImport(data)

        if self.viewport is not None:
            guideSearchRequest.viewport = _convertViewport(self.viewport)

        return guideSearchRequest


# ###### #
# Stamps #
# ###### #

class HTTPStampContent(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('blurb',                            basestring)
        cls.addNestedPropertyList('blurb_references',       HTTPTextReference)
        cls.addNestedPropertyList('images',                 HTTPImage)
        cls.addProperty('created',                          basestring)
        cls.addProperty('modified',                         basestring)

class HTTPBadge(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring, required=True, cast=validateUserId)
        cls.addProperty('genre',                            basestring, required=True)

class HTTPStampMini(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                         basestring, required=True)
        cls.addNestedProperty('entity',                     HTTPEntityMini, required=True)
        cls.addNestedProperty('user',                       HTTPUserMini, required=True)
        cls.addNestedPropertyList('contents',               HTTPStampContent)
        cls.addNestedPropertyList('credits',                HTTPStampPreview)
        cls.addNestedPropertyList('badges',                 HTTPBadge)
        cls.addProperty('via',                              basestring)
        cls.addProperty('url',                              basestring)
        cls.addProperty('created',                          basestring)
        cls.addProperty('modified',                         basestring)
        cls.addProperty('stamped',                          basestring)

        cls.addProperty('num_comments',                     int)
        cls.addProperty('num_likes',                        int)
        cls.addProperty('num_todos',                        int)
        cls.addProperty('num_credits',                      int)

        cls.addProperty('is_liked',                         bool)
        cls.addProperty('is_todo',                          bool)

    def __init__(self):
        Schema.__init__(self)
        self.is_liked           = False
        self.is_todo            = False

class HTTPStamp(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                         basestring, required=True)
        cls.addNestedProperty('entity',                     HTTPEntityMini, required=True)
        cls.addNestedProperty('user',                       HTTPUserMini, required=True)
        cls.addNestedPropertyList('contents',               HTTPStampContent, required=True)
        cls.addNestedPropertyList('credits',                HTTPStampPreview)
        cls.addNestedProperty('previews',                   HTTPPreviews)
        cls.addNestedPropertyList('badges',                 HTTPBadge)
        cls.addProperty('via',                              basestring)
        cls.addProperty('url',                              basestring)
        cls.addProperty('created',                          basestring)
        cls.addProperty('modified',                         basestring)
        cls.addProperty('stamped',                          basestring)
        
        cls.addProperty('num_comments',                     int)
        cls.addProperty('num_likes',                        int)
        cls.addProperty('num_todos',                        int)
        cls.addProperty('num_credits',                      int)

        cls.addProperty('is_liked',                         bool)
        cls.addProperty('is_todo',                          bool)

    def __init__(self):
        Schema.__init__(self)
        self.is_liked           = False
        self.is_todo            = False

    def importStampMini(self, stamp):
        entity                  = stamp.entity
        coordinates             = getattr(entity, 'coordinates', None)
        credits                 = getattr(stamp, 'credits', [])

        data = stamp.dataExport()

        data['contents'] = []
        if 'previews' in data:
            del(data['previews'])
        if 'credits' in data:
            del(data['credits'])
        self.dataImport(data, overflow=True)

        self.user               = HTTPUserMini().importUserMini(stamp.user)
        self.entity             = HTTPEntityMini().importEntity(entity)
        self.entity.coordinates = _coordinatesDictToFlat(coordinates)
        self.created            = stamp.timestamp.stamped
        self.modified           = stamp.timestamp.modified
        self.stamped            = stamp.timestamp.stamped

        if credits is not None and len(credits) > 0:
            httpCredit = []
            for item in credits:
                httpStampPreview = HTTPStampPreview().importStampPreview(item)
                httpCredit.append(httpStampPreview)
            self.credits = httpCredit

        contents = []
        for content in stamp.contents:
            item                    = HTTPStampContent()
            item.blurb              = content.blurb
            item.created            = content.timestamp.created

            if content.blurb is not None:
                blurb, references = _buildTextReferences(content.blurb)
                if len(references) > 0:
                    item.blurb = blurb
                    item.blurb_references = references

            if content.images is not None:
                newImages = []
                for image in content.images:
                    img = HTTPImage().dataImport(image.dataExport())
                    newImages.append(img)
                item.images = newImages

            # Return contents in chronological order
            contents.append(item)

        self.contents = contents

        self.num_comments   = getattr(stamp.stats, 'num_comments', 0)
        self.num_likes      = getattr(stamp.stats, 'num_likes', 0)
        self.num_todos      = getattr(stamp.stats, 'num_todos', 0)
        self.num_credits    = getattr(stamp.stats, 'num_credit', 0)

        self.url = generateStampUrl(stamp)

        if stamp.attributes is not None:
            self.is_liked   = getattr(stamp.attributes, 'is_liked', False)
            self.is_todo    = getattr(stamp.attributes, 'is_todo', False)

        return self

    def importStamp(self, stamp):
        self.importStampMini(stamp)
        previews = HTTPPreviews()

        if stamp.previews.comments is not None:
            comments = []
            for comment in stamp.previews.comments:
                comment = HTTPComment().importComment(comment)
                comments.append(comment)
            previews.comments = comments

        if stamp.previews.todos is not None:
            todos = []
            for user in stamp.previews.todos:
                user    = HTTPUserMini().importUserMini(user)
                todos.append(user)
            previews.todos = todos

        if stamp.previews.likes is not None:
            likes = []
            for user in stamp.previews.likes:
                user    = HTTPUserMini().importUserMini(user)
                likes.append(user)
            previews.likes = likes

        if stamp.previews.credits is not None:
            credits = []
            for credit in stamp.previews.credits:
                credit  = HTTPStampPreview().importStampPreview(credit)
                credits.append(credit)
            previews.credits = credits

        self.previews = previews

        return self

    def minimize(self):
        return HTTPStampMini().dataImport(self.dataExport(), overflow=True)

class HTTPStampNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                        basestring)
        cls.addProperty('search_id',                        basestring)
        cls.addProperty('blurb',                            basestring)
        cls.addProperty('credits',                          basestring) # comma-separated screen names
        cls.addProperty('temp_image_url',                   basestring)

class HTTPStampShare(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('service_name',                     basestring, required=True)
        cls.addProperty('stamp_id',                         basestring, required=True)
        cls.addProperty('temp_image_url',                   basestring)

class HTTPStampEdit(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                         basestring, required=True, cast=validateStampId)
        cls.addProperty('blurb',                            basestring)
        cls.addProperty('credits',                          basestring) # comma-separated screen names

class HTTPStampId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                         basestring, cast=validateStampId)

class HTTPStampRef(Schema):
    @classmethod
    def setSchema(cls):
        # stamp_id or (user_id and stamp_num)
        cls.addProperty('stamp_id',                         basestring)
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('stamp_num',                        int)

class HTTPStampedByGroup(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('count',                            int)
        cls.addNestedPropertyList('stamps',                 HTTPStampPreview)

    def importStampedByGroup(self, group):
        if group.count is not None:
            self.count = group.count 

        if group.stamps is not None:
            self.stamps = [HTTPStampPreview().importStampPreview(s) for s in group.stamps]

        return self

class HTTPStampedBy(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('friends',                    HTTPStampedByGroup)
        cls.addNestedProperty('all',                        HTTPStampedByGroup)

    def importStampedBy(self, stampedBy):
        if stampedBy.friends is not None:
            self.friends = HTTPStampedByGroup().importStampedByGroup(stampedBy.friends)

        if stampedBy.all is not None:
            self.all = HTTPStampedByGroup().importStampedByGroup(stampedBy.all)

        return self


# #### #
# Todo #
# #### #

class HTTPTodoSource(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('entity',                     HTTPEntityMini, required=True)
        cls.addPropertyList('stamp_ids',                    basestring)

class HTTPTodo(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('todo_id',                          basestring, required=True)
        cls.addProperty('user_id',                          basestring, required=True)
        cls.addNestedProperty('source',                     HTTPTodoSource, required=True)
        cls.addProperty('stamp_id',                         basestring) # set if the user has stamped this todo item
        cls.addNestedProperty('previews',                   HTTPPreviews)
        cls.addProperty('created',                          basestring)
        cls.addProperty('complete',                         bool)

    def importTodo(self, todo):
        self.todo_id                = todo.todo_id
        self.user_id                = todo.user.user_id
        self.created                = todo.timestamp.created
        self.complete               = todo.complete

        self.source                 = HTTPTodoSource()
        self.source.entity          = HTTPEntityMini().importEntity(todo.entity)
        if todo.source_stamps is not None:
            self.source.stamp_ids   = map(lambda x: getattr(x, 'stamp_id'), todo.source_stamps)
            
        self.previews               = HTTPPreviews()
        if todo.previews is not None and todo.previews.todos is not None:
            self.previews.todos     = [HTTPUserMini().importUserMini(u) for u in todo.previews.todos]

        if todo.stamp is not None:
            self.stamp_id              = todo.stamp.stamp_id 

        return self

class HTTPTodoNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                        basestring)
        cls.addProperty('search_id',                        basestring)
        cls.addProperty('stamp_id',                         basestring, cast=validateStampId)

class HTTPTodoComplete(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                        basestring)
        cls.addProperty('complete',                         bool)


# ######## #
# Activity #
# ######## #

class  HTTPActivityObjects(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('users',                  HTTPUserMini)
        cls.addNestedPropertyList('stamps',                 HTTPStamp)
        cls.addNestedPropertyList('entities',               HTTPEntityMini)
        cls.addNestedPropertyList('comments',               HTTPComment)

class HTTPActivity(Schema):
    @classmethod
    def setSchema(cls):
        # Metadata
        cls.addProperty('activity_id',                      basestring, required=True)
        cls.addProperty('created',                          basestring)
        cls.addProperty('benefit',                          int)
        cls.addNestedProperty('action',                     HTTPAction)

        # Structure
        cls.addProperty('verb',                             basestring)
        cls.addNestedPropertyList('subjects',               HTTPUserMini)
        cls.addNestedProperty('objects',                    HTTPActivityObjects)
        cls.addProperty('source',                           basestring)

        # Image
        cls.addProperty('image',                            basestring) ### TODO: Change to image_url
        cls.addProperty('icon',                             basestring)

        # Text
        cls.addProperty('header',                           basestring)
        cls.addNestedPropertyList('header_references',      HTTPTextReference)
        cls.addProperty('body',                             basestring)
        cls.addNestedPropertyList('body_references',        HTTPTextReference)
        cls.addProperty('footer',                           basestring)
        cls.addNestedPropertyList('footer_references',      HTTPTextReference)

    def importEnrichedActivity(self, activity):
        data = activity.dataExport()
        data.pop('subjects', None)
        data.pop('objects', None)

        self.dataImport(data, overflow=True)

        self.created = activity.timestamp.created
        if activity.timestamp.modified is not None:
            self.created = activity.timestamp.modified

        if self.icon is not None:
            self.icon = _getIconURL(self.icon)

        if activity.subjects is not None:
            subjects = []
            for user in activity.subjects:
                subjects.append(HTTPUserMini().importUserMini(user))
            self.subjects = subjects

        if not activity.personal:
            del(self.benefit)

        def _addUserObjects():
            if self.objects is None:
                self.objects = HTTPActivityObjects()
            if activity.objects is not None and activity.objects.users is not None:
                userobjects = []
                for user in activity.objects.users:
                    userobjects.append(HTTPUserMini().importUserMini(user))
                self.objects.users = userobjects 

        def _addStampObjects():
            if self.objects is None:
                self.objects = HTTPActivityObjects()
            if activity.objects is not None and activity.objects.stamps is not None:
                stampobjects = []
                for stamp in activity.objects.stamps:
                    stampobjects.append(HTTPStamp().importStamp(stamp))
                self.objects.stamps = stampobjects

        def _addEntityObjects():
            if self.objects is None:
                self.objects = HTTPActivityObjects()
            if activity.objects is not None and activity.objects.entities is not None:
                entityobjects = []
                for entity in activity.objects.entities:
                    entityobjects.append(HTTPEntityMini().importEntity(entity))
                self.objects.entities = entityobjects 

        def _addCommentObjects():
            if self.objects is None:
                self.objects = HTTPActivityObjects()
            if activity.objects is not None and activity.objects.comments is not None:
                commentobjects = []
                for comment in activity.objects.comments:
                    comment = HTTPComment().importComment(comment)
                    commentobjects.append(comment)
                self.objects.comments = commentobjects 

        def _buildStampAction(stamp):
            source              = HTTPActionSource()
            source.name         = 'View "%s"' % stamp.entity.title
            source.source       = 'stamped'
            source.source_id    = stamp.stamp_id

            action              = HTTPAction()
            action.type         = 'stamped_view_stamp'
            action.name         = 'View "%s"' % stamp.entity.title
            action.sources      = [ source ]

            return action

        def _buildEntityAction(entity):
            source              = HTTPActionSource()
            source.name         = 'View "%s"' % entity.title
            source.source       = 'stamped'
            source.source_id    = entity.entity_id

            action              = HTTPAction()
            action.type         = 'stamped_view_entity'
            action.name         = 'View "%s"' % entity.title
            action.sources      = [ source ]

            return action

        def _buildUserAction(user):
            source              = HTTPActionSource()
            source.name         = 'View profile'
            source.source       = 'stamped'
            source.source_id    = user.user_id

            action              = HTTPAction()
            action.type         = 'stamped_view_user'
            action.name         = 'View profile'
            action.sources      = [ source ]

            return action

        def _buildFBLoginAction(user):
            source              = HTTPActionSource()
            source.name         = 'Connect to Facebook'
            source.source       = 'facebook'
            source.endpoint     = 'account/linked/facebook/login.json'
            source.source_id    = user.user_id

            action              = HTTPAction()
            action.type         = 'facebook_connect'
            action.name         = 'Connect to Facebook'
            action.sources      = [ source ]

            return action

        def _formatUserObjects(users, required=True, offset=0):
            if users is None or len(users) == 0:
                if required:
                    raise Exception("No user objects!")
                return None, []

            if len(users) == 1:
                text            = unicode(users[0].screen_name)

                ref0            = HTTPTextReference()
                ref0.indices    = [offset, offset + len(text)]
                ref0.action     = _buildUserAction(users[0])

                return text, [ ref0 ]

            if len(users) == 2:
                text            = '%s and %s' % (users[0].screen_name, users[1].screen_name)

                ref0            = HTTPTextReference()
                ref0.indices    = [offset, offset + len(users[0].screen_name)]
                ref0.action     = _buildUserAction(users[0])

                ref1            = HTTPTextReference()
                ref1.indices    = [offset + len(text) - len(users[1].screen_name), offset + len(text)]
                ref1.action     = _buildUserAction(users[1])

                return text, [ ref0, ref1 ]

            text            = '%s and %s others' % (users[0].screen_name, len(users) - 1)

            ref0            = HTTPTextReference()
            ref0.indices    = [offset, offset + len(users[0].screen_name)]
            ref0.action     = _buildUserAction(users[0])

            ref1            = HTTPTextReference()
            ref1.indices    = [offset + len(users[0].screen_name) + len(' and '), offset + len(text)]

            return text, [ ref0, ref1 ]

        def _formatStampObjects(stamps, required=True, offset=0):
            if stamps is None or len(stamps) == 0:
                if required:
                    raise Exception("No stamp objects!")
                return None, []

            if len(stamps) == 1:
                text            = unicode(stamps[0].entity.title)

                ref0            = HTTPTextReference()
                ref0.indices    = [offset, offset + len(text)]
                ref0.action     = _buildStampAction(stamps[0])

                return text, [ ref0 ]

            if len(stamps) == 2:
                text            = '%s and %s' % (stamps[0].entity.title, stamps[1].entity.title)

                ref0            = HTTPTextReference()
                ref0.indices    = [offset, offset + len(stamps[0].entity.title)]
                ref0.action     = _buildStampAction(stamps[0])

                ref1            = HTTPTextReference()
                ref1.indices    = [offset + len(text) - len(stamps[1].entity.title), offset + len(text)]
                ref1.action     = _buildStampAction(stamps[1])

                return text, [ ref0, ref1 ]

            text            = '%s and %s other stamps' % (stamps[0].entity.title, len(stamps) - 1)

            ref0            = HTTPTextReference()
            ref0.indices    = [offset, offset + len(stamps[0].entity.title)]
            ref0.action     = _buildStampAction(stamps[0])

            ref1            = HTTPTextReference()
            ref1.indices    = [offset + len(stamps[0].entity.title) + len(' and '), offset + len(text)]

            return text, [ ref0, ref1 ]

        def _formatEntityObjects(entities, required=True, offset=0):
            if entities is None or len(entities) == 0:
                if required:
                    raise Exception("No entity objects!")
                return None, []

            if len(entities) == 1:
                text            = unicode(entities[0].title)

                ref0            = HTTPTextReference()
                ref0.indices    = [offset, offset + len(text)]
                ref0.action     = _buildEntityAction(entities[0])

                return text, [ ref0 ]

            if len(entities) == 2:
                text            = '%s and %s' % (entities[0].title, entities[1].title)

                ref0            = HTTPTextReference()
                ref0.indices    = [offset, offset + len(entities[0].title)]
                ref0.action     = _buildEntityAction(entities[0])

                ref1            = HTTPTextReference()
                ref1.indices    = [offset + len(text) - len(entities[1].title), offset + len(text)]
                ref1.action     = _buildEntityAction(entities[1])

                return text, [ ref0, ref1 ]

            text            = '%s and %s others' % (entities[0].title, len(entities) - 1)

            ref0            = HTTPTextReference()
            ref0.indices    = [offset, offset + len(entities[0].title)]
            ref0.action     = _buildEntityAction(entities[0])

            ref1            = HTTPTextReference()
            ref1.indices    = [offset + len(entities[0].title) + len(' and '), offset + len(text)]

            return text, [ ref0, ref1 ]

        def _formatCommentObjects(comments, required=True, offset=0):
            if comments is None or len(comments) == 0:
                if required:
                    raise Exception("No comment objects!")
                return None, []

            if len(comments) == 1:
                text            = '%s: %s' % (comments[0].user.screen_name, comments[0].blurb)

                ref0            = HTTPTextReference()
                ref0.indices    = [offset, offset + len(comments[0].user.screen_name) + 1]
                ref0.action     = _buildUserAction(comments[0].user)

                return text, [ ref0 ]

            raise Exception("Too many comments! \n%s" % comments)

        def _formatStampBlurbObjects(stamps, required=True, offset=0):
            if stamps is None or len(stamps) == 0:
                if required:
                    raise Exception("No stamp objects!")
                return None, []

            if len(stamps) == 1:
                text            = '%s: %s' % (stamps[0].user.screen_name, stamps[0].contents[0].blurb)

                ref0            = HTTPTextReference()
                ref0.indices    = [offset, offset + len(stamps[0].user.screen_name) + 1]
                ref0.action     = _buildUserAction(stamps[0].user)

                return text, [ ref0 ]

            raise Exception("Too many stamps! \n%s" % stamps)

        if self.verb == 'follow':
            _addUserObjects()

            if len(self.subjects) == 1:
                verb = 'is now following'
            else:
                verb = 'are now following'
                self.image = _getIconURL('news_follow_group')

            subjects, subjectReferences = _formatUserObjects(self.subjects)

            if activity.personal:
                self.body = '%s %s you.' % (subjects, verb)
                self.body_references = subjectReferences
                self.icon = _getIconURL('news_follow')

                if len(self.subjects) == 1:
                    self.action = _buildUserAction(self.subjects[0])
                else:
                    ### TODO: Action to go to follower list
                    pass
            else:
                offset = len(subjects) + len(verb) + 2
                userObjects, userObjectReferences = _formatUserObjects(self.objects.users, offset=offset)
                self.body = '%s %s %s.' % (subjects, verb, userObjects)
                self.body_references = subjectReferences + userObjectReferences

                self.action = _buildUserAction(self.objects.users[0])

        elif self.verb == 'restamp' or self.verb == 'credit':
            _addStampObjects()

            subjects, subjectReferences = _formatUserObjects(self.subjects)
            offset = len(subjects) + len(' gave you credit for ')
            stampObjects, stampObjectReferences = _formatStampObjects(self.objects.stamps, offset=offset)

            self.benefit = len(self.subjects)
            self.body = '%s gave you credit for %s.' % (subjects, stampObjects)
            self.body_references = subjectReferences
            if len(self.subjects) > 1:
                self.image = _getIconURL('news_credit_group')

            self.action = _buildStampAction(self.objects.stamps[0])

        elif self.verb == 'like':
            _addStampObjects()

            self.icon = _getIconURL('news_like')
            subjects, subjectReferences = _formatUserObjects(self.subjects)
            verb = 'liked'
            offset = len(subjects) + len(verb) + 2
            stampObjects, stampObjectReferences = _formatStampObjects(self.objects.stamps, offset=offset)
            self.body = '%s %s %s.' % (subjects, verb, stampObjects)
            self.body_references = subjectReferences + stampObjectReferences

            if activity.personal:
                self.benefit = len(self.subjects)
            else:
                stampUsers = map(lambda x: x.user, self.objects.stamps)
                stampUserObjects, stampUserReferences = _formatUserObjects(stampUsers, offset=4)
                self.footer = 'via %s' % stampUserObjects
                self.footer_references = stampUserReferences

            if len(self.subjects) > 1:
                self.image = _getIconURL('news_like_group')

            self.action = _buildStampAction(self.objects.stamps[0])

        elif self.verb == 'todo':
            _addEntityObjects()

            self.icon = _getIconURL('news_todo')
            subjects, subjectReferences = _formatUserObjects(self.subjects)
            verb = 'added'
            offset = len(subjects) + len(verb) + 2
            entityObjects, entityObjectReferences = _formatEntityObjects(self.objects.entities, offset=offset)
            self.body = '%s %s %s as a to-do.' % (subjects, verb, entityObjects)
            self.body_references = subjectReferences + entityObjectReferences

            if len(self.subjects) > 1:
                self.image = _getIconURL('news_todo_group')

            if activity.objects.stamps is not None and len(activity.objects.stamps) > 0:
                _addStampObjects()
                self.action = _buildStampAction(self.objects.stamps[0])
            else:
                self.action = _buildEntityAction(self.objects.entities[0])

        elif self.verb == 'comment':
            _addStampObjects()
            _addCommentObjects()

            verb = 'Comment on'
            offset = len(verb) + 1
            commentObjects, commentObjectReferences = _formatCommentObjects(self.objects.comments)
            stampObjects, stampObjectReferences = _formatStampObjects(self.objects.stamps, offset=offset)
            self.header = '%s %s' % (verb, stampObjects)
            self.header_references = stampObjectReferences
            self.body = '%s' % commentObjects
            self.body_references = commentObjectReferences
            self.action = _buildStampAction(self.objects.stamps[0])

            if activity.personal:
                self.icon = _getIconURL('news_comment')

        elif self.verb == 'reply':
            if not activity.personal:
                logs.debug(self)
                raise Exception("Invalid universal news item: %s" % self.verb)

            _addStampObjects()
            _addCommentObjects()

            verb = 'Reply on'
            offset = len(verb) + 1
            commentObjects, commentObjectReferences = _formatCommentObjects(self.objects.comments)
            stampObjects, stampObjectReferences = _formatStampObjects(self.objects.stamps, offset=offset)
            self.header = '%s %s' % (verb, self.objects.stamps[0].entity.title)
            self.header_references = stampObjectReferences
            self.body = '%s' % commentObjects
            self.body_references = commentObjectReferences
            self.action = _buildStampAction(self.objects.stamps[0])
            self.icon = _getIconURL('news_reply')

        elif self.verb == 'mention':
            if not activity.personal:
                logs.debug(self)
                raise Exception("Invalid universal news item: %s" % self.verb)

            _addStampObjects()
            _addCommentObjects()

            verb = 'Mention on'
            offset = len(verb) + 1
            commentObjects, commentObjectReferences = _formatCommentObjects(self.objects.comments, required=False)
            stampBlurbObjects, stampBlurbObjectReferences = _formatStampBlurbObjects(self.objects.stamps, required=False)
            stampObjects, stampObjectReferences = _formatStampObjects(self.objects.stamps, offset=offset)
            self.header = 'Mention on %s' % self.objects.stamps[0].entity.title
            self.header_references = stampObjectReferences

            if commentObjects is not None:
                self.body = '%s' % commentObjects
                self.body_references = commentObjectReferences
            else:
                self.body = '%s' % stampBlurbObjects
                self.body_references = stampBlurbObjectReferences

            self.action = _buildStampAction(self.objects.stamps[0])
            self.icon = _getIconURL('news_mention')

        elif self.verb.startswith('friend_'):
            if not activity.personal:
                logs.debug(self)
                raise Exception("Invalid universal news item: %s" % self.verb)
            
            if self.verb == 'friend_twitter':
                self.icon = _getIconURL('news_twitter')
            elif self.verb == 'friend_facebook':
                self.icon = _getIconURL('news_facebook')
            else:
                self.icon = _getIconURL('news_friend')

            self.action = _buildUserAction(self.subjects[0])

        elif self.verb.startswith('action_'):
            if not activity.personal:
                logs.debug(self)
                raise Exception("Invalid universal news item: %s" % self.verb)
                
            _addStampObjects()

            if self.source is not None:
                actionMapping = {
                    'listen'            : '%(subjects)s listened to %(objects)s on %(source)s.',
                    'playlist'          : '%(subjects)s added %(objects)s to a playlist on %(source)s.',
                    'download'          : '%(subjects)s checked out %(objects)s on %(source)s.',
                    'reserve'           : '%(subjects)s checked out %(objects)s on %(source)s.',
                    'menu'              : '%(subjects)s viewed the menu for %(objects)s.',
                    'buy'               : '%(subjects)s checked out %(objects)s on %(source)s.',
                    'watch'             : '%(subjects)s checked out %(objects)s on %(source)s.',
                    'tickets'           : '%(subjects)s checked out %(objects)s on %(source)s.',
                    'queue'             : '%(subjects)s added %(objects)s to queue on %(source)s.',
                    }
            else:
                actionMapping = {
                    'listen'            : '%(subjects)s listened to %(objects)s.',
                    'playlist'          : '%(subjects)s added %(objects)s to a playlist.',
                    'download'          : '%(subjects)s checked out %(objects)s.',
                    'reserve'           : '%(subjects)s checked out %(objects)s.',
                    'menu'              : '%(subjects)s viewed the menu for %(objects)s.',
                    'buy'               : '%(subjects)s checked out %(objects)s.',
                    'watch'             : '%(subjects)s checked out %(objects)s.',
                    'tickets'           : '%(subjects)s checked out %(objects)s.',
                    'queue'             : '%(subjects)s added %(objects)s to queue.',
                    }

            subjects, subjectReferences = _formatUserObjects(self.subjects)
            verbs = ('completed', '')

            if self.verb[7:] in actionMapping.keys():
                verbs = actionMapping[self.verb[7:]]

            offset = verbs.index('%(objects)s') - len('%(subjects)s') + len(subjects)
            assert(offset < len(verbs))

            #offset = len(subjects) + len(verbs) + 2
            stampObjects, stampObjectReferences = _formatStampObjects(self.objects.stamps, offset=offset)

            sourceMapping = {
                'appstore'      : 'the App Store',
                'itunes'        : 'iTunes',
                'amazon'        : 'Amazon',
                'rdio'          : 'rdio',
                'spotify'       : 'Spotify',
                'netflix'       : 'Netflix',
                'opentable'     : 'OpenTable',
                'fandango'      : 'Fandango',
            }

            source = self.source
            if self.source in sourceMapping:
                source = sourceMapping[self.source]

            msgDict = {'subjects' : subjects, 'objects' : stampObjects, 'source' : source }
            self.body = verbs % msgDict

            self.body_references = subjectReferences + stampObjectReferences
            self.action = _buildStampAction(self.objects.stamps[0])

            # Action Icons
            actionIcons = set([
                'news_amazon',
                'news_appstore',
                'news_fandango',
                'news_itunes',
                'news_itunes_listen',
                'news_menu',
                'news_netflix_queue',
                'news_netflix_watch',
                'news_opentable',
                'news_rdio',
                'news_rdio_listen',
                'news_rdio_playlist',
                'news_spotify',
                'news_spotify_listen',
                'news_spotify_playlist',
            ])

            if 'news_%s_%s' % (self.source, self.verb[7:]) in actionIcons:
                self.icon = _getIconURL('news_%s_%s' % (self.source, self.verb[7:]))
            elif 'news_%s' % (self.source) in actionIcons:
                self.icon = _getIconURL('news_%s' % (self.source))
            elif 'news_%s' % (self.verb[7:]) in actionIcons:
                self.icon = _getIconURL('news_%s' % (self.verb[7:]))
            else:
                logs.warning("Unable to set icon for source '%s' and verb '%s'" % (self.source, self.verb[7:]))

            # Action Group Icons
            if len(self.subjects) > 1:
                actionGroupIcons = set([
                    'news_amazon_group',
                    'news_appstore_group',
                    'news_fandango_group',
                    'news_itunes_group',
                    'news_listen_group',
                    'news_menu_group',
                    'news_netflix_group',
                    'news_opentable_group',
                    'news_playlist_group',
                    'news_queue_group',
                    'news_rdio_group',
                    'news_spotify_group',
                    'news_watch_group',
                ])

                if 'news_%s_group' % (self.source) in actionGroupIcons:
                    self.image = _getIconURL('news_%s_group' % (self.source))
                elif 'news_%s_group' % (self.verb[7:]) in actionGroupIcons:
                    self.image = _getIconURL('news_%s_group' % (self.verb[7:]))
                else:
                    logs.warning("Unable to set group icon for source '%s' and verb '%s'" % (self.source, self.verb[7:]))
                    self.image = None

        elif self.verb.startswith('notification_'):
            if not activity.personal:
                logs.debug(self)
                raise Exception("Invalid universal news item: %s" % self.verb)
                
            if self.verb == 'notification_welcome':
                _addUserObjects()
                self.header = "Welcome to Stamped"
                self.image = _getIconURL('news_welcome')
                self.action = _buildUserAction(self.objects.users[0])
                
            elif self.verb == 'notification_upgrade':
                _addUserObjects()
                self.header = "Welcome to Stamped 2.0"
                self.image = _getIconURL('news_welcome')
                self.action = _buildUserAction(self.objects.users[0])

            elif self.verb == 'notification_fb_login':
                _addUserObjects()
                self.header = "Turn on Facebook Sharing"
                self.image = _getIconURL('fb_logo')
                self.action = _buildFBLoginAction(self.objects.users[0])

        else:
            raise Exception("Unrecognized verb: %s" % self.verb)

        return self


# #### #
# Menu #
# #### #

class HTTPHours(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('open',                             basestring)
        cls.addProperty('close',                            basestring)
        cls.addProperty('desc',                             basestring)

class HTTPTimes(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('sun',                    HTTPHours)
        cls.addNestedPropertyList('mon',                    HTTPHours)
        cls.addNestedPropertyList('tue',                    HTTPHours)
        cls.addNestedPropertyList('wed',                    HTTPHours)
        cls.addNestedPropertyList('thu',                    HTTPHours)
        cls.addNestedPropertyList('fri',                    HTTPHours)
        cls.addNestedPropertyList('sat',                    HTTPHours)

class HTTPMenuPrice(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                            basestring)
        cls.addProperty('price',                            basestring)
        cls.addProperty('calories',                         int)
        cls.addProperty('unit',                             basestring)
        cls.addProperty('currency',                         basestring)

class HTTPMenuItem(Schema):
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
        cls.addNestedPropertyList('prices',                 HTTPMenuPrice)

class HTTPMenuSection(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                            basestring)
        cls.addProperty('desc',                             basestring)
        cls.addProperty('short_desc',                       basestring)
        cls.addNestedPropertyList('items',                  HTTPMenuItem)

class HTTPSubmenu(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                            basestring)
        cls.addNestedProperty('times',                      HTTPTimes)
        cls.addProperty('footnote',                         basestring)
        cls.addProperty('desc',                             basestring)
        cls.addProperty('short_desc',                       basestring)
        cls.addNestedPropertyList('sections',               HTTPMenuSection)

class HTTPMenu(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('disclaimer',                       basestring)
        cls.addProperty('attribution_image',                basestring)
        cls.addProperty('attribution_image_link',           basestring)
        cls.addNestedPropertyList('menus',                  HTTPSubmenu)

    def importMenu(self, menu):
        self.dataImport(menu.dataExport(), overflow=True)
        return self


# ########## #
# ClientLogs #
# ########## #

class HTTPClientLogsEntry(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('key',                              basestring, required=True)
        cls.addProperty('value',                            basestring)

        # optional ids
        cls.addProperty('stamp_id',                         basestring)
        cls.addProperty('entity_id',                        basestring)
        cls.addProperty('todo_id',                          basestring)
        cls.addProperty('comment_id',                       basestring)
        cls.addProperty('activity_id',                      basestring)

    def exportClientLogsEntry(self):
        entry = ClientLogsEntry()
        entry.dataImport(self.dataExport(), overflow=True)
        return entry
