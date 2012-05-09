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

def _initialize_image_sizes(dest):
    get_image_url = lambda d: dest.image_url.replace('.jpg', '-%dx%d.jpg' % (d, d))
    
    dest.image_url_31  = get_image_url(31)
    dest.image_url_37  = get_image_url(37)
    dest.image_url_46  = get_image_url(46)
    dest.image_url_55  = get_image_url(55)
    dest.image_url_62  = get_image_url(62)
    dest.image_url_72  = get_image_url(72)
    dest.image_url_74  = get_image_url(74)
    dest.image_url_92  = get_image_url(92)
    dest.image_url_110 = get_image_url(110)
    dest.image_url_144 = get_image_url(144)
    
    self.image.sizes.append(ImageSizeSchema({'url': image_url }))
    
    for size in [144, 110, 92, 74, 72, 62, 55, 46, 37, 31]:
        image = ImageSizeSchema({
            'url'    : get_image_url(size), 
            'height' : size, 
            'width'  : size
        })
        
        self.image.sizes.append(image)

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
            raise NotImplementedError(type(schema))
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
            raise NotImplementedError(type(schema))
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
        self.netflix_user_id             = SchemaElement(basestring)
        self.netflix_token          = SchemaElement(basestring)
        self.netflix_secret         = SchemaElement(basestring)

    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'LinkedAccounts':
            schema.twitter_id           = self.twitter_id
            schema.twitter_screen_name  = self.twitter_screen_name
            schema.facebook_id          = self.facebook_id
            schema.facebook_name        = self.facebook_name
            schema.facebook_screen_name = self.facebook_screen_name
            schema.netflix_id           = self.netflix_id
        elif schema.__class__.__name__ == 'TwitterAuthSchema':
            schema.twitter_key          = self.twitter_key
            schema.twitter_secret       = self.twitter_secret
        elif schema.__class__.__name__ == 'FacebookAuthSchema':
            schema.facebook_token       = self.facebook_token
        elif schema.__class__.__name__ == 'NetflixAuthSchema':
            schema.netflix.user_id      = self.netflix_user_id
            schema.netflix.token        = self.netflix_token
            schema.netflix.secret       = self.netflix_secret
        else:
            raise NotImplementedError(type(schema))
        return schema

class HTTPAvailableLinkedAccounts(Schema):
    def setSchema(self):
        self.twitter                = SchemaElement(bool)
        self.facebook               = SchemaElement(bool)
        self.netflix                = SchemaElement(bool)

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
            raise NotImplementedError(type(schema))
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
        
        # TODO (travis 5/3/12): how to best surface multiple image resolutions to clients?
        # NOTE: this is a reoccurring pattern that we should find a cleaner, platform-wide 
        # solution to (e.g., activity item images, entity images, stamp images, etc.). until 
        # then, I'm inlining the available profile image sizes so as not to bake that logic 
        # into the web client (these sizes are already hard-coded in the iOS client...)
        self.image              = HTTPImageSchema()
        self.image_url          = SchemaElement(basestring) # original (historically 500x500)
        self.image_url_31       = SchemaElement(basestring)
        self.image_url_37       = SchemaElement(basestring)
        self.image_url_46       = SchemaElement(basestring)
        self.image_url_55       = SchemaElement(basestring)
        self.image_url_62       = SchemaElement(basestring)
        self.image_url_72       = SchemaElement(basestring)
        self.image_url_74       = SchemaElement(basestring)
        self.image_url_92       = SchemaElement(basestring)
        self.image_url_110      = SchemaElement(basestring)
        self.image_url_144      = SchemaElement(basestring)
        
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
        self.distribution       = SchemaList(HTTPCategoryDistribution())

    def importSchema(self, schema, client=None):
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
            _initialize_image_sizes(self)
            
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
        else:
            raise NotImplementedError(type(schema))
        
        return self

