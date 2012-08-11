#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from schema             import *
from api.Schemas        import *
from api.HTTPSchemas    import *

class HTTPWebTimeSlice(Schema):
    
    def __init__(self, *args, **kwargs):
        Schema.__init__(self, *args, **kwargs)
        self.ajax   = False
        self.mobile = False
    
    @classmethod
    def setSchema(cls):
        # Paging
        cls.addProperty('before',                           int)
        cls.addProperty('limit',                            int)
        cls.addProperty('offset',                           int)
        
        # Filtering
        cls.addProperty('category',                         basestring, cast=validateCategory)
        cls.addProperty('subcategory',                      basestring, cast=validateSubcategory)
        cls.addProperty('viewport',                         basestring, cast=validateViewport)
        
        # Scope
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('screen_name',                      basestring, cast=validateScreenName)
        cls.addProperty('scope',                            basestring)
        
        # Web-specific
        cls.addProperty('ajax',                             bool)
        cls.addProperty('mobile',                           bool)

class HTTPWebTimeMapSlice(Schema):
    
    def __init__(self, *args, **kwargs):
        Schema.__init__(self, *args, **kwargs)
        self.ajax   = False
        self.lite   = False
        self.mobile = False
    
    @classmethod
    def setSchema(cls):
        # Paging
        cls.addProperty('before',                           int)
        cls.addProperty('limit',                            int)
        cls.addProperty('offset',                           int)
        
        # Filtering
        cls.addProperty('category',                         basestring, cast=validateCategory)
        cls.addProperty('subcategory',                      basestring, cast=validateSubcategory)
        cls.addProperty('viewport',                         basestring, cast=validateViewport)
        
        # Scope
        cls.addProperty('user_id',                          basestring)
        cls.addProperty('screen_name',                      basestring, cast=validateScreenName)
        cls.addProperty('scope',                            basestring)
        cls.addProperty('stamp_id',                         basestring)
        
        # Web-specific
        cls.addProperty('ajax',                             bool)
        cls.addProperty('lite',                             bool)
        cls.addProperty('mobile',                           bool)

class HTTPStampDetail(Schema):
    
    def __init__(self, *args, **kwargs):
        Schema.__init__(self, *args, **kwargs)
        self.ajax   = False
    
    @classmethod
    def setSchema(cls):
        cls.addProperty('screen_name',                      basestring)
        cls.addProperty('stamp_num',                        int)
        cls.addProperty('stamp_title',                      basestring)
        cls.addProperty('ajax',                             bool)

class HTTPObjectId(Schema):
    
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                         basestring)

class HTTPIndexSchema(Schema):
    
    def __init__(self, *args, **kwargs):
        Schema.__init__(self, *args, **kwargs)
        self.intro  = False
        self.mobile = False
    
    @classmethod
    def setSchema(cls):
        cls.addProperty('intro',                            bool)
        cls.addProperty('mobile',                           bool)

class HTTPDownloadAppSchema(Schema):
    
    @classmethod
    def setSchema(cls):
        cls.addProperty('phone_number',                     basestring, required=True)
        cls.addProperty('mobile',                           bool)

class HTTPResetEmailSchema(Schema):
    
    @classmethod
    def setSchema(cls):
        cls.addProperty('mobile',                           bool)
        cls.addProperty('email',                            basestring, required=True)

class HTTPResetPasswordViewSchema(Schema):
    
    @classmethod
    def setSchema(cls):
        cls.addProperty('mobile',                           bool)
        cls.addProperty('token',                            basestring, required=True)

class HTTPResetPasswordSchema(Schema):
    
    @classmethod
    def setSchema(cls):
        cls.addProperty('mobile',                           bool)
        cls.addProperty('token',                            basestring, required=True)
        cls.addProperty('password',                         basestring, required=True)

class HTTPSettingsSchema(Schema):
    
    @classmethod
    def setSchema(cls):
        cls.addProperty('mobile',                           bool)
        cls.addProperty('token',                            basestring, required=True)

class HTTPUpdateSettingsSchema(Schema):
    
    @classmethod
    def setSchema(cls):
        cls.addProperty('mobile',                           bool)
        cls.addProperty('token',                            basestring, required=True)
        cls.addProperty('alerts_credits_apns',              bool)
        cls.addProperty('alerts_credits_email',             bool)
        cls.addProperty('alerts_likes_apns',                bool)
        cls.addProperty('alerts_likes_email',               bool)
        cls.addProperty('alerts_todos_apns',                bool)
        cls.addProperty('alerts_todos_email',               bool)
        cls.addProperty('alerts_mentions_apns',             bool)
        cls.addProperty('alerts_mentions_email',            bool)
        cls.addProperty('alerts_comments_apns',             bool)
        cls.addProperty('alerts_comments_email',            bool)
        cls.addProperty('alerts_replies_apns',              bool)
        cls.addProperty('alerts_replies_email',             bool)
        cls.addProperty('alerts_followers_apns',            bool)
        cls.addProperty('alerts_followers_email',           bool)
        cls.addProperty('alerts_friends_apns',              bool)
        cls.addProperty('alerts_friends_email',             bool)
        cls.addProperty('alerts_actions_apns',              bool)
        cls.addProperty('alerts_actions_email',             bool)

class HTTPTestSchema(Schema):
    
    def __init__(self, *args, **kwargs):
        Schema.__init__(self, *args, **kwargs)
        self.mobile = False
    
    @classmethod
    def setSchema(cls):
        cls.addProperty('sketch',                           basestring)
        cls.addProperty('mobile',                           bool)

