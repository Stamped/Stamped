#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from logs import report

try:
    from resolve.BasicFieldGroup        import BasicFieldGroup
except:
    report()
    raise

class AKindTypeGroup(BasicFieldGroup):
    def __init__(self, *args, **kwargs):
        BasicFieldGroup.__init__(self, *args, **kwargs)
        self.__kinds = set( )
        self.__types = set( )
        
    def addKind(self, kind):
        self.__kinds.add(kind)

    def removeKind(self, kind):
        self.__kinds.remove(kind)
        
    def addType(self, t):
        self.__types.add(t)

    def removeType(self, t):
        self.__types.remove(t)

    def getKinds(self):
        return self.__kinds 

    def getTypes(self):
        return self.__types
    
    def eligible(self, entity):
        if len(self.__kinds) == 0 or entity.kind in self.__kinds:
            if len(self.__types) == 0 or len(self.__types.intersection(entity.types)) > 0:
                return True
        return False

class APlaceGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('place')

class APersonGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('person')

class AMediaCollectionGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('media_collection')

class AMediaItemGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('media_item')

class ASoftwareGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('software')

class ARestaurantGroup(APlaceGroup):

    def __init__(self, *args, **kwargs):
        APlaceGroup.__init__(self, *args, **kwargs)
        eligible = set( [
            'restaurant',
            'bar', 
            'bakery',
            'cafe', 
            'market',
            'food',
            'night_club',
        ] )
        for v in eligible:
            self.addType(v)

class ABookGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('media_item')
        self.addType('book')

class AMovieGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('media_item')
        self.addType('movie')

class AFilmGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('media_collection')
        self.addKind('media_item')
        self.addType('movie')
        self.addType('tv')

class AAmazonGroup(AKindTypeGroup):

    def __init__(self, *args, **kwargs):
        AKindTypeGroup.__init__(self, *args, **kwargs)
        self.addKind('media_collection')
        self.addType('album')
        self.addKind('media_item')
        self.addType('book')
        self.addType('track')
        self.addKind('software')
        self.addType('video_game')