class HTTPCategoryDistribution(Schema):
    def setSchema(self):
        self.category           = SchemaElement(basestring, required=True)
        self.name               = SchemaElement(basestring)
        self.icon               = SchemaElement(basestring)
        self.count              = SchemaElement(int)

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
        
        # TODO (travis 5/3/12): how to best surface multiple image resolutions to clients?
        # NOTE: this is a reoccurring pattern that we should find a cleaner, platform-wide 
        # solution to (e.g., activity item images, entity images, stamp images, etc.). until 
        # then, I'm inlining the available profile image sizes so as not to bake that logic 
        # into the web client (these sizes are already hard-coded in the iOS client...)
        self.image              = HTTPImageSchema()
        self.image_url          = SchemaElement(basestring) # original (historically 500x500)
        self.image_url_31       = SchemaElement(basestring)
        self.image_url_37       = SchemaElement(basestring)
        self.image_url_46       = SchemaElement(basestring)
        self.image_url_55       = SchemaElement(basestring)
        self.image_url_62       = SchemaElement(basestring)
        self.image_url_72       = SchemaElement(basestring)
        self.image_url_74       = SchemaElement(basestring)
        self.image_url_92       = SchemaElement(basestring)
        self.image_url_110      = SchemaElement(basestring)
        self.image_url_144      = SchemaElement(basestring)
    
    def importSchema(self, schema):
        if schema.__class__.__name__ == 'UserMini':
            self.importData(schema.exportSparse(), overflow=True)
            self.image_url = _profileImageURL(schema.screen_name, schema.image_cache)
            
            _initialize_image_sizes(self)
        else:
            raise NotImplementedError(type(schema))
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
            raise NotImplementedError(type(schema))
        
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

class HTTPNetflixId(Schema):
    def setSchema(self):
        self.netflix_id         = SchemaElement(basestring)

class HTTPNetflixAuthResponse(Schema):
    def setSchema(self):
        self.stamped_oauth_token= SchemaElement(basestring)
        self.oauth_token        = SchemaElement(basestring)
        self.secret             = SchemaElement(basestring)
        self.oauth_verifier     = SchemaElement(basestring)

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


# ################# #
# Endpoint Response #
# ################# #

class HTTPEndpointResponse(Schema):
    def setSchema(self):
        self.action         = HTTPAction()

    def setAction(self, actionType, name, sources, **kwargs):
        if len(sources) > 0:
            action          = HTTPAction()
            action.type     = actionType
            action.sources  = sources

            self.action = action

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
        self.images             = SchemaList(HTTPImageSchema())
        self.last_modified      = SchemaElement(basestring)
        
        # Location
        self.address            = SchemaElement(basestring)
        self.neighborhood       = SchemaElement(basestring)
        self.coordinates        = SchemaElement(basestring)
        
        # Components
        self.playlist           = HTTPEntityPlaylist()
        self.actions            = SchemaList(HTTPEntityAction())
        self.galleries          = SchemaList(HTTPEntityGallery())
        self.metadata           = SchemaList(HTTPEntityMetadataItem())
        self.stamped_by         = HTTPEntityStampedBy()
        self.related            = HTTPEntityRelated()


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
    
    def _addImages(self, images):
        logs.info('\n### calling addImages')
        for image in images:
            logs.info('\n### iterating through images')
            if len(image.sizes) == 0:
                continue
            newimg = HTTPImageSchema()
            for size in image.sizes:
                if size.url is not None:
                    newsize = HTTPImageSizeSchema({'url': _cleanImageURL(size.url) })
                    newimg.sizes.append(newsize)
            logs.info('\n### adding image')
            self.images.append(newimg)

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

        logs.info("\n HIT importEntity ######")

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
                    item = HTTPImageSchema()
                    item.importSchema(image)
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
                    item = HTTPImageSchema()
                    item.importSchema(screenshot)
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
            self._addImages(entity.images)

        return self
            
    def importSchema(self, schema, client=None):
        if schema.__class__.__name__ == 'EntityMini':
            data                = schema.value
            coordinates         = data.pop('coordinates', None)
            self.importData(data, overflow=True)
            self.coordinates    = _coordinatesDictToFlat(coordinates)
        else:
            raise NotImplementedError(type(schema))
        return self

