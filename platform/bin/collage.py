#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import colorsys, math, os, sys, urllib2, utils

from abc            import ABCMeta, abstractmethod, abstractproperty
from StringIO       import StringIO
from PIL            import Image, ImageFilter
from gevent.pool    import Pool
from api.S3ImageDB  import S3ImageDB

"""

TODO: 
    * AImageCollage
        * GenericImageCollage
        * MusicImageCollage
        * BookImageCollage
        * FilmImageCollage
        * AppImageCollage
        * (Place header is generated separately and doesn't require a collage)

"""

class AImageCollage(object):
    
    __metaclass__ = ABCMeta
    
    def __init__(self, image_urls):
        self._pool  = Pool(8)
        self._db    = S3ImageDB()
        self._tiles = []
        
        def _add_image(image_url):
            utils.log("downloading '%s'" % image_url)
            
            image = self._db.getWebImage(url, "collage"):
            self._tiles.append(image)
            
            #image.save("image%d.jpg" % i, 'JPEG')
        
        for image_url in image_urls:
            self._pool.spawn(_add_image, image_url)
        
        self._pool.join()
        self._sizes = self._get_output_sizes()
    
    @abstractmethod
    def process(self):
        raise NotImplementedError
    
    def _create_collage(self, num_cols):
        num_tiles = len(self._tiles)
        num_rows  = int(math.ceil(num_tiles / num_cols))
        
        for size in self._sizes:
            filename = "collage.%sx%s.jpg" % size
            utils.log("creating collage '%s'" % filename)
            
            canvas    = Image.new("RGB", size)
            cell_size = (size[0] / num_cols, size[1] / num_rows)
            
            # TODO: revisit tile layout algorithm ala http://www.csc.liv.ac.uk/~epa/surveyhtml.html#toc.2.1
            
            offsets = []
            indices = []
            
            for i in xrange(num_rows):
                for j in xrange(num_cols):
                    indices.append(len(offsets))
                    offsets.append((i, j))
            
            indices = utils.shuffle(indices)
            
            for index in indices:
                i, j = offsets[index]
                
                y0 = i * cell_size[1]
                x0 = j * cell_size[0]
                
                # wrap around if necessary to fill last row
                index = (i * num_cols + j) % num_tiles
                tile  = self._tiles[index]
                
                if tile.size[0] / cell_size[0] < tile.size[1] / cell_size[1]:
                    width  = cell_size[0]
                    height = (width * tile.size[1]) / tile.size[0]
                    
                    if height > cell_size[1]:
                        height = int((height + cell_size[1]) * (1.5 / 3.0))
                else:
                    height = cell_size[1]
                    width  = (height * tile.size[0]) / tile.size[1]
                    
                    if width > cell_size[0]:
                        width = int((width + cell_size[0]) * (1.5 / 3.0))
                
                cell   = tile.resize((width, height), Image.ANTIALIAS)
                
                canvas.paste(cell, (x0, y0))
            
            self._apply_postprocessing(canvas)
            canvas.save(filename)
    
    def _get_output_sizes(self):
        return [
            (940, 256), 
            (512, 128), 
            (256, 64), 
        ]
    
    def _apply_postprocessing(self, image):
        # TODO: apply built-in grayscale filter and possibly blur
        pass

class BasicImageCollage(object):
    
    def process(self):
        num_tiles   = len(self._tiles)
        # TODO: dependent on num_tiles
        num_cols    = num_tiles
        
        # TODO: some image collages will have num_rows and num_cols dependent on num_tiles
        AImageCollage._create_collage(num_cols)

def main(images):
    collage = BasicImageCollage(images)

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
    
    main(movies)

