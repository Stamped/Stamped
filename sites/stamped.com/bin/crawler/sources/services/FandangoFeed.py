#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import gevent, os, time, xlrd

from gevent.pool import Pool
from AEntitySource import AExternalDumpEntitySource
from api.Entity import Entity

__all__ = [ "FandangoFeed" ]

class FandangoFeed(AExternalDumpEntitySource):
    """
        Fandango RSS feed importer
    """
    
    NAME = "Fandango"
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, self.NAME, self.TYPES, 128)
    
    def getMaxNumEntities(self):
        return 100 # approximation for now
    
    def _run(self):
        
        pool = Pool(128)
        
        pool.join()
        self._output.put(StopIteration)
        utils.log("[%s] finished parsing %d entities" % (self.NAME, numEntities - 1))
    
    def _parseEntity(self, sheet, index, numEntities):
        if numEntities > 100 and ((index - 1) % (numEntities / 100)) == 0:
            utils.log("[%s] done parsing %s" % \
                (self, utils.getStatusStr(index - 1 - Globals.options.offset, numEntities)))
            time.sleep(0.1)
        
        row = sheet.row_values(index)
        
        entity = Entity()
        entity.subcategory = "movie"
        entity.title = row[1]
        
        entity.fandango = {
            # TODO
        }
        
        self._output.put(entity)

import EntitySources
EntitySources.registerSource('fandango', FandangoFeed)

