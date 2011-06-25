#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from abc import abstractmethod
from AEntityDB import AEntityDB
from Entity import Entity

import EntityDataSources, Utils

class AEntityDataSource(object):
    def __init__(self, name):
        self._name = name
        self._id = EntityDataSources.getSourceID(name)
    
    @abstractmethod
    def importAll(self, entityDB, limit=None): pass
    
    @property
    def name(self): return self._name

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
                    Utils.log("Error storing %d entities to %s from %s" % \
                            (Utils.count(entities), str(entityDB), url))
            except:
                Utils.log("Error crawling " + url + "\n")
                Utils.printException()
    
    @abstractmethod
    def getNextURL(self):
        pass
    
    @abstractmethod
    def getEntitiesFromURL(self, url, limit=None):
        pass

class AExternalServiceEntityDataSource(AExternalEntityDataSource):
    """
        An external service which may be queried as a source of entity data.
    """
    
    def __init__(self, name):
        AExternalEntityDataSource.__init__(self, name)
    
    def importAll(self, entityDB, limit=None):
        return True

class AExternalDumpEntityDataSource(AExternalEntityDataSource):
    """
        An external data dump which may be crawled as a source of entity data 
        (e.g., compressed bulk datafile).
    """
    
    def __init__(self, name):
        AExternalEntityDataSource.__init__(self, name)
    
    @abstractmethod
    def getAll(self, limit=None):
        pass
    
    def importAll(self, entityDB, limit=None):
        entities = self.getAll(limit)
        
        return entityDB.addEntities(entities)

class AUserDataSource(AEntityDataSource):
    """
        User-entered / manual data source.
    """
    
    def __init__(self, name):
        AEntityDataSource.__init__(self, name)

