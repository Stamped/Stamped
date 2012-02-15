#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'AExternalSource' ]

import Globals
from logs import log, report

try:
    from abc        import ABCMeta, abstractmethod, abstractproperty
    from datetime   import datetime
except:
    report()
    raise

class AExternalSource(object):
    """
    Abstract Base Class for Third Party Data-Source wrappers.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def resolveEntity(self, entity, controller):
        """
        Attempt to fill populate id fields based on seed data.

        Returns True if the entity was modified.
        """
        pass
    
    @abstractmethod
    def enrichEntity(self, entity, controller):
        """
        Attempt to populate data fields based on id data.

        Returns True if the entity was modified.
        """
        pass

    @abstractmethod
    def decorateEntity(self, entity, controller, decoration_db):
        """
        Hook for creating/updating external resouces associated with an entity, writing to decorator-specific entity fields if necessary.

        Returns True if the entity was modified.
        """
        pass
    
    @abstractmethod
    def sourceName(self):
        """
        Returns the name of this source as would be used with a SourceController.
        """
        pass

    def writeSingleton(self, entity, group, data, controller=None):
        now = datetime.utcnow()
        if controller is not None:
            now = controller.now()
        if data is None:
            if group in entity:
                del entity[group]
        else:
            entity[group] = data
        entity["%s_source" % (group,)] = self.sourceName
        entity['%s_timestamp' % (group,)] = now
    
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

