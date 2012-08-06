#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils

from PIL import Image, ImageFilter

def clamp(v):
    return min(255, max(0, int(round(v))))

def is_valid_image_url(image_url):
    static_prefix = 'http://maps.gstatic.com/mapfiles/place_api/icons'
    
    return image_url is not None and not image_url.startswith(static_prefix)

__gradient_cache = {}
def get_gradient_image(size, stops):
    key = (len(stops), 
           stops[0][1][0], stops[0][1][1], stops[0][1][2], 
           stops[0][2][0], stops[0][2][1], stops[0][2][2])
    
    try:
        sl = __gradient_cache[key]
        s  = sl[0]
        l  = sl[1]
        
        try:
            return s[size]
        except KeyError:
            if l.size[0] >= size[0] and l.size[1] >= size[1]:
                image   = l.resize(size)
                s[size] = image
                return image
    except KeyError:
        pass
    
    image = Image.new("RGBA", size)
    data  = []
    
    for y in xrange(size[1]):
        dy = y / float(size[1])
        
        for x in xrange(size[0]):
            dx = x / float(size[0])
            dv = dx + dy
            
            start_offset = 0.0
            color = None
            
            for offset, start, end in stops:
                if dv < offset:
                    rgb_func = linear_gradient(start, end, start_offset, 2.0)
                    
                    color = tuple(rgb_func(i, dv) for i in xrange(len(end)))
                    break
                else:
                    start_offset = offset
            
            if color is None:
                end   = stops[-1][2]
                color = tuple(c / 255.0 for i in end)
            
            color = tuple(clamp(c * 255.0) for c in color)
            data.append(color)
    
    image.putdata(data)
    
    try:
        sl = __gradient_cache[key]
        s  = sl[0]
        l  = sl[1]
        
        if l.size[0] <= size[0] and l.size[1] <= size[1]:
            __gradient_cache[key] = [ s, image ]
    except KeyError:
        s = {}
        l = image
        __gradient_cache[key] = [ s, l ]
    
    s[size] = image
    return image

def parse_rgb(color, alpha=255):
    split = (color[0:2], color[2:4], color[4:6])
    color = [int(x, 16) for x in split]
    
    color.append(alpha)
    return color

def linear_gradient(start, stop, start_offset=0.0, stop_offset=1.0):
    return lambda index, offset: (start[index] + ((offset - start_offset) / \
                                 (stop_offset - start_offset) * \
                                 (stop[index] - start[index]))) / 255.0