# HTTPEntity Components

class HTTPImageSchema(Schema):
    def setSchema(self):
        self.sizes                  = SchemaList(HTTPImageSizeSchema())
        self.caption                = SchemaElement(basestring)
        self.action                 = HTTPAction()

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'ImageSchema':
            self.importData(schema.exportSparse(), overflow=True)
        else:
            raise NotImplementedError
        return self

class HTTPImageSizeSchema(Schema):
    def setSchema(self):
        self.url                    = SchemaElement(basestring)
        self.width                  = SchemaElement(int)
        self.height                 = SchemaElement(int)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'ImageSizeSchema':
            self.importData(schema.exportSparse(), overflow=True)
        else:
            raise NotImplementedError
        return self


class HTTPAction(Schema):
    def setSchema(self):
        self.type                   = SchemaElement(basestring, required=True)
        self.name                   = SchemaElement(basestring, required=True)
        self.sources                = SchemaList(HTTPActionSource(), required=True)

class HTTPActionSource(Schema):
    def setSchema(self):
        self.name                   = SchemaElement(basestring, required=True)
        self.source                 = SchemaElement(basestring, required=True)
        self.source_id              = SchemaElement(basestring)
        self.source_data            = SchemaElement(dict)
        self.endpoint               = SchemaElement(basestring)
        self.endpoint_data          = SchemaElement(dict)
        self.link                   = SchemaElement(basestring)
        self.icon                   = SchemaElement(basestring)
        self.completion_endpoint    = SchemaElement(basestring)
        self.completion_data        = SchemaElement(dict) # dictionary?
    
    def setCompletion(self, **kwargs):
        self.completion_endpoint    = COMPLETION_ENDPOINT
        self.completion_data        = HTTPActionCompletionData(kwargs, overflow=True)

class HTTPActionCompletionData(Schema):
    def setSchema(self):
        self.action                 = SchemaElement(basestring)
        self.source                 = SchemaElement(basestring)
        self.source_id              = SchemaElement(basestring)
        self.entity_id              = SchemaElement(basestring)
        self.user_id                = SchemaElement(basestring)
        self.stamp_id               = SchemaElement(basestring)

class HTTPEntityAction(Schema):
    def setSchema(self):
        self.action                 = HTTPAction(required=True)
        self.name                   = SchemaElement(basestring, required=True)
        self.icon                   = SchemaElement(basestring)

class HTTPEntityMetadataItem(Schema):
    def setSchema(self):
        self.name                   = SchemaElement(basestring, required=True)
        self.value                  = SchemaElement(basestring, required=True)
        self.key                    = SchemaElement(basestring)
        self.action                 = HTTPAction()
        self.icon                   = SchemaElement(basestring)
        self.extended               = SchemaElement(bool)
        self.optional               = SchemaElement(bool)

class HTTPEntityGallery(Schema):
    def setSchema(self):
        self.images                 = SchemaList(HTTPImageSchema(), required=True)
        self.name                   = SchemaElement(basestring)
        self.layout                 = SchemaElement(basestring) # 'list' or None

class HTTPEntityPlaylist(Schema):
    def setSchema(self):
        self.data                   = SchemaList(HTTPEntityPlaylistItem(), required=True)
        self.name                   = SchemaElement(basestring)

class HTTPEntityPlaylistItem(Schema):
    def setSchema(self):
        self.entity_id              = SchemaElement(basestring)
        self.name                   = SchemaElement(basestring, required=True)
        self.action                 = HTTPAction()
        self.length                 = SchemaElement(int)
        self.icon                   = SchemaElement(basestring)

