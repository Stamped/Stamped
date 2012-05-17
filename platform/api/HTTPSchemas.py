#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import copy, urllib, urlparse, re, logs, string, time, utils
import libs.ec2_utils

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

if libs.ec2_utils.is_prod_stack():
    COMPLETION_ENDPOINT = 'https://api.stamped.com/v0/actions/complete.json'
else:
    COMPLETION_ENDPOINT = 'https://dev.stamped.com/v0/actions/complete.json'

LINKSHARE_TOKEN = 'QaV3NQJNPRA'
FANDANGO_TOKEN  = '5348839'
AMAZON_TOKEN    = 'stamped01-20'

amazon_image_re = re.compile('(.*)\.[^/.]+\.jpg')
non_numeric_re  = re.compile('\D')
mention_re      = re.compile(r'(?<![a-zA-Z0-9_])@([a-zA-Z0-9+_]{1,20})(?![a-zA-Z0-9_])', re.IGNORECASE)

def _coordinatesDictToFlat(coordinates):
    try:
        if not isinstance(coordinates['lat'], float) or \
           not isinstance(coordinates['lng'], float):
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
        cls.addProperty('refresh_token',      basestring, required=True)
        cls.addProperty('grant_type',         basestring, required=True)

class OAuthLogin(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('login',              basestring, required=True)
        cls.addProperty('password',           basestring, required=True)

# ####### #
# Actions #
# ####### #

class HTTPActionCompletionData(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('action',                 basestring)
        cls.addProperty('source',                 basestring)
        cls.addProperty('source_id',              basestring)
        cls.addProperty('entity_id',              basestring)
        cls.addProperty('user_id',                basestring)
        cls.addProperty('stamp_id',               basestring)

class HTTPActionSource(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',                   basestring, required=True)
        cls.addProperty('source',                 basestring, required=True)
        cls.addProperty('source_id',              basestring)
        cls.addProperty('source_data',            dict)
        cls.addProperty('endpoint',               basestring)
        cls.addProperty('endpoint_data',          dict)
        cls.addProperty('link',                   basestring)
        cls.addProperty('icon',                   basestring)
        cls.addProperty('completion_endpoint',    basestring)
        cls.addProperty('completion_data',        dict) # dictionary?
    
    def setCompletion(self, **kwargs):
        self.completion_endpoint    = COMPLETION_ENDPOINT
        self.completion_data        = HTTPActionCompletionData(kwargs, overflow=True)

class HTTPAction(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('type',                     basestring, required=True)
        cls.addProperty('name',                     basestring, required=True)
        cls.addNestedPropertyList('sources',        HTTPActionSource, required=True)



# ####### #
# General #
# ####### #

class HTTPImageSizeSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('url',                      basestring)
        cls.addProperty('width',                    int)
        cls.addProperty('height',                   int)

class HTTPImageSchema(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('sizes',          HTTPImageSizeSchema)
        cls.addProperty('caption',                  basestring)
        cls.addNestedProperty('action',             HTTPAction)

class HTTPTextReference(Schema):
    @classmethod
    def setSchema(cls):
        cls.addPropertyList('indices',          int)
        cls.addNestedProperty('action',         HTTPAction)


# ####### #
# Account #
# ####### #

class HTTPAccount(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',            basestring, required=True)
        cls.addProperty('name',               basestring, required=True)
        cls.addProperty('email',              basestring, required=True)
        cls.addProperty('screen_name',        basestring, required=True)
        cls.addProperty('privacy',            bool, required=True)
        cls.addProperty('phone',              int)

    def importAccount(self, account):
        self.dataImport(account.dataExport(), overflow=True)
        return self

class HTTPAccountNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',               basestring, required=True)
        cls.addProperty('email',              basestring, required=True)
        cls.addProperty('password',           basestring, required=True)
        cls.addProperty('screen_name',        basestring, required=True)
        cls.addProperty('phone',              int)
        cls.addProperty('profile_image',      basestring) ### TODO: normalize=False ?
        
        # for asynchronous image uploads
        cls.addProperty('temp_image_url',     basestring)
        cls.addProperty('temp_image_width',   int)
        cls.addProperty('temp_image_height',  int)

    def convertToAccount(self):
        return Account().dataImport(self.dataExport(), overflow=True)
        
    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'Account':
            schema.importData(self.exportSparse(), overflow=True)
        else:
            raise NotImplementedError(type(schema))
        return schema

class HTTPAccountSettings(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('email',              basestring)
        cls.addProperty('password',           basestring)
        cls.addProperty('screen_name',        basestring)
        cls.addProperty('privacy',            bool)
        cls.addProperty('phone',              int)

class HTTPAccountProfile(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name',               basestring)
        cls.addProperty('color',              basestring)
        cls.addProperty('bio',                basestring)
        cls.addProperty('website',            basestring)
        cls.addProperty('location',           basestring)

class HTTPCustomizeStamp(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('color_primary',      basestring, required=True)
        cls.addProperty('color_secondary',    basestring, required=True)

class HTTPAccountProfileImage(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('profile_image',      basestring) ### TODO: normalize=False
        
        # for asynchronous image uploads
        cls.addProperty('temp_image_url',     basestring)

class HTTPAccountCheck(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('login',              basestring, required=True)

class HTTPLinkedAccounts(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('twitter_id',               basestring)
        cls.addProperty('twitter_screen_name',      basestring)
        cls.addProperty('twitter_key',              basestring)
        cls.addProperty('twitter_secret',           basestring)
        cls.addProperty('facebook_id',              basestring)
        cls.addProperty('facebook_name',            basestring)
        cls.addProperty('facebook_screen_name',     basestring)
        cls.addProperty('facebook_token',           basestring)
        cls.addProperty('netflix_user_id',          basestring)
        cls.addProperty('netflix_token',            basestring)
        cls.addProperty('netflix_secret',           basestring)

    def exportLinkedAccounts(self):
        schema = LinkedAccounts()

        data = self.dataExport()

        twitter = TwitterAccountSchema()
        twitter.dataImport(data, overflow=True)

        facebook = FacebookAccountSchema()
        facebook.dataImport(data, overflow=True)

        schema.dataImport(self.dataExport(), overflow=True)
        schema.twitter = twitter 
        schema.facebook = facebook

        return schema 

    def exportTwitterAuthSchema(self):
        schema = TwitterAuthSchema()
        schema.dataImport(self.dataExport(), overflow=True)
        return schema 

    def exportFacebookAuthSchema(self):
        schema = FacebookAuthSchema()
        schema.dataImport(self.dataExport(), overflow=True)
        return schema 

    def exportNetflixAuthSchema(self):
        schema = NetflixAuthSchema()
        schema.dataImport(self.dataExport(), overflow=True)
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
        cls.addProperty('ios_alert_fav',          bool)
        cls.addProperty('ios_alert_mention',      bool)
        cls.addProperty('ios_alert_comment',      bool)
        cls.addProperty('ios_alert_reply',        bool)
        cls.addProperty('ios_alert_follow',       bool)
        cls.addProperty('email_alert_credit',     bool)
        cls.addProperty('email_alert_like',       bool)
        cls.addProperty('email_alert_fav',        bool)
        cls.addProperty('email_alert_mention',    bool)
        cls.addProperty('email_alert_comment',    bool)
        cls.addProperty('email_alert_reply',      bool)
        cls.addProperty('email_alert_follow',     bool)

    def __init__(self):
        Schema.__init__(self)
        self.ios_alert_credit           = False
        self.ios_alert_like             = False
        self.ios_alert_fav              = False
        self.ios_alert_mention          = False
        self.ios_alert_comment          = False
        self.ios_alert_reply            = False
        self.ios_alert_follow           = False
        self.email_alert_credit         = False
        self.email_alert_like           = False
        self.email_alert_fav            = False
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
        cls.addProperty('user_id',              basestring)
        cls.addProperty('screen_name',          basestring)

class HTTPUserIds(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_ids',             basestring) # Comma delimited
        cls.addProperty('screen_names',         basestring) # Comma delimited

class HTTPUserSearch(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('q',                    basestring)
        cls.addProperty('limit',                int)
        cls.addProperty('relationship',         basestring)

class HTTPUserRelationship(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id_a',            basestring)
        cls.addProperty('screen_name_a',        basestring)
        cls.addProperty('user_id_b',            basestring)
        cls.addProperty('screen_name_b',        basestring)

class HTTPFindUser(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('q',                    basestring) # Comma delimited

class HTTPFindTwitterUser(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('q',                    basestring) # Comma delimited
        cls.addProperty('twitter_key',          basestring)
        cls.addProperty('twitter_secret',       basestring)

class HTTPFindFacebookUser(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('q',                    basestring) # Comma delimited
        cls.addProperty('facebook_token',       basestring)

class HTTPNetflixId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('netflix_id',           basestring)

class HTTPNetflixAuthResponse(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamped_oauth_token',  basestring)
        cls.addProperty('oauth_token',          basestring)
        cls.addProperty('secret',               basestring)
        cls.addProperty('oauth_verifier',       basestring)

class HTTPCategoryDistribution(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('category',           basestring, required=True)
        cls.addProperty('name',               basestring)
        cls.addProperty('icon',               basestring)
        cls.addProperty('count',              int)

class HTTPUser(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',               basestring, required=True)
        cls.addProperty('name',                  basestring, required=True)
        cls.addProperty('screen_name',           basestring, required=True)
        cls.addProperty('color_primary',         basestring)
        cls.addProperty('color_secondary',       basestring)
        cls.addProperty('bio',                   basestring)
        cls.addProperty('website',               basestring)
        cls.addProperty('location',              basestring)
        cls.addProperty('privacy',               bool, required=True)
        cls.addNestedProperty('image',                HTTPImageSchema)
        
        cls.addProperty('identifier',            basestring)
        cls.addProperty('num_stamps',            int)
        cls.addProperty('num_stamps_left',       int)
        cls.addProperty('num_friends',           int)
        cls.addProperty('num_followers',         int)
        cls.addProperty('num_faves',             int)
        cls.addProperty('num_credits',           int)
        cls.addProperty('num_credits_given',     int)
        cls.addProperty('num_likes',             int)
        cls.addProperty('num_likes_given',       int)
        cls.addNestedPropertyList('distribution',       HTTPCategoryDistribution)

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
        
        self.image = _buildProfileImage(self.screen_name, 
                                        cache=user.timestamp.image_cache, 
                                        sizes=[144, 110, 92, 74, 72, 62, 55, 46, 37, 31])
        
        if 'distribution' in stats:
            data = {}
            for item in stats['distribution']:
                data[item['category']] = item['count']
                
            order = [
                'food',
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
                d.count     = data.pop(i, 0)
                d.icon      = _getIconURL('cat_%s' % i, client=client)
                self.distribution.append(d)
        
        return self

class HTTPSuggestedUser(HTTPUser):
    @classmethod
    def setSchema(cls):
        cls.addPropertyList('explanations', basestring)

class HTTPUserMini(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('user_id',              basestring, required=True)
        cls.addProperty('screen_name',          basestring, required=True)
        cls.addProperty('color_primary',        basestring)
        cls.addProperty('color_secondary',      basestring)
        cls.addProperty('privacy',              bool, required=True)
        cls.addNestedProperty('image',          HTTPImageSchema)

    def importUserMini(self, mini):
        self.dataImport(mini.dataExport(), overflow=True)
        self.image_url = _profileImageURL(mini.screen_name, mini.image_cache)

        self.image = _buildProfileImage(self.screen_name,
            cache=user.timestamp.image_cache,
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


# ####### #
# Invites #
# ####### #

class HTTPEmail(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('email',                basestring)


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
        cls.addProperty('favorite_id',  basestring)
        cls.addProperty('comment_id',   basestring)
        cls.addProperty('activity_id',  basestring)

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
    for image in images:
        if len(image.sizes) == 0:
            continue
        newimg = HTTPImageSchema()
        for size in image.sizes:
            if size.url is not None:
                newsize = HTTPImageSizeSchema({'url': _cleanImageURL(size.url) })
                newimg.sizes.append(newsize)
        dest.images.append(newimg)


class HTTPEntityAction(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('action',         HTTPAction, required=True)
        cls.addProperty('name',                 basestring, required=True)
        cls.addProperty('icon',                 basestring)

class HTTPEntityMetadataItem(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('name,',                basestring, required=True)
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

# Related

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
        cls.addNestedPropertyList('data',       HTTPEntityMini, required=True)
        cls.addProperty('title',                basestring)


class HTTPEntity(Schema):
    @classmethod
    def setSchema(cls):
        # Core
        cls.addProperty('entity_id',            basestring, required=True)
        cls.addProperty('title',                basestring, required=True)
        cls.addProperty('subtitle',             basestring, required=True)
        cls.addProperty('category',             basestring, required=True)
        cls.addProperty('subcategory',          basestring, required=True)
        cls.addProperty('caption',              basestring)
        cls.addNestedPropertyList('images',     HTTPImageSchema)
        cls.addProperty('last_modified',        basestring)

        # Location
        cls.addProperty('address',              basestring)
        cls.addProperty('neighborhood',         basestring)
        cls.addProperty('coordinates',          basestring)

        # Components
        cls.addNestedProperty('playlist',       HTTPEntityPlaylist)
        cls.addNestedPropertyList('actions',    HTTPEntityAction)
        cls.addNestedPropertyList('galleries',  HTTPEntityGallery)
        cls.addNestedPropertyList('metadata',   HTTPEntityMetadataItem)
        cls.addNestedProperty('stamped_by',     HTTPEntityStampedBy)
        cls.addNestedProperty('related',        HTTPEntityRelated)


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

            self.actions.append(item)

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
                action.sources.append(actionSource)

                item.action = action

            if 'action' in kwargs:
                item.action = kwargs['action']

            self.metadata.append(item)

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

        # Restaurant / Bar
        if entity.kind == 'place' and entity.category == 'food':
            self.address        = entity.formatAddress(extendStreet=True)
            self.coordinates    = _coordinatesDictToFlat(entity.coordinates)

            address = entity.formatAddress(extendStreet=True, breakLines=True)
            if address is not None:
                self.caption = address

            # Metadata
            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_food', client=client))
            self._addMetadata('Cuisine', ', '.join(unicode(i) for i in entity.cuisine))
            self._addMetadata('Price', entity.price_range * '$' if entity.price_range is not None else None)
            self._addMetadata('Site', _formatURL(entity.site), link=entity.site)
            self._addMetadata('Description', entity.desc, key='desc', extended=True)

            # Image Gallery

            if entity.gallery is not None and len(entity.gallery) > 0:
                gallery = HTTPEntityGallery()
                for image in entity.gallery:
                    item = HTTPImageSchema().dataImport(image)
                    gallery.images.append(item)
                self.galleries.append(gallery)

            # Actions: Reservation

            actionType  = 'reserve'
            actionIcon  = _getIconURL('act_reserve_primary', client=client)
            sources     = []

            if entity.sources.opentable_id is not None or entity.sources.opentable_nickname is not None:
                source              = HTTPActionSource()
                source.name         = 'Reserve on OpenTable'
                source.source       = 'opentable'
                source.source_id    = entity.sources.opentable_id
                source.link         = _buildOpenTableURL(entity.opentable_id, entity.opentable_nickname, client)
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

            if entity.contact.phone is not None:
                source              = HTTPActionSource()
                source.source       = 'phone'
                source.source_id    = entity.contact.phone
                source.link         = 'tel:%s' % non_numeric_re.sub('', entity.contact.phone)
                sources.append(source)

            self._addAction(actionType, entity.contact.phone, sources, icon=actionIcon)

            # Actions: View Menu

            actionType  = 'menu'
            actionIcon  = _getIconURL('act_menu', client=client)
            sources     = []

            if entity.singleplatform_id is not None:
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

        # Generic Place
        elif entity.kind == 'place':
            self.address        = entity.formatAddress(extendStreet=True)
            self.coordinates    = _coordinatesDictToFlat(entity.coordinates)

            address = entity.formatAddress(extendStreet=True, breakLines=True)
            if address is not None:
                self.caption = address

            # Metadata

            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_place', client=client))
            self._addMetadata('Description', entity.desc, key='desc')
            self._addMetadata('Site', _formatURL(entity.site), link=entity.site)

            # Image gallery

            if entity.gallery is not None and len(entity.gallery) > 0:
                gallery = HTTPEntityGallery()
                for image in entity.gallery:
                    item = HTTPImageSchema()
                    item.importSchema(image)
                    source              = HTTPActionSource()
                    source.source_id    = item.sizes[0].url
                    source.source       = 'stamped'
                    source.link         = item.sizes[0].url
                    action              = HTTPAction()
                    action.type         = 'stamped_view_image'
                    action.sources.append(source)
                    item.action     = action
                    gallery.images.append(item)
                self.galleries.append(gallery)

            # Actions: Call

            actionType  = 'phone'
            actionIcon  = _getIconURL('act_call', client=client)
            sources     = []

            if entity.contact.phone is not None:
                source              = HTTPActionSource()
                source.source       = 'phone'
                source.source_id    = entity.contact.phone
                source.link         = 'tel:%s' % non_numeric_re.sub('', entity.contact.phone)
                sources.append(source)

            self._addAction(actionType, entity.contact.phone, sources, icon=actionIcon)

        # Book
        elif entity.kind == 'media_item' and entity.isType('book'):

            if len(entity.authors) > 0:
                self.caption = 'by %s' % ', '.join(unicode(i.title) for i in entity.authors)

            # Metadata

            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_book', client=client))
            self._addMetadata('Publish Date', self._formatReleaseDate(entity.release_date))
            self._addMetadata('Description', entity.desc, key='desc', extended=True)
            self._addMetadata('Publisher', ', '.join(unicode(i['title']) for i in entity.publishers))

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

            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_film', client=client))
            self._addMetadata('Overview', entity.desc, key='desc', extended=True)
            self._addMetadata('Release Date', self._formatReleaseDate(entity.release_date))
            self._addMetadata('Cast', ', '.join(unicode(i['title']) for i in entity.cast), extended=True, optional=True)
            self._addMetadata('Director', ', '.join(unicode(i['title']) for i in entity.directors), optional=True)
            self._addMetadata('Genres', ', '.join(unicode(i) for i in entity.genres), optional=True)
            if entity.subcategory == 'movie':
                self._addMetadata('Rating', entity.mpaa_rating, key='rating', optional=True)



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
                source.endpoint         = 'https://dev.stamped.com/v0/account/linked/netflix/add_instant.json'
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

        # Movie
        elif entity.kind == 'media_item' and entity.isType('movie'):

            if entity.subcategory == 'movie' and entity.length is not None:
                length = self._formatFilmLength(entity.length)
                if length is not None:
                    self.caption = length

            if entity.subcategory == 'tv' and len(entity.networks) > 0:
                self.caption = ', '.join(unicode(i['title']) for i in entity.networks)

            # Metadata

            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_film', client=client))
            self._addMetadata('Overview', entity.desc, key='desc', extended=True)
            self._addMetadata('Release Date', self._formatReleaseDate(entity.release_date))
            self._addMetadata('Cast', ', '.join(unicode(i['title']) for i in entity.cast), extended=True, optional=True)
            self._addMetadata('Director', ', '.join(unicode(i['title']) for i in entity.directors), optional=True)
            self._addMetadata('Genres', ', '.join(unicode(i) for i in entity.genres), optional=True)
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
                if entity.itunes_url is not None:
                    source.link     = _encodeiTunesShortURL(entity.itunes_url)
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
                source.endpoint         = 'https://dev.stamped.com/v0/account/linked/netflix/add_instant.json'
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

            # Actions: Find Tickets

            actionType  = 'tickets'
            actionIcon  = _getIconURL('act_ticket_primary', client=client)
            if len(self.actions) == 0:
                actionIcon = _getIconURL('act_ticket', client=client)
            sources     = []

            if entity.sources.fandango_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Buy from Fandango'
                source.source       = 'fandango'
                source.source_id    = entity.sources.fandango_id
                if entity.fandango_url is not None:
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

            # Actions: Add to Queue

            ### TODO: Add Netflix

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

            elif entity.isType('album') and len(entity.artists) > 0:
                self.caption = 'by %s' % ', '.join(unicode(i.title) for i in entity.artists)

            elif entity.isType('track') and len(entity.artists) > 0:
                self.caption = 'by %s' % ', '.join(unicode(i.title) for i in entity.artists)

            # Metadata

            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_music', client=client))
            if entity.subcategory == 'artist':
                self._addMetadata('Biography', entity.desc, key='desc')
                self._addMetadata('Genre', ', '.join(unicode(i) for i in entity.genres), optional=True)

            elif entity.subcategory == 'album':
                if len(entity.artists) > 0:
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
                self._addMetadata('Genre', ', '.join(unicode(i) for i in entity.genres))
                self._addMetadata('Release Date', self._formatReleaseDate(entity.release_date))
                self._addMetadata('Album Details', entity.desc, key='desc', optional=True)

            elif entity.subcategory == 'song':
                if len(entity.artists) > 0:
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
                self._addMetadata('Genre', ', '.join(unicode(i) for i in entity.genres))
                self._addMetadata('Release Date', self._formatReleaseDate(entity.release_date))
                self._addMetadata('Song Details', entity.desc, key='desc', optional=True)

            # Actions: Listen

            actionType  = 'listen'
            actionTitle = 'Listen'
            if entity.subcategory == 'artist':
                actionTitle = 'Listen to top songs'
            elif entity.subcategory == 'album':
                actionTitle = 'Listen to album'
            elif entity.subcategory == 'song':
                actionTitle = 'Listen to song'
            actionIcon  = _getIconURL('act_play_primary', client=client)
            sources     = []

            if entity.sources.itunes_id is not None and entity.sources.itunes_preview:
                source              = HTTPActionSource()
                source.name         = 'Listen on iTunes'
                source.source       = 'itunes'
                source.source_id    = entity.sources.itunes_id
                source.source_data  = { 'preview_url': entity.sources.itunes_preview }
                source.icon         = _getIconURL('src_itunes', client=client)
                if entity.itunes_url is not None:
                    source.link     = _encodeiTunesShortURL(entity.itunes_url)
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            if entity.sources.rdio_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Listen on Rdio'
                source.source       = 'rdio'
                source.source_id    = entity.sources.rdio_id
                source.icon         = _getIconURL('src_rdio', client=client)
                if entity.rdio_url is not None:
                    source.link     = entity.rdio_url
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            if entity.sources.spotify_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Listen on Spotify'
                source.source       = 'spotify'
                source.source_id    = entity.sources.spotify_id
                source.icon         = _getIconURL('src_spotify', client=client)
                if entity.spotify_url is not None:
                    source.link     = entity.spotify_url
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
            if entity.subcategory == 'artist':
                actionTitle = 'Add artist to playlist'
            actionIcon  = _getIconURL('act_playlist_music', client=client)
            sources     = []

            if entity.sources.rdio_id is not None:
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

            if entity.sources.spotify_id is not None:
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

            if entity.sources.itunes_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Download from iTunes'
                source.source       = 'itunes'
                source.source_id    = entity.sources.itunes_id
                if entity.itunes_url is not None:
                    source.link     = _encodeiTunesShortURL(entity.itunes_url)
                source.setCompletion(
                    action      = actionType,
                    entity_id   = entity.entity_id,
                    source      = source.source,
                    source_id   = source.source_id,
                )
                sources.append(source)

            self._addAction(actionType, actionTitle, sources, icon=actionIcon)

            # Playlist

            if entity.subcategory in ["album", "artist"] and entity.tracks is not None:
                playlist = HTTPEntityPlaylist()

                if entity.subcategory == 'album':
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

                        if song.sources.itunes_id is not None and song.sources.itunes_preview is not None:
                            source                      = HTTPActionSource()
                            source.name                 = 'Listen on iTunes'
                            source.source               = 'itunes'
                            source.source_id            = song.sources.itunes_id
                            source.source_data          = { 'preview_url': song.sources.itunes_preview }
                            source.icon                 = _getIconURL('src_itunes', client=client)
                            sources.append(source)

                            if item.entity_id is None:
                                item.entity_id = 'T_ITUNES_%s' % song.itunes_id

                        if song.sources.rdio_id is not None:
                            source                      = HTTPActionSource()
                            source.name                 = 'Listen on Rdio'
                            source.source               = 'rdio'
                            source.source_id            = song.sources.rdio_id
                            source.icon                 = _getIconURL('src_rdio', client=client)
                            sources.append(source)

                            if item.entity_id is None:
                                item.entity_id = 'T_RDIO_%s' % song.rdio_id

                        if song.sources.spotify_id is not None:
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
                                    action      = action.type,
                                    entity_id   = entity.entity_id,
                                    source      = source.source,
                                    source_id   = source.source_id,
                                )

                            action.sources = sources

                            item.action = action

                        playlist.data.append(item)

                    except Exception as e:
                        pass

                if len(playlist.data) > 0:
                    self.playlist = playlist

            # Albums

            if entity.isType('artist') and len(entity.albums) > 0:
                from pprint import pformat

                gallery = HTTPEntityGallery()
                gallery.layout = 'list'
                for album in entity.albums:
                    try:
                        item            = HTTPImageSchema()
                        size            = HTTPImageSizeSchema()
                        ### TODO: Add placeholder if image doesn't exist
                        size.url        = _cleanImageURL(album.images[0].sizes[0].url)
                        item.caption    = album.title
                        item.sizes.append(size)

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

                        gallery.images.append(item)
                    except Exception as e:
                        logs.info(e.message)
                        pass
                if len(gallery.images) > 0:
                    self.galleries.append(gallery)

        elif entity.kind == 'software' and entity.isType('app'):

            if len(entity.authors) > 0:
                self.caption = 'by %s' % ', '.join(unicode(i.title) for i in entity.authors)

            # Metadata

            self._addMetadata('Category', subcategory, icon=_getIconURL('cat_app', client=client))
            self._addMetadata('Genre', ', '.join(unicode(i) for i in entity.genres))
            self._addMetadata('Description', entity.desc, key='desc', extended=True)

            # Actions: Download

            actionType  = 'download'
            actionIcon  = _getIconURL('act_download_primary', client=client)
            sources     = []

            if entity.sources.itunes_id is not None:
                source              = HTTPActionSource()
                source.name         = 'Download from iTunes'
                source.source       = 'itunes'
                source.source_id    = entity.sources.itunes_id
                source.icon         = _getIconURL('src_itunes', client=client)
                if entity.itunes_url is not None:
                    source.link     = _encodeiTunesShortURL(entity.itunes_url)
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
                for screenshot in entity.screenshots:
                    item = HTTPImageSchema().dataImport(screenshot)
                    gallery.images.append(item)
                self.galleries.append(gallery)


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
        elif len(entity.images) > 0:
            _addImages(self, entity.images)

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

        kind    = deriveKindFromSubcategory(self.subcategory)
        entity  = buildEntity(kind=kind)

        entity.schema_version   = 0
        entity.types            = list(deriveTypesFromSubcategories([self.subcategory]))
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

class HTTPEntityAutosuggest(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('search_id',            basestring, required=True)
        cls.addProperty('title',                basestring, required=True)
        cls.addProperty('subtitle',             basestring)
        cls.addProperty('category',             basestring, required=True)
        cls.addProperty('distance',             float)

    def importEntity(self, entity, distance=None):
        self.search_id          = entity.search_id
        assert self.search_id is not None

        self.title              = entity.title
        self.subtitle           = entity.subtitle
        self.category           = entity.category

        if isinstance(distance, float) and distance >= 0:
            self.distance       = distance

        return self

class HTTPEntityId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',        basestring, required=True)

class HTTPEntityIdSearchId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',        basestring)
        cls.addProperty('search_id',        basestring)

class HTTPEntitySearch(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('q',                basestring, required=True)
        cls.addProperty('coordinates',      basestring)
        cls.addProperty('category',         basestring)
        cls.addProperty('subcategory',      basestring)
        cls.addProperty('local',            bool)
        cls.addProperty('page',             int)

    def __init__(self):
        Schema.__init__(self)
        self.page = 0

    def exportEntitySearch(self):
        entSearch = EntitySearch().dataImport(self.dataExport(), overflow=True)
        entSearch.coordinates = _coordinatesFlatToDict(self.coordinates)
        return entSearch

#        def exportSchema(self, schema):
#            if schema.__class__.__name__ == 'EntitySearch':
#                schema.importData({'q': self.q})
#                schema.coordinates = _coordinatesFlatToDict(self.coordinates)
#                schema.importData({'category': self.category})
#                schema.importData({'subcategory': self.subcategory})
#                schema.importData({'local': self.local})
#                schema.importData({'page': self.page})
#            else:
#                raise NotImplementedError(type(schema))
#            return schema

class HTTPEntityNearby(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('coordinates',          basestring, required=True)
        cls.addProperty('category',             basestring)
        cls.addProperty('subcategory',          basestring)
        cls.addProperty('page',                 int)

    def __init__(self):
        Schema.__init__(self)
        self.page = 0

    def exportEntityNearby(self):
        entityNearby = EntityNearby().dataImport(self.dataExport(), overflow=True)
        entityNearby.coordinates = _coordinatesFlatToDict(self.coordinates)
        return entityNearby

#        def exportSchema(self, schema):
#            if schema.__class__.__name__ == 'EntityNearby':
#                schema.coordinates = _coordinatesFlatToDict(self.coordinates)
#                schema.importData({'category': self.category})
#                schema.importData({'subcategory': self.subcategory})
#                schema.importData({'page': self.page})
#            else:
#                raise NotImplementedError(type(schema))
#            return schema

class HTTPEntitySuggested(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('coordinates',          basestring)
        cls.addProperty('category',             basestring)
        cls.addProperty('subcategory',          basestring)
        cls.addProperty('limit',                int)

    def exportEntitySuggested(self):
        entitySuggested = EntitySuggested().dataImport(self.dataExport(), overflow=True)
        if self.coordinates is not None:
            entitySuggested.coordinates = _coordinatesFlatToDict(self.coordinates)
        return entitySuggested

#        def exportSchema(self, schema):
#            if schema.__class__.__name__ == 'EntitySuggested':
#                if self.coordinates:
#                    schema.coordinates = _coordinatesFlatToDict(self.coordinates)
#
#                schema.importData({'category': self.category})
#                schema.importData({'subcategory': self.subcategory})
#            else:
#                raise NotImplementedError(type(schema))
#
#            return schema


class HTTPEntityActionEndpoint(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('status',               basestring)
        cls.addProperty('message',              basestring)
        cls.addProperty('redirect',             basestring)

class HTTPActionComplete(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('action',               basestring)
        cls.addProperty('source',               basestring)
        cls.addProperty('source_id',            basestring)
        cls.addProperty('entity_id',            basestring)
        cls.addProperty('user_id',              basestring)
        cls.addProperty('stamp_id',             basestring)


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
        cls.addNestedPropertyList('credit',     CreditSchema)
        cls.addNestedPropertyList('badges',     HTTPBadge)
        cls.addProperty('via',                  basestring)
        cls.addProperty('url',                  basestring)
        cls.addProperty('created',              basestring)
        cls.addProperty('modified',             basestring)
        cls.addProperty('stamped',              basestring)
        cls.addProperty('num_comments',         int)
        cls.addProperty('num_likes',            int)

class HTTPStampPreviews(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('likes',              HTTPUserMini)
        cls.addNestedPropertyList('todos',              HTTPUserMini)
        cls.addNestedPropertyList('credits',            HTTPStampMini)
        # cls.addNestedPropertyList('comments',           HTTPComment)

class HTTPStamp(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',             basestring, required=True)
        cls.addNestedProperty('entity',         HTTPEntityMini, required=True)
        cls.addNestedProperty('user',           HTTPUserMini, required=True)
        cls.addNestedPropertyList('contents',   HTTPStampContent)
        cls.addNestedPropertyList('credit',     CreditSchema)
        cls.addNestedProperty('previews',       HTTPStampPreviews)
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
        cls.addProperty('is_fav',               bool)

    def importStamp(self, stamp):
        entity                  = stamp.entity
        coordinates             = getattr(entity, 'coordinates', None)
        mentions                = getattr(stamp, 'mentions', [])
        credit                  = getattr(stamp, 'credit', [])
        contents                = getattr(stamp, 'contents', [])

        previews                = getattr(stamp, 'previews', {})
        comments                = getattr(previews, 'comments', [])
        likes                   = getattr(previews, 'likes', [])
        todos                   = getattr(previews, 'todos', [])
        credits                 = getattr(previews, 'credits', [])

        if len(credit) > 0:
            self.credit = credit

        self.entity = HTTPEntityMini().importEntity(entity)

        self.dataImport(stamp.dataExport(), overflow=True)
        self.user               = HTTPUserMini().importUserMini(stamp.user)
        self.entity.coordinates = _coordinatesDictToFlat(coordinates)
        self.created            = stamp.timestamp.stamped
        self.modified           = stamp.timestamp.modified
        self.stamped            = stamp.timestamp.stamped

        for content in stamp.contents:
            item                    = HTTPStampContent()
            item.blurb              = content.blurb
            item.created            = content.timestamp.created
            #item.modified          = content.timestamp.modified

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

                item.blurb_references.append(reference)

            for image in content.images:
                img = HTTPImageSchema().dataImport(image)
                # quick fix for now
                # img.sizes[0].url = 'http://static.stamped.com/stamps/%s.jpg' % schema.stamp_id
                item.images.append(img)

            # Insert contents in descending chronological order
            self.contents.insert(0, item)

        self.num_comments   = getattr(stamp, 'num_comments', 0)
        self.num_likes      = getattr(stamp, 'num_likes', 0)
        self.num_todos      = getattr(stamp, 'num_todos', 0)
        self.num_credits    = getattr(stamp, 'num_credits', 0)

        url_title = encodeStampTitle(stamp.entity.title)
        self.url = 'http://www.stamped.com/%s/stamps/%s/%s' %\
                   (stamp.user.screen_name, stamp.stamp_num, url_title)

        if schema.__class__.__name__ == 'Stamp':
            for comment in stamp.previews.comments:
                comment = HTTPComment().importComment(comment)
                #_initialize_comment_html(comment)

                self.previews.comments.append(comment)

            for user in stamp.previews.todos:
                user    = HTTPUserMini().importUserMini(user).exportSparse()
                self.previews.todos.append(user)

            for user in schema.previews.likes:
                user    = HTTPUserMini().importUserMini(user).exportSparse()
                self.previews.likes.append(user)

            for credit in schema.previews.credits:
                credit  = HTTPStamp().importStamp(credit).minimize()
                self.previews.credits.append(credit)

            self.is_liked   = getattr(stamp, 'is_liked', False)
            self.is_fav     = getattr(stamp, 'is_fav', False)

        return self

#        def importSchema(self, schema):
#            if schema.__class__.__name__ in set(['Stamp', 'StampMini']):
#                data                = schema.exportSparse()
#                coordinates         = data['entity'].pop('coordinates', None)
#                mentions            = data.pop('mentions', [])
#                credit              = data.pop('credit', [])
#                contents            = data.pop('contents', [])
#
#                previews            = data.pop('previews', {})
#                comments            = previews.pop('comments', [])
#                likes               = previews.pop('likes', [])
#                todos               = previews.pop('todos', [])
#                credits             = previews.pop('credits', [])
#
#                if len(credit) > 0:
#                    data['credit'] = credit
#
#                data['entity'] = HTTPEntityMini().importSchema(schema.entity).exportSparse()
#
#                self.importData(data, overflow=True)
#                self.user                   = HTTPUserMini().importSchema(schema.user).exportSparse()
#                self.entity.coordinates     = _coordinatesDictToFlat(coordinates)
#                self.created                = schema.timestamp.stamped # Temp
#                self.modified               = schema.timestamp.modified
#                self.stamped                = schema.timestamp.stamped
#
#                for content in schema.contents:
#                    item            = HTTPStampContent()
#                    item.blurb      = content.blurb
#                    item.created    = content.timestamp.created
#                    # item.modified   = content.timestamp.modified
#
#                    for screenName in mention_re.finditer(content.blurb):
#                        source              = HTTPActionSource()
#                        source.name         = 'View profile'
#                        source.source       = 'stamped'
#                        source.source_id    = screenName.groups()[0]
#
#                        action              = HTTPAction()
#                        action.type         = 'stamped_view_screen_name'
#                        action.name         = 'View profile'
#                        action.sources      = [ source ]
#
#                        reference           = HTTPTextReference()
#                        reference.indices   = [ screenName.start(), screenName.end() ]
#                        reference.action    = action
#
#                        item.blurb_references.append(reference)
#
#                    for image in content.images:
#                        img = HTTPImageSchema()
#                        img.importSchema(image)
#                        # quick fix for now
#                        # img.sizes[0].url = 'http://static.stamped.com/stamps/%s.jpg' % schema.stamp_id
#                        item.images.append(img)
#
#                    #_initialize_blurb_html(item)
#
#                    # Insert contents in descending chronological order
#                    self.contents.insert(0, item)
#
#                self.num_comments = 0
#                if schema.num_comments > 0:
#                    self.num_comments       = schema.num_comments
#
#                self.num_likes = 0
#                if schema.num_likes > 0:
#                    self.num_likes          = schema.num_likes
#
#                self.num_todos = 0
#                if schema.num_todos > 0:
#                    self.num_todos          = schema.num_todos
#
#                self.num_credits = 0
#                if schema.num_credits > 0:
#                    self.num_credits        = schema.num_credits
#
#                url_title = encodeStampTitle(schema.entity.title)
#                self.url = 'http://www.stamped.com/%s/stamps/%s/%s' % \
#                    (schema.user.screen_name, schema.stamp_num, url_title)
#
#                if schema.__class__.__name__ == 'Stamp':
#                    for comment in schema.previews.comments:
#                        comment = HTTPComment().importSchema(comment)
#                        #_initialize_comment_html(comment)
#
#                        self.previews.comments.append(comment)
#
#                    for user in schema.previews.todos:
#                        user    = HTTPUserMini().importSchema(user).exportSparse()
#                        self.previews.todos.append(user)
#
#                    for user in schema.previews.likes:
#                        user    = HTTPUserMini().importSchema(user).exportSparse()
#                        self.previews.likes.append(user)
#
#                    for credit in schema.previews.credits:
#                        credit  = HTTPStamp().importSchema(credit).minimize().exportSparse()
#                        self.previews.credits.append(credit)
#
#                    self.is_liked = False
#                    if schema.is_liked:
#                        self.is_liked = True
#
#                    self.is_fav = False
#                    if schema.is_fav:
#                        self.is_fav = True
#            else:
#                logs.warning("unknown import class '%s'; expected 'Stamp'" % schema.__class__.__name__)
#                raise NotImplementedError
#
#            return self

    def minimize(self):
        return HTTPStampMini().dataImport(self.dataExport(), overflow=True)
#            return HTTPStampMini(self.value, overflow=True)

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
        cls.addPropertyList('credit',           basestring) #delimiter=','

class HTTPStampEdit(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',             basestring, required=True)
        cls.addProperty('blurb',                basestring)
        cls.addPropertyList('credit',           basestring) #delimiter=','

class HTTPStampId(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',             basestring, required=True)

#TODO
        #cls.addProperty('limit',                int)
        #cls.addProperty('offset',               int)
        #cls.addProperty('coordinates',          basestring) # "lat,lng"
        #cls.addProperty('category',             basestring)



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
        if 'coordinates' in data:
            try:
                lat, lng = data['coordinates'].split(',')
                data['coordinates'] = {
                    'lat' : float(lat),
                    'lng' : float(lng)
                }
            except Exception:
                raise StampedInputError("invalid coordinates parameter; format \"lat,lng\"")

        if 'since' in data:
            try:
                data['since'] = datetime.utcfromtimestamp(int(data['since']) - 2)
            except Exception:
                raise StampedInputError("invalid since parameter; must be a valid UNIX timestamp")

        if 'before' in data:
            try:
                data['before'] = datetime.utcfromtimestamp(int(data['before']) + 2)
            except Exception:
                raise StampedInputError("invalid since parameter; must be a valid UNIX timestamp")

        # TODO: validate since <= before

        if 'offset' not in data:
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
        return ConsumptionSlice.dataImport(data)

class HTTPStampedBySlice(HTTPGenericCollectionSlice):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',        basestring, required=True)
        cls.addProperty('group',            basestring)

    def exportFriendsSlice(self):
        data = self._convertData(self.dataExport())
        return FriendsSlice().dataImport(data, overflow=True)

    def exportGenericCollectionSlice(self):
        data = self._convertData(self.dataExport())
        return GenericCollectionSlice().dataImport(data, overflow=True)

class HTTPStampedByGroup(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('count',            int)
        cls.addNestedPropertyList('stamps', HTTPStamp)

class HTTPStampedBy(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedProperty('friends',    HTTPStampedByGroup)
        cls.addNestedProperty('fof',        HTTPStampedByGroup)
        cls.addNestedProperty('all',        HTTPStampedByGroup)

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

class HTTPCommentSlice(HTTPGenericSlice):
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',             basestring, required=True)


# ######## #
# Favorite #
# ######## #

class HTTPFavorite(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('favorite_id',          basestring, required=True)
        cls.addProperty('user_id',              basestring, required=True)
        cls.addNestedProperty('entity',         HTTPEntityMini, required=True)
        cls.addNestedProperty('stamp',          HTTPStamp)
        cls.addProperty('created',              basestring)
        cls.addProperty('complete',             bool)

    def importFavorite(self, fav):
        cls.favorite_id             = fav.favorite_id
        cls.user_id                 = fav.user_id
        cls.entity                  = HTTPEntityMini().importEntity(fav.entity)
        cls.created                 = fav.timestamp.created
        cls.complete                = fav.complete

        if fav.stamp is not None:
            self.stamp              = HTTPStamp().dataImport(fav.stamp)

        return self

class HTTPFavoriteNew(Schema):
    @classmethod
    def setSchema(cls):
        cls.addProperty('entity_id',            basestring)
        cls.addProperty('search_id',            basestring)
        cls.addProperty('stamp_id',             basestring)


# ######## #
# Activity #
# ######## #

class HTTPActivityObjects(Schema):
    @classmethod
    def setSchema(cls):
        cls.addNestedPropertyList('users',      HTTPUserMini)
        cls.addNestedPropertyList('stamps',     HTTPStamp)
        cls.addNestedPropertyList('entities',   HTTPEntity)
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
        data            = activity.dataExport()
        data.pop('subjects')
        data.pop('objects')

        self.dataImport(data, overflow=True)

        self.created = activity.timestamp.created

        if self.icon is not None:
            self.icon = _getIconURL(self.icon)

        for user in activity.subjects:
            self.subjects.append(HTTPUserMini().importUserMini(user))

        for user in activity.objects.users:
            self.objects.users.append(HTTPUserMini().importUserMini(user))

        for stamp in activity.objects.stamps:
            self.objects.stamps.append(HTTPStamp().importStamp(stamp))

        for entity in activity.objects.entities:
            self.objects.entities.append(HTTPEntityMini().importEntity(entity))

        for comment in activity.objects.comments:
            comment = HTTPComment().importComment(comment)
            _initialize_comment_html(comment)

            self.objects.comments.append(comment)

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
            if len(users) == 0:
                if required:
                    raise Exception("No user objects!")
                return None, []

            if len(users) == 1:
                text = unicode(users[0].screen_name)
                refs = [
                    {
                        'indices'   : [offset, offset + len(text)],
                        'action'    : _buildUserAction(users[0]),
                    }
                ]
                return text, refs

            if len(users) == 2:
                text = '%s and %s' % (users[0].screen_name, users[1].screen_name)
                refs = [
                    {
                        'indices'   : [offset, offset + len(users[0].screen_name)],
                        'action'    : _buildUserAction(users[0]),
                    },
                    {
                        'indices'   : [offset + len(text) - len(users[1].screen_name), offset + len(text)],
                        'action'    : _buildUserAction(users[1]),
                    }
                ]
                return text, refs

            text = '%s and %s others' % (users[0].screen_name, len(users) - 1)
            refs = [
                {
                    'indices'   : [offset, offset + len(users[0].screen_name)],
                    'action'    : _buildUserAction(users[0]),
                },
                {
                    'indices'   : [offset + len(users[0].screen_name) + len(' and '), offset + len(text)],
                }
            ]
            return text, refs

        def _formatStampObjects(stamps, required=True, offset=0):
            if len(stamps) == 0:
                if required:
                    raise Exception("No stamp objects!")
                return None, []

            if len(stamps) == 1:
                text = unicode(stamps[0].entity.title)
                refs = [{
                    'indices'   : [offset, offset + len(text)],
                    'action'    : _buildStampAction(stamps[0]),
                }]
                return text, refs

            if len(stamps) == 2:
                text = '%s and %s' % (stamps[0].entity.title, stamps[1].entity.title)
                refs = [
                    {
                        'indices'   : [offset, offset + len(stamps[0].entity.title)],
                        'action'    : _buildStampAction(stamps[0]),
                    },
                    {
                        'indices'   : [offset + len(text) - len(stamps[1].entity.title), offset + len(text)],
                        'action'    : _buildStampAction(stamps[1]),
                    }
                ]
                return text, refs

            text = '%s and %s other stamps' % (stamps[0].entity.title, len(stamps) - 1)
            refs = [
                {
                    'indices'   : [offset, offset + len(stamps[0].entity.title)],
                    'action'    : _buildStampAction(stamps[0]),
                },
                {
                    'indices'   : [offset + len(stamps[0].entity.title) + len(' and '), offset + len(text)],
                }
            ]
            return text, refs

        def _formatEntityObjects(entities, required=True, offset=0):
            if len(entities) == 0:
                if required:
                    raise Exception("No entity objects!")
                return None, []

            if len(entities) == 1:
                text = unicode(entities[0].title)
                refs = [{
                    'indices'   : [offset, offset + len(text)],
                    'action'    : _buildEntityAction(entities[0]),
                }]
                return text, refs

            if len(entities) == 2:
                text = '%s and %s' % (entities[0].title, entities[1].title)
                refs = [
                    {
                        'indices'   : [offset, offset + len(entities[0].title)],
                        'action'    : _buildEntityAction(entities[0]),
                    },
                    {
                        'indices'   : [offset + len(text) - len(entities[1].title), offset + len(text)],
                        'action'    : _buildEntityAction(entities[1]),
                    }
                ]
                return text, refs

            text = '%s and %s others' % (entities[0].title, len(entities) - 1)
            refs = [
                {
                    'indices'   : [offset, offset + len(entities[0].title)],
                    'action'    : _buildEntityAction(entities[0]),
                },
                {
                    'indices'   : [offset + len(entities[0].title) + len(' and '), offset + len(text)],
                }
            ]
            return text, refs

        def _formatCommentObjects(comments, required=True, offset=0):
            if len(comments) == 0:
                if required:
                    raise Exception("No comment objects!")
                return None, []

            if len(comments) == 1:
                text = '%s: %s' % (comments[0].user.screen_name, comments[0].blurb)
                refs = [{
                    'indices'   : [offset, offset + len(comments[0].user.screen_name) + 1],
                    'action'    : _buildUserAction(comments[0].user),
                }]
                return text, refs

            raise Exception("Too many comments! \n%s" % comments)

        def _formatStampBlurbObjects(stamps, required=True, offset=0):
            if len(stamps) == 0:
                if required:
                    raise Exception("No stamp objects!")
                return None, []

            if len(stamps) == 1:
                text = '%s: %s' % (stamps[0].user.screen_name, stamps[0].contents[0].blurb)
                refs = [{
                    'indices'   : [offset, offset + len(stamps[0].user.screen_name) + 1],
                    'action'    : _buildUserAction(stamps[0].user),
                }]
                return text, refs

            raise Exception("Too many stamps! \n%s" % stamps)

        if self.verb == 'follow':
            if len(self.subjects) == 1:
                verb = 'is now following'
                self.image = self.subjects[0].image_url
            else:
                verb = 'are now following'
                self.image = _getIconURL('news_follow')

            subjects, subjectReferences = _formatUserObjects(self.subjects)

            if schema.personal:
                self.body = '%s %s you.' % (subjects, verb)
                self.body_references = subjectReferences
            else:
                offset = len(subjects) + len(verb) + 2
                userObjects, userObjectReferences = _formatUserObjects(self.objects.users, offset=offset)
                self.body = '%s %s %s.' % (subjects, verb, userObjects)
                self.body_references = subjectReferences + userObjectReferences

            self.action = _buildUserAction(self.objects.users[0])

        elif self.verb == 'restamp':
            subjects, subjectReferences = _formatUserObjects(self.subjects)

            if schema.personal:
                self.body = '%s gave you credit.' % (subjects)
                self.body_references = subjectReferences
                self.image = _getIconURL('news_benefit_2')
            else:
                verb = 'gave'
                offset = len(subjects) + len(verb) + 2
                userObjects, userObjectReferences = _formatUserObjects(self.objects.users, offset=offset)
                self.body = '%s %s %s credit.' % (subjects, verb, userObjects)
                self.body_references = subjectReferences + userObjectReferences
                self.image = self.subjects[0].image_url

            self.action = _buildStampAction(self.objects.stamps[0])

        elif self.verb == 'like':
            self.icon = _getIconURL('news_like')
            subjects, subjectReferences = _formatUserObjects(self.subjects)
            verb = 'liked'
            offset = len(subjects) + len(verb) + 2
            stampObjects, stampObjectReferences = _formatStampObjects(self.objects.stamps, offset=offset)
            self.body = '%s %s %s.' % (subjects, verb, stampObjects)
            self.body_references = subjectReferences + stampObjectReferences

            if not schema.personal:
                stampUsers = map(lambda x: x['user'], self.objects.stamps)
                stampUserObjects, stampUserReferences = _formatUserObjects(stampUsers, offset=4)
                self.footer = 'via %s' % stampUserObjects
                self.footer_references = stampUserReferences

            if schema.personal and self.benefit is not None:
                self.image = _getIconURL('news_benefit_1')
            elif len(self.subjects) == 1:
                self.image = self.subjects[0].image_url
            else:
                ### TODO: What should this image be?
                self.image = _getIconURL('news_like')

            self.action = _buildStampAction(self.objects.stamps[0])

        elif self.verb == 'todo':
            self.icon = _getIconURL('news_todo')
            subjects, subjectReferences = _formatUserObjects(self.subjects)
            verb = 'added'
            offset = len(subjects) + len(verb) + 2
            entityObjects, entityObjectReferences = _formatEntityObjects(self.objects.entities, offset=offset)
            self.body = '%s %s %s as a to-do.' % (subjects, verb, entityObjects)
            self.body_references = subjectReferences + entityObjectReferences

            if len(self.subjects) == 1:
                self.image = self.subjects[0].image_url
            else:
                ### TODO: What should this image be?
                self.image = _getIconURL('news_todo')

            if len(self.objects.stamps) > 0:
                self.action = _buildStampAction(self.objects.stamps[0])
            else:
                self.action = _buildEntityAction(self.objects.entities[0])

        elif self.verb == 'comment':
            verb = 'Comment on'
            offset = len(verb) + 1
            commentObjects, commentObjectReferences = _formatCommentObjects(self.objects.comments)
            stampObjects, stampObjectReferences = _formatStampObjects(self.objects.stamps, offset=offset)
            self.header = '%s %s' % (verb, stampObjects)
            self.header_references = stampObjectReferences
            self.body = '%s' % commentObjects
            self.body_references = commentObjectReferences
            self.image = self.subjects[0].image_url
            self.action = _buildStampAction(self.objects.stamps[0])

        elif self.verb == 'reply':
            verb = 'Reply on'
            offset = len(verb) + 1
            commentObjects, commentObjectReferences = _formatCommentObjects(self.objects.comments)
            stampObjects, stampObjectReferences = _formatStampObjects(self.objects.stamps, offset=offset)
            self.header = '%s %s' % (verb, self.objects.stamps[0].entity.title)
            self.header_references = stampObjectReferences
            self.body = '%s' % commentObjects
            self.body_references = commentObjectReferences
            self.image = self.subjects[0].image_url
            self.action = _buildStampAction(self.objects.stamps[0])

        elif self.verb == 'mention':
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

            self.image = self.subjects[0].image_url
            self.action = _buildStampAction(self.objects.stamps[0])

        elif self.verb.startswith('friend_'):
            self.icon = _getIconURL('news_friend')
            self.image = self.subjects[0].image_url
            self.action = _buildUserAction(self.subjects[0])

        elif self.verb.startswith('action_'):
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
            self.image = self.subjects[0].image_url
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

