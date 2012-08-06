#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import feedparser, re

from datetime           import *
from api.Schemas            import *
from optparse           import OptionParser
from api.MongoStampedAPI    import MongoStampedAPI

stampedAPI = MongoStampedAPI()

def importFandango():

    feeds = [
        'http://www.fandango.com/rss/comingsoonmoviesmobile.rss?pid=5348839&a=12170', 
        'http://www.fandango.com/rss/openingthisweekmobile.rss?pid=5348839&a=12169', 
        'http://www.fandango.com/rss/top10boxofficemobile.rss?pid=5348839&a=12168', 
    ]

    for url in feeds:
        data = feedparser.parse(url)
        print '\n\n%s\n%s' % ('='*40, data['feed']['title'])
        
        id_re           = re.compile('.*\/([0-9]*)$')
        title_re        = re.compile('^([0-9][0-9]?). (.*) (\$[0-9.M]*)')
        url_title_re    = re.compile('[^a-zA-Z0-9:]')
        
        for entry in data.entries:
            if entry.title == 'More Movies':
                continue
            
            try:
                print 
                print '%s' % entry.title
                
                # Extract fandango id
                id_match = id_re.match(entry.id)
                assert id_match is not None
                fandango_id = id_match.groups()[0]

                # Extract title and parse url title                
                title = entry.title 
                url_title = None
                
                title_match = title_re.match(entry.title)
                if title_match is not None:
                    title_match_groups = title_match.groups()
                    title = title_match_groups[1]
                
                url_title = url_title_re.sub('', title).lower()
                
                # Extract release date from description
                release_date = None
                
                release_date_match = entry.summary[-23:].split('Release Date:')
                if len(release_date_match) == 2:
                    month, day, year = map(lambda x: int(x), release_date_match[-1].split('/'))
                    if month >= 1 and month <= 12 and day >= 1 and day <= 31 and year > 1800 and year < 2200:
                        release_date = datetime(year, month, day)
                
                # Results
                print '  TITLE:     %s' % title
                print '  ID:        %s_%s' % (fandango_id, url_title)
                print '  RELEASED:  %s' % release_date
                
                entity                      = Entity()
                entity.subcategory          = 'movie'
                entity.title                = title
                entity.release_date         = release_date
                entity.fandango_id          = fandango_id
                entity.fandango_url         = 'http://www.fandango.com/%s_%s/movieoverview' % (url_title, fandango_id)
                entity.fandango_source      = 'fandango'
                entity.fandango_timestamp   = datetime.utcnow()
                
                stampedAPI.mergeEntity(entity)

            except Exception as e:
                print 'ERROR: %s' % e

def parseCommandLine():
    usage   = "Usage: %prog [options] [sources]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-s", "--source", default=None, type="string", 
        dest="source",  help="Select source to import (e.g. fandango)")

    (options, args) = parser.parse_args()

    return options

def main():
    options = parseCommandLine()

    if options.source is None:
        return
    
    if options.source.lower() == 'fandango':
        importFandango()
    else:
        print 'Invalid source'

if __name__ == '__main__':
    main()

