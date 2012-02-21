#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'BasicSourceContainer' ]

import Globals
from logs import log, report

try:
    from ASourceContainer       import ASourceContainer
    from ASourceController      import ASourceController
    from datetime               import datetime
    from datetime               import timedelta
    from copy                   import deepcopy
    from pprint                 import pformat
    from Schemas                import Entity
    import logs                 
except:
    report()
    raise

class BasicSourceContainer(ASourceContainer,ASourceController):
    """
    """

    def __init__(self):
        ASourceContainer.__init__(self)
        ASourceController.__init__(self)
        self.__now = None
        self.__global_priorities = {}
        self.__group_priorities = {}
        self.__groups = {}
        self.__sources = []
        self.__default_max_iterations = 10
        self.__global_max_age = timedelta(7)
        self.__failedValues = {}
        self.failedIncrement = 10
        self.passedDecrement = 2
        self.failedCutoff    = 40
        self.failedCooldown  = 1
        self.failedPunishment = 20
    
    def enrichEntity(self, entity, decorations, max_iterations=None, timestamp=None):
        self.setNow(timestamp)
        if max_iterations == None:
            max_iterations = self.__default_max_iterations
        modified_total = False
        failedSources = set()
        for i in range(max_iterations):
            modified = False
            for source in self.__sources:
                if source not in failedSources and self.__failedValues[source] < self.failedCutoff:
                    groups = source.groups
                    targetGroups = set()
                    for group in groups:
                        if self.shouldEnrich(group, source.sourceName, entity, self.now):
                            targetGroups.add(group)
                    if len(targetGroups) > 0:
                        copy = Entity().importData(entity.value)
                        timestamps = {}
                        localDecorations = {}
                        try:
                            enriched = source.enrichEntity(copy, self, localDecorations, timestamps)
                            if enriched:
                                for group in targetGroups:
                                    localTimestamp = self.now
                                    if group in timestamps:
                                        localTimestamp = timestamps[group]
                                    if self.shouldEnrich(group, source.sourceName, entity, localTimestamp):
                                        groupObj = self.getGroup(group)
                                        assert( groupObj is not None )
                                        fieldsChanged = groupObj.syncFields(copy, entity)
                                        if group in localDecorations:
                                            decorations[group] = localDecorations[group]
                                        if fieldsChanged or group in timestamps or group in localDecorations:
                                            groupObj.setTimestamp(entity, localTimestamp)
                                            groupObj.setSource(entity, source.sourceName)
                                            modified = True
                            self.__failedValues[source] = max(self.__failedValues[source] - self.passedDecrement, 0)
                        except Exception:
                            logs.warning("Source %s threw an exception when enriching %s" % (source, pformat(entity) ) )
                            failedSources.add(source)
                            self.__failedValues[source] += self.failedIncrement
                            if self.__failedValues[source] < self.failedCutoff:
                                logs.warning("%s is still below failed cutoff; it won't be used for this enrichment" % (source,))
                            else:
                                logs.warning("%s is beyond the failed cutoff; placing on cooldown list" % (source,))
                            self.__failedValues[source] += self.failedPunishment
            if not modified:
                break
            else:
                modified_total = True
        for source, value in self.__failedValues.items():
            self.__failedValues[source] = max(value - self.failedCooldown, 0)
        return modified_total

    def shouldEnrich(self, group, source, entity,timestamp=None):
        if timestamp is None:
            timestamp = self.now
        if group in self.__groups:
            groupObj = self.__groups[group]
            if groupObj.eligible(entity):
                currentSource = groupObj.getSource(entity)
                if currentSource is None:
                    return True
                else:
                    priority = self.getPriority(source)
                    currentPriority = self.getPriority(currentSource)
                    if priority > currentPriority:
                        return True
                    elif priority < currentPriority:
                        return False
                    else:
                        maxAge = self.getMaxAge(group, source)
                        if self.now - timestamp > maxAge:
                            return False
                        else:
                            currentMaxAge = self.getMaxAge(group, currentSource)
                            currentTimestamp = groupObj.getTimestamp(entity)
                            if self.now - currentTimestamp > currentMaxAge:
                                return True
                            else:
                                return False
            else:
                return False
        else:
            return False

    @property
    def now(self):
        if self.__now is None:
            self.__now = datetime.utcnow()
        return self.__now

    def setNow(self,timestamp=None):
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.__now = timestamp

    def setGlobalPriority(self, source, value):
        self.__global_priorities[source] = value
    
    def getGlobalPriority(self, source):
        if source in self.__global_priorities:
            return self.__global_priorities[source]
        else:
            return 0

    def setGroupPriority(self, source, value):
        self.__group_priorities[source] = value
    
    def getGroupPriority(self, source):
        if source in self.__group_priorities:
            return self.__group_priorities[source]
        else:
            return self.getGlobalPriority(source)
    
    def getPriority(self, source):
        return self.getGroupPriority(source)

    def addSource(self, source):
        self.__sources.append(source)
        self.__failedValues[source] = 0

    def getGroup(self, name):
        if name in self.__groups:
            return self.__groups[name]
        else:
            return None

    def addGroup(self, group):
        self.__groups[group.groupName] = group
        
    def setGlobalMaxAge(self, age):
        self.__global_max_age = age

    def getGlobalMaxAge(self):
        return self.__global_max_age

    def getMaxAge(self, group, source):
        return self.getGlobalMaxAge()