class HTTPEntityStampedBy(Schema):
    def setSchema(self):
        self.friends                = SchemaElement(int, required=True)
        self.friends_of_friends     = SchemaElement(int)
        self.everyone               = SchemaElement(int)

class HTTPEntityRelated(Schema):
    def setSchema(self):
        self.data                   = SchemaList(HTTPEntityMini(), required=True)
        self.title                  = SchemaElement(basestring)

# Related

class HTTPEntityMini(Schema):
    def setSchema(self):
        self.entity_id              = SchemaElement(basestring, required=True)
        self.title                  = SchemaElement(basestring, required=True)
        self.subtitle               = SchemaElement(basestring, required=True)
        self.category               = SchemaElement(basestring, required=True)
        self.subcategory            = SchemaElement(basestring, required=True)
        self.coordinates            = SchemaElement(basestring)
        self.images                 = SchemaList(HTTPImageSchema())

    def importSchema(self, schema):
        if isinstance(schema, BasicEntity):
            self.entity_id          = schema.entity_id
            self.title              = schema.title 
            self.subtitle           = schema.subtitle
            self.category           = schema.category
            self.subcategory        = schema.subcategory
            self.images             = schema.images

            try:
                if 'coordinates' in schema.value:
                    self.coordinates    = _coordinatesDictToFlat(schema.coordinates)
            except Exception:
                pass
        else:
            raise NotImplementedError(type(schema))
        return self


class HTTPEntityNew(Schema):
    def setSchema(self):
        self.title                  = SchemaElement(basestring, required=True)
        self.subtitle               = SchemaElement(basestring, required=True)
        self.category               = SchemaElement(basestring, required=True)
        self.subcategory            = SchemaElement(basestring, required=True)
        self.desc                   = SchemaElement(basestring)
        self.address                = SchemaElement(basestring)
        self.coordinates            = SchemaElement(basestring)
        self.cast                   = SchemaElement(basestring)
        self.director               = SchemaElement(basestring)
        self.release_date           = SchemaElement(basestring)
        self.artist                 = SchemaElement(basestring)
        self.album                  = SchemaElement(basestring)
        self.author                 = SchemaElement(basestring)

    def exportEntity(self, authUserId):

        kind    = deriveKindFromSubcategory(self.subcategory)
        entity  = buildEntity(kind=kind)

        entity.schema_version   = 0
        entity.types            = list(deriveTypesFromSubcategories([self.subcategory]))
        entity.title            = self.title 

        def addField(entity, field, value, timestamp):
            if value is not None:
                try:
                    entity[field] = value
                    entity['%s_source' % field] = 'seed'
                    entity['%s_timestamp' % field] = timestamp
                except Exception:
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
                except Exception:
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
                'category':     self.category,
                'subcategory':  self.subcategory,
                'desc':         self.desc
            })
            schema.details.place.address = self.address 
            schema.coordinates = _coordinatesFlatToDict(self.coordinates)
        else:
            raise NotImplementedError(type(schema))
        return schema

class HTTPEntityAutosuggest(Schema):
    def setSchema(self):
        self.search_id          = SchemaElement(basestring, required=True)
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring)
        self.category           = SchemaElement(basestring, required=True)
        self.distance           = SchemaElement(float)
    
    def importSchema(self, schema, distance=None):
        if isinstance(schema, BasicEntity):
            self.search_id = schema.search_id
            assert self.search_id is not None
            
            self.title          = schema.title 
            self.subtitle       = schema.subtitle
            self.category       = schema.category 
            
            if isinstance(distance, float) and distance >= 0:
                self.distance   = distance
        else:
            raise NotImplementedError(type(schema))
        
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
            raise NotImplementedError(type(schema))
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
            raise NotImplementedError(type(schema))
        return schema

