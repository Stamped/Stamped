#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'BasicFieldGroup' ]

import Globals
from logs import log, report

try:
    from AFieldGroup    import AFieldGroup
except:
    report()
    raise

class BasicFieldGroup(AFieldGroup):
    """
    """

    def __init__(self, name, source_path=None, timestamp_path=None, *fields):
        if source_path is None:
            source_path = [ '%s_source' % name ]
        if timestamp_path is None:
            timestamp_path = [ '%s_timestamp' % name ]
        self.__name = name
        self.__fields = [ list(field) for field in fields ]
        self.__source = list(source_path)
        self.__timestamp = list(timestamp_path)

    @property
    def groupName(self):
        return self.__name

    def getSource(self, entity):
        return self.getValue(entity, self.__source)

    def setSource(self, entity, source):
        self.setValue(entity, self.__source, source)
    
    def getTimestamp(self, entity):
        return self.getValue(entity, self.__timestamp)

    def setTimestamp(self, entity, timestamp):
        self.setValue(entity, self.__timestamp, timestamp)

    def syncFields(self, entity, destination):
        modified = False
        for field in self.__fields:
            old_value = self.getValue(destination, field)
            new_value = self.getValue(entity, field)
            if old_value != new_value:
                self.setValue(destination, field, new_value)
                modified = True
        return modified

    def addField(self, path):
        self.__fields.append(list(path))
    
    def getValue(self, entity, path):
        cur = entity
        for p in path[:-1]:
            cur = cur[p]
        return cur[path[-1]]

    def setValue(self, entity, path, value):
        cur = entity
        for p in path[:-1]:
            cur = cur[p]
        cur[path[-1]] = value

    def addNameField(self):
        self.addField([self.groupName])
