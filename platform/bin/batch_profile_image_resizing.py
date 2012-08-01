#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import keys.aws, logs, utils, time

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
    screenNames = stampedAPI._userDB._getAllScreenNames()
    sizes = [24, 48, 60, 96, 144]

    for screenName in screenNames:

        # Check if image exists
        key = '/users/%s.jpg' % screenName
        if not _checkImageOnS3(bucket, key):
            logs.info("No user image exists: %s" % screenName)
            continue

        # Check what images need to be resized
        newSizes = set()
        for size in sizes:
            key = '/users/%s-%sx%s.jpg' % (screenName, size, size)
            if not _checkImageOnS3(bucket, key):
                newSizes.add(size)

        if len(newSizes) == 0:
            logs.info("No need to resize: %s" % screenName)
            continue

        # Get current full-size image
        key = '/users/%s.jpg' % screenName
        imgData = _getImageFromS3(bucket, key)
        io = StringIO(imgData)
        img = Image.open(io)

        for size in newSizes:
            resized = img.resize((size, size), Image.ANTIALIAS)
            out = StringIO()
            resized.save(out, 'jpeg', optimize=True, quality=90)
            key = '/users/%s-%sx%s.jpg' % (screenName, size, size)
            _addImageToS3(bucket, key, out)
            logs.info("Added image: /users/%s-%sx%s.jpg" % (screenName, size, size))


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


def _getImageFromS3(bucket, name):
    num_retries = 0
    max_retries = 5

    while True:
        try:
            key = Key(bucket, name)
            data = key.get_contents_as_string()
            key.close()
            return data

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

        finally:
            try:
                if not key.closed:
                    key.close()
            except Exception:
                logs.warning("Error closing key")


def _addImageToS3(bucket, name, data):
    num_retries = 0
    max_retries = 5

    while True:
        try:
            key = Key(bucket, name)
            key.set_metadata('Content-Type', 'image/jpeg')
            key.set_contents_from_string(data.getvalue(), policy='public-read')
            key.close()
            return key

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

        finally:
            try:
                if not key.closed:
                    key.close()
            except Exception:
                logs.warning("Error closing key")

if __name__ == '__main__':
    main()
