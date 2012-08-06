#!/usr/bin/env python
from __future__ import absolute_import

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, re, time, urllib2

from gevent.pool import Pool
from crawler.AEntitySource import AExternalEntitySource
from Schemas import Entity

__all__ = [ "UrbanspoonCrawler" ]

class UrbanspoonCrawler(AExternalEntitySource):
    """ 
        Entity crawler which exhaustively outputs all of the (high quality) 
        Urbanspoon-rated restaurants from Urbanspoon.com.
    """
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "Urbanspoon", self.TYPES, 512)
        self.base = 'http://www.urbanspoon.com'
    
    def getMaxNumEntities(self):
        return 8000 # return an approximation for now
    
    def _run(self):
        utils.log("[%s] parsing site" % (self, ))
        
        pool = Pool(512)
        seed = self.base + '/choose'
        
        # parse the top-level page containing links to all regions (states for the US)
        self._parseLocationsPage(pool, seed)
        
        pool.join()
        self._output.put(StopIteration)
    
    def _parseLocationsPage(self, pool, href):
        try:
            soup = utils.getSoup(href)
        except:
            utils.log("[%s] error downloading page %s" % (self, href))
            return
        
        # find all links to domestic urbanspoon regions (states)
        locations = soup.findAll("table")[3].findAll('a')
        
        # parse each individual location page (state)
        for location in locations:
            name = location.getText().strip()
            href = location.get("href")
            pool.spawn(self._parseLocationPage, pool, name, href)
    
    def _parseLocationPage(self, pool, region_name, href):
        utils.log("[%s] parsing region '%s' (%s)" % (self, region_name, href))
        
        try:
            soup = utils.getSoup(href)
        except:
            utils.log("[%s] error downloading page %s" % (self, href))
            return
        
        try:
            # find all metropolitan areas within this state
            areas = soup.find('table', {"style" : "width:100%"}).find('td').findAll('a')
        except AttributeError:
            # no cities found within this region; return gracefully
            return
        
        # asynchronously parse each metropolitan area within this region
        for area in areas:
            area_name = area.getText().strip()
            area_href = area.get("href")
            
            pool.spawn(self._parseAreaPage, pool, region_name, area_name, area_href)
    
    def _parseAreaPage(self, pool, region_name, area_name, href):
        utils.log("[%s] parsing area '%s.%s' (%s)" % (self, region_name, area_name, href))
        
        try:
            soup = utils.getSoup(href)
        except:
            utils.log("[%s] error downloading page %s" % (self, href))
            return
        
        region_list_link = soup.find('table', {'style' : 'width:100%'}).find('a')
        region_list_href = region_list_link.get('href')
        
        try:
            soup2 = utils.getSoup(region_list_href)
        except:
            utils.log("[%s] error downloading page %s" % (self, region_list_href))
            return
        
        restaurant_list_link = soup2.find('div', {'id' : 'center'}).findAll('p')[1].find('a')
        restaurant_list_href = restaurant_list_link.get('href')
        
        self._parseAllRestaurantsInArea(pool, region_name, area_name, restaurant_list_href, 'A', True)
    
    def _parseAllRestaurantsInArea(self, pool, region_name, area_name, href, letter, parse_letters):
        utils.log("[%s] parsing all restaurants in area '%s.%s' beginning with '%s' (%s)" % (self, region_name, area_name, letter, href))
        
        try:
            soup = utils.getSoup(href)
        except:
            utils.log("[%s] error downloading page %s" % (self, href))
            return
        
        if parse_letters:
            pages = soup.find('div', {'id' : 'center'}).findAll('a', recursive=False)
            
            for page in pages:
                page_letter = page.getText().strip()
                page_href   = page.get('href')
                
                pool.spawn(self._parseAllRestaurantsInArea, pool, region_name, area_name, page_href, page_letter, False)
        
        try:
            # parse next page
            next_page = soup.find('span', {'class' : 'minor-text'}).findAll('a')[-1]
            if next_page.getText().find('next page') != -1:
                next_page_href = self.base + next_page.get("href")
                pool.spawn(self._parseAllRestaurantsInArea, pool, region_name, area_name, next_page_href, letter, False)
        except AttributeError:
            # no next paginated page for restaurants within this area
            pass
        
        restaurants = soup.find('table', {'id' : 'r-t'}).findAll('tr')
        # parse all restaurants on this page
        for restaurant in restaurants:
            r = restaurant.findAll('td')[1].findAll('a')[-2]
            restaurant_name = r.getText().strip()
            restaurant_href = r.get("href")
            
            # asynchronously parse this restaurant
            pool.spawn(self._parseRestaurantPage, pool, region_name, area_name, restaurant_name, restaurant_href)
    
    def _parseRestaurantPage(self, pool, region_name, area_name, restaurant_name, href):
        utils.log("[%s] parsing restaurant '%s.%s.%s' (%s)" % (self, region_name, area_name, restaurant_name, href))
        
        try:
            soup = utils.getSoup(href)
        except:
            utils.log("[%s] error downloading page %s" % (self, href))
            return
        
        # parse the address for the current restaurant
        addr     = soup.find('span', {'class' : 'adr'})
        street   = addr.find('span', {'class' : 'street-address'}).getText().strip()
        locality = addr.find('span', {'class' : 'locality'}).getText().strip()
        region   = addr.find('span', {'class' : 'region'}).getText().strip()
        zipcode  = addr.find('a', {'class' : re.compile('postal-code')}).getText().strip()
        
        address = "%s, %s, %s %s" % (street, locality, region, zipcode)
        
        # add the current restaurant to the output for this crawler
        entity = Entity()
        entity.subcategory = "restaurant"
        entity.title   = restaurant_name
        entity.address = address
        entity.sources.urbanspoon = {
            'uurl' : href, 
        }
        
        self._output.put(entity)

from crawler import EntitySources
EntitySources.registerSource('urbanspoon', UrbanspoonCrawler)

