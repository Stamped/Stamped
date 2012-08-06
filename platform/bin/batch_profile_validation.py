#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import keys.aws, logs, utils, time
import datetime

try:
    import Image, ImageFile
    from StringIO import StringIO
    from errors   import *
    from api.MongoStampedAPI import globalMongoStampedAPI
    
    from boto.cloudfront    import CloudFrontConnection
    from boto.s3.connection import S3Connection
    from boto.s3.key        import Key
except:
    utils.printException()
    pass


def main():
    conn = S3Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
    bucketName = 'stamped.com.static.images'
    bucket = conn.lookup(bucketName)
    
    stampedAPI  = globalMongoStampedAPI()
    
    users = stampedAPI._userDB._collection.find({'timestamp.image_cache': {'$exists': True}})
    
    failed = set()
    
    for user in users:
        screenName = user['screen_name_lower']
        
        # Check if image exists
        key = '/users/%s.jpg' % screenName
        if not _checkImageOnS3(bucket, key):
            if user['timestamp']['image_cache'] < datetime.datetime.utcnow() - datetime.timedelta(hours=1):
                logs.info("No user image exists: %s" % screenName)
                failed.add(user['_id'])
                stampedAPI._userDB._collection.update({'_id': user['_id']}, {'$unset': {'timestamp.image_cache': 1}})
    
    print "%s missing photos" % len(failed)
    print failed


def _checkImageOnS3(bucket, name):
    num_retries = 0
    max_retries = 5
    
    while True:
        try:
            if bucket.get_key(name) is not None:
                return True
            return False

        except Exception as e:
            logs.warning('S3 Exception: %s' % e)
            num_retries += 1
            if num_retries > max_retries:
                msg = "Unable to connect to S3 after %d retries (%s)" % \
                    (max_retries, self.__class__.__name__)
                logs.warning(msg)
                raise Exception(msg)
            
            logs.info("Retrying (%s)" % (num_retries))
            time.sleep(0.5)


