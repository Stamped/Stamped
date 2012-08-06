#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals, utils
import keys.aws, time

from gevent.pool        import Pool
from optparse           import OptionParser

from boto.s3.connection import S3Connection
from boto.s3.key        import Key

#-----------------------------------------------------------

def parseCommandLine():
    usage   = "Usage: %prog [options] [sources]"
    version = "%prog " + __version__
    parser  = OptionParser(usage=usage, version=version)
    
    parser.add_option("-v", "--verbose", default=False, action="store_true", 
        help="yell at you a lot")
    
    return parser.parse_args()

def main():
    options, args = parseCommandLine()
    
    bucket_name = 'stamped.com.static.images'
    conn = S3Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
    rs = conn.get_all_buckets()
    rs = filter(lambda b: b.name == bucket_name, rs)
    
    if 1 != len(rs):
        utils.log("error finding bucket to warm cache with")
        return
    
    pool   = Pool(64)
    count  = 0
    
    bucket = rs[0]
    result = list(bucket.list(prefix='search/v2/'))
    utils.log("warming %d keys" % len(reslt))
    
    for key in result:
        pool.spawn(_warm, key, options)
        
        count += 1
        if 0 == (count % 100):
            utils.log("warmed %d keys" % count)
    
    pool.join()

def _warm(key, options):
    url = "http://static.stamped.com/%s" % key.name
    if options.verbose:
        utils.log("warming '%s' (%s)" % (key.name, url))
    
    try:
        utils.getFile(url)
    except:
        if options.verbose:
            utils.log("unable to download key '%s' (%s)" % (key.name, url))

if __name__ == '__main__':
    main()

