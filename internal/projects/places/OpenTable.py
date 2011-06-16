#!/usr/bin/python

import urllib, string, re, os
import Utils

from ThreadPool import ThreadPool
from threading import Lock

class SiteOpenTable:
    """OpenTable-specific crawling logic"""
    
    s_lock  = Lock()
    s_pages = set()
    s_first = True
    
    def __init__(self, crawler):
        self.crawler = crawler;
        self.baseURL = "http://www.opentable.com/"
        self.name = "OpenTable"
        self.pool = ThreadPool(64)
        
        SiteOpenTable.s_lock.acquire()
        if SiteOpenTable.s_first:
            # first time ctor has been called; treat it as static ctor
            SiteOpenTable.s_first = False
            self.initPages()
        SiteOpenTable.s_lock.release()
    
    def initPages(self):
        if self.crawler.options.test:
            # hardcoded page of ~20 new york restaurants for testing purposes
            SiteOpenTable.s_pages.add("http://www.opentable.com/opentables.aspx?t=reg&n=11,18,66,7376,7382,7394,7397,7616,7628,7682&m=8&p=2&d=6/14/2011%207:00:00%20PM&scpref=108")
            return
        
        self.crawler.log("\n")
        self.crawler.log("Initializing crawl index for " + self.name + " (" + self.baseURL + ")\n")
        self.crawler.log("\n")
        
        url   = self.baseURL + "state.aspx"
        soup  = Utils.getSoup(url)
        links = soup.find("div", {"id" : "Global"}).findAll("a", {"href" : re.compile("(city)|(country).*")})
        
        pages = set()
        pages.add(url)
        
        for link in links:
            href = link.get("href")
            linkURL = self.baseURL + href
            pages.add(linkURL)
            
            #self.crawler.log(str(i) + ") " + str(rid))
            self.pool.add_task(self.parsePage, linkURL, pages)
        
        self.pool.wait_completion()
        
        self.crawler.log("\n")
        self.crawler.log("Done initializing crawl index for " + self.name + " (" + self.baseURL + ")\n")
        self.crawler.log("\n")
    
    def parsePage(self, url, pages):
        #http://www.opentable.com/start.aspx?m=74&mn=1309
        self.crawler.log("Crawling " + url)
        soup = Utils.getSoup(url)
        links = soup.findAll("a", {"href" : re.compile(".*m=[0-9]*.*mn=[0-9]*")})
        
        for link in links:
            #name = link.renderContents().strip()
            href = link.get("href")
            linkURL = self.baseURL + href
            
            if not linkURL in pages:
                pages.add(linkURL)
                self.pool.add_task(self.parseSubPage, linkURL)
    
    def parseSubPage(self, url):
        self.crawler.log("Crawling " + url)
        soup = Utils.getSoup(url)
        resultsURL = soup.find("div", {"class" : "BrowseAll"}).find("a").get("href")
        
        SiteOpenTable.s_pages.add(resultsURL)
    
    def getNextURL(self):
        SiteOpenTable.s_lock.acquire()
        
        if len(SiteOpenTable.s_pages) <= 0:
            # no more pages left to crawl!
            return None
        else:
            url = SiteOpenTable.s_pages.pop()
        
        SiteOpenTable.s_lock.release()
        return url
    
    def parseEntity(self, row):
        return {
            'name' : row.find("a").renderContents().strip(), 
            'desc' : row.find("div").renderContents().strip()
        }
    
    def getEntityDetailsRequest(self, rid):
        return AsyncWebRequest(url);
    
    def getEntityDetails(self, rid, entity):
        baseURL = "http://www.opentable.com/httphandlers/RestaurantinfoLiteNew.ashx";
        url = baseURL + "?" + urllib.urlencode({ 'rid' : rid })
        
        detailsSoup = Utils.getSoup(url)
        
        entity['address'] = detailsSoup.find("div", {"class" : re.compile(".*address")}).renderContents().strip()
        self.crawler.log(entity)
        
        #entity['numRatings'] = detailsSoup.find("div", {"class" : re.compile("cuisine_pop")}).contents[1].strip()
        # note: also easily available / parsable:
        #     Cross Street, Neighborhood, Parking Info, Cuisine, Price
    
    def extractData(self, url):
        soup = Utils.getSoup(url)
        
        resultList = soup.findAll("tr", {"class" : re.compile("ResultRow.*")})
        results = {}
        
        for i in xrange(len(resultList)):
            result = resultList[i]
            # note: some pages have <div class="rinfo" rid=###> and some have <div rid=###>...
            row = result.find("div", {"rid" : re.compile(".*")})
            rid = row.get("rid")
            entity = self.parseEntity(row)
            results[rid] = entity
            
            #self.crawler.log(str(i) + ") " + str(rid))
            self.pool.add_task(self.getEntityDetails, rid, entity)
        
        self.pool.wait_completion()
        return results

