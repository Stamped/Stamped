#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import colorsys, math, os, sys, urllib2, utils

from libs.ImageCollages import *

def main(image_urls):
    collage = MusicImageCollage()
    images  = collage.get_images(image_urls)
    
    collage.generate(images)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--db', action='store')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    
    args = parser.parse_args()
    
    if args.db is not None:
        utils.init_db_config(args.db)
    
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

