#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__ = "TODO"

import Globals, utils
import os, re, time, urllib2

from gevent.pool import Pool
from crawler.AEntitySource import AExternalEntitySource
from Schemas import Entity

__all__ = [ "ZagatCrawler" ]

class ZagatCrawler(AExternalEntitySource):
    """ 
        Entity crawler which exhaustively outputs all of the (high quality) 
        Zagat-rated restaurants from Zagat.com.
    """
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalEntitySource.__init__(self, "Zagat", self.TYPES, 512)
        self.base = 'http://www.zagat.com'
    
    def getMaxNumEntities(self):
        return 9000 # return an approximation for now
    
    def _run(self):
        utils.log("[%s] parsing site" % (self, ))
        
        pool = Pool(512)
        seed = self.base + '/locations'
        
        # parse the top-level page containing links to all regions (states for the US)
        self._parseLocationsPage(pool, seed)
        
        pool.join()
        self._output.put(StopIteration)
    
    def _parseLocationsPage(self, pool, href):
        try:
            soup = utils.getSoup(href)
        except:
            utils.printException()
            utils.log("[%s] error downloading page %s" % (self, href))
            return
        
        # find all links to domestic zagat regions (states)
        locations = soup.find("div", {"id" : "loc_domestic"}).findAll("a")
        
        # parse each individual location page (state)
        for location in locations:
            name = location.getText().strip()
            href = self.base + location.get("href")
            pool.spawn(self._parseLocationPage, pool, name, href)
    
    def _parseLocationPage(self, pool, region_name, href):
        utils.log("[%s] parsing region '%s' (%s)" % (self, region_name, href))
        
        try:
            soup = utils.getSoup(href)
        except:
            utils.printException()
            utils.log("[%s] error downloading page %s" % (self, href))
            return
        
        try:
            # find all cities within this state
            # note: could be none if zagat has not rated any cities within a given state (such as Alaska)
            cityLists = soup.find("div", {"id" : "loc_allCities"}).findAll("div", {"class" : "letterBlock"})
        except AttributeError:
            # no cities found within this region; return gracefully
            return
        
        # asynchronously parse each city within this region
        for cityList in cityLists:
            cityList = cityList.find('ul')
            cities = cityList.findAll('a')
            
            for city in cities:
                city_name = city.getText().strip()
                city_href = self.base + city.get("href")
                
                pool.spawn(self._parseCityPage, pool, region_name, city_name, city_href)
    
    def _parseCityPage(self, pool, region_name, city_name, href):
        utils.log("[%s] parsing city '%s.%s' (%s)" % (self, region_name, city_name, href))
        
        try:
            soup = utils.getSoup(href)
        except:
            utils.printException()
            utils.log("[%s] error downloading page %s" % (self, href))
            return
        
        # use the 'all' link on the zagat search homepage for this city to parse all 
        # restaurants within this city
        restaurant_list_link = soup.find("div", {"class" : "upper-links"}).find("a")
        restaurant_list_href = self.base + restaurant_list_link.get("href")
        
        self._parseAllRestaurantsInCityPage(pool, region_name, city_name, restaurant_list_href)
    
    def _parseAllRestaurantsInCityPage(self, pool, region_name, city_name, href):
        utils.log("[%s] parsing all restaurants in city '%s.%s' (%s)" % (self, region_name, city_name, href))
        
        try:
            soup = utils.getSoup(href)
        except:
            utils.printException()
            utils.log("[%s] error downloading page %s" % (self, href))
            return
        
        # parse all zagat-rated restaurants on this page
        restaurants = soup.findAll("li", {"class" : "zr"})
        if restaurants is not None:
            for restaurant in restaurants:
                a = restaurant.find('a')
                restaurant_name = a.getText().strip()
                restaurant_href = self.base + a.get("href")
                
                # asynchronously parse the current restaurant
                pool.spawn(self._parseRestaurantPage, pool, region_name, city_name, restaurant_name, restaurant_href)
        
        try:
            # parse next page
            next_page = soup.find("li", {"class" : re.compile("pager-next")}).find("a", {"class" : "active"})
            if next_page is not None:
                next_page_href = self.base + next_page.get("href")
                self._parseAllRestaurantsInCityPage(pool, region_name, city_name, next_page_href)
        except AttributeError:
            # no next paginated page for restaurants within this city
            pass
    
    def _parseRestaurantPage(self, pool, region_name, city_name, restaurant_name, href):
        utils.log("[%s] parsing restaurant '%s.%s.%s' (%s)" % (self, region_name, city_name, restaurant_name, href))
        
        try:
            soup = utils.getSoup(href)
        except:
            utils.printException()
            utils.log("[%s] error downloading page %s" % (self, href))
            return
        
        # parse the address for the current restaurant
        addr   = soup.find('div', {'class' : 'address'})
        street = addr.find('span', {'class' : 'street'}).getText().strip()
        geo    = addr.find('span', {'class' : 'geo'}).getText().strip()
        
        address = "%s, %s" % (street, geo)
        
        # add the current restaurant to the output for this crawler
        entity = Entity()
        entity.subcategory = "restaurant"
        entity.title   = restaurant_name
        entity.address = address
        entity.sources.zagat = {
            'zurl' : self.base + href, 
        }
        
        #self._globals['soup'] = soup
        # parse cuisine
        header = soup.find('div', {'id' : "block-zagat_restaurants-14"})
        if header is not None:
            header = header.find('ul').find('li', {'class' : 'first'})
            
            if header is not None:
                entity.cuisine = header.getText()
        
        # parse website
        site = soup.find('span', {'class' : 'website'})
        if site is not None:
            site = site.find('a')
            
            if site is not None:
                entity.site = site.get('href')
        
        # parse preview image
        img = soup.find('div', {'id' : 'content'}).find('div', {'class' : 'photo'})
        if img is not None:
            img = img.find('img')
            
            if img is not None:
                entity.image = img.get('src')
        
        self._output.put(entity)

from crawler import EntitySources
EntitySources.registerSource('zagat', ZagatCrawler)

