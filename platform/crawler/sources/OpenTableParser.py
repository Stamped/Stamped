#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import re, string, urllib

from Schemas import Entity

__BASE_URL = "http://www.opentable.com/"

def parseEntity(entity):
    """Attempts to find and append OpenTable details to the given entity."""
    #utils.log("[OpenTable] parsing '%s'" % entity.title)
    
    def encodeTitle(title):
        toReplace = {
            "'" : "", 
            "+" : "and", 
            "&" : "and", 
            "@" : "at", 
            "(" : " ", 
            ")" : " ", 
            "/" : " ", 
            "-" : " ", 
            "..." : " ", 
            "." : " ", 
        }
        
        def __replaceAll(text, dic):
            for i, j in dic.iteritems():
                text = text.replace(i, j)
            
            return text
        
        title  = __replaceAll(title.strip().lower(), toReplace)
        words = title.split()
        
        return string.joinfields(words, '-').strip()
    
    title = entity.title
    nicktitle = entity.openTable['reserveURL']
    
    encodedTitle = encodeTitle(title)
    
    urls = [
        __BASE_URL + encodedTitle, 
        __BASE_URL + nicktitle, 
        __BASE_URL + 'reserve/' + nicktitle
    ]
    
    index = 0
    numOrigURLs = len(urls)
    
    while index < len(urls):
        try:
            url = urls[index]
            utils.log("[OpenTable] crawling " + url)
            soup = utils.getSoup(url)
            
            if index == numOrigURLs - 1:
                url = None
                topNav = soup.find("ul", {"id" : "TopNav_breadcrumbs"})
                
                if topNav is not None:
                    links = topNav.findAll("a")
                    
                    if links is not None and len(links) > 0:
                        relativeURL = links[-1].get("href")
                        url = __BASE_URL + relativeURL
                        urls.append(url)
            else:
                break
        except:
            #utils.printException()
            url = None
        
        index += 1
    
    if url is None:
        utils.log("[OpenTable] Error retrieving detailed page for '%s' => '%s' ('%s')" % \
                (title, encodedTitle, nicktitle))
        return None
    
    try:
        #elem = soup.find("h2", {"class" : "RestaurantProfileNameHeader2"})
        #if elem is not None:
        #    entity.title = elem.renderContents().strip()
        
        elem = soup.find("span", {"id" : re.compile("RestaurantProfile.*Description")})
        if elem is not None:
            entity.desc = elem.getText().strip()
        
        details = { }
        
        toParse = [
            'diningStyle', 
            'cuisine', 
            'neighborhood', 
            'crossStreet', 
            'price', 
            'site', 
            'email', 
            'phone', 
            'hoursOfOperation', 
            'payment', 
            'dressCode', 
            'acceptsWalkins', 
            'offers', 
            'publicTransit', 
            'parking', 
            'parkingDetails', 
            'privatePartyFacilities', 
            'privatePartyContact', 
            'entertainment', 
            'specialEvents', 
            'catering', 
        ]
        
        for item in toParse:
            title  = item[0:1].upper() + item[1:]
            itemID = re.compile("RestaurantProfile.*" + title)
            elem   = soup.find("span", {"id" : itemID})
            
            if elem is not None:
                raw = elem.getText()
                regex = re.compile(r'[^:]*:(.*)')
                details[item] = regex.sub(r'\1', raw).strip()
                #utils.log("'%s' => '%s'" % (item, details[item]))
        
        imageWrapper = soup.find("div", {"class" : "restaurantImageWrapper"})
        
        if imageWrapper is not None:
            imageWrapper = imageWrapper.find("img")
            
            if imageWrapper is not None:
                imageRelativeURL = imageWrapper.get("src")
                
                if imageRelativeURL is not None:
                    imageAbsoluteURL = __BASE_URL + imageRelativeURL
                    details['image'] = imageAbsoluteURL
        
        for k, v in details.iteritems():
            if k == 'price':
                k = 'priceScale'
            
            entity[k] = v
    except:
        utils.log("[OpenTable] Error crawling " + url)
        utils.printException()
    
    return entity

"""
from crawler.sources.dumps.OpenTableDump import OpenTableDump
dump = OpenTableDump()
entities = dump.getAll()
opentable = OpenTable()

for e1 in entities:
    e2 = opentable.parseEntity(e1['title'], e1['sources'][0]['reserveURL'])
    if e2 is None:
        print "ERROR: " + str(e1)
"""