class HTTPEntitySuggested(Schema):
    def setSchema(self):
        self.coordinates        = SchemaElement(basestring)
        self.category           = SchemaElement(basestring)
        self.subcategory        = SchemaElement(basestring)
        self.limit              = SchemaElement(int)
    
    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'EntitySuggested':
            if self.coordinates:
                schema.coordinates = _coordinatesFlatToDict(self.coordinates)
            
            schema.importData({'category': self.category})
            schema.importData({'subcategory': self.subcategory})
        else:
            raise NotImplementedError(type(schema))
        
        return schema


class HTTPEntityActionEndpoint(Schema):
    def setSchema(self):
        self.status             = SchemaElement(basestring)
        self.message            = SchemaElement(basestring)
        self.redirect           = SchemaElement(basestring)

class HTTPActionComplete(Schema):
    def setSchema(self):
        self.action             = SchemaElement(basestring)
        self.source             = SchemaElement(basestring)
        self.source_id          = SchemaElement(basestring)
        self.entity_id          = SchemaElement(basestring)
        self.user_id            = SchemaElement(basestring)
        self.stamp_id           = SchemaElement(basestring)



# ###### #
# Stamps #
# ###### #

class HTTPStampContent(Schema):
    def setSchema(self):
        self.blurb              = SchemaElement(basestring)
        self.blurb_references   = SchemaList(HTTPTextReference())
        self.blurb_formatted    = SchemaElement(basestring)
        self.images             = SchemaList(HTTPImageSchema())
        self.created            = SchemaElement(basestring)
        self.modified           = SchemaElement(basestring)

class HTTPStampPreviews(Schema):
    def setSchema(self):
        self.likes              = SchemaList(HTTPUserMini())
        self.todos              = SchemaList(HTTPUserMini())
        self.credits            = SchemaList(HTTPStampMini())
        self.comments           = SchemaList(HTTPComment())

