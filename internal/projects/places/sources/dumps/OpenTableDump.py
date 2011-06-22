#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

# http://pypi.python.org/pypi/xlrd/0.7.1
import xlrd

from AEntityDataSource import AExternalDumpEntityDataSource
from Entity import Entity
import OpenTableParser

from ThreadPool import ThreadPool
from threading import Lock

class OpenTableDump(AExternalDumpEntityDataSource):
    """
        OpenTable XLS dump importer
    """
    
    # TODO: automate downloading latest dump file from the OpenTable FTP server
    DUMP_FILE = "opentabledata.raw.xls"
    NAME = "OpenTable"
    
    def __init__(self):
        AExternalDumpEntityDataSource.__init__(self, self.NAME)
    
    def getAll(self, limit=None):
        book  = xlrd.open_workbook(self.DUMP_FILE)
        sheet = book.sheet_by_index(0)
        
        numEntities = min(sheet.nrows, limit or sheet.nrows)
        entities = (self._parseEntity(sheet, i) for i in xrange(1, numEntities))
        
        return entities
    
    def _parseEntity(self, sheet, index):
        row = sheet.row_values(index)
        
        entity = Entity()
        entity.name = self._decode(row[1])
        entity.addr = self._decode(row[3]) + ', ' + 
                      self._decode(row[4]) + ', ' + 
                      self._decode(row[5]) + ' ' + 
                      self._decode(row[6])
        
        entity.openTable = {
            'id' : int(row[8]), 
            'reserveURL' : self._decode(row[9]), 
            'countryID' : self._decode(row[10]), 
            'metroName' : self._decode(row[0]), 
            'neighborhoodName' : self._decode(row[2]), 
        }
        
        OpenTableParser.parseEntity(entity)
        return entity
    
    def _removeNonAscii(self, s):
        return "".join(ch for ch in s if ord(ch) < 128)
    
    def _decode(self, s):
        if isinstance(s, unicode):
            return self._removeNonAscii(s.encode("utf-8"))
        else:
            return s

"""
dump = OpenTableDump()
entities = dump.importAll(None)
for e in entities:
    print str(e._data)
"""

