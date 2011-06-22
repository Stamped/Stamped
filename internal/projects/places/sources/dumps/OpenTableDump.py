#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

# http://pypi.python.org/pypi/xlrd/0.7.1
import xlrd

from AEntityDataSource import AExternalDumpEntityDataSource
from Entity import Entity

from ThreadPool import ThreadPool
from threading import Lock

class OpenTableDump(AExternalDumpEntityDataSource):
    """OpenTable XLS dump importer"""
    
    # TODO: automate downloading latest dump file from OpenTable FTP server
    DUMP_FILE = "opentabledata.raw.xls"
    NAME = "OpenTable"
    
    def __init__(self):
        AExternalDumpEntityDataSource.__init__(self, self.NAME)
    
    def importAll(self, entityDB, limit=None):
        book  = xlrd.open_workbook(self.DUMP_FILE)
        sheet = book.sheet_by_index(0)
        
        numEntities = min(sheet.nrows, limit or sheet.nrows)
        entities = (self._parseEntity(sheet, i) for i in xrange(1, numEntities))
        
        return entities
        if not entityDB.addEntities(entities):
            return False
    
    def _parseEntity(self, sheet, index):
        row = sheet.row_values(index)
        
        return Entity({
            'name' : row[1], 
            'addr' : row[3] + ', ' + row[4] + ', ' + row[5] + ' ' + row[6], 
            'sources' : {
                self._id : {
                    'phone' : row[7], 
                    'rid' : int(row[8]), 
                    'reserveURL' : row[9], 
                    'countryID' : row[10], 
                    'metroName' : row[0], 
                    'neighborhoodName' : row[2], 
                }
            }
        })

dump = OpenTableDump()
entities = dump.importAll(None)
for e in entities:
    print str(e._data)

