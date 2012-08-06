#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'AExternalSource' ]

import Globals
from logs import report

try:
    from abc        import ABCMeta, abstractmethod, abstractproperty
except:
    report()
    raise

class AExternalSource(object):
    """
    Abstract Base Class for Third Party Data-Source wrappers.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def enrichEntity(self, entity, groups, controller, decorations, timestamps):
        """
        Hook for creating/updating external resources associated with an entity, writing to decorator-specific entity
        fields if necessary.

        Returns True if the entity was modified.
        """
        pass
    
    @abstractproperty
    def sourceName(self):
        """
        Returns the name of this source as would be used with a SourceController.
        """
        pass

    @abstractmethod
    def getGroups(self, entity=None):
        pass

    
    def writeField(self, entity, data, path):
        """
        Writes the given data to the field identified by path.

        Entity may be any object with attributes such that path identifies a valid nesting.

        Path must contains strings.
        """
        if len(path) == 0:
            raise RuntimeError('empty path')
        cur = entity
        if len(path) > 1:
            for k in path[:-1]:
                cur = getattr(entity, k)
        if data is None:
            if hasattr(cur, path[-1]):
                delattr(cur, path[-1])
        else:
            setattr(cur, path[-1], data)

    def writeFields(self, entity, data, fields):
        """
        For each path-function pair in fields, the value of function(data) is written to the field identified by path.

        As with writeField, all paths must be non-empty.

        All functions must accept one argument.
        """
        for k,v in fields.items():
            self.writeField(entity, v(data), k)

