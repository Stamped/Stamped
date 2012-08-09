#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'BasicSourceContainer' ]

import Globals
from logs import log, report

from resolve.ASourceContainer       import ASourceContainer
from resolve.ASourceController      import ASourceController
from resolve.EntityGroups           import *
from datetime               import datetime
from datetime               import timedelta
from copy                   import deepcopy
from pprint                 import pformat, pprint
from api.Entity                 import buildEntity
import logs                 
from libs.ec2_utils         import is_prod_stack, is_ec2

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
        if is_prod_stack():
            self.__global_max_age = timedelta(7)
        elif is_ec2():
            self.__global_max_age = timedelta(2)
        else:
            self.__global_max_age = timedelta(minutes=0)

        for group in allGroups:
            self.addGroup(group())
        self.setGlobalPriority('seed', 100)
        self.setGlobalPriority('manual', 10000)
        self.setGlobalPriority('derived', -100)
    
    def enrichEntity(self, entity, decorations, max_iterations=None, timestamp=None):
        """
            (might be named enrichedEntityWithSources)
        enrichEntity takes a entity schema object (defined in api/Schemas.py), an output dict of decorations that is
            opaque to this class - only group objects and sources have an understanding of the decorations format
            the group method syncDecorations() handles all propagation of source local decorations to the output decoration dict
          returns a bool value indicating whether the entity was enriched
        """
        self.setNow(timestamp)
        max_iterations = max_iterations or self.__default_max_iterations
        modified_total = False
        logs.debug("Begin enrichment: %s (%s)" % (entity.title, entity.entity_id))

        # We will loop through all sources multiple times, because as data is enriched, previous unresolvable sources
        # may become resolvable and can enrich in turn.  If no fields are modified by any source in a given iteration,
        # then there's no reason to loop again
        for i in range(max_iterations):
            modified = False
            for source in self.__sources:
                if entity.kind not in source.kinds:
                    continue

                if entity.types and source.types and not set(entity.types).intersection(source.types):
                    continue

                groups = source.getGroups(entity)
                targetGroups = set()
                for group in groups:
                    if self.shouldEnrich(group, source.sourceName, entity):
                        targetGroups.add(group)
                if not targetGroups:
                    continue

                #  We have groups that are eligible for enrichment.  We'll modify a deep-copy of the entity
                copy = buildEntity(entity.dataExport())
                # timestamps is passed down to the source. If the source enriches a group, a mapping is added from the
                # group name to the time it was enriched (now, essentially). When the data we get from external source
                # is identical to what we already have, presence of the group in this map is the only way we can tell
                # that we received fresh data.
                # TODO: This is a dictionary for legacy reasons, it should really be a set.
                timestamps = {}
                localDecorations = {} # opaque decorations, for group object based extensions (i.e. Menus)
                logs.debug("Enriching with '%s' for groups %s" % (source.sourceName, sorted(targetGroups) ))
                groupObjs = [self.getGroup(group) for group in targetGroups]
                try:
                    enriched = source.enrichEntity(copy, groupObjs, self, localDecorations, timestamps)
                    if enriched:
                        for groupObj in groupObjs:
                            fieldsChanged = groupObj.syncFields(copy, entity)
                            decorationsChanged = groupObj.syncDecorations(localDecorations, decorations)
                            if fieldsChanged or groupObj.groupName in timestamps or decorationsChanged:
                                groupObj.setTimestamp(entity, self.now)
                                groupObj.setSource(entity, source.sourceName)
                                modified = True
                except Exception as e:
                    report()
            if not modified:
                break
            modified_total |= modified
        return modified_total

    def shouldEnrich(self, group, source, entity, dataTimestamp=None):
        if group not in self.__groups:
            return False

        groupObj = self.__groups[group]
        if not groupObj.eligible(entity):
            return False

        currentSource = groupObj.getSource(entity)
        if currentSource is None:
            return True

        priority = self.getGroupPriority(group, source)
        currentPriority = self.getGroupPriority(group, currentSource)
        if priority > currentPriority:
            return True
        if priority < currentPriority:
            return False

        currentMaxAge = self.getMaxAge(group, currentSource)
        currentTimestamp = groupObj.getTimestamp(entity)
        if currentTimestamp is None:
            return True

        dataTimestamp = dataTimestamp or self.now
        if self.now - dataTimestamp > currentMaxAge:
            # If the data we get from the source is too old, we don't even bother.
            return False
        return self.now - currentTimestamp > currentMaxAge

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

    def setGroupPriority(self, group, source, value):
        if source in self.__group_priorities:
            self.__group_priorities[source][group] = value 
        else:
            self.__group_priorities[source] = { group : value }
    
    def getGroupPriority(self, group, source):
        return self.__group_priorities.get(source, {}).get(
                group, self.getGlobalPriority(source))

    def addSource(self, source):
        self.__sources.append(source)

    def clearSources(self):
        self.__sources = []

    def getGroup(self, name):
        if name in self.__groups:
            return self.__groups[name]
        else:
            return None

    def addGroup(self, group):
        self.__groups[group.groupName] = group
        
    @property
    def groups(self):
        return set(self.__groups.values())

    def setGlobalMaxAge(self, age):
        self.__global_max_age = age

    def getGlobalMaxAge(self):
        return self.__global_max_age

    def getMaxAge(self, group, source):
        return self.getGlobalMaxAge()

