#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AEntityDataSource import AExternalDumpEntityDataSource
from Entity import Entity

import CSVUtils, Globals, Utils

class FactualUSPlacesDump(AExternalDumpEntityDataSource):
    """
        Factual US POI and Business listings importer
    """
    
    DUMP_FILE = "sources/dumps/data/factual/test.csv"
    NAME = "Factual US POI and Businesses"
    TYPES = set([ 'place', 'contact', 'restaurant' ])
    
    _map = {
        'Factual ID' : 'fid', 
        'name' : 'name', 
        'tel' : 'phone', 
        'fax' : 'fax', 
        'website' : 'site', 
        'latitude' : 'lat', 
        'longitude' : 'lng', 
    }
    
    def __init__(self):
        AExternalDumpEntityDataSource.__init__(self, self.NAME, self.TYPES)
    
    def getAll(self, limit=None):
        csvFile = open(self.DUMP_FILE, 'rb')
        reader = CSVUtils.UnicodeReader(csvFile)
        entities = [ ]
        
        cat = set()
        for row in reader:
            #Utils.log('Parsing %s' % row['name'])
            Utils.log(row)
            
            if row['category'] == '1':
                Utils.log("_____________")
                import sys
                sys.exit(0)
            
            """
            if row['category'] is not None and len(row['category']) > 0:
                curCat = row['category']
                if not curCat in cat:
                    cat.add(curCat)
                    print ""
                    print curCat
                    print row
                    print ""
        
        Utils.log(cat)
        """
        """
            if limit and len(entities) >= limit:
                break
            
            entity = Entity()
            entity.factual = {
                'table' : 'usPlaces.csv'
            }
            
            for srcKey, destKey in self._map.iteritems():
                if srcKey in row and row[srcKey]:
                    entity[destKey] = row[srcKey]
            
            entities.append(entity)
        """
        csvFile.close()
        Utils.log("%s parsed %d entities" % (self.NAME, len(entities)))
        return entities

#import EntityDataSources
#EntityDataSources.registerSource('factualUSPlaces', FactualUSPlacesDump)

