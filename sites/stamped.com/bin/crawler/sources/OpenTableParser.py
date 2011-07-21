#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import re, string, urllib

from api.Entity import Entity

__BASE_URL = "http://www.opentable.com/"

def parseEntity(entity):
    """Attempts to find and append OpenTable details to the given entity."""
    #utils.log("[OpenTable] parsing '%s'" % entity.name)
    
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
        
        def __replaceAll(text, dic):
            for i, j in dic.iteritems():
                text = text.replace(i, j)
            
            return text
        
        name  = __replaceAll(name.strip().lower(), toReplace)
        words = name.split()
        
        return string.joinfields(words, '-').strip()
    
    name = entity.name
    nickname = entity.openTable['reserveURL']
    
    encodedName = encodeName(name)
    
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
            #utils.log("[OpenTable] crawling " + url)
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
                (name, encodedName, nickname))
        return None
    
    try:
        #elem = soup.find("h2", {"class" : "RestaurantProfileNameHeader2"})
        #if elem is not None:
        #    entity.name = elem.renderContents().strip()
        
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
        
        """
        imageWrapper = soup.find("div", {"class" : "restaurantImageWrapper"})
        
        if imageWrapper is not None:
            imageWrapper = imageWrapper.find("img")
            
            if imageWrapper is not None:
                imageRelativeURL = imageWrapper.get("src")
                
                if imageRelativeURL is not None:
                    imageAbsoluteURL = __BASE_URL + imageRelativeURL
                    imageData = utils.getFile(imageAbsoluteURL)
                    details['images'] = [ imageData ]
        """
        
        entity.add(details)
    except:
        utils.log("[OpenTable] Error crawling " + url)
        utils.printException()
    
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

