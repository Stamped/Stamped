#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import keys.aws, logs, utils
import os, time, zlib, struct, array, random, urllib2

from gevent.pool import Pool

try:
    import PIL, Image, ImageFile
except:
    utils.printException()
    pass

from api.AImageDB       import AImageDB
from StringIO           import StringIO
from errors             import *
from api.Schemas        import ImageSizeSchema

from boto.cloudfront    import CloudFrontConnection
from boto.s3.connection import S3Connection
from boto.s3.key        import Key

from libs.ec2_utils     import is_prod_stack

class S3ImageDB(AImageDB):
    
    def __init__(self, bucket_name='stamped.com.static.images'):
        # find or create bucket
        # ---------------------
        conn = S3Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)

        self.bucket = conn.lookup(bucket_name)

        if not self.bucket:
            self.bucket = conn.create_bucket(bucket_name)
        
        self.bucket_name = bucket_name

        self.base_url = 'http://static.stamped.com'
    
    @property
    def profileImageMaxSize(self):
        return (500, 500)
    
    @property
    def profileImageSizes(self):
        # NOTE (travis 5/3/12):  the specifics of where these images are 
        # referenced throughout the stamped platform are deprecated, but 
        # the available image sizes that we will continue to support has 
        # not changed.

        sizes = [24, 48, 60, 96, 144]
        result = {}
        for size in sizes:
            result['%sx%s' % (size, size)] = (size, size)

        return result
        
        ### DEPRECATED
        return {
            # shown in user's profile
            '144x144': (144, 144), # 2x
            '72x72': (72, 72),  # 1x
            
            # shown in sDetail, sCreate, people tab (me)
            '110x110': (110, 110), # 2x
            '55x55': (55, 55),  # 1x
            
            # shown in sDetail (also stamped by), eDetail (stamped by)
            '92x92': (92, 92),  # 2x
            '46x46': (46, 46),  # 1x
            
            # shown in inbox, activity (credit), people (list)
            '74x74': (74, 74),  # 2x
            '37x37': (37, 37),  # 1x
            
            # shown in activity, sDetail (comments)
            '62x62': (62, 62),  # 2x
            '31x31': (31, 31),  # 1x
        }
    
    def addResizedProfileImages(self, screen_name, image_url):
        # Filename is lowercase screen name
        prefix = 'users/%s' % screen_name.lower()

        # Retry getting web image multiple times in case of bad connection
        num_retries = 0
        max_retries = 5

        while True:
            try:
                image = utils.getWebImage(image_url, "profile")
                break
            except urllib2.HTTPError as e:
                logs.warning('Get web image exception: %s' % e)
                num_retries += 1
                if num_retries > max_retries:
                    msg = "Unable to connect to get web image after %d retries (%s)" % (max_retries, image_url)
                    logs.warning(msg)
                    raise 
                
                logs.info("Retrying (%s)" % (num_retries))
                time.sleep(30)

        if image.format not in ('JPEG', 'PNG'):
            logs.warning("Cannot add a profile image of format '%s', only JPEG or PNG")
            return

        sizes    = self.profileImageSizes
        max_size = self.profileImageMaxSize

        def cropImageToSquare(image):
            width, height = image.size

            if width != height:
                # Extract a square aspect ratio image by cropping the longer side
                diff = abs(height - width) / 2

                if width > height:
                    box = (diff, 0, width - diff, height)
                else:
                    box = (0, diff, width, height - diff)

                square = image.crop(box)
            else:
                # image is already square
                square = image
            return square


        image = cropImageToSquare(image)
        self._addImageSizes(prefix, image, max_size, sizes, original_url=image_url)
    
    def removeProfileImage(self, screen_name):
        if not is_prod_stack():
            return

        # Filename is lowercase screen name
        prefix = 'users/%s' % screen_name.lower()
        suffix = '.jpg'
        
        sizes = self.profileImageSizes

        try:
            self._removeFromS3('%s%s' % (prefix, suffix))
            
            for size in sizes:
                self._removeFromS3('%s-%s%s' % (prefix, size, suffix))
        except Exception:
            logs.warning('Warning: Failed to remove file')
    
    def addEntityImage(self, entityId, image):
        assert isinstance(image, Image.Image)

        if image.format not in ('JPEG', 'PNG'):
            logs.warning("Cannot add a entity image of format '%s', only JPEG or PNG" % image.format)
            return
        
        prefix   = 'entities/%s' % entityId
        max_size = (960, 960)
        
        sizes = {
            'ios1x': (196, 288),
            'ios2x': (96, 144),
        }
        
        # Add images in all sizes
        self._addImageSizes(prefix, image, max_size, sizes)
    
    def addStampImage(self, stampId, image):
        assert isinstance(image, Image.Image)
        
        prefix   = 'stamps/%s' % stampId
        url      = 'http://stamped.com.static.images.s3.amazonaws.com/%s.jpg' % prefix
        max_size = (960, 960)
        
        # Add images in all sizes
        self._addImageSizes(prefix, image, max_size)
        return url
    
    def addResizedStampImages(self, sourceUrl, imageId, maxSize, sizes):
        image    = utils.getWebImage(sourceUrl, "stamp")
        prefix   = 'stamps/%s' % imageId

        return self._addImageSizes(prefix, image, maxSize, sizes, original_url=sourceUrl)
    
    def changeProfileImageName(self, oldScreenName, newScreenName):
        # Filename is lowercase screen name
        oldPrefix = 'users/%s' % oldScreenName.lower()
        newPrefix = 'users/%s' % newScreenName.lower()
        suffix = '.jpg'
        
        sizes = self.profileImageSizes
        
        old = '%s%s' % (oldPrefix, suffix)
        new = '%s%s' % (newPrefix, suffix)
        self._copyInS3(old, new)
        
        for size in sizes:
            old = '%s-%s%s' % (oldPrefix, size, suffix)
            new = '%s-%s%s' % (newPrefix, size, suffix)
            self._copyInS3(old, new)

        # TODO: add Async task to clean up unused profile images
    
    def _addImageSizes(self, prefix, image, max_size, sizes=None, original_url=None):
        assert isinstance(image, Image.Image)

        result = []
        
        def resizeImage(image, size):
            ratio = 1.0
            
            if size[0] is not None:
                ratio = min(ratio, float(size[0]) / image.size[0])
            
            if size[1] is not None:
                ratio = min(ratio, float(size[1]) / image.size[1])
            
            if ratio < 1.0:
                # Maintain aspect ratio
                width  = int(image.size[0] * ratio)
                height = int(image.size[1] * ratio)
                
                if width < 1:
                    width = 1
                if height < 1:
                    height = 1
                
                size    = (width, height)
                resized = image.resize(size, Image.ANTIALIAS)
            else:
                resized = image
            
            return resized
        
        # Save original
        if original_url is None or original_url.lower() != ("%s.jpg" % prefix).lower():
            original = resizeImage(image, max_size)
            url = self._addJPG(prefix, original)
            output = ImageSizeSchema()
            output.width = original.size[0]
            output.height = original.size[1]
            output.url = url
            result.append(output)
        
        # Save resized versions
        if sizes is not None:
            for name, size in sizes.iteritems():
                resized = resizeImage(image, size)
                name = '%s-%s' % (prefix, name)
                url = self._addJPG(name, resized)
                output = ImageSizeSchema()
                output.width = resized.size[0]
                output.height = resized.size[1]
                output.url = url
                result.append(output)

        return result
    
    def addWebEntityImage(self, image_url):
        utils.log("downloading '%s'" % image_url)
        
        image    = utils.getWebImage(image_url)
        suffix   = os.path.basename(image_url)
        filename = "entities/%s" % suffix
        
        return self.addImage(filename, image)
    
    def addEntityImages(self, image_urls):
        pool = Pool(8)
        
        for image_url in image_urls:
            pool.spawn(self.addWebEntityImage, image_url)
        
        pool.join()
    
    def addImage(self, name, image, jpeg_optimize=True, jpeg_quality=90):
        prefix, suffix = os.path.splitext(name)
        suffix = suffix.lower()
        
        if image.format == 'JPG':
            return self._addJPG(prefix, image, optimize=jpeg_optimize, quality=jpeg_quality)
        elif image.format == 'PNG':
            return self._addPNG(prefix, image)
        else:
            raise Exception("unsupported image type: '" + suffix + "'")
    
    def _addJPG(self, name, image, optimize=True, quality=90):
        name    = "%s.jpg" % name
        out     = StringIO()

        try:
            image.save(out, 'jpeg', optimize=optimize, quality=quality)
        except IOError as e:
            # TODO (travis): where does this MAXBLOCK logic coming from? really needs a comment!
            prev_max_block     = ImageFile.MAXBLOCK
            ImageFile.MAXBLOCK = (image.size[0] * image.size[1]) + 1
            out = StringIO()

            image.save(out, 'jpeg', optimize=False)
            ImageFile.MAXBLOCK = prev_max_block
        
        logs.info('[%s] adding image %s (%dx%d)' % (self, name, image.size[0], image.size[1]))
        return self.addDataToS3(name, out, 'image/jpeg')
    
    def _addPNG(self, name, image):
        name    = "%s.png" % name
        out     = StringIO()
        
        image.save(out, 'png')
        
        logs.info('[%s] adding image %s (%dx%d)' % (self, name, image.size[0], image.size[1]))
        return self.addDataToS3(name, out, 'image/png')
    
    def addDataToS3(self, name, data, contentType):
        num_retries = 0
        max_retries = 5

        while True:
            try:
                conn = S3Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
                bucket = conn.lookup(self.bucket_name)
                key = Key(bucket, name)
                key.set_metadata('Content-Type', contentType)
                # for some reason, if we use set_contents_from_file here, an empty file is created
                key.set_contents_from_string(data.getvalue(), policy='public-read')
                #key.set_contents_from_file(data, policy='public-read')
                key.close()
                
                return "%s/%s" % (self.base_url, name)

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

    def _removeFromS3(self, name):
        num_retries = 0
        max_retries = 5
        logs.info('### removing from S3 with name: %s' % name)
        
        while True:
            try:
                if self.bucket.get_key(name) is not None:
                    self.bucket.delete_key(name)
                return True
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

    def _copyInS3(self, oldKey, newKey):
        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                conn = S3Connection(keys.aws.AWS_ACCESS_KEY_ID, keys.aws.AWS_SECRET_KEY)
                bucket = conn.lookup(self.bucket_name)

                if not self.bucket.get_key(oldKey):
                    return True
                
                bucket.copy_key(newKey, self.bucket_name, oldKey, preserve_acl=True)
                return True

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
    
    def _parse(self, source, params):
        try:
            from jinja2 import Template
        except ImportError:
            logs.warning("error: must install python module Jinja2")
            return
        
        template = Template(source)
        return template.render(params)


    def generateStamp(self, primary_color, secondary_color):
        def output_chunk(out, chunk_type, data):
            out.write(struct.pack("!I", len(data)))
            out.write(chunk_type)
            out.write(data)
            checksum = zlib.crc32(data, zlib.crc32(chunk_type))
            out.write(struct.pack("!i", checksum))
        
        def get_data(width, height, rgb_func):
            fw = float(width)
            fh = float(height)
            compressor = zlib.compressobj()
            data = array.array("B")
            for y in range(height):
                data.append(0)
                fy = float(y)
                for x in range(width):
                    fx = float(x)
                    data.extend([min(255, max(0, int(v * 255))) \
                        for v in rgb_func(fx / fw, fy / fh)])
            compressed = compressor.compress(data.tostring())
            flushed = compressor.flush()
            return compressed + flushed
        
        def linear_gradient(start_value, stop_value, start_offset=0.0, stop_offset=1.0):
            return lambda offset: (start_value + ((offset - start_offset) / \
                                    (stop_offset - start_offset) * \
                                    (stop_value - start_value))) / 255.0
        
        def gradient(DATA):
            def gradient_function(x, y):
                initial_offset = 0.0
                v = x + y
                for offset, start, end in DATA:
                    if v < offset:
                        r = linear_gradient(start[0], end[0], initial_offset, offset)(v)
                        g = linear_gradient(start[1], end[1], initial_offset, offset)(v)
                        b = linear_gradient(start[2], end[2], initial_offset, offset)(v)
                        return r, g, b
                    initial_offset = offset
                return end[0] / 255.0, end[1] / 255.0, end[2] / 255.0
            return gradient_function
        
        def rgb(c):
            split = (c[0:2], c[2:4], c[4:6])
            return [int(x, 16) for x in split]

        def generateImage(filename, mask, width, height, rgb_func):
            out = StringIO()
            out.write(struct.pack("8B", 137, 80, 78, 71, 13, 10, 26, 10))
            output_chunk(out, "IHDR", struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0))
            output_chunk(out, "IDAT", get_data(width, height, rgb_func))
            output_chunk(out, "IEND", "")
            out.seek(0)
            
            image = Image.open(out)
            __dir__  = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(__dir__, mask)
            mask = Image.open(filepath).convert('RGBA').split()[3]
            image.putalpha(mask)
            
            self._addPNG('logos/%s' % filename, image)
        
        output = [
            (195, 195, 'stamped_logo_mask.png',   'logo'),
            (36,  36,  'stamped_email_mask.png',  'email'),
            (18,  18,  'stamped_credit_mask.png', 'credit'),
        ]
        
        for width, height, mask, suffix in output:
            filename = '%s-%s-%s-%sx%s' % (primary_color.upper(), 
                secondary_color.upper(), suffix, width, height)
            
            generate = False
            try:
                generate = not self.bucket.get_key("logos/%s.png" % filename)
            except Exception:
                generate = True
                utils.printException()
            
            if generate:
                generateImage(filename, mask, width, height, gradient([
                    (2.0, rgb(primary_color), rgb(secondary_color)),
                ]))

