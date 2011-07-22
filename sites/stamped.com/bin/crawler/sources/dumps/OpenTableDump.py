#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import gevent, xlrd
import sources.OpenTableParser as OpenTableParser

from gevent.pool import Pool
from api.AEntitySource import AExternalDumpEntitySource
from api.Entity import Entity

__all__ = [ "OpenTableDump" ]

class OpenTableDump(AExternalDumpEntitySource):
    """
        OpenTable XLS dump importer
    """
    
    # TODO: automate downloading latest dump file from the OpenTable FTP server
    DUMP_FILE_PREFIX      = "sources/dumps/data/"
    DUMP_FILE_NAME        = "opentabledata"
    DUMP_FILE_SUFFIX      = ".xls"
    DUMP_FILE = DUMP_FILE_PREFIX + DUMP_FILE_NAME + DUMP_FILE_SUFFIX
    
    NAME = "OpenTable"
    TYPES = set([ 'place', 'contact', 'restaurant' ])
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, self.NAME, self.TYPES, 128)
        
        self._dumpFile = self.DUMP_FILE
    
    def _run(self):
        book  = xlrd.open_workbook(self._dumpFile)
        sheet = book.sheet_by_index(0)
        
        if self.limit:
            # add one to limit to account for the first row containing header info
            numEntities = min(sheet.nrows, self.limit + 1)
        else:
            numEntities = sheet.nrows
        
        pool = Pool(128)
        for i in xrange(1, numEntities):
            pool.spawn(self._parseEntity, sheet, i, numEntities)
        
        pool.join()
        self._output.put(StopIteration)
        utils.log("[%s] finished parsing %d entities" % (self.NAME, numEntities - 1))
    
    def _parseEntity(self, sheet, index, numEntities):
        if numEntities > 100 and ((index - 1) % (numEntities / 100)) == 0:
            utils.log("[%s] dont parsing %s" % \
                (self.NAME, utils.getStatusStr(index - 1, numEntities)))
        
        row = sheet.row_values(index)
        
        entity = Entity()
        entity.category = "restaurant"
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
            OpenTableParser.parseEntity(entity)
        
        self._output.put(entity)

"""
dump = OpenTableDump()
entities = dump.importAll(None)
for e in entities:
    print str(e._data)
"""

import EntitySources
EntitySources.registerSource('opentable', OpenTableDump)

