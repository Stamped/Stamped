#!/usr/bin/python

"""
Interface for Spotify API


Top-level functions for spotimeta module:

    canonical(url_or_uri)
        returns a spotify uri, regardless if a url or uri is passed in
    
    entrytype(url_or_uri)
        Return "album", "artist" or "track" based on the type of entry the uri
        or url refers to.
    
    lookup(self, uri, detail=0) method of Metadata instance
        Lookup metadata for a URI. Optionally ask for extra details.
        The details argument is an int: 0 for normal ammount of detauls, 1
        for extra details, and 2 for most details. For tracks the details
        argument is ignored, as the Spotify api only has one level of detail
        for tracks. For the meaning of the detail levels, look at the
        Spotify api docs
    
    search_album(self, term, page=None) method of Metadata instance
        The first page is numbered 1!
    
    search_artist(self, term, page=None) method of Metadata instance
        The first page is numbered 1!
    
    search_track(self, term, page=None) method of Metadata instance
        The first page is numbered 1!


"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

class Spotify(object):

	def __init__(self):
		pass

	def search_album(self,term):
		pass

if __name__ == "__main__":
	print("Not implemented yet")