class HTTPStamp(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.entity             = HTTPEntityMini(required=True)
        self.user               = HTTPUserMini(required=True)
        self.contents           = SchemaList(HTTPStampContent())
        self.credit             = SchemaList(CreditSchema())
        self.previews           = HTTPStampPreviews()
        self.badges             = SchemaList(HTTPBadge())
        self.via                = SchemaElement(basestring)
        self.url                = SchemaElement(basestring)
        self.created            = SchemaElement(basestring)
        self.modified           = SchemaElement(basestring)
        self.stamped            = SchemaElement(basestring)
        self.num_comments       = SchemaElement(int)
        self.num_likes          = SchemaElement(int)
        self.is_liked           = SchemaElement(bool)
        self.is_fav             = SchemaElement(bool)
    
    def importSchema(self, schema):
        if schema.__class__.__name__ in set(['Stamp', 'StampMini']):
            data                = schema.exportSparse()
            coordinates         = data['entity'].pop('coordinates', None)
            mentions            = data.pop('mentions', [])
            credit              = data.pop('credit', [])
            contents            = data.pop('contents', [])
            
            previews            = data.pop('previews', {})
            comments            = previews.pop('comments', [])
            likes               = previews.pop('likes', [])
            todos               = previews.pop('todos', [])
            credits             = previews.pop('credits', [])
            
            if len(credit) > 0:
                data['credit'] = credit
            
            data['entity'] = HTTPEntityMini().importSchema(schema.entity).exportSparse()
            
            self.importData(data, overflow=True)
            self.user                   = HTTPUserMini().importSchema(schema.user).exportSparse()
            self.entity.coordinates     = _coordinatesDictToFlat(coordinates)
            self.created                = schema.timestamp.stamped # Temp
            self.modified               = schema.timestamp.modified
            self.stamped                = schema.timestamp.stamped 
            
            for content in schema.contents:
                item            = HTTPStampContent()
                item.blurb      = content.blurb 
                item.created    = content.timestamp.created 
                # item.modified   = content.timestamp.modified 
                
                for screenName in mention_re.finditer(content.blurb):
                    source              = HTTPActionSource()
                    source.name         = 'View profile'
                    source.source       = 'stamped'
                    source.source_id    = screenName.groups()[0]
                    
                    action              = HTTPAction()
                    action.type         = 'stamped_view_screen_name'
                    action.name         = 'View profile'
                    action.sources      = [ source ]
                    
                    reference           = HTTPTextReference()
                    reference.indices   = [ screenName.start(), screenName.end() ]
                    reference.action    = action
                    
                    item.blurb_references.append(reference)
                
                for image in content.images:
                    img = HTTPImageSchema()
                    img.importSchema(image)
                    item.images.append(img)
                
                #_initialize_blurb_html(item)
                
                # Insert contents in descending chronological order
                self.contents.insert(0, item)
            
            self.num_comments = 0
            if schema.num_comments > 0:
                self.num_comments       = schema.num_comments
            
            self.num_likes = 0
            if schema.num_likes > 0:
                self.num_likes          = schema.num_likes
            
            url_title = encodeStampTitle(schema.entity.title)
            self.url = 'http://www.stamped.com/%s/stamps/%s/%s' % \
                (schema.user.screen_name, schema.stamp_num, url_title)
            
            if schema.__class__.__name__ == 'Stamp':
                for comment in schema.previews.comments:
                    comment = HTTPComment().importSchema(comment)
                    #_initialize_comment_html(comment)
                    
                    self.previews.comments.append(comment)
                
                for user in schema.previews.todos:
                    user    = HTTPUserMini().importSchema(user).exportSparse()
                    self.previews.todos.append(user)
                
                for user in schema.previews.likes:
                    user    = HTTPUserMini().importSchema(user).exportSparse()
                    self.previews.likes.append(user)
                
                for credit in schema.previews.credits:
                    credit  = HTTPStamp().importSchema(credit).minimize().exportSparse()
                    self.previews.credits.append(credit)
                
                self.is_liked = False
                if schema.is_liked:
                    self.is_liked = True
                
                self.is_fav = False
                if schema.is_fav:
                    self.is_fav = True
        else:
            logs.warning("unknown import class '%s'; expected 'Stamp'" % schema.__class__.__name__)
            raise NotImplementedError
        
        return self
    
    def minimize(self):
        return HTTPStampMini(self.value, overflow=True)

class HTTPStampMini(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.entity             = HTTPEntityMini(required=True)
        self.user               = HTTPUserMini(required=True)
        self.contents           = SchemaList(HTTPStampContent())
        self.credit             = SchemaList(CreditSchema())
        self.badges             = SchemaList(HTTPBadge())
        self.via                = SchemaElement(basestring)
        self.url                = SchemaElement(basestring)
        self.created            = SchemaElement(basestring)
        self.modified           = SchemaElement(basestring)
        self.stamped            = SchemaElement(basestring)
        self.num_comments       = SchemaElement(int)
        self.num_likes          = SchemaElement(int)
        # self.is_liked           = SchemaElement(bool)
        # self.is_fav             = SchemaElement(bool)

class HTTPBadge(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.genre              = SchemaElement(basestring, required=True)

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


#TODO
        # self.limit              = SchemaElement(int)
        # self.offset             = SchemaElement(int)
        # self.coordinates        = SchemaElement(basestring) # "lat,lng"
        # self.category           = SchemaElement(basestring)


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
            except Exception:
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

class HTTPConsumptionSlice(HTTPGenericCollectionSlice):
    def setSchema(self):
        HTTPGenericCollectionSlice.setSchema(self)

        #you, friends, friends of friends, everyone

        self.scope              = SchemaElement(basestring)



    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'ConsumptionSlice':
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

class HTTPActivityObjects(Schema):
    def setSchema(self):
        self.users              = SchemaList(HTTPUserMini())
        self.stamps             = SchemaList(HTTPStamp())
        self.entities           = SchemaList(HTTPEntity())
        self.comments           = SchemaList(HTTPComment())

class HTTPActivity(Schema):
    def setSchema(self):
        # Metadata
        self.activity_id        = SchemaElement(basestring, required=True)
        self.created            = SchemaElement(basestring)
        self.benefit            = SchemaElement(int)
        self.action             = HTTPAction()

        # Structure
        self.verb               = SchemaElement(basestring)
        self.subjects           = SchemaList(HTTPUserMini())
        self.objects            = HTTPActivityObjects()

        # Image
        self.image              = SchemaElement(basestring)
        self.icon               = SchemaElement(basestring)

        # Text
        self.header             = SchemaElement(basestring)
        self.header_references  = SchemaList(HTTPTextReference())
        self.body               = SchemaElement(basestring)
        self.body_references    = SchemaList(HTTPTextReference())
        self.footer             = SchemaElement(basestring)
        self.footer_references  = SchemaList(HTTPTextReference())


    def importSchema(self, schema):
        if schema.__class__.__name__ == 'EnrichedActivity':
            data        = schema.value
            data.pop('subjects', None)
            data.pop('objects', None)
            
            self.importData(data, overflow=True)
            
            self.created = schema.timestamp.created
            
            if self.icon is not None:
                self.icon = _getIconURL(self.icon)
            
            for user in schema.subjects:
                self.subjects.append(HTTPUserMini().importSchema(UserMini(user)).value)
            
            for user in schema.objects.users:
                self.objects.users.append(HTTPUserMini().importSchema(UserMini(user)).value)
            
            for stamp in schema.objects.stamps:
                self.objects.stamps.append(HTTPStamp().importSchema(stamp).value)
            
            for entity in schema.objects.entities:
                self.objects.entities.append(HTTPEntityMini().importSchema(entity).value)
            
            for comment in schema.objects.comments:
                comment = HTTPComment().importSchema(comment).value
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
        
        else:
            raise NotImplementedError
        
        return self

class HTTPTextReference(Schema):
    def setSchema(self):
        self.indices            = SchemaList(SchemaElement(int))
        self.action             = HTTPAction()

class HTTPActivitySlice(HTTPGenericSlice):
    def setSchema(self):
        HTTPGenericSlice.setSchema(self)
        self.distance           = SchemaElement(int)

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
            raise NotImplementedError(type(schema))

        validEntities = set([
            'BasicEntity',
            'PlaceEntity',
            'PersonEntity',
            'MediaCollectionEntity',
            'MediaItemEntity',
            'SoftwareEntity',
        ])

        if schema.__class__.__name__ in validEntities:
            
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

            self.address            = schema.formatAddress()
            self.coordinates        = _coordinatesDictToFlat(schema.coordinates)

            if len(schema.cuisine) > 0:
                self.cuisine        = ', '.join(unicode(i) for i in schema.cuisine)

            if schema.price_range is not None:
                self.price_scale    = '$' * schema.price_range

        if schema.__class__.__name__ == 'PersonEntity':

            if len(schema.genres) > 0:
                self.genre          = ', '.join(unicode(i) for i in schema.genres)

            if len(schema.tracks) > 0:
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

            if len(schema.genres) > 0:
                self.genre          = ', '.join(unicode(i) for i in schema.genres)


            if len(schema.authors) > 0:
                self.author         = ', '.join(unicode(i['title']) for i in schema.authors)

            if len(schema.artists) > 0:
                self.artist_name    = ', '.join(unicode(i['title']) for i in schema.artists)

            if len(schema.publishers) > 0:
                self.publisher      = ', '.join(unicode(i['title']) for i in schema.publishers)

            if len(schema.cast) > 0:
                self.cast           = ', '.join(unicode(i['title']) for i in schema.cast)

            if len(schema.directors) > 0:
                self.director       = ', '.join(unicode(i['title']) for i in schema.directors)

            if len(schema.networks) > 0:
                self.network        = ', '.join(unicode(i['title']) for i in schema.networks)

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

