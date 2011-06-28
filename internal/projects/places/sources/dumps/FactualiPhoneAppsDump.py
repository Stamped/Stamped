#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AEntityDataSource import AExternalDumpEntityDataSource
from Entity import Entity

import CSVUtils, Globals, Utils

class FactualiPhoneAppsDump(AExternalDumpEntityDataSource):
    """
        Factual iPhoneApps data importer
    """
    
    DUMP_FILE = "sources/dumps/data/factual/iPhone_Apps.csv"
    NAME = "Factual iPhone Apps"
    TYPES = set([ 'iPhoneApp' ])
    
    _map = {
        'Name' : 'name', 
        'Developer' : 'developer', 
        'Developer_URL' : 'developerURL', 
        'Developer_support_URL' : 'developerSupportURL', 
        'Publisher' : 'publisher', 
        'Release_Date' : 'releaseDate', 
        'Price' : 'price', 
        'Category' : 'category', 
        'Language' : 'language', 
        'Rating' : 'rating', 
        'Popularity' : 'popularity', 
        'Parental_Rating' : 'parentalRating', 
        'Platform' : 'platform', 
        'Requirements' : 'requirements', 
        'Size' : 'size', 
        'Version' : 'version', 
        'Download_URL' : 'downloadURL', 
        'Thumbnail_URL' : 'thumbnailURL', 
        'Screenshot_URL' : 'screenshotURL', 
        'Video_URL' : 'videoURL', 
    }
    
    def __init__(self):
        AExternalDumpEntityDataSource.__init__(self, self.NAME, self.TYPES)
    
    def getAll(self, limit=None):
        reader = CSVUtils.openCSVFile(self.DUMP_FILE)
        entities = [ ]
        
        for row in reader:
            #Utils.log('Parsing %s' % row['Name'])
            
            if limit and len(entities) >= limit:
                break
            
            entity = Entity()
            entity.factual = {
                'table' : 'iPhone_Apps.csv'
            }
            
            for srcKey, destKey in self._map.iteritems():
                if srcKey in row and row[srcKey] and len(row[srcKey]) > 0:
                    entity[destKey] = row[srcKey]
            
            entities.append(entity)
        
        Utils.log("%s parsed %d entities" % (self.NAME, len(entities)))
        return entities

import EntityDataSources
EntityDataSources.registerSource('factualiPhoneApps', FactualiPhoneAppsDump)

