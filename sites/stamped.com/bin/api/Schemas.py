#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import copy
from datetime import datetime
from schema import *


# ##### #
# Users #
# ##### #

class UserSchema(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.first_name         = SchemaElement(basestring, required=True)
        self.last_name          = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.display_name       = SchemaElement(basestring, required=True)
        self.profile_image      = SchemaElement(basestring, required=True)
        self.color_primary      = SchemaElement(basestring, required=True)
        self.color_secondary    = SchemaElement(basestring)
        self.bio                = SchemaElement(basestring)
        self.website            = SchemaElement(basestring)
        self.privacy            = SchemaElement(bool, required=True)
        self.flags              = FlagsSchema()
        self.stats              = UserStatsSchema()
        self.timestamp          = TimestampSchema()

class UserMiniSchema(Schema):
    def setSchema(self):
        self.user_id            = SchemaElement(basestring, required=True)
        self.screen_name        = SchemaElement(basestring, required=True)
        self.display_name       = SchemaElement(basestring, required=True)
        self.profile_image      = SchemaElement(basestring, required=True)
        self.color_primary      = SchemaElement(basestring, required=True)
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
        self.locked             = SchemaElement(bool, default=True)


# ##### #
# Stats #
# ##### #

class UserStatsSchema(Schema):
    def setSchema(self):
        self.num_stamps         = SchemaElement(int)
        self.num_following      = SchemaElement(int)
        self.num_followers      = SchemaElement(int)
        self.num_todos          = SchemaElement(int)
        self.num_cred_received  = SchemaElement(int)
        self.num_cred_given     = SchemaElement(int)

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


# ######## #
# Entities #
# ######## #

class EntityMiniSchema(Schema):
    def setSchema(self):
        self.entity_id          = SchemaElement(basestring, required=True)
        self.title              = SchemaElement(basestring, required=True)
        self.subtitle           = SchemaElement(basestring, required=True)
        self.category           = SchemaElement(basestring, required=True)
        self.coordinates        = CoordinatesSchema()

class CoordinatesSchema(Schema):
    def setSchema(self):
        self.lat                = SchemaElement(float, required=True)
        self.lng                = SchemaElement(float, required=True)


# ###### #
# Stamps #
# ###### #

class StampSchema(Schema):
    def setSchema(self):
        self.stamp_id           = SchemaElement(basestring, required=True)
        self.entity             = EntityMiniSchema(required=True)
        self.user               = UserMiniSchema(required=True)
        self.blurb              = SchemaElement(basestring)
        self.image              = SchemaElement(basestring)
        self.mentions           = SchemaList(SchemaElement(basestring, required=True))
        self.credit             = SchemaList(UserTinySchema())
        self.comment_preview    = SchemaElement(list)
        self.timestamp          = TimestampSchema(required=True)
        self.flags              = StampFlagsSchema()
        self.stats              = StampStatsSchema()

    def _exportFlat(self):
        ret = {}
        ret['stamp_id']         = self.stamp_id.value
        ret['entity']           = self.entity.value
        ret['user']             = self.user.value
        ret['blurb']            = self.blurb.value
        ret['image']            = self.image.value
        ret['mentions']         = self.mentions.value
        ret['credit']           = self.credit.value
        ret['comment_preview']  = self.comment_preview.value
        ret['created']          = self.timestamp.created.value
        ret['flags']            = self.flags.locked.value
        ret['num_comments']     = self.stats.num_comments.value

        ret['entity']['coordinates'] = '%s,%s' % (
            self.entity.coordinates.lat,
            self.entity.coordinates.lng)

        return ret


