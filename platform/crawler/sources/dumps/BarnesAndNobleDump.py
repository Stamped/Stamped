#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import gevent, gzip, os, re, time

from crawler.sources.dumps.Netflix import NetflixClient
from crawler.AEntitySource import AExternalDumpEntitySource
from Schemas import Entity
from pprint import pprint

try:
    from lxml import etree
except ImportError:
    utils.log("warning: couldn't find lxml")

__all__ = [ "BarnesAndNobleDump" ]

class BarnesAndNobleDump(AExternalDumpEntitySource):
    """
        Barnes & Noble
    """
    
    TYPES = set([ 'restaurant' ])
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, 'Barnes & Noble', self.TYPES, 512)
    
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
        offset = 0
        count  = 0
        
        # loop through XML and parse each product element as a book Entity
        for event, elem in context:
            if event == "end" and elem.tag == "product" and elem.get('product_id') is not None:
                root.clear()
                
                if offset < Globals.options.offset:
                    offset += 1
                    continue
                
                if Globals.options.limit and count >= Globals.options.limit:
                    break
                
                try:
                    #assert 'books' == elem.find('.//primary').text.lower()
                    #assert 'USD' == elem.find('price').get('currency')
                    #assert float(elem.find('price').find('retail').text) >= 0.0
                    
                    entity = Entity()
                    entity.subcategory  = "book"
                    
                    entity.title        = elem.get('name')
                    entity.bid          = int(elem.get('product_id'))
                    entity.sku_number   = elem.get('sku_number')
                    entity.image        = elem.find('.//productImage').text
                    
                    entity.author       = elem.find('.//Author').text
                    entity.publisher    = elem.find('.//Publisher').text
                    entity.publish_date = elem.find('.//Publish_Date').text
                    isbn = elem.find('.//ISBN').text
                    
                    if isbn is None or len(isbn) <= 0:
                        continue
                    
                    entity.isbn         = isbn
                    
                    desc = elem.find('description')
                    is_english = 'nglish' in etree.tostring(desc)
                    
                    if not is_english:
                        continue
                    
                    #print etree.tostring(elem, pretty_print=True)
                    #self._globals['books'] = elem
                    #pprint(entity.value)
                    
                    self._output.put(entity)
                    count += 1
                    
                    # give the downstream consumer threads an occasional chance to work
                    if 0 == (count % 512):
                        time.sleep(0.1)
                    
                    parent = elem.getparent()
                    while True:
                        prev = elem.getprevious()
                        if prev is None:
                            break
                        parent.remove(prev)
                    
                    elem.clear()
                except Exception, e:
                    utils.printException()
                    #self._globals['books'] = elem
        
        Globals.options.offset -= offset
        if Globals.options.limit:
            Globals.options.limit = max(0, Globals.options.limit - count)
        
        f.close()
        return count

from crawler import EntitySources
EntitySources.registerSource('barnesandnoble', BarnesAndNobleDump)

