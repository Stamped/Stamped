#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'FullResolveContainer' ]

import Globals
from logs import report

try:
    from BasicSourceContainer   import BasicSourceContainer

    from EntityGroups           import *

    from FactualSource          import FactualSource
    from GooglePlacesSource     import GooglePlacesSource
    from SinglePlatformSource   import SinglePlatformSource
    from TMDBSource             import TMDBSource
    from FormatSource           import FormatSource
except:
    report()
    raise

class FullResolveContainer(BasicSourceContainer):
    """
    """

    def __init__(self):
        BasicSourceContainer.__init__(self)
        
        groups = [
            FactualGroup(),
            SinglePlatformGroup(),
            GooglePlacesGroup(),
            TMDBGroup(),

            AddressGroup(),
            PhoneGroup(),
            SiteGroup(),
            PriceRangeGroup(),
            CuisineGroup(),
            MenuGroup(),
            ReleaseDateGroup(),
            DirectorGroup(),
            CastGroup(),
            SubtitleGroup(),
        ]
        for group in groups:
            self.addGroup(group)

        sources = [
            FormatSource(),
            FactualSource(),
            GooglePlacesSource(),
            SinglePlatformSource(),
            #TMDBSource(),
        ]
        for source in sources:
            self.addSource(source)
