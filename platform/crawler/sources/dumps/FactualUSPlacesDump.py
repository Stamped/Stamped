#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from crawler.sources.dumps import CSVUtils
import Globals

from gevent.pool import Pool
from crawler.AEntitySource import AExternalDumpEntitySource
from Schemas import Entity

__all__ = [ "FactualUSPlacesDump" ]

class FactualUSPlacesDump(AExternalDumpEntitySource):
    """
        Factual US POI and Business listings importer
    """
    
    DUMP_FILE = "sources/dumps/data/factual/test.csv"
    NAME = "Factual US POI and Businesses"
    TYPES = set([ 'restaurant' ])
    
    _map = {
        'Factual ID' : 'fid', 
        'name' : 'title', 
        'tel' : 'phone', 
        'fax' : 'fax', 
        'website' : 'site', 
        'latitude' : 'lat', 
        'longitude' : 'lng', 
    }
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, self.NAME, self.TYPES)
    
    def _run(self):
        """
        csvFile = open(self.DUMP_FILE, 'rb')
        reader = CSVUtils.UnicodeReader(csvFile)
        entities = [ ]
        
        cat = set()
        for row in reader:
            #utils.log('Parsing %s' % row['title'])
            utils.log(row)
            
            if row['category'] == '1':
                utils.log("_____________")
                import sys
                sys.exit(0)
            
            if row['category'] is not None and len(row['category']) > 0:
                curCat = row['category']
                if not curCat in cat:
                    cat.add(curCat)
                    print ""
                    print curCat
                    print row
                    print ""
        
        utils.log(cat)
        """
        """
            if self.limit and len(entities) >= self.limit:
                break
            
            entity = Entity()
            entity.factual = {
                'table' : 'usPlaces.csv'
            }
            
            for srcKey, destKey in self._map.iteritems():
                if srcKey in row and row[srcKey]:
                    entity[destKey] = row[srcKey]
            
            entities.append(entity)
        csvFile.close()
        """
        utils.log("%s parsed %d entities" % (self.NAME, len(entities)))
        return entities

#import EntitySources
#EntitySources.registerSource('factualUSPlaces', FactualUSPlacesDump)

