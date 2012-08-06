#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'ASourceController', "AlwaysSourceController" ]

import Globals
from logs import log, report

try:
    from abc        import ABCMeta, abstractmethod, abstractproperty
    from datetime   import datetime
    from utils      import lazyProperty
except:
    report()
    raise

class ASourceController(object):
    """
    Abstact base class for the controller interface expected by subclasses of AEntitySource.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def shouldEnrich(self, group, source, entity, timestamp=None):
        """
        Returns whether an EntitySource should write to the given group.

        The optional timestamp parameter can be used to indicate state data from the current source.
        """
        pass

    @abstractproperty
    def now(self):
        """
        Returns the timestamp that should be used in place of datetime.utcnow() for timestamp unification.
        """
        pass


class AlwaysSourceController(ASourceController):

    def __init__(self):
        ASourceController.__init__(self)

    def shouldEnrich(self, group, source, entity, timestamp=None):
        return True

    @lazyProperty
    def now(self):
        return datetime.utcnow()

