#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, CSVUtils, FactualUtils, Utils

from gevent.pool import Pool
from AEntitySource import AExternalDumpEntitySource
from Entity import Entity

class FactualUSRestaurantsDump(AExternalDumpEntitySource):
    """
        Factual US Restaurants importer
    """
    
    DUMP_FILE = "sources/dumps/data/factual/US_Restaurants_V2.csv"
    NAME = "Factual US Restaurants"
    TYPES = set([ 'place', 'contact', 'restaurant' ])
    
    _map = {
        'Factual ID' : 'fid', 
        'name' : 'name', 
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
        AExternalDumpEntitySource.__init__(self, self.NAME, self.TYPES)
    
    def _run(self):
        Utils.log("%s parsing '%s'" % (self.NAME, self.DUMP_FILE))
        
        csvFile = open(self.DUMP_FILE, 'rb')
        reader  = CSVUtils.UnicodeReader(csvFile)
        
        #Utils.logRaw("Parsing restaurant:                 ")
        pool  = Pool(256)
        count = 0
        
        for row in reader:
            if self.limit and count >= self.limit:
                break
            
            #update = str(count).ljust(16)
            #Utils.logRaw('\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b%s' % update)
            #Utils.log('Parsing %s' % row['name'])
            #Utils.log(row)
            
            pool.spawn(self._parseEntity, row)
            count += 1
        
        pool.join()
        self._output.put(StopIteration)
        csvFile.close()
        
        Utils.log("")
        Utils.log("%s parsed %d entities" % (self.NAME, count))
        Utils.log("")
    
    def _parseEntity(self, row):
        entity = Entity()
        entity.factual = {
            'table' : 'US_Restaurants_V2.csv'
        }
        
        address = FactualUtils.parseAddress(row)
        if address is not None:
            entity.address = address
        
        for srcKey, destKey in self._map.iteritems():
            if srcKey in row and row[srcKey]:
                entity[destKey] = row[srcKey]
        
        #Utils.log(entity)
        self._output.put(entity)

import EntitySources
EntitySources.registerSource('factualUSRestaurants', FactualUSRestaurantsDump)

