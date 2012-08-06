#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import argparse, math, os, pymongo, re, time

from gevent.pool    import Pool
from pymongo.errors import AutoReconnect
from pprint         import pprint
from BeautifulSoup  import BeautifulSoup

def __get_collection(db, ns):
    collection = db
    
    for component in ns.split('.'):
        collection = collection[component]
    
    return collection

def parse_work(title, genre, link, output):
    utils.log("parsing work %s) %s (%s)" % (title, genre, link))
    
    try:
        soup = utils.getSoup(link)
    except Exception, e:
        utils.log("error parsing work %s) %s (%s) - %s" % (title, genre, link, e))
        utils.printException()
    
    blockquotes = soup.findAll('blockquote')
    
    for blockquote in blockquotes:
        lines    = list(blockquote.findAll('a'))
        if not lines:
            # TODO: optionally take italicized setting / action descriptions
            continue
        
        lines       = map(lambda l: { 'ref' : l.get('name'), 'line' : l.getText() }, lines)
        generator   = blockquote.previousSiblingGenerator(); generator.next()
        speaker     = generator.next().getText().title()
        
        document = {
            'title'   : title, 
            'genre'   : genre, 
            'speaker' : speaker, 
            'lines'   : lines, 
        }
        
        output.append(document)

def process_shakespeare_works():
    """ 
        Downloads, parses, and returns a list of lines aggregated across all of 
        Shakespeare's plays, where each line is represented by a simple dict 
        format.
    """
    
    # initialize environment, download and parse shakespeare index page
    # -----------------------------------------------------------------
    
    pool    = Pool(16)
    seed    = "http://shakespeare.mit.edu"
    soup    = utils.getSoup(seed)
    output  = [ ]
    
    table   = soup.find('table', {'cellpadding' : '5'})
    rows    = table.findAll('tr')
    cols    = rows[1].findAll('td')
    genres  = map(lambda td: td.getText(), rows[0].findAll('td'))
    
    assert len(cols) == len(genres)
    assert len(rows) == 2
    
    # find and process each work's full text in parallel
    # --------------------------------------------------
    
    # note: we're only interested in plays so we're skipping the last genre, poetry
    for i in xrange(len(genres) - 1):
        genre = genres[i]
        col   = cols[i]
        works = col.findAll('a')
        
        for work in works:
            href  = work.get('href')
            href  = href.replace('index.html', 'full.html')
            link  = "%s/%s" % (seed, href)
            title = work.getText().replace('\n', ' ')
            
            if title and href:
                pool.spawn(parse_work, title, genre, link, output)
    
    pool.join()
    return output

def export_documents(coll, documents, drop = True, batch_size = 64):
    """
        Exports documents to mongo in batches.
    """
    
    num_docs    = len(documents)
    num_batches = int(math.ceil(num_docs / float(batch_size)))
    
    # drop the collection before beginning insertion
    if drop:
        coll.drop()
    
    utils.log("exporting %d documents... (%d batches of %d documents)" % 
              (num_docs, num_batches, batch_size))
    
    for i in xrange(num_batches):
        offset  = i * batch_size
        batch   = documents[offset : offset + batch_size]
        
        safe_insert(coll, batch)

def safe_insert(coll, documents, retries = 5, delay = 0.25):
    """
        Retry wrapper around a single mongo bulk insertion.
    """
    
    while True:
        try:
            return coll.insert(documents)
        except AutoReconnect as e:
            retries -= 1
            
            if retries <= 0:
                raise
            
            time.sleep(delay)
            delay *= 2

def export(*args):
    parser  = argparse.ArgumentParser(description="exports structured works of shakespeare to mongodb")
    
    parser.add_argument('-n', '--noshakespeare', action="store_true", default=False,
                        help=("disable exporting complete works of shakespeare"))
    parser.add_argument('-d', '--drop', action="store_true", default=False,
                        help="drop existing collections before performing any insertions")
    parser.add_argument('-H', '--mongo_host', type=str, default="localhost",
                        help=("hostname or IP address of mongo server (for output)"))
    parser.add_argument('-P', '--mongo_port', type=int, default=27017,
                        help=("port number of mongo server (for output)"))
    parser.add_argument('-o', '--output_namespace', type=str, default="test.lines",
                        help=("mongo db and collection namespace to store output to "
                              "in dot-notation (e.g., defaults to test.lines)"))
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    
    if args:
        args    = parser.parse_args(args = args)
    else:
        args    = parser.parse_args()
    
    conn        = pymongo.Connection(args.mongo_host, args.mongo_port)
    output      = None
    
    if not args.noshakespeare:
        output  = process_shakespeare_works()
    
    if output:
        coll    = __get_collection(conn, args.output_namespace)
        export_documents(coll, output, args.drop)

if __name__ == '__main__':
    export()

