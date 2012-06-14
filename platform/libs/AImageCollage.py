#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import math, os, pprint, utils

from abc            import ABCMeta, abstractmethod, abstractproperty
from PIL            import Image, ImageFilter
from gevent.pool    import Pool
from api.S3ImageDB  import S3ImageDB
from LRUCache       import lru_cache

class AImageCollage(object):
    
    __metaclass__ = ABCMeta
    
    def __init__(self):
        self._db    = S3ImageDB()
        self._sizes = self._get_output_sizes()
        self._pool  = Pool(32)
    
    def get_entity_images(self, entities):
        image_urls  = []
        
        for entity in entities:
            if entity.images is not None and len(entity.images) > 0 and len(entity.images[0].sizes) > 0:
                image_url = entity.images[0].sizes[0].url
                
                if image_url is not None:
                    image_urls.append(image_url)
        
        return self.get_images(image_urls)
    
    def get_images(self, image_urls):
        images = []
        
        def _add_image(image_url):
            utils.log("downloading '%s'" % image_url)
            
            image = self._db.getWebImage(image_url, "collage")
            images.append(image)
        
        for image_url in image_urls:
            self._pool.spawn(_add_image, image_url)
        
        self._pool.join()
        utils.log()
        
        return images
    
    def generate_from_user(self, user, entities):
        images = self.get_entity_images(entities)
        
        return self.generate(images, user)
    
    @abstractmethod
    def generate(self, images, user=None):
        raise NotImplementedError
    
    @abstractmethod
    def get_cell_bounds_func(self, size, num_cols, num_rows, i, j, image):
        raise NotImplementedError
    
    def _create_collage(self, 
                        users, 
                        images, 
                        num_rows=None, 
                        num_cols=None, 
                        respect_aspect_ratio=False, 
                        adaptive_image_resizing=True, 
                        enable_drop_shadows=False, 
                        row_major=True, 
                        shuffle_images=False):
        
        # must specify num_cols or num_rows, but not both
        assert (num_cols is not None and num_cols > 0) != (num_rows is not None and num_rows > 0)
        
        num_images = len(images)
        output     = []
        
        if num_rows is None:
            num_cols = int(num_cols)
            num_rows = int(math.ceil(num_images / num_cols))
        elif num_cols is None:
            num_rows = int(num_rows)
            num_cols = int(math.ceil(num_images / num_rows))
        
        for size in self._sizes:
            utils.log("[%s] creating %sx%s collage" % (self, size[0], size[1]))
            
            canvas  = Image.new("RGBA", size, (255, 255, 255, 255))
            offsets = []
            indices = []
            
            if row_major:
                for i in xrange(num_rows):
                    for j in xrange(num_cols):
                        indices.append(len(offsets))
                        offsets.append((i, j))
            else:
                for j in xrange(num_cols):
                    for i in xrange(num_rows):
                        indices.append(len(offsets))
                        offsets.append((i, j))
            
            if shuffle_images:
                indices = utils.shuffle(indices)
            
            for index in indices:
                i, j = offsets[index]
                
                # wrap images around if necessary to fill last row
                index = (i * num_cols + j) % num_images
                image = images[index]
                
                cell_size, pos = self.get_cell_bounds_func(size, num_cols, num_rows, i, j, image)
                
                # adjust cell layout bounds to align to integer grid (helps minimize aliasing)
                cell_size = int(math.ceil(cell_size[0])), int(math.ceil(cell_size[1]))
                x0, y0    = int(math.floor(pos[0])),      int(math.floor(pos[1]))
                
                #utils.log("SIZE: %dx%d, POS: %d,%d" % (cell_size[0], cell_size[1], x0, y0))
                
                width  = cell_size[0]
                height = cell_size[1]
                
                if adaptive_image_resizing:
                    if image.size[0] / cell_size[0] < image.size[1] / cell_size[1]:
                        width  = cell_size[0]
                        height = (width * image.size[1]) / image.size[0]
                        
                        if not respect_aspect_ratio and height > cell_size[1]:
                            height = int((height + cell_size[1]) * .5)
                    else:
                        height = cell_size[1]
                        width  = (height * image.size[0]) / image.size[1]
                        
                        if not respect_aspect_ratio and width > cell_size[0]:
                            width = int((width + cell_size[0]) * .5)
                
                cell  = image.resize((width, height), Image.ANTIALIAS)
                w     = min(width,  cell_size[0])
                h     = min(height, cell_size[1])
                cell  = cell.crop((0, 0, w, h))
                
                if enable_drop_shadows:
                    self._paste_image_with_drop_shadow(canvas, cell, (x0, y0))
                else:
                    canvas.paste(cell, (x0, y0))
            
            canvas = self._apply_postprocessing(canvas)
            output.append(canvas)
        
        return output
    
    def _apply_postprocessing(self, image):
        return image.convert("L")
    
    def _paste_image_with_drop_shadow(self, canvas, image, pos, size=None, iterations=10, color=(0,0,0,255)):
        if size is None:
            size = int(max(2, canvas.size[0] / 64.0))
        
        shadow = self._get_drop_shadow(image.size, size, iterations, color)
        
        canvas.paste(shadow, (pos[0] - size, pos[1] - size), shadow)
        canvas.paste(image, pos)
    
    @lru_cache(maxsize=64)
    def _get_drop_shadow(self, size, shadow_size, iterations, color):
        width   = size[0] + shadow_size * 2
        height  = size[1] + shadow_size * 2
        
        shadow0 = Image.new("RGBA", (width, height), (125,125,125,0))
        shadow1 = Image.new("RGBA", (size[0], size[1]), color)
        
        shadow0.paste(shadow1, (shadow_size, shadow_size))
        
        for i in xrange(iterations):
            shadow0 = shadow0.filter(ImageFilter.BLUR)
        
        return shadow0
    
    def _get_output_sizes(self):
        return [
            (940, 256), 
            (512, 128), 
            (256, 64), 
        ]
    
    def __str__(self):
        return self.__class__.__name__

