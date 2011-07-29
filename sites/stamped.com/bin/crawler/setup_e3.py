#!/usr/bin/env python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import Globals
import os, utils

from boto.s3.connection import S3Connection, Location
from boto.s3.key import Key

AWS_ACCESS_KEY_ID = 'AKIAIXLZZZT4DMTKZBDQ'
AWS_SECRET_KEY = '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'

#def main():
base = os.path.dirname(os.path.abspath(__file__))
epf_base = os.path.join(base, "sources/dumps/data/apple")
files = [
    "artist", 
    "collection", 
    "collection_type", 
    "songs", 
    "albums", 
    "video", 
]

conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_KEY)


#if __name__ == '__main__':
#    main()

