#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from AEntityDataSource import AExternalDumpEntityDataSource
from Entity import Entity

import CSVUtils, FactualUtils, Globals, Utils

class FactualUSRestaurantsDump(AExternalDumpEntityDataSource):
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
        AExternalDumpEntityDataSource.__init__(self, self.NAME, self.TYPES)
    
    def getAll(self, limit=None):
        Utils.log("%s parsing '%s'" % (self.NAME, self.DUMP_FILE))
        
        csvFile = open(self.DUMP_FILE, 'rb')
        reader = CSVUtils.UnicodeReader(csvFile)
        entities = [ ]
        
        Utils.logRaw("Parsing restaurant:                 ")
        
        cat = set()
        for row in reader:
            if limit and len(entities) >= limit:
                break
            
            update = str(len(entities)).ljust(16)
            Utils.logRaw('\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b\b%s' % update)
            
            #Utils.log('Parsing %s' % row['name'])
            #Utils.log(row)
            
            entity = Entity()
            entity.factual = {
                'table' : 'US_Restaurants_V2.csv'
            }
            
            address = FactualUtils.parseAddress(row)
            if address:
                entity.address = address
            
            for srcKey, destKey in self._map.iteritems():
                if srcKey in row and row[srcKey]:
                    entity[destKey] = row[srcKey]
            
            #Utils.log(entity)
            entities.append(entity)
        
        csvFile.close()
        Utils.logRaw("\n")
        Utils.log("")
        Utils.log("%s parsed %d entities" % (self.NAME, len(entities)))
        Utils.log("")
        
        return entities

import EntityDataSources
EntityDataSources.registerSource('factualUSRestaurants', FactualUSRestaurantsDump)

