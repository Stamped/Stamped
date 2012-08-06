#!/usr/bin/env python
from __future__ import absolute_import

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__ = "TODO"

import urllib, string, re, os
import Globals, utils

from crawler.AEntitySource import AExternalSiteEntitySource
from threading import Lock

__all__ = [ "OpenTableCrawler" ]

class OpenTableCrawler(AExternalSiteEntitySource):
    """
        OpenTable-specific crawling logic
    """
    
    BASE_URL = "http://www.opentable.com/"
    NAME     = "OpenTable"
    
    s_lock  = Lock()
    s_pages = set()
    s_first = True
    
    def __init__(self, crawler):
        AExternalSiteEntitySource.__init__(self, self.NAME)
        
        self._crawler = crawler;
        self._pool = Globals.threadPool
        
        self.s_lock.acquire()
        if self.s_first:
            # first time ctor has been called; treat it as static ctor
            self.s_first = False
            self._initPages()
        self.s_lock.release()
    
    def _initPages(self):
        """
        if self._crawler.options.test or not self._crawler.options.crawl:
            # hardcoded page of ~30 new york restaurants for testing purposes
            self.s_pages.add("http://www.opentable.com/opentables.aspx?t=reg&n=11,18,66,2987,2999,3032,3044,3047,3068,3101,3113,3128,3131,3161,7376,7382,7394,7397,7616,7628,7682&m=8&p=2&d=6/14/2011%207:00:00%20PM&scpref=108")
            return
        """
        
        self._crawler.log("\n")
        self._crawler.log("Initializing crawl index for " + self._name + " (" + self.BASE_URL + ")\n")
        self._crawler.log("\n")
        
        url   = self.BASE_URL + "state.aspx"
        soup  = utils.getSoup(url)
        links = soup.find("div", {"id" : "Global"}).findAll("a", {"href" : re.compile("(city)|(country).*")})
        
        pages = set()
        pages.add(url)
        
        for link in links:
            href = link.get("href")
            linkURL = self.BASE_URL + href
            pages.add(linkURL)
            
            #self._crawler.log(str(i) + ") " + str(rid))
            self._pool.add_task(self._parsePage, linkURL, pages)
        
        self._pool.wait_completion()
        
        self._crawler.log("\n")
        self._crawler.log("Done initializing crawl index for " + self._name + " (" + self.BASE_URL + ")\n")
        self._crawler.log("\n")
    
    def _parsePage(self, url, pages):
        #http://www.opentable.com/start.aspx?m=74&mn=1309
        self._crawler.log("Crawling " + url)
        soup = utils.getSoup(url)
        links = soup.findAll("a", {"href" : re.compile(".*m=[0-9]*.*mn=[0-9]*")})
        
        for link in links:
            #name = link.renderContents().strip()
            href = link.get("href")
            linkURL = self.BASE_URL + href
            
            if not linkURL in pages:
                pages.add(linkURL)
                self._pool.add_task(self._parseSubPage, linkURL)
    
    def _parseSubPage(self, url):
        self._crawler.log("Crawling " + url)
        soup = utils.getSoup(url)
        resultsURL = soup.find("div", {"class" : "BrowseAll"}).find("a").get("href")
        
        self.s_pages.add(resultsURL)
    
    def _parseEntity(self, row):
        return {
            'title' : row.find("a").renderContents().strip(), 
            'desc' : row.find("div").renderContents().strip(), 
            'rid'  : row.get("rid")
        }
    
    def _getEntityDetails(self, entity):
        baseURL = "http://www.opentable.com/httphandlers/RestaurantinfoLiteNew.ashx";
        url = baseURL + "?" + urllib.urlencode({ 'rid' : entity['rid'] })
        
        detailsSoup = utils.getSoup(url)
        
        entity['address'] = detailsSoup.find("div", {"class" : re.compile(".*address")}).renderContents().strip()
        self._crawler.log(entity)
        
        #entity['numRatings'] = detailsSoup.find("div", {"class" : re.compile("cuisine_pop")}).contents[1].strip()
        # note: also easily available / parsable:
        #     Cross Street, Neighborhood, Parking Info, Cuisine, Price
    
    def getNextURL(self):
        self.s_lock.acquire()
        
        if len(self.s_pages) <= 0:
            # no more pages left to crawl!
            return None
        else:
            url = self.s_pages.pop()
        
        self.s_lock.release()
        return url
    
    def getEntitiesFromURL(self, url, limit=None):
        soup = utils.getSoup(url)
        
        resultList = soup.findAll("tr", {"class" : re.compile("ResultRow.*")})
        results = []
        
        resultsCount = len(resultsList)
        resultsCount = min(resultsCount, limit or resultsCount)
        
        for i in xrange(resultsCount):
            result = resultList[i]
            # note: some pages have <div class="rinfo" rid=###> and some have <div rid=###>...
            row = result.find("div", {"rid" : re.compile(".*")})
            entity = self._parseEntity(row)
            
            results.append(entity)
            self._pool.add_task(self._getEntityDetails, entity)
        
        self._pool.wait_completion()
        return results

