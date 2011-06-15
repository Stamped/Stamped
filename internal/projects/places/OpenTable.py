#!/usr/bin/python

import urllib, string, re, os, sqlite3
from BeautifulSoup import BeautifulSoup
from AsyncWebRequest import *

import Stamped.Backend.Entity;

class SiteOpenTable:
    """OpenTable-specific crawling logic"""
    
    def __init__(self, crawler):
        self.crawler = crawler;
        self.isFirst = False;
    
    def getDBInfo(self):
        return { 'dbName' : 'opentable', 'mainTable' : 'opentablevideos', 'relatedVideosTable' : 'opentablevideosrelated' };
    
    def getURLFromViewkey(self, viewkey):
        return "http://www.opentable.com/view_video.php?viewkey=" + viewkey;
    
    def getNextURL(self, db):
        if (self.isFirst):
            self.isFirst = False;
        else: # lock still acquired from first time through
            self.crawler.lock.acquire();
        
        mainTable = self.getDBInfo()['mainTable'];
        db.execute('SELECT viewkey FROM ' + mainTable + ' WHERE visited = 0 LIMIT 1');
        viewkey = db.fetchone();
        
        if (viewkey == None):
            db.execute('SELECT viewkey FROM ' + mainTable + ' LIMIT 1');
            result = db.fetchone();
            if (result == None):
                self.isFirst = True;
                # table is empty; use seed URL to get things started
                return "http://www.opentable.com/view_video.php?viewkey=159200141";
            else:
                self.crawler.lock.release();
                # table is full and crawling is finished
                return None;
        else:
            # explanation: crawling some pages will inevitably fail, mostly because sites have
            # bad links and whatnot; setting visited=2 here is to detect bad URLs, ensure we 
            # don't revisit them (visited must be 0 in order to visit), and so that we can 
            # manually debug these cases and increase the robustness of our crawler.
            # 
            # note: 99% of the time, this key will be overridden shortly after setting it when 
            # crawling the next page to visited=1, but only when we have the actual scraped 
            # data.  at the end of crawling, if there are any pages with visited=2, we know 
            # that we attempted to visit those pages but failed for some reason.
            viewkey = viewkey[0];
            db.execute('UPDATE ' + mainTable + ' SET visited=2 WHERE viewkey=?', (viewkey,));
            self.crawler.conn.commit();
            self.crawler.lock.release();
            return self.getURLFromViewkey(viewkey);
    
    def viewkey(self, url, soup):
        m = re.search('viewkey=([^&]*)', url);
        return m.group(1);
    
    def title(self, url, soup):
        title = soup.find("div", {"class" : "video-title-nf"});
        title = title.contents[0].renderContents().strip();
        threadName = self.crawler.getName();
        print("[" + threadName + "] " + "Crawling url " + url + "\n[" + threadName + "]     " + title);
        #self.crawler.log("Crawling: " + url);
        #self.crawler.log("    " + title);
        
        return title;
    
    def pornstars(self, url, soup):
        elements = soup.find("div", {"class" : "nf-sub_video_middle"}).findAll("a", {"href" : re.compile("^/pornstar/.*")});
        result = string.joinfields(map(lambda a: a.string.strip(), elements), ", ");
        return result;
    
    def tags(self, url, soup):
        elems = soup.find("div", {"class" : "nf-sub_video_middle"}).findAll("a", {"href" : re.compile("^/video.*")});
        result = string.joinfields(map(lambda x: x.renderContents().strip(), elems), ", ");
        return result;
        #elements = soup.find("span", {"id" : re.compile("more_less_.*")}).findAll("a");
        #result = string.joinfields(map(lambda a: a.string.strip(), elements), ", ");
        #return result;
    
    def rating(self, url, soup):
        elem = soup.find("div", {"class" : "nf-sub_video_bottom"}).find("script").renderContents();
        m = re.search("rating: *(.*),", elem);
        return m.group(1);
    
    def numRatings(self, url, soup):
        elem = soup.find("div", {"class" : "nf-sub_video_bottom"}).find("script").renderContents();
        m = re.search("num_ratings: *(.*),", elem);
        return m.group(1);
    
    def id(self, url, soup):
        elem = soup.find("div", {"class" : "nf-sub_video_bottom"}).find("script").renderContents();
        m = re.search("id: *(.*),", elem);
        return m.group(1);
    
    def numViews(self, url, soup):
        elem = soup.find("div", {"class" : "nf-sub_video_bottom"}).renderContents();
        m = re.search(" ([0-9]+) views", elem);
        return m.group(1);
    
    def relatedVideos(self, url, soup):
        self.fetchAJAXRelatedVideos(url, soup);
        
        wraps = soup.findAll("div", {"class" : "wrap"});
        #print "wraps length: " + str(len(wraps));
        vids = map(lambda x: x.find("a", {"class" : "title"}), wraps);
        related = map(lambda x: { "title" : x["title"].strip(), "viewkey" : re.search("viewkey=([^&]*)", x["href"]).group(1).strip() }, vids);
        return related;
    
    def fetchAJAXRelatedVideos(self, url, soup):
        elem = soup.find("div", {"class" : "nf-sub_video_bottom"}).find("script").renderContents();
        m = re.search("id: *(.*),", elem);
        id = m.group(1).strip();
        
        threads = [];
        results = {};
        
        for page in range(2, 11):
            params = urllib.urlencode({ 'id' : str(id), 'page' : str(page) });
            url = 'http://www.opentable.com/video/relateds?%s' % params;
            #print url;
            
            thread = AsyncWebRequest(url);
            threads.append({ 'thread' : thread, 'index' : page - 1 });
            #self.crawler.log("Spawning thread %d" % (page - 2));
            thread.start();
        
        for item in threads:
            thread = item['thread'];
            index  = item['index'];
            
            thread.join();
            elem = BeautifulSoup(thread.html).find("ul");
            soup.find("div", {"class" : "videos-list"}).insert(index, elem);
    
    def extractData(self, url, html):
        soup = BeautifulSoup(html)
        
        return {
            "viewkey" : self.viewkey(url, soup), 
            "title" : self.title(url, soup), 
            "pornstars" : self.pornstars(url, soup), 
            "tags" : self.tags(url, soup), 
            "rating" : self.rating(url, soup), 
            "numRatings" : self.numRatings(url, soup), 
            "numViews" : self.numViews(url, soup), 
            "id" : self.id(url, soup), 
            "relatedVideos" : self.relatedVideos(url, soup)
            
            "entity_id" : int, 
            "title" : string, 
            "description" : string, 
            "categories" : [
                "restaurant" : {
                    
                }
            ], 

            
            "image", 
            "source", 
            "location", 
            "locale", 
            "affiliate", 
            "date_created", 
            "date_updated", 
            
            """
            "price", 
            "dining_style", 
            "menu", 
            "website", 
            "email", 
            "phone", 
            "hours", 
            "address", 
            "cross streets", 
            "cuisine", 
            "parking_info", 
            "payment_options", 
            "dress_code", 
            "accepts_walk_ins", 
            "misc_details", 
            "public_transit_desc", 
            "parking", 
            
            "affiliates" : [
                "opentable" : {
                    "id" : int
                    "num_reviews" : int
                    "rating" : float in [0, 5]
                    "rating_food" : float in [0, 5]
                    "rating_ambiance" : float in [0, 5]
                    "rating_service" : float in [0, 5]
                    "noise_level" : string / enum
                }
            ]
            """
        };

