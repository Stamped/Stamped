#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import math, utils

from AImageCollage import AImageCollage

# NOTE (travis): the use of rounding functions (e.g., round, floor, and ceil) 
# throughout the layout functions in this file is very precise, though it may 
# seem arbitrary. don't change them unless you have good reason to.

class ImageCollage(AImageCollage):
    
    def __init__(self, **kwargs):
        AImageCollage.__init__(self)
        
        self._options = kwargs
    
    def _get_layout(self, num_images):
        num_rows = int(math.ceil((num_images + 1) / 8.0))
        num_cols = None
        
        # 1  => 1x1
        # 2  => 2x1
        # 3  => 3x1
        # 4  => 4x1
        # 5  => 5x1
        # 6  => 6x1
        # 7  => 7x1
        # 8  => 5x2
        # 9  => 5x2
        # 10 => 5x2
        # 11 => 6x2
        # 12 => 6x2
        # 13 => 7x2
        # 14 => 7x2
        # 15 => 8x2
        # 16 => 6x3
        # 17 => 6x3
        # 18 => 6x3
        # 19 => 7x3
        # 20 => 7x3
        # 21 => 7x3
        # 22 => 8x3
        # 23 => 8x3
        # 24 => 8x3
        # ...
        
        return num_rows, num_cols
    
    def generate(self, images, user=None):
        num_images  = len(images)
        num_rows, num_cols = self._get_layout(num_images)
        
        return AImageCollage._create_collage(self, user, images, 
                                             num_rows=num_rows, 
                                             num_cols=num_cols, 
                                             **self._options)

class BasicImageCollage(ImageCollage):
    
    def get_cell_bounds_func(self, size, num_cols, num_rows, i, j, image):
        raise NotImplementedError

class MusicImageCollage(ImageCollage):
    
    def get_cell_bounds_func(self, size, num_cols, num_rows, i, j, image):
        base_cell_width  = size[0] / num_cols
        base_cell_height = size[1] / num_rows
        #base_cell_height = base_cell_width
        
        pad = max(2, round(size[0] / 128.0))
        
        offset_x = (pad / (num_cols - 1) if num_cols > 1 else 0)
        offset_y = (pad / (num_rows - 1) if num_rows > 1 else 0)
        #offset   = min(offset_x, offset_y)
        
        # adjust offsets to remove the outer padding from the last row and column
        base_cell_width  += offset_x
        base_cell_height += offset_y
        
        cell_width  = math.ceil(base_cell_width  - pad)
        cell_height = math.ceil(base_cell_height - pad)
        
        x = math.floor(base_cell_width  * j)
        y = math.floor(base_cell_height * i)
        
        if num_cols == 1:
            x = (size[0] - base_cell_width)  / 2
        
        if num_rows == 1:
            y = (size[1] - base_cell_height) / 2
        
        return ((cell_width, cell_height), (x, y))

class BookImageCollage(ImageCollage):
    
    def __init__(self):
        ImageCollage.__init__(self, adaptive_image_resizing=False, enable_drop_shadows=True)
    
    def _get_layout(self, num_images):
        num_rows = 1
        num_cols = None
        
        return num_rows, num_cols
    
    def get_cell_bounds_func(self, size, num_cols, num_rows, i, j, image):
        base_cell_width  = (size[0] / max(num_cols * .5, 1))
        base_cell_height = max(size[1], (base_cell_width * image.size[1]) / image.size[0])
        
        x = math.floor(size[0] * j / num_cols)
        y = (size[1] - base_cell_height) / 2.0
        
        return ((base_cell_width, base_cell_height), (x, y))

class FilmImageCollage(ImageCollage):
    
    def __init__(self):
        ImageCollage.__init__(self, 
                              adaptive_image_resizing=False, 
                              enable_drop_shadows=True, 
                              row_major=False)
    
    def get_cell_bounds_func(self, size, num_cols, num_rows, i, j, image):
        base_cell_width  = (size[0] / max(num_cols * .95, 1))
        base_cell_offset = (size[1] / max(num_rows * .95, 1))
        base_cell_height = max(base_cell_offset, (base_cell_width * image.size[1]) / image.size[0])
        
        offset = -0.5 * base_cell_offset
        
        if ((j & 1) == 1):
            offset = 0
        
        x = math.floor(base_cell_width * j)
        y = (offset + i * base_cell_offset)
        
        return ((base_cell_width, base_cell_height), (x, y))

class AppImageCollage(ImageCollage):
                   
    def get_cell_bounds_func(self, size, num_cols, num_rows, i, j, image):
        base_cell_width  = size[0] / num_cols
        #base_cell_height = size[1] / num_rows
        base_cell_height = base_cell_width
        
        pad = max(2, round(size[0] / 128.0))
        
        offset_x = (pad / (num_cols - 1) if num_cols > 1 else 0)
        offset_y = (pad / (num_rows - 1) if num_rows > 1 else 0)
        
        # adjust offsets to remove the outer padding from the last row and column
        base_cell_width  += offset_x
        base_cell_height += offset_y
        
        cell_width  = math.ceil(base_cell_width  - pad)
        cell_height = math.ceil(base_cell_height - pad)
        
        x = math.floor(base_cell_width  * j)
        y = math.floor(base_cell_height * i)
        
        if num_cols == 1:
            x = (size[0] - base_cell_width)  / 2
        
        if num_rows == 1:
            y = (size[1] - base_cell_height) / 2
        
        return ((cell_width, cell_height), (x, y))

