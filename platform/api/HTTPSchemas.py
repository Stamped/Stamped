#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import copy, urllib, urlparse, re, logs, string, time, utils
import libs.ec2_utils
import Entity

from errors             import *
from schema             import *
from api.Schemas        import *
from Entity             import *

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

def _coordinatesDictToFlat(coordinates):
    try:
        if isinstance(coordinates, Schema):
            coordinates = coordinates.dataExport()

        if not isinstance(coordinates['lat'], float) or not isinstance(coordinates['lng'], float):
            raise
        
        return '%s,%s' % (coordinates['lat'], coordinates['lng'])
    except Exception:
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

def _buildProfileImage(screenName, cache=None, sizes=[]):
    if not cache:
        url = 'http://static.stamped.com/users/default.jpg'
    elif cache + timedelta(days=1) <= datetime.utcnow():
        url = 'http://static.stamped.com/users/%s.jpg?%s' % \
              (str(screenName).lower(), int(time.mktime(cache.timetuple())))
    else:
        url = 'http://stamped.com.static.images.s3.amazonaws.com/users/%s.jpg?%s' % \
              (str(screenName).lower(), int(time.mktime(cache.timetuple())))

    image           = HTTPImageSchema()
    image_sizes     = []
    original        = HTTPImageSizeSchema()
    original.url    = url 
    image_sizes.append(original)

    for size in sizes:
        s           = HTTPImageSizeSchema()
        s.url       = url.replace('.jpg', '-%dx%d.jpg' % (size, size))
        s.width     = size 
        s.height    = size
        image_sizes.append(s)

    image.sizes = image_sizes
    
    return image

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

def _initialize_blurb_html(content):
    # TODO: debug
    """
    blurb = content.blurb
    data  = []
    
    # assumes non-overlapping blurb references
    for reference in content.blurb_references:
        action = reference.action
        
        if action.type == 'stamped_view_screen_name':
            repl_pre  = "<a class='screen-name' href=\"%s\">" % (action.sources[0].source_id)
            repl_post = "</a>"
        
        data.append((reference.indices, repl_pre, repl_post))
    
    html = [ ]
    last = 0
    
    for repl in sorted(data):
        indices, repl_pre, repl_post = repl
        
        html.append(blurb[last:indices[0]])
        html.append(repl_pre)
        html.append(blurb[indices[0]:indices[1]])
        html.append(repl_post)
        
        last = indices[1]
    
    html.append(blurb[last:])
    content.blurb_formatted = "".join(html)
    """
    pass

def _initialize_comment_html(comment):
    # TODO: debug
    """
    blurb = comment.blurb
    data  = []
    
    for mention in comment.mentions:
        repl_pre  = "<a class='screen-name' href=\"%s\">" % (mention.screen_name)
        repl_post = "</a>"
        
        data.append((mention.indices, repl_pre, repl_post))
    
    html = []
    last = 0
    
    for repl in sorted(data):
        indices, repl_pre, repl_post = repl
        
        html.append(blurb[last:indices[0]])
        html.append(repl_pre)
        html.append(blurb[indices[0]:indices[1]])
        html.append(repl_post)
        
        last = indices[1]
    
    html.append(blurb[last:])
    comment.blurb_formatted = "".join(html)
    """
    pass






# ######### #
# OAuth 2.0 #
# ######### #

