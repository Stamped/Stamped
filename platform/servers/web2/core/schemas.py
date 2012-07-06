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
        cls.addProperty('mobile',                           bool)

class HTTPObjectId(Schema):
    
    @classmethod
    def setSchema(cls):
        cls.addProperty('stamp_id',                         basestring)

