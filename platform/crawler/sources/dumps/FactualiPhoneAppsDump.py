#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from crawler.sources.dumps import CSVUtils
import os, time

from gevent.pool import Pool
from crawler.AEntitySource import AExternalDumpEntitySource
from Schemas import Entity

__all__ = [ "FactualiPhoneAppsDump" ]

class FactualiPhoneAppsDump(AExternalDumpEntitySource):
    """
        Factual iPhoneApps data importer
    """
    
    DUMP_FILE_PREFIX      = os.path.dirname(os.path.abspath(__file__)) + "/data/factual/"
    DUMP_FILE_NAME        = "iPhone_Apps"
    DUMP_FILE_SUFFIX      = ".csv"
    DUMP_FILE_TEST_SUFFIX = ".test"
    DUMP_FILE = DUMP_FILE_PREFIX + DUMP_FILE_NAME + DUMP_FILE_SUFFIX
    DUMP_FILE_TEST = DUMP_FILE_PREFIX + DUMP_FILE_NAME + DUMP_FILE_TEST_SUFFIX + DUMP_FILE_SUFFIX
    
    NAME = "Factual iPhone Apps"
    TYPES = set([ 'app' ])
    
    _map = {
        'Name' : 'title', 
        'Developer' : 'developer', 
        'Developer_URL' : 'developerURL', 
        'Developer_support_URL' : 'developerSupportURL', 
        'Publisher' : 'publisher', 
        'Release_Date' : 'releaseDate', 
        'Price' : 'price', 
        'Category' : 'appCategory', 
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
        
        if Globals.options.test:
            self._dumpFile = self.DUMP_FILE_TEST
        else:
            self._dumpFile = self.DUMP_FILE
    
    def getMaxNumEntities(self):
        csvFile  = open(self._dumpFile, 'rb')
        numLines = max(0, utils.getNumLines(csvFile) - 1)
        csvFile.close()
        
        return numLines
    
    def _run(self):
        csvFile  = open(self._dumpFile, 'rb')
        numLines = max(0, utils.getNumLines(csvFile) - 1)
        if Globals.options.limit: numLines = max(0, min(Globals.options.limit, numLines - Globals.options.offset))
        
        utils.log("[%s] parsing %d entities from '%s'" % \
            (self.NAME, numLines, self.DUMP_FILE_NAME))
        
        reader = CSVUtils.UnicodeReader(csvFile)
        pool   = Pool(512)
        count  = 0
        offset = 0
        
        for row in reader:
            if offset < Globals.options.offset:
                offset += 1
                continue
            
            if Globals.options.limit and count >= Globals.options.limit:
                break
            
            pool.spawn(self._parseEntity, row, count)
            count += 1
            
            if numLines > 100 and (count % (numLines / 100)) == 0:
                utils.log("[%s] done parsing %s" % \
                    (self.NAME, utils.getStatusStr(count, numLines)))
                time.sleep(0.1)
        
        Globals.options.offset = 0
        if Globals.options.limit:
            Globals.options.limit = max(0, Globals.options.limit - count)
        
        pool.join()
        self._output.put(StopIteration)
        csvFile.close()
        
        utils.log("[%s] finished parsing %d entities" % (self.NAME, count))
    
    def _parseEntity(self, row, count):
        #utils.log("[%s] parsing entity %d" % (self.NAME, count))
        
        entity = Entity()
        entity.subcategory = "app"
        
        entity.factual = {
            'table' : 'iPhone_Apps.csv'
        }
        
        for srcKey, destKey in self._map.iteritems():
            if srcKey in row and row[srcKey] and len(row[srcKey]) > 0:
                entity[destKey] = row[srcKey]
        
        self._output.put(entity)

from crawler import EntitySources
EntitySources.registerSource('factualiPhoneApps', FactualiPhoneAppsDump)

