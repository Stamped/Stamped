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
        self.setGlobalPriority('derived',-100)
    
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
        #logs.debug("Begin enrichment: %s (%s)" % (entity.title, entity.entity_id))

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
                    if self.shouldEnrich(group, source.sourceName, entity, self.now):
                        targetGroups.add(group)
                if not targetGroups:
                    continue

                #  We have groups that are eligible for enrichment.  We'll modify a deep-copy of the entity
                copy = buildEntity(entity.dataExport())
                # timestamps - { GROUP - timestamp }
                # empty, single-use timestamps map for specifying failed attempts,
                # assignment regardless of current value,
                # and stale data (rare)
                # output dictionaries for source.enrichEntity for optional special cases
                # timestamps is used for specifying stale data, failed lookups, and UNOBSERVABLE changes (same value)
                timestamps = {} # { GROUP : TIMESTAMP ... } optional
                localDecorations = {} # opaque decorations, for group object based extensions (i.e. Menus)
                #logs.debug("Enriching with '%s' for groups %s" % (source.sourceName, sorted(targetGroups) ))
                groupObjs = [self.getGroup(group) for group in targetGroups]
                try:
                    enriched = source.enrichEntity(copy, groupObjs, self, localDecorations, timestamps)
                    if enriched:
                        for group in targetGroups:
                            localTimestamp = self.now
                            if group in timestamps:
                                localTimestamp = timestamps[group]
                            if self.shouldEnrich(group, source.sourceName, entity, localTimestamp):
                                groupObj = self.getGroup(group)
                                assert groupObj is not None
                                fieldsChanged = groupObj.syncFields(copy, entity)
                                decorationsChanged = groupObj.syncDecorations(localDecorations, decorations)
                                if fieldsChanged or group in timestamps or decorationsChanged:
                                    groupObj.setTimestamp(entity, localTimestamp)
                                    groupObj.setSource(entity, source.sourceName)
                                    modified = True
                except Exception as e:
                    report()
            modified_total |= modified
        return modified_total

    def shouldEnrich(self, group, source, entity, timestamp=None):
        if timestamp is None:
            timestamp = self.now
        if group in self.__groups:
            groupObj = self.__groups[group]
            if groupObj.eligible(entity):
                currentSource = groupObj.getSource(entity)
                if currentSource is None:
                    # TODO: This screws up the data we manually inject into the
                    # db, which don't have sources, but we also want to somehow
                    # keep them.
                    return True
                else:
                    priority = self.getGroupPriority(group, source)
                    currentPriority = self.getGroupPriority(group, currentSource)
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
                            if currentTimestamp is None:
                                return True
                            try:
                                currentTimestamp = currentTimestamp.replace(tzinfo=None)
                                # if data is stale...
                                if self.now - currentTimestamp > currentMaxAge:
                                    return True
                            except Exception as e:
                                logs.warning('FAIL (%s / %s): self.now (%s) - currentTimestamp (%s) > currentMaxAge (%s)\n%s' % \
                                    (source, group, self.now, currentTimestamp, currentMaxAge, e))
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

