#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AEntityDatabase import AEntityDatabase
from Entity import Entity

import thread

class AEntityDataSource(object):
    SOURCES = Utils.createEnum('OpenTable', 'GooglePlaces')
    
    def __init__(self, name):
        self._name = name
        self._id = self._getSourceID(name)
    
    def import(self, entityDB, entityIDs=None, limit=None):
        pass
    
    def _getSourceID(name):
        if name in self.SOURCES:
            return self.SOURCES[name]
        else:
            return None

class AExternalEntityDataSource(AEntityDataSource):
    
    def __init__(self, name):
        AEntityDataSource.__init__(self, name))

class AExternalSiteEntityDataSource(AExternalEntityDataSource):
    """
        An external site which may be crawled as a source of entity data.
    """
    
    def __init__(self, name):
        AExternalEntityDataSource.__init__(self, name))
    
    def import(self, entityDB, entityIDs=None, limit=None):
        url = self.getNextURL()
        
        while url is not None and len(url) > 0 and ((not self.options.test) or len(self.entities) < 30):
            try:
                entities = self.getEntitiesFromURL(url)
                
                entityDB.addEntities(entities)
            except (KeyboardInterrupt, SystemExit):
                thread.interrupt_main()
                raise
            except:
                self.log("Error crawling " + url + "\n")
                Utils.printException()
                pass
    
    def getNextURL(self):
        pass
    
    def getEntityFromURL(self, url, entityID=None):
        if entityID is None:
            entities = self.getEntitiesFromURL(url, entityIDs: None, limit: 1)
        else:
            entities = self.getEntitiesFromURL(url, entityIDs: [ entityID ], limit: 1)
    
    def getEntitiesFromURL(self, url, entityIDs=None, limit=None):
        pass

class AExternalServiceEntityDataSource(AExternalEntityDataSource):
    """
        An external service which may be queried as a source of entity data.
    """
    
    def __init__(self, name):
        AExternalEntityDataSource.__init__(self, name))
    

class AExternalDropEntityDataSource(AExternalEntityDataSource):
    """
        An external data drop which may be crawled as a source of entity data 
        (e.g., compressed bulk datafile).
    """
    
    def __init__(self, name):
        AExternalEntityDataSource.__init__(self, name))
    

class AUserDataSource(AEntityDataSource):
    """
        User-entered / manual data source.
    """
    
    def __init__(self, name):
        AEntityDataSource.__init__(self, name))
    

