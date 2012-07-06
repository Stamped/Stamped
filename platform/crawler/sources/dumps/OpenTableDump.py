#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import gevent, os, time, xlrd
from crawler.sources import OpenTableParser as OpenTableParser

from gevent.pool import Pool
from crawler.AEntitySource import AExternalDumpEntitySource
from Schemas import Entity

__all__ = [ "OpenTableDump" ]

class OpenTableDump(AExternalDumpEntitySource):
    """
        OpenTable XLS dump importer
    """
    
    # TODO: automate downloading latest dump file from the OpenTable FTP server
    DUMP_FILE_PREFIX      = os.path.dirname(os.path.abspath(__file__)) + "/data/"
    DUMP_FILE_NAME        = "opentabledata"
    DUMP_FILE_SUFFIX      = ".xls"
    DUMP_FILE = DUMP_FILE_PREFIX + DUMP_FILE_NAME + DUMP_FILE_SUFFIX
    
    NAME = "OpenTable"
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, self.NAME, self.TYPES, 128)
        
        self._dumpFile = self.DUMP_FILE
    
    def getMaxNumEntities(self):
        book  = xlrd.open_workbook(self._dumpFile)
        sheet = book.sheet_by_index(0)
        return max(0, sheet.nrows - 1)
    
    def _run(self):
        book  = xlrd.open_workbook(self._dumpFile)
        sheet = book.sheet_by_index(0)
        
        if Globals.options.limit:
            # add one to limit to account for the first row containing header info
            numEntities = max(0, min(sheet.nrows - Globals.options.offset, Globals.options.limit + 1))
        else:
            numEntities = max(0, sheet.nrows - Globals.options.offset)
        
        utils.log("[%s] parsing %d entities" % (self, numEntities - 1))
        
        pool = Pool(128)
        for i in xrange(1, numEntities):
            pool.spawn(self._parseEntity, sheet, Globals.options.offset + i, numEntities)
        
        Globals.options.offset = 0
        if Globals.options.limit:
            Globals.options.limit = max(0, Globals.options.limit - numEntities + 1)
        
        pool.join()
        self._output.put(StopIteration)
        utils.log("[%s] finished parsing %d entities" % (self, numEntities - 1))
    
    def _parseEntity(self, sheet, index, numEntities):
        if numEntities > 100 and ((index - 1) % (numEntities / 100)) == 0:
            utils.log("[%s] done parsing %s" % \
                (self.NAME, utils.getStatusStr(index - 1 - Globals.options.offset, numEntities)))
            time.sleep(0.1)
        
        row = sheet.row_values(index)
        
        entity = Entity()
        entity.subcategory = "restaurant"
        entity.title = row[1]
        entity.address = row[3] + ', ' + \
                         row[4] + ', ' + \
                         row[5] + ' ' + \
                         row[6]
        
        entity.openTable = {
            'rid' : int(row[8]), 
            'reserveURL' : row[9], 
            'countryID' : row[10], 
            'metroName' : row[0], 
            'neighborhoodName' : row[2], 
        }
        
        # don't make external calls to opentable in test mode
        if not Globals.options.test:
            result = OpenTableParser.parseEntity(entity)
            if result is None:
                return
        
        if entity is not None:
            #print entity.title
            #from pprint import pprint
            #pprint(entity.getDataAsDict())
            self._output.put(entity)

from crawler import EntitySources
EntitySources.registerSource('opentable', OpenTableDump)

