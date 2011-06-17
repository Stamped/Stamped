#!/usr/bin/python

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import urllib, string
from threading import *

class AsyncWebRequest(Thread):
   """
      Fetches a web request asynchronously
      Usage:
         thread = AsyncWebRequest(url)
         thread.start();
         thread.join();
         html = thread.html;
   """
   
   def __init__(self, url):
      Thread.__init__(self)
      self.url = url
   
   def run(self):
      self.html = urllib.urlopen(self.url).read()

