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
    
    def __init__(self, **kwargs):
        self._square_cells = kwargs.pop('square_cells', False)
        self._pad_coeff    = kwargs.pop('pad_coeff', 128.0)
        
        ImageCollage.__init__(self, **kwargs)
    
    def get_cell_bounds_func(self, size, num_cols, num_rows, i, j, image):
        base_cell_width  = size[0] / num_cols
        
        if self._square_cells:
            base_cell_height = base_cell_width
        else:
            base_cell_height = size[1] / num_rows
        
        pad = max(2, round(size[0] / self._pad_coeff))
        
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
        
        logo_size = (cell_width / 5.0, cell_width / 5.0)
        logo_pos  = ((x + cell_width - logo_size[0] * (4.0 / 5.0)), y - logo_size[1] / 5.0)
        
        return ((cell_width, cell_height), (x, y), logo_size, logo_pos)

class MusicImageCollage(BasicImageCollage):
    
    def __init__(self):
        BasicImageCollage.__init__(self, square_cells=False, pad_coeff=128.0)

class BookImageCollage(ImageCollage):
    
    def __init__(self):
        ImageCollage.__init__(self, adaptive_image_resizing=False, enable_drop_shadows=True)
    
    def _get_layout(self, num_images):
        num_rows = 1
        num_cols = None
        
        return num_rows, num_cols
    
    def get_cell_bounds_func(self, size, num_cols, num_rows, i, j, image):
        cell_width  = (size[0] / max(num_cols * .5, 1))
        cell_height = max(size[1], (cell_width * image.size[1]) / image.size[0])
        
        x = math.floor(size[0] * j / num_cols)
        y = (size[1] - cell_height) / 2.0
        
        logo_size = (cell_width / 5.0, cell_width / 5.0)
        logo_pos  = ((x + logo_size[0] / 2.0), y + cell_height - logo_size[1] * 1.5)
        
        return ((cell_width, cell_height), (x, y), logo_size, logo_pos)

class FilmImageCollage(ImageCollage):
    
    def __init__(self):
        ImageCollage.__init__(self, 
                              adaptive_image_resizing=False, 
                              enable_drop_shadows=True, 
                              row_major=False)
    
    def get_cell_bounds_func(self, size, num_cols, num_rows, i, j, image):
        cell_width  = (size[0] / max(num_cols * .95, 1))
        cell_offset = (size[1] / max(num_rows * .95, 1))
        cell_height = max(cell_offset, (cell_width * image.size[1]) / image.size[0])
        
        offset = -0.5 * cell_offset
        
        if ((j & 1) == 1):
            offset = 0
        
        x = math.floor(cell_width * j)
        y = (offset + i * cell_offset)
        
        logo_size = (cell_width / 5.0, cell_width / 5.0)
        logo_pos  = ((x + cell_width - logo_size[0] * (4.0 / 5.0)), y - logo_size[1] / 5.0)
        
        return ((cell_width, cell_height), (x, y), logo_size, logo_pos)

class AppImageCollage(BasicImageCollage):
    
    def __init__(self):
        BasicImageCollage.__init__(self, square_cells=True, pad_coeff=32.0)

