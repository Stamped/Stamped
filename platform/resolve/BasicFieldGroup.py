#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'BasicFieldGroup' ]

import Globals
from logs import log, report

try:
    from AFieldGroup    import AFieldGroup
    from pprint         import pformat, pprint
    # from schema         import SchemaElement
except:
    report()
    raise

class BasicFieldGroup(AFieldGroup):
    """
    """

    # TODO: Shouldn't *fields be before kwargs???
    def __init__(self, name, source_path=None, timestamp_path=None, *fields):
        if source_path is None:
            source_path = [ '%s_source' % name ]
        if timestamp_path is None:
            timestamp_path = [ '%s_timestamp' % name ]
        self.__name = name
        self.__fields = [ list(field) for field in fields ]
        self.__decorations = [ ]
        self.__source = list(source_path)
        self.__timestamp = list(timestamp_path)

    @property
    def groupName(self):
        return self.__name

    def isSet(self, entity):
        for field in self.__fields:
            v = self.getValue(entity, field)
            if isinstance(v, Schema):
                v = v.dataExport()
            if v is not None:
                return True
        return False

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
            if isinstance(old_value, Schema):
                old_value = old_value.dataExport()
            if isinstance(new_value, Schema):
                new_value = new_value.dataExport()
            if old_value != new_value:
                self.setValue(destination, field, new_value)
                modified = True
        return modified

    def syncDecorations(self, entity, destination):
        modified = False
        for field in self.__decorations:
            old_value = self.getValue(destination, field)
            new_value = self.getValue(entity, field)
            if isinstance(old_value, Schema):
                old_value = old_value.dataExport()
            if isinstance(new_value, Schema):
                new_value = new_value.dataExport()
            if old_value != new_value:
                self.setValue(destination, field, new_value)
                modified = True
        return modified

    def addField(self, path):
        self.__fields.append(list(path))

    def addDecoration(self, path):
        self.__decorations.append(list(path))
    
    def getValue(self, entity, path):
        cur = entity
        for p in path[:-1]:
            if p in cur:
                cur = cur[p]
            else:
                return None
        if path[-1] in cur:
            return cur[path[-1]]
        else:
            return None

    def setValue(self, entity, path, value):
        cur = entity
        for p in path[:-1]:
            cur = cur[p]
        cur[path[-1]] = value

    def addNameField(self):
        self.addField([self.groupName])
