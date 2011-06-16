#!/usr/bin/python

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

