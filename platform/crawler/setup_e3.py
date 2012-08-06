#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import os, utils

from gevent.pool import Pool
from boto.s3.connection import S3Connection, Location
from boto.s3.key import Key
from boto.exception import S3ResponseError

AWS_ACCESS_KEY_ID = 'AKIAIXLZZZT4DMTKZBDQ'
AWS_SECRET_KEY = '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'

S3_BUCKET_PREFIX = AWS_ACCESS_KEY_ID.lower()
S3_BUCKET_DATA_PREFIX = S3_BUCKET_PREFIX + ".crawler"

def create_bucket(conn, name):
    bucket_name = "%s.%s" % (S3_BUCKET_DATA_PREFIX, name)
    
    try:
        conn.delete_bucket(bucket_name)
    except S3ResponseError:
        pass
    
    utils.log("creating bucket '%s'" % bucket_name)
    bucket = conn.create_bucket(bucket_name)
    utils.log("done creating bucket '%s'" % bucket_name)
    
    return bucket

def create_key(conn, bucket, name, filename):
    utils.log("bucket '%s' creating key '%s'" % (bucket.name, name))
    utils.log(filename)
    
    key = Key(bucket)
    key.key = name
    key.set_contents_from_filename(filename)
    
    utils.log("bucket '%s' done creating key '%s'" % (bucket.name, name))

#def main():
base = os.path.dirname(os.path.abspath(__file__))
epf_base = os.path.join(base, "sources/dumps/data/apple")

files = [
    "artist", 
    "collection", 
    "collection_type", 
    #"song", 
    "video", 
]

conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)

"""
bucket = create_bucket(conn, "apple")
pool = Pool(64)

utils.log("adding %d keys to bucket '%s'" % (len(files), bucket.name))
for name in files:
    filename = os.path.join(epf_base, name)
    
    zipped = filename + ".gz"
    if os.path.exists(zipped):
        filename = zipped
    
    pool.spawn(create_key, conn, bucket, name, filename)

pool.join()
utils.log("done adding %d keys to bucket '%s'" % (len(files), bucket.name))

if __name__ == '__main__':
    main()
"""

