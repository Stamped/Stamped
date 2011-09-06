#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import init
import utils

from libs.AmazonAPI         import AmazonAPI
from match.EntityMatcher    import EntityMatcher
from MongoStampedAPI        import MongoStampedAPI
from difflib                import SequenceMatcher
from optparse               import OptionParser
from pprint                 import pprint

def parseCommandLine():
    usage   = "Usage: %prog [options] query"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-d", "--db", default=None, type="string", 
        action="store", dest="db", help="db to connect to")
    
    parser.add_option("-n", "--noop", default=False, action="store_true", 
        help="run in noop mode without modifying anything")
    
    parser.add_option("-v", "--verbose", default=False, action="store_true", 
        help="enable verbose logging")
    
    (options, args) = parser.parse_args()
    
    if options.db:
        utils.init_db_config(options.db)
    
    return (options, args)

def strip_title(title):
    delimiters = [ ':', '(', ';' ]
    
    for delimiter in delimiters:
        l = title.find(delimiter)
        if l > 0: title = title[:l]
    
    return title.strip().lower()

def main():
    options, args = parseCommandLine()
    
    amazonAPI  = AmazonAPI()
    stampedAPI = MongoStampedAPI()
    matcher    = EntityMatcher(stampedAPI, options)
    entityDB   = stampedAPI._entityDB
    
    rs = entityDB._collection.find({"subcategory" : "book"})
    is_junk = " \t-,:'()".__contains__
    
    num_processed = 0
    num_converted = 0
    num_failed    = 0
    
    for result in rs:
        entity = entityDB._convertFromMongo(result)
        orig_title = entity.title
        num_processed += 1
        
        if 'asin' in entity:
            params = dict(
                transform=True, 
                SearchIndex='Books', 
                ItemId=entity.asin, ResponseGroup='Large', 
            )
            
            amazon_results = amazonAPI.item_lookup(**params)
        else:
            for i in xrange(0, 2):
                if i != 0:
                    orig_title = strip_title(entity.title)
                
                params = dict(
                    transform=True, 
                    SearchIndex='Books', 
                    Title=orig_title, 
                )
                
                if 'author' in entity:
                    author = entity.author
                    if ',' in author:
                        author = author.split(',')[0]
                    
                    params['Author'] = author
                
                amazon_results = amazonAPI.item_detail_search(**params)
                
                if len(amazon_results) > 0:
                    break
        
        success = False
        orig_titlel = strip_title(orig_title)
        
        # inspect amazon lookup results
        for amazon_result in amazon_results:
            amazon_titlel = amazon_result.title.lower()
            
            for i in xrange(0, 2):
                if i != 0:
                    amazon_titlel = strip_title(amazon_titlel)
                
                if len(amazon_titlel) > len(orig_titlel):
                    success |= amazon_titlel.startswith(orig_titlel) or amazon_titlel.endswith(orig_titlel)
                else:
                    success |= orig_titlel.startswith(amazon_titlel) or orig_titlel.endswith(amazon_titlel)
                
                if not success:
                    ratio = SequenceMatcher(is_junk, orig_titlel, amazon_titlel).ratio()
                    
                    if ratio >= 0.75:
                        success |= True
                
                if success:
                    break
            
            if success:
                break
            else:
                utils.log("%s vs %s" % (orig_title, amazon_result.title))
                utils.log("%s vs %s" % (orig_titlel, amazon_titlel))
        
        if success:
            entity = matcher.mergeDuplicates(entity, [ amazon_result ])
            utils.log("Success: %s vs %s" % (orig_title, entity.title))
            num_converted += 1
        else:
            utils.log("Failure: %s" % entity.title)
            pprint(params)
            pprint(entity.value)
            utils.log(len(amazon_results))
            num_failed += 1
    
    print "num processed: %d" % num_processed
    print "num converted: %d" % num_converted
    print "num failed:    %d" % num_failed

if __name__ == '__main__':
    main()

