#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, CSVUtils, Utils
import gevent

from gevent.pool import Pool
from AEntitySource import AExternalDumpEntitySource
from Entity import Entity

class FactualiPhoneAppsDump(AExternalDumpEntitySource):
    """
        Factual iPhoneApps data importer
    """
    
    DUMP_FILE_PREFIX = "sources/dumps/data/factual/"
    DUMP_FILE_NAME   = "iPhone_Apps"
    DUMP_FILE_SUFFIX = ".csv"
    DUMP_FILE = DUMP_FILE_PREFIX + DUMP_FILE_NAME + DUMP_FILE_SUFFIX
    
    NAME = "Factual iPhone Apps"
    TYPES = set([ 'iPhoneApp' ])
    
    _map = {
        'Name' : 'name', 
        'Developer' : 'developer', 
        'Developer_URL' : 'developerURL', 
        'Developer_support_URL' : 'developerSupportURL', 
        'Publisher' : 'publisher', 
        'Release_Date' : 'releaseDate', 
        'Price' : 'price', 
        'Category' : 'category', 
        'Language' : 'language', 
        'Rating' : 'rating', 
        'Popularity' : 'popularity', 
        'Parental_Rating' : 'parentalRating', 
        'Platform' : 'platform', 
        'Requirements' : 'requirements', 
        'Size' : 'size', 
        'Version' : 'version', 
        'Download_URL' : 'downloadURL', 
        'Thumbnail_URL' : 'thumbnailURL', 
        'Screenshot_URL' : 'screenshotURL', 
        'Video_URL' : 'videoURL', 
    }
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, self.NAME, self.TYPES, 512)
    
    def _run(self):
        csvFile  = open(self.DUMP_FILE, 'rb')
        numLines = max(1, CSVUtils.getNumLines(csvFile) - 1)
        if self.limit: numLines = min(self.limit, numLines)
        
        Utils.log("[%s] parsing %d entities from '%s'" % \
            (self.NAME, numLines, self.DUMP_FILE_NAME))
        
        reader = CSVUtils.UnicodeReader(csvFile)
        pool   = Pool(512)
        count  = 0
        
        for row in reader:
            if self.limit and count >= self.limit:
                break
            
            pool.spawn(self._parseEntity, row, count)
            count += 1
            
            if numLines > 100 and (count % (numLines / 100)) == 0:
                Utils.log("[%s] done parsing %s" % \
                    (self.NAME, Utils.getStatusStr(count, numLines)))
        
        pool.join()
        self._output.put(StopIteration)
        csvFile.close()
        
        Utils.log("[%s] finished parsing %d entities" % (self.NAME, count))
    
    def _parseEntity(self, row, count):
        #Utils.log("[%s] parsing entity %d" % (self.NAME, count))
        
        entity = Entity()
        entity.factual = {
            'table' : 'iPhone_Apps.csv'
        }
        
        for srcKey, destKey in self._map.iteritems():
            if srcKey in row and row[srcKey] and len(row[srcKey]) > 0:
                entity[destKey] = row[srcKey]
        
        self._output.put(entity)

import EntitySources
EntitySources.registerSource('factualiPhoneApps', FactualiPhoneAppsDump)

