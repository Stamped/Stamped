#!/usr/bin/env python

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
    def enrichEntity(self, entity, controller, decorations, timestamps):
        """
        Hook for creating/updating external resouces associated with an entity, writing to decorator-specific entity 
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
        Writes the given data to the field indentified by path.

        Entity may be any indexable object, such that path is identifies a valid nesting.

        Path may contain any objects suitable for indexing into the entity but it may not be empty.
        """
        if len(path) == 0:
            raise RuntimeError('empty path')
        cur = entity
        if len(path) > 1:
            for k in path[:-1]:
                cur = entity[k]
        if data is None:
            if path[-1] in cur:
                del cur[path[-1]]
        else:
            cur[path[-1]] = data
    
    def writeFields(self, entity, data, fields):
        """
        For each path-function pair in fields, the value of function(data) is written to the field identified by path.

        As with writeField, all paths must be non-empty.

        All functions must accept one argument.
        """
        for k,v in fields.items():
            self.writeField(entity, v(data), k)

