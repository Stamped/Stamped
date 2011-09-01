#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import copy, urllib, urlparse
from datetime import datetime
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
        self.screen_name        = SchemaElement(basestring, required=True)
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
        # self.language           = SchemaElement(basestring)
        # self.time_zone          = SchemaElement(basestring)

class HTTPAccountProfile(Schema):
    def setSchema(self):
        self.name               = SchemaElement(basestring)
        self.color              = SchemaElement(basestring)
        self.bio                = SchemaElement(basestring)
        self.website            = SchemaElement(basestring)
        self.location           = SchemaElement(basestring)

class HTTPAccountProfileImage(Schema):
    def setSchema(self):
        self.profile_image      = SchemaElement(basestring, normalize=False)

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
        self.num_stamps         = SchemaElement(int)
        self.num_stamps_left    = SchemaElement(int)
        self.num_friends        = SchemaElement(int)
        self.num_followers      = SchemaElement(int)
        self.num_faves          = SchemaElement(int)
        self.num_credits        = SchemaElement(int)
        self.num_credits_given  = SchemaElement(int)

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

        self.address            = SchemaElement(basestring)
        self.neighborhood       = SchemaElement(basestring)
        self.coordinates        = SchemaElement(basestring)

        self.phone              = SchemaElement(int)
        self.site               = SchemaElement(basestring)
        self.hours              = SchemaElement(basestring)

        self.cuisine            = SchemaElement(basestring)

        self.author             = SchemaElement(basestring)
        self.isbn               = SchemaElement(basestring)
        self.publisher          = SchemaElement(basestring)
        self.format             = SchemaElement(basestring)
        self.language           = SchemaElement(basestring)

        self.rating             = SchemaElement(basestring)
        self.track_length       = SchemaElement(basestring)
        self.release_date       = SchemaElement(basestring)
        self.genre              = SchemaElement(basestring)
        self.cast               = SchemaElement(basestring)
        self.director           = SchemaElement(basestring)
        self.channel            = SchemaElement(basestring)

        self.artist             = SchemaElement(basestring)
        self.album              = SchemaElement(basestring)

        self.opentable_url      = SchemaElement(basestring)
        self.itunes_url         = SchemaElement(basestring)
        self.itunes_short_url   = SchemaElement(basestring)
        self.netflix_url        = SchemaElement(basestring)
        self.fandango_url       = SchemaElement(basestring)
        self.barnesnoble_url    = SchemaElement(basestring)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Entity':
            from Entity import setSubtitle
            setSubtitle(schema)
            
            data                = schema.value
            coordinates         = data.pop('coordinates', None)
            
            self.importData(data, overflow=True)

            self.last_modified  = schema.timestamp.created
            
            # Place
            self.address        = schema.address
            self.neighborhood   = schema.neighborhood
            self.coordinates    = _coordinatesDictToFlat(coordinates)

            # Contact
            self.phone          = schema.phone
            self.site           = schema.site
            self.hours          = schema.hoursOfOperation
            
            # Food
            self.cuisine        = schema.cuisine

            # Book
            self.author         = schema.author
            self.isbn           = schema.isbn
            self.publisher      = schema.publisher
            # self.format         = None
            # self.language       = None

            # Film
            self.rating         = schema.mpaa_rating
            self.track_length   = schema.track_length
            self.release_date   = schema.original_release_date
            self.cast           = schema.cast
            self.director       = schema.director
            self.channel        = schema.channel
            # self.genre          = None

            # Music
            self.artist         = schema.artist_display_name
            self.album          = schema.album_name
            ### TODO
            
            # Affiliates
            if schema.sources.openTable.reserveURL != None:
                url = "http://www.opentable.com/reserve/%s&ref=9166" % \
                        (schema.sources.openTable.reserveURL)
                self.opentable_url = url
            
            if schema.sources.apple.view_url != None:
                itunes_url  = schema.sources.apple.view_url
                base_url    = "http://click.linksynergy.com/fs-bin/stat"
                params      = "id=%s&offerid=146261&type=3&subid=0&tmpid=1826" \
                            % (LINKSHARE_TOKEN)
                deep_url    = "%s?%s&RD_PARM1=%s" % (base_url, params, \
                                    _encodeLinkShareDeepURL(itunes_url))
                short_url   = _encodeiTunesShortURL(itunes_url)

                self.itunes_url         = deep_url
                self.itunes_short_url   = short_url

            # if schema.sources.netflix

            # if schema.sources.fandango.url != None:

            # if schema.sources.barnesAndNoble
            

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
        self.entity_id          = SchemaElement(basestring, required=True)
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring)
        self.category           = SchemaElement(basestring, required=True)
    
    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Entity':
            from Entity import setSubtitle
            setSubtitle(schema)
            self.importData(schema.value, overflow=True)
            
            if schema.address is not None:
                self.subtitle = schema.address
            if self.subtitle is None:
                self.subtitle = schema.subcategory
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
        self.image              = SchemaElement(basestring)
        self.mentions           = SchemaList(MentionSchema())
        self.credit             = SchemaList(CreditSchema())
        self.comment_preview    = SchemaList(HTTPComment())
        self.created            = SchemaElement(basestring)
        self.num_comments       = SchemaElement(int)

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
            self.num_comments = schema.stats.num_comments
            self.entity.coordinates = _coordinatesDictToFlat(coordinates)
            self.created = schema.timestamp.created

        else:
            raise NotImplementedError
        return self

class HTTPStampNew(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring, required=True)
        self.blurb              = SchemaElement(basestring)
        self.image              = SchemaElement(basestring)
        self.credit             = SchemaList(SchemaElement(basestring), delimiter=',')

class HTTPStampEdit(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.blurb              = SchemaElement(basestring)
        self.image              = SchemaElement(basestring)
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
            entity              = Entity(data.pop('entity', None))
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
            
            if schema.link.stamp_id != None:
                self.link_stamp_id = schema.link.stamp_id
            elif schema.link.user_id != None:
                self.link_user_id = schema.link.user_id
            elif schema.link.entity_id != None:
                self.link_entity_id = schema.link.entity_id
            elif schema.link.url != None:
                self.link_url = schema.link.url

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
