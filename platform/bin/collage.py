#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import math, os, sys, urllib2, utils

from StringIO       import StringIO
from PIL            import Image, ImageFilter
from gevent.pool    import Pool

class ImageCollage(object):
    
    def __init__(self, *image_urls):
        pool  = Pool(8)
        tiles = []
        
        def _add_image(i, image_url):
            utils.log("downloading '%s'" % image_url)
            
            try:
                data = utils.getFile(image_url)
            except urllib2.HTTPError:
                logs.warn("unable to download image '%s'" % image_url)
                raise
            
            image = self._get_image(data)
            tiles.append(image)
            
            #image.save("image%d.jpg" % i, 'JPEG')
        
        for i in xrange(len(image_urls)):
            image_url = image_urls[i]
            pool.spawn(_add_image, i, image_url)
        
        pool.join()
        
        sizes  = [
            (512, 128), 
            (256, 64), 
        ]
        
        size_map = {
            1  : (1, 1), 
            2  : (2, 1), 
            3  : (3, 1), 
            4  : (3, 2), 
            5  : (3, 2), 
            6  : (3, 2), 
            7  : (4, 2), 
            8  : (4, 2), 
            9  : (4, 3), 
            10 : (4, 3), 
            11 : (4, 3), 
            12 : (4, 3), 
            13 : (5, 3), 
            14 : (5, 3), 
            15 : (5, 3), 
            16 : (5, 4), 
            17 : (5, 4), 
            18 : (5, 4), 
            19 : (5, 4), 
            20 : (6, 4), 
            21 : (6, 4), 
            22 : (6, 4), 
            23 : (6, 4), 
            24 : (6, 4), 
        }
        
        num_tiles = len(tiles)
        num_cols  = size_map[num_tiles][0]
        num_rows  = size_map[num_tiles][1]
        
        num_blurs = 0
        #num_cols  = 5
        #num_rows  = math.ceil(((float) num_tiles) / num_cols)
        
        for size in sizes:
            filename = "collage.%sx%s.jpg" % size
            utils.log("creating collage '%s'" % filename)
            
            canvas    = Image.new("RGB", size)
            cell_size = (size[0] / num_cols, size[1] / num_rows)
            
            for i in xrange(num_rows):
                y0 = i * cell_size[1]
                
                for j in xrange(num_cols):
                    x0 = j * cell_size[0]
                    
                    # wrap around if necessary to fill last row
                    index  = (i * num_cols + j) % num_tiles
                    tile   = tiles[index]
                    
                    if tile.size[0] / cell_size[0] < tile.size[1] / cell_size[1]:
                        width  = cell_size[0]
                        height = (width * tile.size[1]) / tile.size[0]
                        
                        if height > cell_size[1]:
                            height = int((height + cell_size[1]) * (2.0 / 3.0));
                    else:
                        height = cell_size[1]
                        width  = (height * tile.size[0]) / tile.size[1]
                        
                        if width > cell_size[0]:
                            width = int((width + cell_size[0]) * (2.0 / 3.0));
                    
                    cell   = tile.resize((width, height), Image.ANTIALIAS)
                    
                    canvas.paste(cell, (x0, y0))
                    #canvas.paste(cell, (x0, y0, x0 + cell.size[0], y0 + cell.size[1]))
            
            utils.log("blurring collage '%s'" % filename)
            '''
            kernel = [ 1,  4,  7,  4,  1, \
                       4, 20, 33, 20,  4, \
                       7, 33, 55, 33,  7, \
                       4, 20, 33, 20,  4, \
                       1,  4,  7,  4,  1]
            
            """
            kernel = []
            
            for a in xrange(5):
                for b in xrange(5):
                    x = (a - 2)
                    y = (b - 2)
                    
                    if (x == 0 and y == 0):
                        d = 1
                    else:
                        d = 1.0 / math.sqrt((x * x) + (y * y))
                    
                    kernel.append(d)
            
            """
            k = ImageFilter.Kernel((5, 5), kernel)
            
            for i in xrange(num_blurs):
                canvas = canvas.filter(k)
            '''
            
            for i in xrange(num_blurs):
                canvas = canvas.filter(ImageFilter.BLUR)
            
            canvas.save(filename, 'JPEG')
    
    def _get_image(self, data):
        assert isinstance(data, basestring)
        
        io = StringIO(data)
        im = Image.open(io)
        
        return im

def main(*images):
    collage = ImageCollage(*images)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    args = parser.parse_args()
    
    movies = [ 
        'http://ia.media-imdb.com/images/M/MV5BMTk2NTI1MTU4N15BMl5BanBnXkFtZTcwODg0OTY0Nw@@._V1._SY317_CR0,0,214,317_.jpg', 
        'http://ia.media-imdb.com/images/M/MV5BMjc0NzAyMzI1MF5BMl5BanBnXkFtZTcwMTE0NDQ1Nw@@._V1._SY317_CR0,0,214,317_.jpg', 
        'http://ia.media-imdb.com/images/M/MV5BMTQ5ODQwNzIxNV5BMl5BanBnXkFtZTYwNzAyMDE3._V1._SY317_CR0,0,214,317_.jpg', 
        'http://ia.media-imdb.com/images/M/MV5BMjQ0MTE1NDAwNl5BMl5BanBnXkFtZTYwNzMxMDE5._V1._SY317_CR1,0,214,317_.jpg', 
        'http://ia.media-imdb.com/images/M/MV5BMTM2NjEyNzk2OF5BMl5BanBnXkFtZTcwNjcxNjUyMQ@@._V1._SY317_.jpg', 
        'http://ia.media-imdb.com/images/M/MV5BMjE0NzIwNzY0M15BMl5BanBnXkFtZTYwNTAyMDg5._V1._SY317_.jpg', 
        'http://ia.media-imdb.com/images/M/MV5BMTYwOTEwNjAzMl5BMl5BanBnXkFtZTcwODc5MTUwMw@@._V1._SY317_CR0,0,214,317_.jpg', 
        'http://ia.media-imdb.com/images/M/MV5BMjE4MjA1NTAyMV5BMl5BanBnXkFtZTcwNzM1NDQyMQ@@._V1._SY317_.jpg', 
        'http://ia.media-imdb.com/images/M/MV5BMTMxNTMwODM0NF5BMl5BanBnXkFtZTcwODAyMTk2Mw@@._V1._SY317_CR0,0,214,317_.jpg', 
        'http://ia.media-imdb.com/images/M/MV5BMTc2NDIxNTQyNF5BMl5BanBnXkFtZTcwNzIwMzM3MQ@@._V1._SY317_.jpg', 
        'http://ia.media-imdb.com/images/M/MV5BMjEyMzgwNTUzMl5BMl5BanBnXkFtZTcwNTMxMzM3Ng@@._V1._SY317_CR15,0,214,317_.jpg', 
        'http://ia.media-imdb.com/images/M/MV5BMzk3MTE5MDU5NV5BMl5BanBnXkFtZTYwMjY3NTY3._V1._SY317_CR0,0,214,317_.jpg', 
        'http://ia.media-imdb.com/images/M/MV5BMTMwODY3NzQzNF5BMl5BanBnXkFtZTcwNzUxNjc0MQ@@._V1._SY317_CR6,0,214,317_.jpg', 
        'http://ia.media-imdb.com/images/M/MV5BMTMwODg0NDY1Nl5BMl5BanBnXkFtZTcwMjkwNTgyMg@@._V1._SY317_.jpg', 
    ]
    
    main(*movies)

