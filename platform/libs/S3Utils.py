#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import gzip, keys.aws, logs, threading, time, utils

from boto.s3.connection import S3Connection
from boto.s3.key        import Key

class S3Utils(object):
    
    def __init__(self, bucket_name='stamped.com.static.images', temp_gzip_prefix=None):
        # find or create bucket
        # ---------------------
        conn = S3Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
        rs   = conn.get_all_buckets()
        rs   = filter(lambda b: b.name == bucket_name, rs)
        
        if 1 == len(rs):
            self.bucket = rs[0]
        else:
            self.bucket = conn.create_bucket(bucket_name)
        
        self.bucket_name = bucket_name
        self.temp_gzip_prefix = temp_gzip_prefix
    
    def add_key(self, name, value, content_type=None, apply_gzip=False, headers=None):
        assert isinstance(value, basestring)
        
        if apply_gzip:
            if self.temp_gzip_prefix is not None:
                temp_gzip_prefix = self.temp_gzip_prefix
            else:
                temp_gzip_prefix = threading.currentThread().getName()
            
            # TODO: why does zlib compression not work?
            #value = zlib.compress(value, 6)
            temp  = '.temp.%s.gz' % temp_gzip_prefix
            tries = 0
            
            while True:
                try:
                    f = gzip.open(temp, 'wb')
                    f.write(value)
                    f.close()
                    f = open(temp, 'rb')
                    value = f.read()
                    f.close()
                    break
                except:
                    tries += 1
                    
                    if tries >= 5:
                        raise
        
        key = Key(self.bucket, name)
        
        meta = { }
        if content_type is not None:
            meta['Content-Type'] = content_type
        
        if apply_gzip:
            meta['Content-Encoding'] = 'gzip'
        
        if headers is not None:
            for k, v in headers.iteritems():
                meta[k] = v
        
        if len(meta) > 0:
            key.update_metadata(meta)
        
        retries = 5
        
        while True:
            try:
                # note that the order of setting the key's metadata, contents, and 
                # ACL is important for some seriously stupid boto reason...
                key.set_contents_from_string(value)
                key.set_acl('public-read')
                key.close()
                break
            except Exception:
                retries -= 1
                
                if retries < 0:
                    raise
                
                time.sleep(0.1)

