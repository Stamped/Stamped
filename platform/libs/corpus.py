#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import os, re

from gevent.pool    import Pool
from pprint         import pprint
from BeautifulSoup  import BeautifulSoup

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
        
        lines       = map(lambda l: (l.get('name'), l.getText()), lines)
        generator   = blockquote.previousSiblingGenerator(); generator.next()
        speaker     = generator.next().getText().title()
        
        document = {
            'title'   : title, 
            'genre'   : genre, 
            'speaker' : speaker, 
            'lines'   : lines, 
        }
        
        output.append(document)
        pprint(document)

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

