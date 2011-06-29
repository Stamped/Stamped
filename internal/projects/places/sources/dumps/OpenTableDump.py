#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, Utils
import gevent, xlrd
import sources.OpenTableParser as OpenTableParser

from gevent.pool import Pool
from AEntitySource import AExternalDumpEntitySource
from Entity import Entity

class OpenTableDump(AExternalDumpEntitySource):
    """
        OpenTable XLS dump importer
    """
    
    # TODO: automate downloading latest dump file from the OpenTable FTP server
    DUMP_FILE = "sources/dumps/data/opentabledata.raw.xls"
    NAME = "OpenTable"
    TYPES = set([ 'place', 'contact', 'restaurant' ])
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, self.NAME, self.TYPES)
    
    def _run(self):
        book  = xlrd.open_workbook(self.DUMP_FILE)
        sheet = book.sheet_by_index(0)
        
        if self.limit:
            # add one to limit to account for the first row containing header info
            numEntities = min(sheet.nrows, self.limit + 1)
        else:
            numEntities = sheet.nrows
        
        pool = Pool(256)
        for i in xrange(1, numEntities):
            pool.spawn(self._parseEntity, sheet, i)
        
        pool.join()
        self._output.put(StopIteration)
    
    def _parseEntity(self, sheet, index):
        row = sheet.row_values(index)
        
        entity = Entity()
        entity.name = row[1]
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

