#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals, utils
import gevent, gzip, os, re, time

from Netflix import NetflixClient
from AEntitySource import AExternalDumpEntitySource
from Schemas import Entity
from pprint import pprint
from lxml import etree

__all__ = [ "BarnesAndNobleDump" ]

class BarnesAndNobleDump(AExternalDumpEntitySource):
    """
        Barnes & Noble
    """
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, 'Barnes & Noble', self.TYPES, None)
    
    def getMaxNumEntities(self):
        return 100000 # approximation for now
    
    def _run(self):
        utils.log("[%s] parsing book dump" % (self, ))
        
        prefix   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        filename = 'books.xml.gz'
        filepath = os.path.join(prefix, filename)
        
        count = self._parse_dump(filepath)
        
        self._output.put(StopIteration)
        utils.log("[%s] finished parsing %d books" % (self, count))
    
    def _parse_dump(self, filepath):
        f = gzip.open(filepath, 'rb')
        context = iter(etree.iterparse(f, events=("start", "end")))
        
        event, root = context.next()
        count = 0
        
        # loop through each XML catalog_title element and parse it as a book Entity
        for event, elem in context:
            if event == "end" and elem.tag == "product" and elem.get('product_id') is not None:
                root.clear()
                
                try:
                    assert 'books' == elem.find('.//primary').text.lower()
                    
                    entity = Entity()
                    entity.subcategory = "book"
                    
                    entity.title        = elem.get('name')
                    entity.bid          = int(elem.get('product_id'))
                    entity.sku_number   = elem.get('sku_number')
                    entity.image        = elem.find('.//productImage').text
                    
                    entity.author       = elem.find('.//Author').text
                    entity.isbn         = elem.find('.//ISBN').text
                    entity.publisher    = elem.find('.//Publisher').text
                    entity.publish_date = elem.find('.//Publish_Date').text
                    
                    #print etree.tostring(elem, pretty_print=True)
                    #self._globals['books'] = elem
                    pprint(entity.value)
                    
                    #self._output.put(entity)
                    count += 1
                    
                    # give the downstream consumer threads an occasional chance to work
                    if 0 == (count % 512):
                        time.sleep(0.1)
                    
                    elem.clear()
                except Exception, e:
                    utils.printException()
                    #self._globals['books'] = elem
        
        f.close()
        return count

import EntitySources
EntitySources.registerSource('barnesandnoble', BarnesAndNobleDump)

