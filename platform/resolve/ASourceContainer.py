#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'ASourceContainer' ]

import Globals
from logs import log, report

try:
    from abc        import ABCMeta, abstractmethod
except:
    report()
    raise

class ASourceContainer(object):
    """
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def enrichEntity(self, entity, decorations, max_iterations=None, timestamp=None):
        pass