class OAuthTokenRequest(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('refresh_token',                basestring, required=True)
        cls.addProperty('grant_type',                   basestring, required=True)

class OAuthLogin(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('login',                        basestring, required=True)
        cls.addProperty('password',                     basestring, required=True)

# TODO: Consolidate OAuthFacebookLogin and OAuthTwitterLogin after linked account generification?

class OAuthFacebookLogin(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_token',                     basestring, required=True)

class OAuthTwitterLogin(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_token',                   basestring, required=True)
        cls.addProperty('user_secret',                  basestring, required=True)

# ####### #
# Actions #
# ####### #

class HTTPActionCompletionData(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('action',                       basestring)
        cls.addProperty('source',                       basestring)
        cls.addProperty('source_id',                    basestring)
        cls.addProperty('entity_id',                    basestring)
        cls.addProperty('user_id',                      basestring)
        cls.addProperty('stamp_id',                     basestring)

class HTTPActionSource(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                         basestring, required=True)
        cls.addProperty('source',                       basestring, required=True)
        cls.addProperty('source_id',                    basestring)
        cls.addProperty('source_data',                  dict)
        cls.addProperty('endpoint',                     basestring)
        cls.addProperty('endpoint_data',                dict)
        cls.addProperty('link',                         basestring)
        cls.addProperty('icon',                         basestring)
        cls.addProperty('completion_endpoint',          basestring)
        cls.addProperty('completion_data',              dict) # dictionary?
    
    def setCompletion(self, **kwargs):
        self.completion_endpoint    = COMPLETION_ENDPOINT
        self.completion_data        = HTTPActionCompletionData().dataImport(kwargs, overflow=True).dataExport()

class HTTPAction(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('type',                         basestring, required=True)
        cls.addProperty('name',                         basestring, required=True)
        cls.addNestedPropertyList('sources',            HTTPActionSource, required=True)



# ####### #
# General #
# ####### #

class HTTPImageSizeSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('url',                          basestring)
        cls.addProperty('width',                        int)
        cls.addProperty('height',                       int)

class HTTPImageSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('sizes',              HTTPImageSizeSchema)
        cls.addProperty('caption',                      basestring)
        cls.addNestedProperty('action',                 HTTPAction)

class HTTPTextReference(Schema):
    @classmethod
    def setSchema(cls):
        cls.addPropertyList('indices',                  int, required=True)
        cls.addNestedProperty('action',                 HTTPAction)


# ####### #
# Account #
# ####### #

class HTTPAccount(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                          basestring, required=True)
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('auth_service',                     basestring, required=True)
        cls.addProperty('email',                            basestring, required=True)
        cls.addProperty('screen_name',                      basestring, required=True)
        cls.addProperty('privacy',                          bool, required=True)
        cls.addProperty('phone',                            basestring)

    def importAccount(self, account):
        self.dataImport(account.dataExport(), overflow=True)
        return self

class HTTPAccountNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('email',                            basestring, required=True)
        cls.addProperty('password',                         basestring, required=True)
        cls.addProperty('screen_name',                      basestring, required=True)
        cls.addProperty('phone',                            int)

        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring)
        cls.addProperty('location',                         basestring)
        cls.addProperty('color_primary',                    basestring)
        cls.addProperty('color_secondary',                  basestring)

        # for asynchronous image uploads
        cls.addProperty('temp_image_url',                   basestring)

    def convertToAccount(self):
        return Account().dataImport(self.dataExport(), overflow=True)

class HTTPFacebookAccountNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('screen_name',                      basestring, required=True)
        cls.addProperty('user_token',                       basestring, required=True)
        cls.addProperty('email',                            basestring)
        cls.addProperty('phone',                            int)

        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring)
        cls.addProperty('location',                         basestring)
        cls.addProperty('color_primary',                    basestring)
        cls.addProperty('color_secondary',                  basestring)

        cls.addProperty('temp_image_url',                   basestring)

    def convertToFacebookAccountNew(self):
        return FacebookAccountNew().dataImport(self.dataExport(), overflow=True)

class HTTPTwitterAccountNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                             basestring, required=True)
        cls.addProperty('screen_name',                      basestring, required=True)
        cls.addProperty('user_token',                       basestring, required=True)
        cls.addProperty('user_secret',                      basestring, required=True)
        cls.addProperty('email',                            basestring)
        cls.addProperty('phone',                            int)

        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring)
        cls.addProperty('location',                         basestring)
        cls.addProperty('color_primary',                    basestring)
        cls.addProperty('color_secondary',                  basestring)

        cls.addProperty('temp_image_url',                   basestring)

    def convertToTwitterAccountNew(self):
        return TwitterAccountNew().dataImport(self.dataExport(), overflow=True)



class HTTPAccountSettings(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('email',                            basestring)
        cls.addProperty('password',                         basestring)
        cls.addProperty('screen_name',                      basestring)
        cls.addProperty('privacy',                          bool)
        cls.addProperty('phone',                            int)

class HTTPAccountProfile(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                             basestring)
        cls.addProperty('bio',                              basestring)
        cls.addProperty('website',                          basestring)
        cls.addProperty('location',                         basestring)

class HTTPCustomizeStamp(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('color_primary',                    basestring, required=True)
        cls.addProperty('color_secondary',                  basestring, required=True)

class HTTPAccountProfileImage(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('profile_image',                    basestring) ### TODO: normalize=False
        
        # for asynchronous image uploads
        cls.addProperty('temp_image_url',                   basestring)

class HTTPAccountCheck(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('login',                            basestring, required=True)

class HTTPRemoveLinkedAccountForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('service_name',                     basestring, required=True)

class HTTPLinkedAccount(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('service_name',                     basestring, required=True)
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('screen_name',                      basestring)
        cls.addProperty('name',                             basestring)
        cls.addProperty('token',                            basestring)
        cls.addProperty('secret',                           basestring)
        cls.addProperty('token_expiration',                 datetime)

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

    def importLinkedAccounts(self, linked):
        if linked.twitter is not None:
            self.twitter = HTTPLinkedAccount().importLinkedAccount(linked.twitter)
        if linked.facebook is not None:
            self.facebook = HTTPLinkedAccount().importLinkedAccount(linked.facebook)
        if linked.netflix is not None:
            self.netflix = HTTPLinkedAccount().importLinkedAccount(linked.netflix)
        return self

    def exportLinkedAccounts(self):
        schema = LinkedAccounts()

        if self.twitter is not None:
            schema.twitter = LinkedAccount().dataImport(self.twitter.dataExport(), overflow=True)
        if self.facebook is not None:
            schema.facebook = LinkedAccount().dataImport(self.facebook.dataExport(), overflow=True)
        if self.twitter is not None:
            schema.netflix = LinkedAccount().dataImport(self.netflix.dataExport(), overflow=True)

        return schema 


class HTTPAvailableLinkedAccounts(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('twitter',                bool)
        cls.addProperty('facebook',               bool)
        cls.addProperty('netflix',                bool)

class HTTPAccountChangePassword(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('old_password',       basestring, required=True)
        cls.addProperty('new_password',       basestring, required=True)

class HTTPAccountAlerts(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('ios_alert_credit',       bool)
        cls.addProperty('ios_alert_like',         bool)
        cls.addProperty('ios_alert_todo',          bool)
        cls.addProperty('ios_alert_mention',      bool)
        cls.addProperty('ios_alert_comment',      bool)
        cls.addProperty('ios_alert_reply',        bool)
        cls.addProperty('ios_alert_follow',       bool)
        cls.addProperty('email_alert_credit',     bool)
        cls.addProperty('email_alert_like',       bool)
        cls.addProperty('email_alert_todo',        bool)
        cls.addProperty('email_alert_mention',    bool)
        cls.addProperty('email_alert_comment',    bool)
        cls.addProperty('email_alert_reply',      bool)
        cls.addProperty('email_alert_follow',     bool)

    def __init__(self):
        Schema.__init__(self)
        self.ios_alert_credit           = False
        self.ios_alert_like             = False
        self.ios_alert_todo             = False
        self.ios_alert_mention          = False
        self.ios_alert_comment          = False
        self.ios_alert_reply            = False
        self.ios_alert_follow           = False
        self.email_alert_credit         = False
        self.email_alert_like           = False
        self.email_alert_todo           = False
        self.email_alert_mention        = False
        self.email_alert_comment        = False
        self.email_alert_reply          = False
        self.email_alert_follow         = False

    def importAccount(self, account):
        alerts = getattr(account, 'alerts', None)
        if alerts is not None:
            self.dataImport(alerts.dataExport(), overflow=True)

        return self

class HTTPAPNSToken(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('token',              basestring, required=True)

# ##### #
# Users #
# ##### #

class HTTPUserId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                      basestring)
        cls.addProperty('screen_name',                  basestring)

class HTTPUserIds(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_ids',                     basestring) # Comma delimited
        cls.addProperty('screen_names',                 basestring) # Comma delimited

class HTTPUserSearch(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('q',                            basestring)
        cls.addProperty('limit',                        int)
        cls.addProperty('relationship',                 basestring)

class HTTPUserRelationship(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id_a',                    basestring)
        cls.addProperty('screen_name_a',                basestring)
        cls.addProperty('user_id_b',                    basestring)
        cls.addProperty('screen_name_b',                basestring)

class HTTPFindUser(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('q',                            basestring) # Comma delimited

class HTTPFindTwitterUser(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_token',                   basestring)
        cls.addProperty('user_secret',                  basestring)

class HTTPFindFacebookUser(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_token',                   basestring)

class HTTPFacebookLoginResponse(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('state',                        basestring) # passed back state value to prevent csrf attacks
        cls.addProperty('code',                         basestring) # code we'll exchange for a user token

class HTTPFacebookAuthResponse(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('access_token',                 basestring)
        cls.addProperty('expires',                      int)        # seconds until token expires

class HTTPNetflixId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('netflix_id',                   basestring)

class HTTPNetflixAuthResponse(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamped_oauth_token',          basestring)
        cls.addProperty('oauth_token',                  basestring)
        cls.addProperty('secret',                       basestring)
        cls.addProperty('oauth_verifier',               basestring)

class HTTPCategoryDistribution(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('category',                     basestring, required=True)
        cls.addProperty('name',                         basestring)
        cls.addProperty('icon',                         basestring)
        cls.addProperty('count',                        int)

class HTTPUser(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',                      basestring, required=True)
        cls.addProperty('name',                         basestring, required=True)
        cls.addProperty('screen_name',                  basestring, required=True)
        cls.addProperty('color_primary',                basestring)
        cls.addProperty('color_secondary',              basestring)
        cls.addProperty('bio',                          basestring)
        cls.addProperty('website',                      basestring)
        cls.addProperty('location',                     basestring)
        cls.addProperty('privacy',                      bool, required=True)
        cls.addNestedProperty('image',                  HTTPImageSchema)
        cls.addProperty('image_url',                    basestring)
        cls.addNestedPropertyList('distribution',       HTTPCategoryDistribution)
        
        cls.addProperty('following',                    bool)

        cls.addProperty('num_stamps',                   int)
        cls.addProperty('num_stamps_left',              int)
        cls.addProperty('num_friends',                  int)
        cls.addProperty('num_followers',                int)
        cls.addProperty('num_faves',                    int)
        cls.addProperty('num_credits',                  int)
        cls.addProperty('num_credits_given',            int)
        cls.addProperty('num_likes',                    int)
        cls.addProperty('num_likes_given',              int)

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
        self.image = _buildProfileImage(self.screen_name, 
                                        cache=user.timestamp.image_cache, 
                                        sizes=[144, 110, 92, 74, 72, 62, 55, 46, 37, 31])
        
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
        cls.addProperty('user_id',                      basestring, required=True)
        cls.addProperty('name',                         basestring, required=True)
        cls.addProperty('screen_name',                  basestring, required=True)
        cls.addProperty('color_primary',                basestring)
        cls.addProperty('color_secondary',              basestring)
        cls.addProperty('privacy',                      bool, required=True)
        cls.addNestedProperty('image',                  HTTPImageSchema)
        cls.addProperty('image_url',                    basestring)

    def importUserMini(self, mini):
        self.dataImport(mini.dataExport(), overflow=True)
        self.image_url = _profileImageURL(mini.screen_name, mini.timestamp.image_cache)
        self.image = _buildProfileImage(self.screen_name,
            cache=mini.timestamp.image_cache,
            sizes=[144, 110, 92, 74, 72, 62, 55, 46, 37, 31])

        return self

class HTTPSuggestedUserRequest(Schema):
    @classmethod
    def setSchema(cls):
        # paging
        cls.addProperty('limit',              int)
        cls.addProperty('offset',             int)
        
        cls.addProperty('personalized',       bool)
        cls.addProperty('coordinates',        basestring)
        
        # third party keys for optionally augmenting friend suggestions with 
        # knowledge from other social networks
        cls.addProperty('twitter_key',        basestring)
        cls.addProperty('twitter_secret',     basestring)
        
        cls.addProperty('facebook_token',     basestring)

    def __init__(self):
        Schema.__init__(self)
        self.limit          = 10
        self.offset         = 0
        self.personalized   = False

    def convertToSuggestedUserRequest(self):
        data = self.dataExport()
        coordinates = data.pop('coordinates', None)
        if coordinates is not None:
            data['coordinates'] = _coordinatesFlatToDict(coordinates)

        return SuggestedUserRequest().dataImport(data)

class HTTPUserImages(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('sizes',                  HTTPImageSizeSchema)

    def importUser(self, user):
        sizes = [144, 110, 92, 74, 72, 62, 55, 46, 37, 31]
        imageSizes = []

        for size in sizes:
            image           = HTTPImageSizeSchema()
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
        cls.addProperty('email',                basestring)

# ######## #
# Comments #
# ######## #

class HTTPComment(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('comment_id',           basestring, required=True)
        cls.addNestedProperty('user',           HTTPUserMini, required=True)
        cls.addProperty('stamp_id',             basestring, required=True)
        cls.addProperty('restamp_id',           basestring)
        cls.addProperty('blurb',                basestring, required=True)
        cls.addNestedPropertyList('mentions',   MentionSchema)
        cls.addProperty('created',              basestring)

    def importComment(self, comment):
        self.dataImport(comment.dataExport(), overflow=True)
        self.created = comment.timestamp.created
        self.user = HTTPUserMini().importUserMini(comment.user)
        return self

class HTTPCommentNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',             basestring, required=True)
        cls.addProperty('blurb',                basestring, required=True)

class HTTPCommentId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('comment_id',           basestring, required=True)


# ######## #
# Previews #
# ######## #

class HTTPStampPreview(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                         basestring)
        cls.addNestedProperty('user',                       HTTPUserMini)

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


# ########## #
# ClientLogs #
# ########## #

class HTTPClientLogsEntry(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('key',          basestring, required=True)
        cls.addProperty('value',        basestring)

        # optional ids
        cls.addProperty('stamp_id',     basestring)
        cls.addProperty('entity_id',    basestring)
        cls.addProperty('todo_id',      basestring)
        cls.addProperty('comment_id',   basestring)
        cls.addProperty('activity_id',  basestring)

    def exportClientLogsEntry(self):
        entry = ClientLogsEntry()
        entry.dataImport(self.dataExport(), overflow=True)
        return entry

# ################# #
# Endpoint Response #
# ################# #

class HTTPEndpointResponse(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('action',     HTTPAction)

    def setAction(self, actionType, name, sources, **kwargs):
        if len(sources) > 0:
            action          = HTTPAction()
            action.type     = actionType
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
            newimg = HTTPImageSchema()
            sizes = []
            for size in image.sizes:
                if size.url is not None:
                    newsize = HTTPImageSizeSchema()
                    newsize.url = _cleanImageURL(size.url)
                    sizes.append(newsize)
            newimg.sizes = sizes
            newImages.append(newimg)

    dest.images = newImages


class HTTPEntityAction(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('action',         HTTPAction, required=True)
        cls.addProperty('name',                 basestring, required=True)
        cls.addProperty('icon',                 basestring)

class HTTPEntityMetadataItem(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                basestring, required=True)
        cls.addProperty('value',                basestring, required=True)
        cls.addProperty('key',                  basestring)
        cls.addNestedProperty('action',         HTTPAction)
        cls.addProperty('icon',                 basestring)
        cls.addProperty('extended',             bool)
        cls.addProperty('optional',             bool)

class HTTPEntityGallery(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('images',     HTTPImageSchema, required=True)
        cls.addProperty('name',                 basestring)
        cls.addProperty('layout',               basestring) # 'list' or None

class HTTPEntityPlaylistItem(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',            basestring)
        cls.addProperty('name',                 basestring, required=True)
        cls.addNestedProperty('action',         HTTPAction)
        cls.addProperty('length',               int)
        cls.addProperty('icon',                 basestring)

class HTTPEntityPlaylist(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('data',       HTTPEntityPlaylistItem, required=True)
        cls.addProperty('name',                 basestring)

class HTTPEntityStampedBy(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('friends',              int, required=True)
        cls.addProperty('friends_of_friends',   int)
        cls.addProperty('everyone',             int)

class HTTPEntityMini(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',            basestring, required=True)
        cls.addProperty('title',                basestring, required=True)
        cls.addProperty('subtitle',             basestring, required=True)
        cls.addProperty('category',             basestring, required=True)
        cls.addProperty('subcategory',          basestring, required=True)
        cls.addProperty('coordinates',          basestring)
        cls.addNestedPropertyList('images',     HTTPImageSchema)

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
        cls.addNestedPropertyList('data',               HTTPEntityMini, required=True)
        cls.addProperty('title',                        basestring)


class HTTPEntity(Schema):
    @classmethod
    def setSchema(cls):
        # Core
        cls.addProperty('entity_id',                    basestring, required=True)
        cls.addProperty('title',                        basestring, required=True)
        cls.addProperty('subtitle',                     basestring, required=True)
        cls.addProperty('category',                     basestring, required=True)
        cls.addProperty('subcategory',                  basestring, required=True)
        cls.addProperty('caption',                      basestring)
        cls.addNestedPropertyList('images',             HTTPImageSchema)
        cls.addProperty('last_modified',                basestring)
        cls.addNestedProperty('previews',               HTTPPreviews)

        # Location
        cls.addProperty('address',                      basestring)
        cls.addProperty('neighborhood',                 basestring)
        cls.addProperty('coordinates',                  basestring)

        # Components
        cls.addNestedProperty('playlist',               HTTPEntityPlaylist)
        cls.addNestedPropertyList('actions',            HTTPEntityAction)
        cls.addNestedPropertyList('galleries',          HTTPEntityGallery)
        cls.addNestedPropertyList('metadata',           HTTPEntityMetadataItem)
        cls.addNestedProperty('stamped_by',             HTTPEntityStampedBy)
        cls.addNestedProperty('related',                HTTPEntityRelated)

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
                actionSource.name = 'View link'
                actionSource.source = 'link'

                action = HTTPAction()
                action.type = 'link'
                action.name = 'View link'
                action.sources = [actionSource]

                item.action = action

            if 'action' in kwargs:
                item.action = kwargs['action']

            metadata = self.metadata
            if metadata is None:
                metadata = []
            metadata.append(item)

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
        self.last_modified      = entity.timestamp.created
        
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
                    item                = HTTPImageSchema().dataImport(image.dataExport())
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
            
            if entity.sources.singleplatform_id is not None:
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
                    item = HTTPImageSchema().dataImport(image.dataExport(), overflow=True)
                    source              = HTTPActionSource()
                    source.source_id    = item.sizes[0].url
                    source.source       = 'stamped'
                    source.link         = item.sizes[0].url
                    action              = HTTPAction()
                    action.type         = 'stamped_view_image'
                    action.sources.append(source)
                    item.action     = action
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

            if entity.sources.amazon_underlying is not None:
                source              = HTTPActionSource()
                source.name         = 'Buy from Amazon'
                source.source       = 'amazon'
                source.source_id    = entity.sources.amazon_underlying
                source.icon         = _getIconURL('src_amazon', client=client)
                source.link         = _buildAmazonURL(entity.sources.amazon_underlying)
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
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
                source.name         = 'Watch on iTunes'
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

            self._addAction(actionType, 'Watch now', sources, icon=actionIcon)

            # Actions: Add to Netflix Instant Queue
            actionType  = 'add_to_instant_queue'
            actionIcon  = _getIconURL('act_play_primary', client=client)
            sources     = []
            
            if (entity.sources.netflix_id is not None and
                entity.sources.netflix_is_instant_available is not None and
                entity.sources.netflix_instant_available_until is not None and
                entity.sources.netflix_instant_available_until > datetime.now()):
                source                  = HTTPActionSource()
                source.name             = 'Add to Netflix Instant Queue'
                source.source           = 'netflix'
                source.source_id        = entity.sources.netflix_id
                source.endpoint         = 'account/linked/netflix/add_instant.json'
                source.endpoint_data    = {'netflix_id': entity.sources.netflix_id}
                source.icon             = _getIconURL('src_itunes', client=client)
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

            # Actions: Watch Now
            
            actionType  = 'watch'
            actionIcon  = _getIconURL('act_play_primary', client=client)
            sources     = []
            
            if entity.sources.itunes_id is not None and entity.sources.itunes_preview is not None:
                source              = HTTPActionSource()
                source.name         = 'Watch on iTunes'
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
            
            self._addAction(actionType, 'Watch now', sources, icon=actionIcon)
            
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

            actionType  = 'add_to_instant_queue'
            actionIcon  = _getIconURL('act_play_primary', client=client)
            sources     = []

            if (entity.sources.netflix_id is not None and
                entity.sources.netflix_is_instant_available is not None and
                entity.sources.netflix_instant_available_until is not None and
                entity.sources.netflix_instant_available_until > datetime.now()):
                source                  = HTTPActionSource()
                source.name             = 'Add to Netflix Instant Queue'
                source.source           = 'netflix'
                source.source_id        = entity.sources.netflix_id
                source.endpoint         = 'account/linked/netflix/add_instant.json'
                source.endpoint_data    = { 'netflix_id': entity.sources.netflix_id }
                source.icon             = _getIconURL('src_itunes', client=client)
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            self._addAction(actionType, 'Add to Netflix Instant Queue', sources, icon=actionIcon)

            # Actions: Watch Trailer

            ### TODO: Add source

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
                        self._addMetadata('Artist', entity.artists[0].title, action=action, optional=True)
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
                        self._addMetadata('Artist', entity.artists[0].title, action=action, optional=True)
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
                if getattr(entity.sources, 'itunes_url', None) is not None:
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
                        if song.entity_id is not None:
                            item.entity_id = song.entity_id
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
                                item.entity_id = 'T_ITUNES_%s' % song.itunes_id

                        if getattr(song.sources, 'rdio_id', None) is not None:
                            source                      = HTTPActionSource()
                            source.name                 = 'Listen on Rdio'
                            source.source               = 'rdio'
                            source.source_id            = song.sources.rdio_id
                            source.icon                 = _getIconURL('src_rdio', client=client)
                            sources.append(source)

                            if item.entity_id is None:
                                item.entity_id = 'T_RDIO_%s' % song.rdio_id

                        if getattr(song.sources, 'spotify_id', None) is not None:
                            source                      = HTTPActionSource()
                            source.name                 = 'Listen on Spotify'
                            source.source               = 'spotify'
                            source.source_id            = song.sources.spotify_id
                            source.icon                 = _getIconURL('src_spotify', client=client)
                            sources.append(source)

                            if item.entity_id is None:
                                item.entity_id = 'T_SPOTIFY_%s' % song.spotify_id

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
                        pass

                if len(data) > 0:
                    playlist.data = data
                    self.playlist = playlist

            # Albums

            if entity.isType('artist') and entity.albums is not None and len(entity.albums) > 0:
                gallery = HTTPEntityGallery()
                gallery.layout = 'list'
                images = []
                for album in entity.albums:
                    try:
                        item            = HTTPImageSchema()
                        size            = HTTPImageSizeSchema()
                        ### TODO: Add placeholder if image doesn't exist
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
                source.name         = 'Download from iTunes'
                source.source       = 'itunes'
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
                    item = HTTPImageSchema().dataImport(screenshot.dataExport())
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
            self.coordinates    = _coordinatesDictToFlat(mini.coordinates)

        return self

# HTTPEntity Components




class HTTPEntityNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                basestring, required=True)
        cls.addProperty('subtitle',             basestring, required=True)
        cls.addProperty('category',             basestring, required=True)
        cls.addProperty('subcategory',          basestring, required=True)
        cls.addProperty('desc',                 basestring)
        cls.addProperty('address',              basestring)
        cls.addProperty('coordinates',          basestring)
        cls.addProperty('cast',                 basestring)
        cls.addProperty('director',             basestring)
        cls.addProperty('release_date',         basestring)
        cls.addProperty('artist',               basestring)
        cls.addProperty('album',                basestring)
        cls.addProperty('author',               basestring)

    def exportEntity(self, authUserId):

        kind    = list(mapSubcategoryToKinds(self.subcategory))[0]
        entity  = buildEntity(kind=kind)

        entity.schema_version   = 0
        entity.types            = list(mapSubcategoryToTypes(self.subcategory))
        entity.title            = self.title

        def addField(entity, field, value, timestamp):
            if value is not None:
                try:
                    setattr(entity, field, value)
                    setattr(entity, '%s_source' % field, 'seed')
                    setattr(entity, '%s_timestamp' % field, timestamp)
                except AttributeError:
                    pass

        def addListField(entity, field, value, entityMini=None, timestamp=None):
            if value is not None:
                try:
                    if entityMini is not None:
                        item = entityMini()
                        entityMini.title = value
                    else:
                        item = value
                    getattr(entity, field).append(item)
                    setattr(entity, '%s_source' % field, 'seed')
                    setattr(entity, '%s_timestamp' % field, timestamp)
                except AttributeError:
                    pass

        now = datetime.utcnow()

        addField(entity, 'desc', self.desc, now)
        addField(entity, 'formatted_address', self.address, now)
        addField(entity, 'release_date', self.release_date, now)

        if _coordinatesFlatToDict(self.coordinates) is not None:
            coords = CoordinatesSchema().dataImport(_coordinatesFlatToDict(self.coordinates))
            addField(entity, 'coordinates', coords, now)

        entity.sources.user_generated_id            = authUserId
        entity.sources.user_generated_subtitle      = self.subtitle
        entity.sources.user_generated_timestamp     = now

        addListField(entity, 'directors', self.director, PersonEntityMini, now)
        addListField(entity, 'cast', self.cast, PersonEntityMini, now)
        addListField(entity, 'authors', self.author, PersonEntityMini, now)
        addListField(entity, 'artists', self.artist, PersonEntityMini, now)
        addListField(entity, 'collections', self.album, MediaCollectionEntityMini, now)

        return entity

#    class HTTPEntityEdit(Schema):
#        @classmethod
#        def setSchema(cls):
#            cls.addProperty('entity_id',            basestring, required=True)
#            cls.addProperty('title',                basestring)
#            cls.addProperty('subtitle',             basestring)
#            cls.addProperty('category',             basestring)
#            cls.addProperty('subcategory',          basestring)
#            cls.addProperty('desc',                 basestring)
#            cls.addProperty('address',              basestring)
#            cls.addProperty('coordinates',          basestring)
#
#        def exportSchema(self, schema):
#            if schema.__class__.__name__ == 'Entity':
#                schema.importData({
#                    'entity_id':    self.entity_id,
#                    'title':        self.title,
#                    'subtitle':     self.subtitle,
#                    'category':     self.category,
#                    'subcategory':  self.subcategory,
#                    'desc':         self.desc
#                })
#                schema.details.place.address = self.address
#                schema.coordinates = _coordinatesFlatToDict(self.coordinates)
#            else:
#                raise NotImplementedError(type(schema))
#            return schema

class HTTPEntityId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                    basestring, required=True)

class HTTPEntityIdSearchId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',                    basestring)
        cls.addProperty('search_id',                    basestring)

class HTTPEntityAutoSuggestForm(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('query',                        basestring, required=True)
        cls.addProperty('category',                     basestring)
        cls.addProperty('coordinates',                  basestring)

    def exportEntityAutoSuggestForm(self):
        return EntityAutoSuggestForm().dataImport(self.dataExport(), overflow=True)

class HTTPEntitySearch(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('q',                            basestring, required=True)
        cls.addProperty('coordinates',                  basestring)
        cls.addProperty('category',                     basestring)
        cls.addProperty('local',                        bool)

    def __init__(self):
        Schema.__init__(self)

    def exportEntitySearch(self):
        data = self.dataExport()
        if 'coordinates' in data:
            del(data['coordinates'])
        if 'category' in data and data['category'] is not None:
            if data['category'] not in Entity.categories:
                raise StampedInputError("Invalid category: %s" % data['category'])

        entSearch = EntitySearch().dataImport(data, overflow=True)
        if self.coordinates is not None:
            coords = CoordinatesSchema().dataImport(_coordinatesFlatToDict(self.coordinates))
            entSearch.coordinates = coordinates 
        return entSearch

class HTTPEntityNearby(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('coordinates',                  basestring, required=True)
        cls.addProperty('category',                     basestring)
        cls.addProperty('subcategory',                  basestring)
        cls.addProperty('page',                         int)

    def __init__(self):
        Schema.__init__(self)
        self.page = 0

    def exportEntityNearby(self):
        data = self.dataExport()
        del(data['coordinates'])

        entityNearby = EntityNearby().dataImport(data, overflow=True)

        coords = CoordinatesSchema().dataImport(_coordinatesFlatToDict(self.coordinates))
        entityNearby.coordinates = coords
        return entityNearby

class HTTPEntitySuggested(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('coordinates',                  basestring)
        cls.addProperty('category',                     basestring)
        cls.addProperty('subcategory',                  basestring)
        cls.addProperty('limit',                        int)

    def exportEntitySuggested(self):
        data = self.dataExport()
        coordinates = data.pop('coordinates', None)

        entitySuggested = EntitySuggested().dataImport(data, overflow=True)

        if coordinates is not None:
            coords = CoordinatesSchema().dataImport(_coordinatesFlatToDict(coordinates))
            entitySuggested.coordinates = coords

        return entitySuggested



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

        if isinstance(distance, float) and distance >= 0:
            self.distance       = distance
            
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
        # Paging
        cls.addProperty('before',               int)
        cls.addProperty('limit',                int)
        cls.addProperty('offset',               int)

        # Filtering
        cls.addProperty('category',             basestring)
        cls.addProperty('subcategory',          basestring)
        # cls.addProperty('properties',           basestring) # comma-separated list
        cls.addProperty('viewport',             basestring) # lat0,lng0,lat1,lng1

        # Scope
        cls.addProperty('user_id',              basestring)
        cls.addProperty('scope',                basestring) # me, inbox, friends, fof, popular

    def exportTimeSlice(self):
        data                = self.dataExport()
        beforeData          = data.pop('before', None)
        viewportData        = data.pop('viewport', None)
        propertiesData      = data.pop('properties', None)

        slc                 = TimeSlice()
        slc.dataImport(data)

        if self.before is not None:
            slc.before          = datetime.utcfromtimestamp(int(self.before))

        if self.viewport is not None:
            viewportData        = self.viewport.split(',')
            
            coordinates0        = CoordinatesSchema()
            coordinates0.lat    = viewportData[0]
            coordinates0.lng    = viewportData[1]
            
            coordinates1        = CoordinatesSchema()
            coordinates1.lat    = viewportData[2]
            coordinates1.lng    = viewportData[3]

            viewport            = ViewportSchema()
            viewport.upperLeft  = coordinates0
            viewport.lowerRight = coordinates1

            slc.viewport        = viewport 

        # if self.properties is not None:
        #     slc.properties      = self.properties.split(',')

        return slc

class HTTPSearchSlice(Schema):
    @classmethod
    def setSchema(cls):
        # Paging
        cls.addProperty('limit',                int) # Max 50

        # Filtering
        cls.addProperty('category',             basestring)
        cls.addProperty('subcategory',          basestring)
        # cls.addProperty('properties',           basestring) # comma-separated list
        cls.addProperty('viewport',             basestring) # lat0,lng0,lat1,lng1

        # Scope
        cls.addProperty('user_id',              basestring)
        cls.addProperty('scope',                basestring) # me, inbox, friends, fof, popular
        cls.addProperty('query',                basestring, required=True)

    def exportSearchSlice(self):
        data                = self.dataExport()
        beforeData          = data.pop('before', None)
        viewportData        = data.pop('viewport', None)
        propertiesData      = data.pop('properties', None)

        slc                 = SearchSlice()
        slc.dataImport(data)

        if self.viewport is not None:
            viewportData        = self.viewport.split(',')
            
            coordinates0        = CoordinatesSchema()
            coordinates0.lat    = viewportData[0]
            coordinates0.lng    = viewportData[1]
            
            coordinates1        = CoordinatesSchema()
            coordinates1.lat    = viewportData[2]
            coordinates1.lng    = viewportData[3]

            viewport            = ViewportSchema()
            viewport.upperLeft  = coordinates0
            viewport.lowerRight = coordinates1

            slc.viewport        = viewport 

        # if self.properties is not None:
        #     slc.properties      = self.properties.split(',')

        return slc

class HTTPRelevanceSlice(Schema):
    @classmethod
    def setSchema(cls):
        # Filtering
        cls.addProperty('category',             basestring)
        cls.addProperty('subcategory',          basestring)
        cls.addProperty('properties',           basestring) # comma-separated list
        cls.addProperty('viewport',             basestring) # lat0,lng0,lat1,lng1

        # Scope
        cls.addProperty('user_id',              basestring)
        cls.addProperty('scope',                basestring) # me, inbox, friends, fof, popular

    def exportRelevanceSlice(self):
        data                = self.dataExport()
        beforeData          = data.pop('before', None)
        viewportData        = data.pop('viewport', None)
        propertiesData      = data.pop('properties', None)

        slc                 = RelevanceSlice()
        slc.dataImport(data)

        if self.viewport is not None:
            viewportData        = self.viewport.split(',')
            
            coordinates0        = CoordinatesSchema()
            coordinates0.lat    = viewportData[0]
            coordinates0.lng    = viewportData[1]
            
            coordinates1        = CoordinatesSchema()
            coordinates1.lat    = viewportData[2]
            coordinates1.lng    = viewportData[3]

            viewport            = ViewportSchema()
            viewport.upperLeft  = coordinates0
            viewport.lowerRight = coordinates1

            slc.viewport        = viewport 

        # if self.properties is not None:
        #     slc.properties      = self.properties.split(',')

        return slc

class HTTPCommentSlice(Schema):
    @classmethod
    def setSchema(cls):
        # Paging
        cls.addProperty('before',               int)
        cls.addProperty('limit',                int)
        cls.addProperty('offset',               int)

        # Scope
        cls.addProperty('stamp_id',             basestring)

    def exportCommentSlice(self):
        data                = self.dataExport()
        beforeData          = data.pop('before', None)

        slc                 = CommentSlice()
        slc.dataImport(data)

        if self.before is not None:
            slc.before = datetime.utcfromtimestamp(int(self.before))

        return slc



class HTTPGenericSlice(Schema):
    @classmethod
    def setSchema(cls):
        # paging
        cls.addProperty('limit',                int)
        cls.addProperty('offset',               int)

        # sorting
        # (relevance, popularity, proximity, created, modified, alphabetical)
        cls.addProperty('sort',                 basestring)
        cls.addProperty('reverse',              bool)
        cls.addProperty('coordinates',          basestring)

        # filtering
        cls.addProperty('since',                int)
        cls.addProperty('before',               int)

    def __init__(self):
        Schema.__init__(self)
        self.sort = 'modified'
        self.reverse = False

    def _convertData(self, data):
        coordinates = data.pop('coordinates', None)
        if coordinates is not None:
            data['coordinates'] = _coordinatesFlatToDict(coordinates)
            if data['coordinates'] is None:
                raise StampedInputError("invalid coordinates parameter; format \"lat,lng\"")

        since = data.pop('since', None)
        if since is not None:
            try:
                data['since'] = datetime.utcfromtimestamp(int(since) - 2)
            except Exception:
                raise StampedInputError("invalid since parameter; must be a valid UNIX timestamp")

        before = data.pop('before', None)
        if before is not None:
            try:
                data['before'] = datetime.utcfromtimestamp(int(before) + 2)
            except Exception:
                raise StampedInputError("invalid since parameter; must be a valid UNIX timestamp")

        # TODO: validate since <= before

        if 'offset' not in data or data['offset'] == None:
            data['offset'] = 0

        return data

    def exportGenericSlice(self):
        data = self._convertData(self.dataExport())

        return GenericSlice().dataImport(data)

class HTTPGenericCollectionSlice(HTTPGenericSlice):
    @classmethod
    def setSchema(cls):
        # filtering
        cls.addProperty('query',                basestring)
        cls.addProperty('category',             basestring)
        cls.addProperty('subcategory',          basestring)
        cls.addProperty('viewport',             basestring) # "lat0,lng0,lat1,lng1"

        # misc options
        cls.addProperty('quality',              int)
        cls.addProperty('deleted',              bool)
        cls.addProperty('comments',             bool)
        cls.addProperty('unique',               bool)

    def __init__(self):
        Schema.__init__(self)
        self.quality            = 1
        self.deleted            = False
        self.comments           = True
        self.unique             = False

    def _convertData(self, data):
        data = super(HTTPGenericCollectionSlice, self)._convertData(data)

        viewport = data.pop('viewport', None)
        if viewport is not None:
            try:
                lat0, lng0, lat1, lng1 = viewport.split(',')

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
            except Exception:
                raise StampedInputError("invalid viewport parameter; format \"lat0,lng0,lat1,lng1\"")

        return data

    def exportGenericCollectionSlice(self):
        data = self._convertData(self.dataExport())
        return GenericCollectionSlice().dataImport(data)

class HTTPUserCollectionSlice(HTTPGenericCollectionSlice):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',          basestring)
        cls.addProperty('screen_name',      basestring)

    def exportUserCollectionSlice(self):
        data = self._convertData(self.dataExport())
        return UserCollectionSlice().dataImport(data)

class HTTPFriendsSlice(HTTPGenericCollectionSlice):
    @classmethod
    def setSchema(cls):
        cls.addProperty('distance',         int)
        cls.addProperty('inclusive',        bool)

    def exportFriendsSlice(self):
        data = self._convertData(self.dataExport())
        return FriendsSlice().dataImport(data)

class HTTPConsumptionSlice(HTTPGenericCollectionSlice):
    @classmethod
    def setSchema(cls):
        cls.addProperty('scope',            basestring) # you, friends, fof, everyone

    def exportConsumptionSlice(self):
        data = self._convertData(self.dataExport())
        return ConsumptionSlice().dataImport(data)


class HTTPGuideRequest(Schema):
    @classmethod
    def setSchema(cls):
        def checkSection(section):
            if section is None:
                return None
            section = section.lower()
            if section in set(['food', 'music', 'film', 'book', 'app']):
                return section 
            raise StampedInputError("Invalid section: %s" % section)

        def checkSubsection(subsection):
            if subsection is None:
                return None
            subsection = subsection.lower()
            if subsection in set(['restaurant', 'bar', 'cafe', 'artist', 'album', 'track', 'movie', 'tv']):
                return subsection
            raise StampedInputError("Invalid subsection: %s" % subsection)

        cls.addProperty('limit',                            int)
        cls.addProperty('offset',                           int)
        cls.addProperty('section',                          basestring, required=True, cast=checkSection)
        cls.addProperty('subsection',                       basestring, cast=checkSubsection)
        cls.addProperty('viewport',                         basestring) # lat0,lng0,lat1,lng1
        cls.addProperty('scope',                            basestring)

    def exportGuideRequest(self):
        # return GuideRequest().dataImport(self.dataExport(), overflow=True)

        data = self.dataExport()
        if 'viewport' in data:
            del(data['viewport'])
        guideRequest = GuideRequest()
        guideRequest.dataImport(data)

        if self.viewport is not None:
            viewportData            = self.viewport.split(',')
            
            coordinates0            = CoordinatesSchema()
            coordinates0.lat        = viewportData[0]
            coordinates0.lng        = viewportData[1]
            
            coordinates1            = CoordinatesSchema()
            coordinates1.lat        = viewportData[2]
            coordinates1.lng        = viewportData[3]

            viewport                = ViewportSchema()
            viewport.upperLeft      = coordinates0
            viewport.lowerRight     = coordinates1

            guideRequest.viewport   = viewport 

        return guideRequest

class HTTPGuideSearchRequest(HTTPGuideRequest):
    @classmethod
    def setSchema(cls):
        cls.addProperty('query',                            basestring, required=True)

    def __init__(self):
        HTTPGuideRequest.__init__(self)




# ###### #
# Stamps #
# ###### #

class HTTPStampContent(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('blurb',                        basestring)
        cls.addNestedPropertyList('blurb_references',   HTTPTextReference)
        cls.addProperty('blurb_formatted',              basestring)
        cls.addNestedPropertyList('images',             HTTPImageSchema)
        cls.addProperty('created',                      basestring)
        cls.addProperty('modified',                     basestring)

class HTTPBadge(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',              basestring, required=True)
        cls.addProperty('genre',                basestring, required=True)

class HTTPStampMini(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',             basestring, required=True)
        cls.addNestedProperty('entity',         HTTPEntityMini, required=True)
        cls.addNestedProperty('user',           HTTPUserMini, required=True)
        cls.addNestedPropertyList('contents',   HTTPStampContent)
        cls.addNestedPropertyList('credit',     HTTPStampPreview)
        cls.addNestedPropertyList('badges',     HTTPBadge)
        cls.addProperty('via',                  basestring)
        cls.addProperty('url',                  basestring)
        cls.addProperty('created',              basestring)
        cls.addProperty('modified',             basestring)
        cls.addProperty('stamped',              basestring)
        
        cls.addProperty('num_comments',         int)
        cls.addProperty('num_likes',            int)
        cls.addProperty('num_todos',            int)
        cls.addProperty('num_credits',          int)

        cls.addProperty('is_liked',             bool)
        cls.addProperty('is_todo',               bool)

    def __init__(self):
        Schema.__init__(self)
        self.is_liked           = False
        self.is_todo            = False

class HTTPStamp(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',             basestring, required=True)
        cls.addNestedProperty('entity',         HTTPEntityMini, required=True)
        cls.addNestedProperty('user',           HTTPUserMini, required=True)
        cls.addNestedPropertyList('contents',   HTTPStampContent, required=True)
        cls.addNestedPropertyList('credit',     HTTPStampPreview)
        cls.addNestedProperty('previews',       HTTPPreviews)
        cls.addNestedPropertyList('badges',     HTTPBadge)
        cls.addProperty('via',                  basestring)
        cls.addProperty('url',                  basestring)
        cls.addProperty('created',              basestring)
        cls.addProperty('modified',             basestring)
        cls.addProperty('stamped',              basestring)

        cls.addProperty('num_comments',         int)
        cls.addProperty('num_likes',            int)
        cls.addProperty('num_todos',            int)
        cls.addProperty('num_credits',          int)

        cls.addProperty('is_liked',             bool)
        cls.addProperty('is_todo',               bool)

    def __init__(self):
        Schema.__init__(self)
        self.is_liked           = False
        self.is_todo            = False

    def importStampMini(self, stamp):
        entity                  = stamp.entity
        coordinates             = getattr(entity, 'coordinates', None)
        credit                  = getattr(stamp, 'credit', [])

        data = stamp.dataExport()
        data['contents'] = []
        if 'previews' in data:
            del(data['previews'])
        if 'credit' in data:
            del(data['credit'])
        self.dataImport(data, overflow=True)

        self.user               = HTTPUserMini().importUserMini(stamp.user)
        self.entity             = HTTPEntityMini().importEntity(entity)
        self.entity.coordinates = _coordinatesDictToFlat(coordinates)
        self.created            = stamp.timestamp.stamped
        self.modified           = stamp.timestamp.modified
        self.stamped            = stamp.timestamp.stamped

        if credit is not None and len(credit) > 0:
            httpCredit = []
            for item in credit:
                httpStampPreview = HTTPStampPreview().importStampPreview(item)
                httpCredit.append(httpStampPreview)
            self.credit = httpCredit

        contents = []
        for content in stamp.contents:
            item                    = HTTPStampContent()
            item.blurb              = content.blurb
            item.created            = content.timestamp.created
            #item.modified          = content.timestamp.modified

            blurb_references        = []
            for screenName in mention_re.finditer(content.blurb):
                source                  = HTTPActionSource()
                source.name             = 'View profile'
                source.source           = 'stamped'
                source.source_id        = screenName.groups()[0]

                action              = HTTPAction()
                action.type         = 'stamped_view_screen_name'
                action.name         = 'View profile'
                action.sources      = [ source ]

                reference           = HTTPTextReference()
                reference.indices   = [ screenName.start(), screenName.end() ]
                reference.action    = action

                blurb_references.append(reference)

            if len(blurb_references) > 0:
                item.blurb_references = blurb_references

            if content.images is not None:
                newImages = []
                for image in content.images:
                    img = HTTPImageSchema().dataImport(image.dataExport())
                    # quick fix for now
                    # img.sizes[0].url = 'http://static.stamped.com/stamps/%s.jpg' % schema.stamp_id
                    newImages.append(img)
                item.images = newImages

            # Insert contents in descending chronological order
            contents.insert(0, item)
        self.contents = contents

        self.num_comments   = getattr(stamp.stats, 'num_comments', 0)
        self.num_likes      = getattr(stamp.stats, 'num_likes', 0)
        self.num_todos      = getattr(stamp.stats, 'num_todos', 0)
        self.num_credits    = getattr(stamp.stats, 'num_credits', 0)

        url_title = encodeStampTitle(stamp.entity.title)
        self.url = 'http://www.stamped.com/%s/stamps/%s/%s' %\
                   (stamp.user.screen_name, stamp.stats.stamp_num, url_title)

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
                #_initialize_comment_html(comment)
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

class HTTPStampDetail(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('screen_name',              basestring)
        cls.addProperty('stamp_num',                int)
        cls.addProperty('stamp_title',              basestring)

class HTTPImageUpload(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('image',                basestring)

        # for asynchronous image uploads
        cls.addProperty('temp_image_url',       basestring)
        cls.addProperty('temp_image_width',     int)
        cls.addProperty('temp_image_height',    int)

class HTTPStampNew(HTTPImageUpload):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',            basestring)
        cls.addProperty('search_id',            basestring)
        cls.addProperty('blurb',                basestring)
        cls.addProperty('credit',               basestring) #delimiter=','

class HTTPStampEdit(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',             basestring, required=True)
        cls.addProperty('blurb',                basestring)
        cls.addPropertyList('credit',           basestring) #delimiter=','

class HTTPStampId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',             basestring)

class HTTPStampRef(Schema):
    @classmethod
    def setSchema(cls):
        # stamp_id or (user_id and stamp_num)
        cls.addProperty('stamp_id',             basestring)
        cls.addProperty('user_id',              basestring)
        cls.addProperty('stamp_num',            int)


#TODO
        #cls.addProperty('limit',                int)
        #cls.addProperty('offset',               int)
        #cls.addProperty('coordinates',          basestring) # "lat,lng"
        #cls.addProperty('category',             basestring)


class HTTPStampedByGroup(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('count',                int)
        cls.addNestedPropertyList('stamps',     HTTPStampPreview)

    def importStampedByGroup(self, group):
        if group.count is not None:
            self.count = group.count 

        if group.stamps is not None:
            self.stamps = [HTTPStampPreview().importStampPreview(s) for s in group.stamps]

        return self

class HTTPStampedBy(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('friends',        HTTPStampedByGroup)
        cls.addNestedProperty('all',            HTTPStampedByGroup)

    def importStampedBy(self, stampedBy):
        if stampedBy.friends is not None:
            self.friends = HTTPStampedByGroup().importStampedByGroup(stampedBy.friends)

        if stampedBy.all is not None:
            self.all = HTTPStampedByGroup().importStampedByGroup(stampedBy.all)

        return self

class HTTPStampImage(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',         basestring, required=True)
        cls.addProperty('image',            basestring, required=True) # normalize=False

class HTTPDeletedStamp(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',         basestring, required=True)
        cls.addProperty('modified',         basestring)
        cls.addProperty('deleted',          bool)

    def importDeletedStamp(self, delStamp):
        self.dataImport(delStamp.dataExport(), overflow=True)
        self.modified = delStamp.timestamp.modified
        return self


# #### #
# Todo #
# #### #

class HTTPTodoSource(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('entity',         HTTPEntityMini, required=True)
        cls.addPropertyList('stamp_ids',        basestring)

class HTTPTodo(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('todo_id',              basestring, required=True)
        cls.addProperty('user_id',              basestring, required=True)
        cls.addNestedProperty('source',         HTTPTodoSource, required=True)
        #cls.addNestedProperty('entity',         HTTPEntityMini, required=True)
        #cls.addNestedProperty('stamp',          HTTPStamp)
        cls.addProperty('stamp_id',             basestring) # set if the user has stamped this todo item
        cls.addNestedProperty('previews',       HTTPPreviews)
        cls.addProperty('created',              basestring)
        cls.addProperty('complete',             bool)

    def importTodo(self, todo):
        self.todo_id                = todo.todo_id
        self.user_id                = todo.user.user_id
        self.source                 = HTTPTodoSource()
        self.source.entity          = HTTPEntityMini().importEntity(todo.entity)
        if todo.stamp is not None:
            self.source.stamp_ids   = [ todo.stamp.stamp_id ]
        if todo.previews is not None and todo.previews.todos is not None:
            self.previews           = HTTPPreviews()
            self.previews.todos     = [HTTPUserMini().importUserMini(u) for u in todo.previews.todos]
        self.created                = todo.timestamp.created
        self.complete               = todo.complete

        if todo.stamp is not None:
            self.stamp_id              = todo.stamp.stamp_id#= HTTPStamp().importStampMini(todo.stamp)

        return self

class HTTPTodoNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',            basestring)
        cls.addProperty('search_id',            basestring)
        cls.addProperty('stamp_id',             basestring)

class HTTPTodoComplete(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',            basestring)
        cls.addProperty('complete',             bool)


# ######## #
# Activity #
# ######## #

class HTTPActivityObjects(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('users',      HTTPUserMini)
        cls.addNestedPropertyList('stamps',     HTTPStamp)
        cls.addNestedPropertyList('entities',   HTTPEntityMini)
        cls.addNestedPropertyList('comments',   HTTPComment)

class HTTPActivity(Schema):
    @classmethod
    def setSchema(cls):
        # Metadata
        cls.addProperty('activity_id',                  basestring, required=True)
        cls.addProperty('created',                      basestring)
        cls.addProperty('benefit',                      int)
        cls.addNestedProperty('action',                 HTTPAction)

        # Structure
        cls.addProperty('verb',                         basestring)
        cls.addNestedPropertyList('subjects',           HTTPUserMini)
        cls.addNestedProperty('objects',                HTTPActivityObjects)

        # Image
        cls.addProperty('image',                        basestring)
        cls.addProperty('icon',                         basestring)

        # Text
        cls.addProperty('header',                       basestring)
        cls.addNestedPropertyList('header_references',  HTTPTextReference)
        cls.addProperty('body',                         basestring)
        cls.addNestedPropertyList('body_references',    HTTPTextReference)
        cls.addProperty('footer',                       basestring)
        cls.addNestedPropertyList('footer_references',  HTTPTextReference)

    def importEnrichedActivity(self, activity):
        data = activity.dataExport()
        data.pop('subjects')
        data.pop('objects')

        self.dataImport(data, overflow=True)

        self.created = activity.timestamp.created

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
            if activity.objects is not None and activity.objects.users is not None:
                if self.objects is None:
                    self.objects = HTTPActivityObjects()
                userobjects = []
                for user in activity.objects.users:
                    userobjects.append(HTTPUserMini().importUserMini(user))
                self.objects.users = userobjects 

        def _addStampObjects():
            if activity.objects is not None and activity.objects.stamps is not None:
                if self.objects is None:
                    self.objects = HTTPActivityObjects()
                stampobjects = []
                for stamp in activity.objects.stamps:
                    stampobjects.append(HTTPStamp().importStamp(stamp))
                self.objects.stamps = stampobjects 

        def _addEntityObjects():
            if activity.objects is not None and activity.objects.entities is not None:
                if self.objects is None:
                    self.objects = HTTPActivityObjects()
                entityobjects = []
                for entity in activity.objects.entities:
                    entityobjects.append(HTTPEntityMini().importEntity(entity))
                self.objects.entities = entityobjects 

        def _addCommentObjects():
            if activity.objects is not None and activity.objects.comments is not None:
                if self.objects is None:
                    self.objects = HTTPActivityObjects()
                commentobjects = []
                for comment in activity.objects.comments:
                    comment = HTTPComment().importComment(comment)
                    _initialize_comment_html(comment)
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

        elif self.verb == 'restamp':
            _addStampObjects()

            subjects, subjectReferences = _formatUserObjects(self.subjects)

            if activity.personal:
                self.benefit = len(self.subjects)
                self.body = '%s gave you credit.' % (subjects)
                self.body_references = subjectReferences
                if len(self.subjects) > 1:
                    self.image = _getIconURL('news_stamp_group')
            else:
                verb = 'gave'
                offset = len(subjects) + len(verb) + 2
                userObjects, userObjectReferences = _formatUserObjects(self.objects.users, offset=offset)
                self.body = '%s %s %s credit.' % (subjects, verb, userObjects)
                self.body_references = subjectReferences + userObjectReferences

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

        elif self.verb == 'reply':
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

        elif self.verb == 'mention':
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

        elif self.verb.startswith('friend_'):
            self.icon = _getIconURL('news_friend')
            self.action = _buildUserAction(self.subjects[0])

        elif self.verb.startswith('action_'):
            _addStampObjects()
            
            actionMapping = {
                'listen'    : ('listened to', ''),
                'playlist'  : ('added', 'to their playlist'),
                'download'  : ('downloaded', ''),
                'reserve'   : ('made a reservation at', ''),
                'menu'      : ('viewed the menu for', ''),
                'buy'       : ('bought', ''),
                'watch'     : ('watched', ''),
                'tickets'   : ('bought tickets for', ''),
            }
            subjects, subjectReferences = _formatUserObjects(self.subjects)
            verbs = ('completed', '')

            if self.verb[7:] in actionMapping.keys():
                verbs = actionMapping[self.verb[7:]]

            offset = len(subjects) + len(verbs[0]) + 2
            stampObjects, stampObjectReferences = _formatStampObjects(self.objects.stamps, offset=offset)

            if len(verbs[1]) > 0:
                self.body = '%s %s %s %s.' % (subjects, verbs[0], stampObjects, verbs[1])
            else:
                self.body = '%s %s %s.' % (subjects, verbs[0], stampObjects)

            self.body_references = subjectReferences + stampObjectReferences
            self.action = _buildStampAction(self.objects.stamps[0])

        else:
            raise Exception("Uncrecognized verb: %s" % self.verb)

        return self

class HTTPActivitySlice(HTTPGenericSlice):
    @classmethod
    def setSchema(cls):
        cls.addProperty('distance',             int)

class HTTPLinkedURL(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('url',                  basestring, required=True)
        cls.addProperty('chrome',               bool)

    def importLinkedURL(self, linkedurl):
        self.dataImport(linkedurl.dataExport(), overflow=True)
        return self


# #### #
# Menu #
# #### #

class HTTPHours(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('open',                     basestring)
        cls.addProperty('close',                    basestring)
        cls.addProperty('desc',                     basestring)

class HTTPTimes(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('sun',            HTTPHours)
        cls.addNestedPropertyList('mon',            HTTPHours)
        cls.addNestedPropertyList('tue',            HTTPHours)
        cls.addNestedPropertyList('wed',            HTTPHours)
        cls.addNestedPropertyList('thu',            HTTPHours)
        cls.addNestedPropertyList('fri',            HTTPHours)
        cls.addNestedPropertyList('sat',            HTTPHours)

class HTTPMenuPrice(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                    basestring)
        cls.addProperty('price',                    basestring)
        cls.addProperty('calories',                 int)
        cls.addProperty('unit',                     basestring)
        cls.addProperty('currency',                 basestring)

class HTTPMenuItem(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                    basestring)
        cls.addProperty('desc',                     basestring)
        cls.addPropertyList('categories',           basestring)
        cls.addProperty('short_desc',               basestring)
        cls.addProperty('spicy',                    int)
        cls.addPropertyList('allergens',            basestring)
        cls.addPropertyList('allergen_free',        basestring)
        cls.addPropertyList('restrictions',         basestring)
        cls.addNestedPropertyList('prices',         HTTPMenuPrice)

class HTTPMenuSection(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                    basestring)
        cls.addProperty('desc',                     basestring)
        cls.addProperty('short_desc',               basestring)
        cls.addNestedPropertyList('items',          HTTPMenuItem)

class HTTPSubmenu(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('title',                    basestring)
        cls.addNestedProperty('times',              HTTPTimes)
        cls.addProperty('footnote',                 basestring)
        cls.addProperty('desc',                     basestring)
        cls.addProperty('short_desc',               basestring)
        cls.addNestedPropertyList('sections',       HTTPMenuSection)

class HTTPMenu(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('disclaimer',               basestring)
        cls.addProperty('attribution_image',        basestring)
        cls.addProperty('attribution_image_link',   basestring)
        cls.addNestedPropertyList('menus',          HTTPSubmenu)

    def importMenuSchema(self, menu):
        self.dataImport(menu.dataExport(), overflow=True)
        return self

