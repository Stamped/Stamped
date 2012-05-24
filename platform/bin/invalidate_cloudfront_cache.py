#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import datetime, os, sys, urllib2, utils
import keys.aws

from boto.cloudfront import CloudFrontConnection

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    args = parser.parse_args()
    
    files = [ '/assets/css/screen.css', '/assets/css/styles.css' ]
    
    conn = CloudFrontConnection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
    
    # NOTE: this cloudfront distribution id is hardcoded to the static.stamped.com distro
    distribution_id = 'E17S1XTPOFC1EQ'
    print conn.create_invalidation_request(distribution_id, files)

