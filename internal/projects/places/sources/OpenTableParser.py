#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import re, string, urllib, Utils
from Entity import Entity

__BASE_URL = "http://www.opentable.com/"

def parseEntity(entity):
    def encodeName(name):
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
        
        def replaceAll(text, dic):
            for i, j in dic.iteritems():
                text = text.replace(i, j)
            
            return text
        
        name  = __replaceAll(name.strip().lower(), toReplace)
        words = name.split()
        
        return string.joinfields(words, '-').strip()
    
    name = entity.name
    nickname = entity.openTable['reserveURL']
    
    encodedName = encodeName(name)
    entity = None
    
    urls = [
        __BASE_URL + encodedName, 
        __BASE_URL + nickname, 
        __BASE_URL + 'reserve/' + nickname
    ]
    
    index = 0
    numOrigURLs = len(urls)
    
    while index < len(urls):
        try:
            url = urls[index]
            Utils.log("[OpenTable] crawling " + url)
            soup = Utils.getSoup(url)
            
            if index == numOrigURLs - 1:
                url = None
                topNav = soup.find("ul", {"id" : "TopNav_breadcrumbs"})
                
                if topNav:
                    links = topNav.findAll("a")
                    
                    if links and len(links) > 0:
                        relativeURL = links[-1].get("href")
                        url = __BASE_URL + relativeURL
                        urls.append(url)
            else:
                break
        except:
            #Utils.printException()
            url = None
        
        index += 1
    
    if url is None:
        Utils.log("[OpenTable] Error retrieving detailed page for '%s' => '%s' ('%s')" % \
                (name, encodedName, nickname))
        return None
    
    try:
        entity = { }
        
        elem = soup.find("h2", {"class" : "RestaurantProfileNameHeader2"})
        if elem is None:
            return None
        
        #entity.name = elem.renderContents().strip()
        
        elem = soup.find("span", {"id" : re.compile("RestaurantProfile.*Description")})
        if elem is None:
            return None
        
        entity.desc = elem.renderContents().strip()
        
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
            'catering', 
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
                raw = elem.renderContents()
                regex = re.compile(r'[^:]*:(.*)')
                details[item] = regex.sub(r'\1', raw).strip()
        
        """
        imageWrapper = soup.find("div", {"class" : "restaurantImageWrapper"})
        
        if imageWrapper is not None:
            imageWrapper = imageWrapper.find("img")
            
            if imageWrapper is not None:
                imageRelativeURL = imageWrapper.get("src")
                
                if imageRelativeURL is not None:
                    imageAbsoluteURL = __BASE_URL + imageRelativeURL
                    imageData = Utils.getFile(imageAbsoluteURL)
                    details['images'] = [ imageData ]
        """
        
        entity.add(details)
    except:
        Utils.log("[OpenTable] Error crawling " + url)
        #Utils.printException()
    
    return entity

"""
from dumps.OpenTableDump import OpenTableDump
dump = OpenTableDump()
entities = dump.getAll()
opentable = OpenTable()

for e1 in entities:
    e2 = opentable.parseEntity(e1['name'], e1['sources'][0]['reserveURL'])
    if e2 is None:
        print "ERROR: " + str(e1)
"""

