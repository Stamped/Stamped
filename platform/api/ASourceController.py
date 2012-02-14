#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'ASourceController' ]

import Globals
from logs import log, report

try:
    from abc        import ABCMeta, abstractmethod
    from datetime   import datetime
except:
    report()
    raise

class ASourceController(object):
    """
    Abstact base class for the controller interface expected by subclasses of AEntitySource.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        self.__now = None

    @abstractmethod
    def shouldResolve(self, group, source, entity,timestamp=None):
        """
        Returns whether an EntitySource should write to the given id-field group.

        The optional timestamp parameter can be used to indicate state data from the current source.
        """
        pass

    @abstractmethod
    def shouldEnrich(self, group, source, entity,timestamp=None):
        """
        Returns whether an EntitySource should write to the given data-field group.

        The optional timestamp parameter can be used to indicate state data from the current source.
        """
        pass

    @abstractmethod
    def shouldDecorate(self, group, source, entity,timestamp=None):
        """
        Returns whether an EntitySource should create the named decoration group.

        The optional timestamp parameter can be used to indicate state data from the current source.
        """
        pass

    def now():
        """
        Returns the timestamp that should be used in place of datetime.utcnow() for timestamp unification.
        """
        if self.__now is None:
            self.__now = datetime.utcnow()
        return self.__now

    def clearNow():
        """
        Should be called to clear out cached now field.
        """
        self.__now = None

