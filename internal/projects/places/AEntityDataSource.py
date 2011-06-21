#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AEntityDB import AEntityDB
from Entity import Entity

import Utils

class AEntityDataSource(object):
    SOURCES = Utils.createEnum('OpenTable', 'GooglePlaces')
    
    def __init__(self, name):
        self._name = name
        self._id = self._getSourceID(name)
    
    def importAll(self, entityDB, limit=None):
        raise NotImplementedError
    
    def update(self, entityDB, entities):
        raise NotImplementedError
    
    def _getSourceID(self, name):
        if name in self.SOURCES:
            return self.SOURCES[name]
        else:
            return None

class AExternalEntityDataSource(AEntityDataSource):
    
    def __init__(self, name):
        AEntityDataSource.__init__(self, name)

class AExternalSiteEntityDataSource(AExternalEntityDataSource):
    """
        An external site which may be crawled as a source of entity data.
    """
    
    def __init__(self, name):
        AExternalEntityDataSource.__init__(self, name)
    
    def importAll(self, entityDB, limit=None):
        url = self.getNextURL()
        
        while url is not None and len(url) > 0 and ((not self.options.test) or len(self.entities) < 30):
            try:
                entities = self.getEntitiesFromURL(url)
                
                if not entityDB.addEntities(entities):
                    self.log("Error storing %d entities to %s from %s" % \
                            (len(entities), str(entityDB), url))
            except:
                self.log("Error crawling " + url + "\n")
                Utils.printException()
    
    def getNextURL(self):
        raise NotImplementedError
    
    def getEntitiesFromURL(self, url, limit=None):
        raise NotImplementedError

class AExternalServiceEntityDataSource(AExternalEntityDataSource):
    """
        An external service which may be queried as a source of entity data.
    """
    
    def __init__(self, name):
        AExternalEntityDataSource.__init__(self, name)
    

class AExternalDumpEntityDataSource(AExternalEntityDataSource):
    """
        An external data dump which may be crawled as a source of entity data 
        (e.g., compressed bulk datafile).
    """
    
    def __init__(self, name):
        AExternalEntityDataSource.__init__(self, name)
    

class AUserDataSource(AEntityDataSource):
    """
        User-entered / manual data source.
    """
    
    def __init__(self, name):
        AEntityDataSource.__init__(self, name)
    

