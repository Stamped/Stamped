#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import copy
from datetime import datetime
from schema import *
from Schemas import *

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
        self.first_name         = SchemaElement(basestring, required=True)
        self.last_name          = SchemaElement(basestring, required=True)
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
        self.first_name         = SchemaElement(basestring, required=True)
        self.last_name          = SchemaElement(basestring, required=True)
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
        self.first_name         = SchemaElement(basestring)
        self.last_name          = SchemaElement(basestring)
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
        self.num_stamps         = SchemaElement(int)
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
        self.display_name       = SchemaElement(basestring, required=True)
        self.profile_image      = SchemaElement(basestring)
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

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Entity':
            data                = schema.exportSparse()
            coordinates         = data.pop('coordinates', None)
            
            self.importData(data, overflow=True)
            
            self.address        = schema.details.place.address
            self.neighborhood   = schema.details.place.neighborhood
            self.phone          = schema.details.contact.phone
            self.site           = schema.details.contact.site
            self.hours          = schema.details.contact.hoursOfOperation
            self.cuisine        = schema.details.restaurant.cuisine
            self.coordinates    = _coordinatesDictToFlat(coordinates)
            
            self.last_modified  = schema.timestamp.created
            
            if schema.sources.openTable.reserveURL != None:
                url = "http://www.opentable.com/reserve/%s&ref=9166" % \
                        (schema.sources.openTable.reserveURL)
                self.opentable_url = url
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
            self.importData(schema.exportSparse(), overflow=True)
            
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

    def exportSchema(self, schema):
        if schema.__class__.__name__ == 'EntitySearch':
            schema.importData({'q': self.q})
            schema.coordinates = _coordinatesFlatToDict(self.coordinates)
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
        self.credit             = SchemaList(HTTPUserMini())
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
        self.comment            = HTTPComment()
        self.stamp              = HTTPStamp()
        self.favorite           = HTTPFavorite()
        self.created            = SchemaElement(basestring)

    def importSchema(self, schema):
        if schema.__class__.__name__ == 'Activity':
            data                = schema.exportSparse()
            user                = UserMini(data.pop('user', None))
            stamp               = Stamp(data.pop('stamp', None))
            comment             = Comment(data.pop('comment', None))
            favorite            = Favorite(data.pop('favorite', None))

            data['user']        = HTTPUserMini().importSchema(user).exportSparse()

            if stamp.stamp_id != None:
                data['stamp']   = HTTPStamp().importSchema(stamp).exportSparse()
                if 'num_comments' in data['stamp']:
                    del(data['stamp']['num_comments'])
            if comment.comment_id != None:
                data['comment'] = HTTPComment().importSchema(comment).exportSparse()
            if favorite.favorite_id != None:
                data['favorite']= HTTPFavorite().importSchema(favorite).exportSparse()

            self.importData(data, overflow=True)
            self.created = schema.timestamp.created
        else:
            raise NotImplementedError
        return self

