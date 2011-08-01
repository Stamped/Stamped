#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, CSVUtils, FactualUtils, utils, os

from gevent.pool import Pool
from AEntitySource import AExternalDumpEntitySource
from api.Entity import Entity

__all__ = [ "FactualUSRestaurantsDump" ]

class FactualUSRestaurantsDump(AExternalDumpEntitySource):
    """
        Factual US Restaurants importer
    """
    
    DUMP_FILE_PREFIX      = os.path.dirname(os.path.abspath(__file__)) + "/data/factual/"
    DUMP_FILE_NAME        = "US_Restaurants_V2"
    DUMP_FILE_SUFFIX      = ".csv"
    DUMP_FILE_TEST_SUFFIX = ".test"
    DUMP_FILE = DUMP_FILE_PREFIX + DUMP_FILE_NAME + DUMP_FILE_SUFFIX
    DUMP_FILE_TEST = DUMP_FILE_PREFIX + DUMP_FILE_NAME + DUMP_FILE_TEST_SUFFIX + DUMP_FILE_SUFFIX
    
    NAME = "Factual US Restaurants"
    TYPES = set([ 'place', 'contact', 'restaurant' ])
    
    _map = {
        'Factual ID' : 'fid', 
        'name' : 'title', 
        'tel' : 'phone', 
        'fax' : 'fax', 
        'website' : 'site', 
        'email' : 'email', 
        'latitude' : 'lat', 
        'longitude' : 'lng', 
        'parking' : 'parking', 
        'link_to_menu' : 'menuLink', 
        'alcohol' : 'alcohol', 
        #'breakfast' : None, 
        #'lunch' : None, 
        #'dinner' : None, 
        #'good_for_kids' : 'lng', 
        #'childrens_menu' : 'lng', 
        'takeout' : 'takeout', 
        'delivery' : 'delivery', 
        'kosher' : 'kosher', 
        #'halal' : None, 
        #'vegan_or_vegetarian' : None, 
        #'gluten_free_options' : None, 
        #'healthy_options' : None, 
        #'low_fat_options' : None, 
        #'low_salt_options' : None, 
        #'organic_options' : None, 
        'wheelchair_access' : 'wheelchairAccess', 
        'hours' : 'hoursOfOperation', 
        #'open_24_hours' : None, 
        'price' : 'price', 
        #'link_to_image' : 'lng', 
        'chef' : 'chef', 
        'owner' : 'owner', 
        #'founded' : 'founded', 
        'reservations' : 'acceptsReservations', 
        #'cash_only' : 'lng', 
        'catering' : 'catering', 
        'private_room' : 'privatePartyFacilities', 
        'bar' : 'bar', 
        'link_to_reviews' : 'reviewLinks', 
        #'category' : None, 
    }
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, self.NAME, self.TYPES, 512)
        
        if Globals.options.test:
            self._dumpFile = self.DUMP_FILE_TEST
        else:
            self._dumpFile = self.DUMP_FILE
    
    def getMaxNumEntities(self):
        csvFile  = open(self._dumpFile, 'rb')
        numLines = max(0, CSVUtils.getNumLines(csvFile) - 1)
        csvFile.close()
        
        return numLines
    
    def _run(self):
        csvFile  = open(self._dumpFile, 'rb')
        numLines = max(0, CSVUtils.getNumLines(csvFile) - 1)
        if Globals.options.limit: numLines = max(0, min(Globals.options.limit, numLines - Globals.options.offset))
        
        utils.log("[%s] parsing %d entities from '%s'" % \
            (self.NAME, numLines, self.DUMP_FILE_NAME))
        
        reader = CSVUtils.UnicodeReader(csvFile)
        pool   = Pool(512)
        count  = 0
        offset = 0
        
        for row in reader:
            if offset < Globals.options.offset:
                offset += 1
                continue
            
            if Globals.options.limit and count >= Globals.options.limit:
                break
            
            pool.spawn(self._parseEntity, row, count)
            count += 1
            
            if numLines > 100 and (count % (numLines / 100)) == 0:
                utils.log("[%s] done parsing %s" % \
                    (self.NAME, utils.getStatusStr(count, numLines)))
        
        Globals.options.offset = 0
        if Globals.options.limit:
            Globals.options.limit = max(0, Globals.options.limit - count)
        
        pool.join()
        self._output.put(StopIteration)
        csvFile.close()
        
        utils.log("[%s] finished parsing %d entities" % (self.NAME, count))
    
    def _parseEntity(self, row, count):
        #utils.log("[%s] parsing entity %d" % (self.NAME, count))
        
        entity = Entity()
        entity.category = "restaurant"
        entity.factual = {
            'table' : 'US_Restaurants_V2.csv'
        }
        
        address = FactualUtils.parseAddress(row)
        if address is not None:
            entity.address = address
        
        for srcKey, destKey in self._map.iteritems():
            if srcKey in row and row[srcKey]:
                entity[destKey] = row[srcKey]
        
        #utils.log(entity)
        self._output.put(entity)

import EntitySources
EntitySources.registerSource('factualUSRestaurants', FactualUSRestaurantsDump)

