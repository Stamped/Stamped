#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import logs
from utils import lazyProperty

from db.mongodb.MongoGuideCollection import MongoGuideCollection

class GuideDB(object):

    @lazyProperty
    def __guide_collection(self):
        return MongoGuideCollection()

    
    def checkIntegrity(self, key, repair=False, api=None):
        return self.__guide_collection.checkIntegrity(key, repair=repair, api=api)


    def addGuide(self, guide):
        return self.__guide_collection.addGuide(guide)
    
    def removeGuide(self, userId):
        return self.__guide_collection.removeGuide(userId)
    
    def getGuide(self, userId):
        return self.__guide_collection.getGuide(userId)

    def updateGuide(self, guide):
        return self.__guide_collection.updateGuide(guide)

