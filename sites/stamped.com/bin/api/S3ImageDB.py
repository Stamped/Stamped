#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import Image, ImageFile
import aws, logs, os, utils
import zlib, struct, array, random

from AImageDB import AImageDB
from StringIO import StringIO

from boto.cloudfront    import CloudFrontConnection
from boto.s3.connection import S3Connection
from boto.s3.key        import Key

class S3ImageDB(AImageDB):
    
    def __init__(self, bucket_name='stamped.com.static.images'):
        # find or create bucket
        # ---------------------
        conn = S3Connection(aws.AWS_ACCESS_KEY_ID, aws.AWS_SECRET_KEY)
        rs = conn.get_all_buckets()
        rs = filter(lambda b: b.name == bucket_name, rs)
        
        ImageFile.MAXBLOCK = 1000000 # default is 64k
        
        if 1 == len(rs):
            self.bucket = rs[0]
        else:
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
    
    def addProfileImage(self, screenName, image):
        assert isinstance(image, Image.Image)
        
        prefix = 'users/%s' % screenName
        images = []
        
        width, height = image.size
        
        if width != height:
            # extract a square aspect ratio image by cropping the longer side
            diff = abs(height - width) / 2
            
            if width > height:
                box = (diff, 0, width - diff, height)
            else:
                box = (0, diff, width, height - diff)
            
            square = image.crop(box)
        else:
            # image is already square
            square = image
        
        sizes = [
            # shown in user's profile
            144, # 2x
            72,  # 1x
            
            # shown in sDetail, sCreate, people tab (me)
            110, # 2x
            55,  # 1x
            
            # shown in sDetail (also stamped by), eDetail (stamped by)
            92,  # 2x
            46,  # 1x
            
            # shown in inbox, activity (restamp), people (list)
            74,  # 2x
            37,  # 1x
            
            # shown in activity, sDetail (comments)
            62,  # 2x
            31,  # 1x
        ]
        
        # add original image
        images.append((self._addImage(prefix, image), 'original'))
        
        # add cache of resized images
        for size in sizes:
            resized = square.resize((size, size), Image.ANTIALIAS)
            name = '%s-%dx%d' % (prefix, size, size)
            
            images.append((self._addImage(name, resized), '%dx%d' % (size, size)))
        
        # save an html index file of all the images
        """
        images = map(lambda i: ("http://static.stamped.com/%s" % i[0], i[1]), images)
        images = map(lambda i: { 'url' : i[0], 'size' : i[1] }, images)
        
        params = {
            "name" : userId, 
            "images" : images, 
        }
        
        base = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base, 'template.html')
        
        f = open(path, 'r')
        source = f.read()
        f.close()
        
        html = self._parse(source, params)
        self._addKeyFromString("%s.html" % prefix, html)
        """
    
    def addEntityImage(self, entityId, image):
        assert isinstance(image, Image.Image)
        
        prefix = 'entities/%s' % entityId
        
        sizes = [
            (196, 288), # 2x
            (96,  144), # 1x
        ]
        
        # add original image
        self._addImage(prefix, image)
        
        # add cache of resized images
        self._addResizedImages(prefix, image, sizes)
    
    def addStampImage(self, stampId, image):
        assert isinstance(image, Image.Image)
        
        prefix = 'stamps/%s' % stampId
        
        sizes = [
            (400, None), # 2x
            (200, None), # 1x
            
            (640, 960), # 2x
            (320, 480), # 1x
        ]
        
        # add original image
        self._addImage(prefix, image)
        
        # add cache of resized images
        self._addResizedImages(prefix, image, sizes)
    
    def _addResizedImages(self, prefix, image, sizes):
        assert isinstance(image, Image.Image)
        
        for size in sizes:
            ratio = 1.0
            
            if size[0] is not None:
                ratio = min(ratio, float(size[0]) / image.size[0])
            
            if size[1] is not None:
                ratio = min(ratio, float(size[1]) / image.size[1])
            
            if ratio < 1.0:
                # maintain aspect ratio
                width  = int(image.size[0] * ratio)
                height = int(image.size[1] * ratio)
                
                if width < 1:
                    width = 1
                if height < 1:
                    height = 1
                
                size    = (width, height)
                resized = image.resize(size, Image.ANTIALIAS)
            else:
                size    = image.size
                resized = image
            
            name = '%s-%dx%d' % (prefix, size[0], size[1])
            self._addImage(name, resized)
    
    def _addImage(self, name, image):
        assert isinstance(image, Image.Image)
        
        # if 
        suffix = ".jpg"
        name   = "%s%s" % (name, suffix)
        temp   = "temp%s" % (suffix, )
        
        logs.info('[%s] adding image %s (%dx%d)' % \
            (self, name, image.size[0], image.size[1]))
        
        # rely on JPEG encoder to save image to temporary file
        image.save(temp, optimize=True)
        
        key = Key(self.bucket, name)
        key.set_contents_from_filename(temp)
        key.set_acl('public-read')
        key.close()
        
        return name
    
    def _addPNG(self, name, image):
        assert isinstance(image, Image.Image)
        
        suffix = ".png"
        name   = "%s%s" % (name, suffix)
        temp   = "temp%s%s" % (random.random(), suffix)
        
        logs.info('[%s] adding image %s (%dx%d)' % \
            (self, name, image.size[0], image.size[1]))
        
        image.save(temp)
        
        key = Key(self.bucket, name)
        key.set_contents_from_filename(temp)
        key.set_acl('public-read')
        key.close()
        
        return name
    
    def _addKeyFromString(self, name, value):
        key = Key(self.bucket, name)
        key.set_contents_from_string(value)
        key.set_acl('public-read')
        key.close()
    
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

        def write_png(filename, mask, width, height, rgb_func):
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
            (195, 195, 'stamped_logo_mask.png', 'logo'),
            (18, 18, 'stamped_credit_mask.png', 'credit'),
        ]
        
        for width, height, mask, suffix in output:
            filename = '%s-%s-%s-%sx%s' % (primary_color.upper(), \
                secondary_color.upper(), suffix, width, height)
            write_png(filename, mask, width, height, gradient([
                (2.0, rgb(primary_color), rgb(secondary_color)),
            ]))

