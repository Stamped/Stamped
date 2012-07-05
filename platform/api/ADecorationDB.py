#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'ADecorationDB' ]

import Globals
from logs import report

try:
    from utils      import abstract
except:
    report()
    raise

class ADecorationDB(object):
    """
    Abstract Base Class for Decoration storage as used with ExternalSource.decorateEntity.
    """

    @abstract
    def updateDecoration(self, name, value):
        """
        Update the named decoration.

        Decorations may be purged without notice so they should only contain reproducable data.
        """
        raise NotImplementedError

