#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__   = "TODO"

import Globals
import Image, ImageFile
import aws, logs, os, utils, time
import zlib, struct, array, random

from AImageDB import AImageDB
from StringIO import StringIO

from boto.cloudfront    import CloudFrontConnection
from boto.s3.connection import S3Connection
from boto.s3.key        import Key
# from boto.s3.bucket     import Bucket

class S3ImageDB(AImageDB):
    
    def __init__(self, bucket_name='stamped.com.static.images'):
        # find or create bucket
        # ---------------------
        conn = S3Connection(aws.AWS_ACCESS_KEY_ID, aws.AWS_SECRET_KEY)

        self.bucket = conn.lookup(bucket_name)

        if not self.bucket:
            self.bucket = conn.create_bucket(bucket_name)
        
        self.bucket.set_acl('public-read')
        self.bucket_name = bucket_name
        
        # find or create distribution
        # ---------------------------
        """
        cdn = CloudFrontConnection(aws.AWS_ACCESS_KEY_ID, aws.AWS_SECRET_KEY)
        rs = cdn.get_all_distributions()
        self.distro = None
        
        for distro in rs:
            if distro.origin.dns_name.startswith(bucket_name):
                self.distro = distro
                break
        
        if self.distro is None:
            origin = "%s.s3.amazonaws.com" % bucket_name
            logs.info("[%s] creating new distro (%s)..." % (self, origin))
            self.distro = cdn.create_distribution(origin=origin, enabled=True)
            
            while self.distro.status == u'InProgress':
                self.distro.update()
        """
    
    def getImage(self, data):
        assert isinstance(data, basestring)
        
        io = StringIO(data)
        im = Image.open(io)
        
        return im

    @property
    def profileImageSizes(self):
        maxSize = (500, 500)
        
        sizes = {
            # shown in user's profile
            '144x144': (144, 144), # 2x
            '72x72': (72, 72),  # 1x
            
            # shown in sDetail, sCreate, people tab (me)
            '110x110': (110, 110), # 2x
            '55x55': (55, 55),  # 1x
            
            # shown in sDetail (also stamped by), eDetail (stamped by)
            '92x92': (92, 92),  # 2x
            '46x46': (46, 46),  # 1x
            
            # shown in inbox, activity (restamp), people (list)
            '74x74': (74, 74),  # 2x
            '37x37': (37, 37),  # 1x
            
            # shown in activity, sDetail (comments)
            '62x62': (62, 62),  # 2x
            '31x31': (31, 31),  # 1x
        }

        return maxSize, sizes

    
    def addProfileImage(self, screenName, image):
        assert isinstance(image, Image.Image)
        
        prefix = 'users/%s' % screenName
        images = []
        
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

        maxSize, sizes = self.profileImageSizes

        # Add images in all sizes
        self._addImageSizes(prefix, image, maxSize, sizes)

    def removeProfileImage(self, screenName):
        prefix = 'users/%s' % screenName
        suffix = '.jpg'

        maxSize, sizes = self.profileImageSizes

        try:
            self._removeFromS3('%s%s') % (prefix, suffix)

            for size in sizes:
                self._removeFromS3('%s-%s%s') % (prefix, size, suffix)
        except:
            logs.warning('Failed to remove file')
    
    def addEntityImage(self, entityId, image):
        assert isinstance(image, Image.Image)
        
        prefix = 'entities/%s' % entityId
        
        maxSize = (960, 960)

        sizes = {
            'ios1x': (196, 288),
            'ios2x': (96, 144),
        }
        
        # Add images in all sizes
        self._addImageSizes(prefix, image, maxSize, sizes)
    
    def addStampImage(self, stampId, image):
        assert isinstance(image, Image.Image)
        
        prefix = 'stamps/%s' % stampId

        maxSize = (960, 960)

        sizes = {
            'ios1x': (200, None),
            'ios2x': (400, None),
            'web': (580, None),
            'mobile': (572, None),
        }
        
        # Add images in all sizes
        self._addImageSizes(prefix, image, maxSize, sizes)
    
    def _addImageSizes(self, prefix, image, maxSize, sizes=None):
        assert isinstance(image, Image.Image)

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
        original = resizeImage(image, maxSize)
        self._addJPG(prefix, original)

        # Save resized versions
        for name, size in sizes.iteritems():
            resized = resizeImage(image, size)
            name = '%s-%s' % (prefix, name)
            self._addJPG(name, resized)
    
    def _addJPG(self, name, image):
        assert isinstance(image, Image.Image)
        
        name    = "%s.jpg" % name

        out     = StringIO()
        image.save(out, 'jpeg', optimize=True)
        
        logs.info('[%s] adding image %s (%dx%d)' % \
            (self, name, image.size[0], image.size[1]))
        
        self._addDataToS3(name, out, 'image/jpeg')
        
        return name
    
    def _addPNG(self, name, image):
        assert isinstance(image, Image.Image)
        
        name    = "%s.png" % name

        out     = StringIO()
        image.save(out, 'png')
        
        logs.info('[%s] adding image %s (%dx%d)' % \
            (self, name, image.size[0], image.size[1]))
        
        self._addDataToS3(name, out, 'image/png')
        
        return name

    def _addDataToS3(self, name, data, contentType):
        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                logs.info('CREATE NEW CONNECTION & ASSIGN BUCKET')
                conn = S3Connection(aws.AWS_ACCESS_KEY_ID, aws.AWS_SECRET_KEY)
                bucket = conn.lookup(self.bucket_name)

                logs.info('GET KEY')
                key = Key(bucket, name)

                logs.info('GOT KEY / SET CONTENT-TYPE')
                key.set_metadata('Content-Type', contentType)

                logs.info('CONTENT-TYPE SET / SET DATA')
                key.set_contents_from_file(data, policy='public-read')

                logs.info('DATA SET / CLOSE KEY')
                key.close()

                logs.info('KEY IS CLOSED!')
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
                        logs.info('CLOSE KEY!')
                        key.close()
                except:
                    pass

    def _removeFromS3(self, name):
        num_retries = 0
        max_retries = 5
        
        while True:
            try:
                if self.bucket.get_key(name):
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
            __dir__ = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(__dir__, mask)
            mask = Image.open(filepath).convert('RGBA').split()[3]
            image.putalpha(mask)
            
            self._addPNG('logos/%s' % filename, image)
        
        output = [
            (195, 195, 'stamped_logo_mask.png',   'logo'),
            (18,  18,  'stamped_credit_mask.png', 'credit'),
        ]
        
        for width, height, mask, suffix in output:
            filename = '%s-%s-%s-%sx%s' % (primary_color.upper(), 
                secondary_color.upper(), suffix, width, height)
            
            generateImage(filename, mask, width, height, gradient([
                (2.0, rgb(primary_color), rgb(secondary_color)),
            ]))

