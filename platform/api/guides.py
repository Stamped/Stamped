#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from api_old.Schemas import *

import utils
import datetime
import logs
import time

from db.mongodb.MongoUserCollection import MongoUserCollection
from db.mongodb.MongoTodoCollection import MongoTodoCollection
from db.mongodb.MongoGuideCollection import MongoGuideCollection
from db.mongodb.MongoStampCollection import MongoStampCollection, MongoStampStatsCollection
from db.mongodb.MongoEntityCollection import MongoEntityCollection, MongoEntityStatsCollection
from db.mongodb.MongoCollectionCollection import MongoCollectionCollection
from db.mongodb.MongoFriendshipCollection import MongoFriendshipCollection


from utils import lazyProperty, LoggingThreadPool

from api.module import APIModule

class Guides(APIModule):

    def __init__(self):
        APIModule.__init__(self)

    @lazyProperty
    def _userDB(self):
        return MongoUserCollection()

    @lazyProperty
    def _todoDB(self):
        return MongoTodoCollection()
    
    @lazyProperty
    def _guideDB(self):
        return MongoGuideCollection()
    
    @lazyProperty
    def _stampDB(self):
        return MongoStampCollection()

    @lazyProperty
    def _entityDB(self):
        return MongoEntityCollection()

    @lazyProperty
    def _friendshipDB(self):
        return MongoFriendshipCollection()
    
    @lazyProperty
    def _collectionDB(self):
        return MongoCollectionCollection()
    
    @lazyProperty
    def _stampStatsDB(self):
        return MongoStampStatsCollection()

    @lazyProperty
    def _entityStatsDB(self):
        return MongoEntityStatsCollection()


    def _mapGuideSectionToTypes(self, section=None, subsection=None):
        if subsection is not None:
            return [ subsection ]
        elif section is not None:
            if section == 'food':
                return [ 'restaurant', 'bar', 'cafe', 'food' ]
            else:
                return list(Entity.mapCategoryToTypes(section))
        else:
            raise StampedMissingParametersError("No section or subsection specified for guide")

    def getPersonalGuide(self, guideRequest, authUserId):
        assert(authUserId is not None)

        # Todos (via TimeSlice)
        timeSlice = TimeSlice()
        timeSlice.limit = guideRequest.limit
        timeSlice.offset = guideRequest.offset
        timeSlice.viewport = guideRequest.viewport
        timeSlice.types = self._mapGuideSectionToTypes(guideRequest.section, guideRequest.subsection)
        todos = self._todoDB.getTodos(authUserId, timeSlice)

        # User
        user = self._userDB.getUser(authUserId).minimize()

        # Enrich entities
        entityIds = {}
        for todo in todos:
            entityIds[str(todo.entity.entity_id)] = None
        entities = self._entityDB.getEntities(entityIds.keys())
        for entity in entities:
            if entity.sources.tombstone_id is not None:
                # Convert to newer entity
                replacement = self._entityDB.getEntity(entity.sources.tombstone_id)
                entityIds[entity.entity_id] = replacement
                # Call async process to update references
                self.call_task(self.updateTombstonedEntityReferencesAsync, {'oldEntityId': entity.entity_id})
            else:
                entityIds[entity.entity_id] = entity

        # Build guide
        result = []
        for item in todos:
            ### TODO: Add friends' stamps / to-dos
            entity = entityIds[item.entity.entity_id]
            previews = Previews()
            previews.todos = [ user ]
            entity.previews = previews
            result.append(entity)

        return result

    def getUserGuide(self, guideRequest, authUserId):
        assert(authUserId is not None)

        forceRefresh = False
        
        try:
            guide = self._guideDB.getGuide(authUserId)
        except (StampedUnavailableError, KeyError):
            # Temporarily build the full guide synchronously. Can't do this in prod (obviously..)
            guide = self._buildUserGuide(authUserId)

        try:
            allItems = getattr(guide, guideRequest.section)
            if allItems is None:
                logs.info("Nothing in guide")
                return []
        except AttributeError:
            raise StampedInputError("Guide request for invalid section: %s" % guideRequest.section)

        limit = 20
        if guideRequest.limit is not None:
            limit = guideRequest.limit
        offset = 0
        if guideRequest.offset is not None:
            offset = guideRequest.offset
            
            
        entityIds = {}
        userIds = {}
        items = []

        if guideRequest.viewport is not None:
            latA = guideRequest.viewport.lower_right.lat
            latB = guideRequest.viewport.upper_left.lat
            lngA = guideRequest.viewport.upper_left.lng
            lngB = guideRequest.viewport.lower_right.lng

        i = 0
        for item in allItems:
            # Filter tags
            if guideRequest.subsection is not None and guideRequest.subsection not in item.tags:
                continue

            # Filter coordinates
            if guideRequest.viewport is not None:
                if item.coordinates is None:
                    continue

                latCheck = False
                lngCheck = False

                if latA < latB:
                    if latA <= item.coordinates.lat and item.coordinates.lat <= latB:
                        latCheck = True
                elif latA > latB:
                    if latA <= item.coordinates.lat or item.coordinates.lat <= latB:
                        latCheck = True

                if lngA < lngB:
                    if lngA <= item.coordinates.lng and item.coordinates.lng <= lngB:
                        lngCheck = True
                elif lngA > lngB:
                    if lngA <= item.coordinates.lng or item.coordinates.lng <= lngB:
                        lngCheck = True

                if not latCheck or not lngCheck:
                    continue

            items.append(item)
            entityIds[item.entity_id] = None
            if item.stamps is not None:
                for stampPreview in item.stamps:
                    userIds[stampPreview.user.user_id] = None
            if item.todo_user_ids is not None:
                for userId in item.todo_user_ids:
                    userIds[userId] = None
            i += 1

            if i >= limit + offset:
                break
        
        items = items[offset:]

        if len(items) == 0:
            return []
        
        # Simulated lottery to shuffle the top 20 (or whatever limit is given when offset == 0)
        if items[0].score is not None: 
            if offset == 0 and guideRequest.section != "food":
                lotterySize = min(limit, len(items))
                lotteryItems = map(lambda x: (x.score,x), items[0:lotterySize])
                items = utils.weightedLottery(lotteryItems)
                items = map(lambda x: x[1], items)
                
        # Entities
        entities = self._entityDB.getEntities(entityIds.keys())

        for entity in entities:
            if entity.sources.tombstone_id is not None:
                # Convert to newer entity
                replacement = self._entityDB.getEntity(entity.sources.tombstone_id)
                entityIds[entity.entity_id] = replacement
                # Call async process to update references
                self.call_task(self.updateTombstonedEntityReferencesAsync, {'oldEntityId': entity.entity_id})
            else:
                entityIds[entity.entity_id] = entity

        # Users
        users = self._userDB.lookupUsers(list(userIds.keys()))

        for user in users:
            userIds[user.user_id] = user.minimize()

        # Build guide
        result = []
        for item in items:
            entity = entityIds[item.entity_id]
            if entity is None:
                logs.warning("Missing entity: %s" % item.entity_id)
                forceRefresh = True
                continue
            previews = Previews()
            if item.stamps is not None:
                stamps = []
                for stampPreview in item.stamps:
                    stampPreviewUser = userIds[stampPreview.user.user_id]
                    if stampPreviewUser is None:
                        logs.warning("Stamp Preview: User (%s) not found in entity (%s)" %\
                                     (stampPreview.user.user_id, item.entity_id))
                        # Trigger update to entity stats
                        self.call_task(self.updateEntityStatsAsync, {'entityId': item.entity_id})
                        continue
                    stampPreview.user = stampPreviewUser
                    stamps.append(stampPreview)
                previews.stamps = stamps
            if item.todo_user_ids is not None:
                previews.todos = [ userIds[x] for x in item.todo_user_ids ]
            if previews.stamps is not None or previews.todos is not None:
                entity.previews = previews
            result.append(entity)

        # Refresh guide
        if guide.timestamp is not None and datetime.datetime.utcnow() > guide.timestamp.generated + datetime.timedelta(days=1):
            self.call_task(self.buildGuideAsync, {'authUserId': authUserId})

        return result

    def getTastemakerGuide(self, guideRequest):
        # Get popular stamps
        types = self._mapGuideSectionToTypes(guideRequest.section, guideRequest.subsection)
        limit = 500
        viewport = guideRequest.viewport
        if viewport is not None:
            since = None
            limit = 250
        if guideRequest.section in ['book', 'film', 'music']:
            entityIds = self._entityDB.getWhitelistedTastemakerEntityIds(guideRequest.section)
            entityStats = self._entityStatsDB.getStatsForEntities(entityIds)
            entityStats = filter(lambda x: True in [x.isType(t) for t in types], entityStats)
        else:
            entityStats = self._entityStatsDB.getPopularEntityStats(types=types, viewport=viewport, limit=limit)

        # Rank entities
        limit = 20
        if guideRequest.limit is not None:
            limit = guideRequest.limit
        offset = 0
        if guideRequest.offset is not None:
            offset = guideRequest.offset

        # TODO: Do this in db request
        entityStats = entityStats[offset:offset+limit+5]
        
        userIds = {}

        entityIdsWithScore = {}
        for stat in entityStats:
            if stat.score is None:
                entityIdsWithScore[stat.entity_id] = 0.0
            else:
                entityIdsWithScore[stat.entity_id] = stat.score

            if stat.popular_users is not None:
                for userId in stat.popular_users[:10]:
                    userIds[userId] = None

        scoredEntities = []
        entities = self._entityDB.getEntities(entityIdsWithScore.keys())
        for entity in entities:
            scoredEntities.append((entityIdsWithScore[entity.entity_id], entity))

        scoredEntities.sort(key=lambda x: x[0], reverse=True)

        # Remove the buffer we added earlier (in case any entities no longer exist)
        scoredEntities = scoredEntities[:limit]

        # Apply Lottery
        if offset == 0 and guideRequest.section != "food":
            scoredEntities = utils.weightedLottery(scoredEntities)

        # Users
        users = self._userDB.lookupUsers(list(userIds.keys()))
        for user in users:
            userIds[user.user_id] = user.minimize()

        # Build previews
        entityStampPreviews = {}
        for stat in entityStats:
            if stat.popular_users is not None and stat.popular_stamps is not None:
                if len(stat.popular_users) != len(stat.popular_stamps):
                    logs.warning("Mismatch between popular_users and popular_stamps: entity_id=%s" % stat.entity_id)
                    continue
                stampPreviews = []
                for i in range(min(len(stat.popular_users), 10)):
                    stampPreview = StampPreview()
                    stampPreview.user = userIds[stat.popular_users[i]]
                    stampPreview.stamp_id = stat.popular_stamps[i]
                    if stampPreview.user is None:
                        logs.warning("Stamp Preview: User (%s) not found in entity (%s)" % \
                            (stat.popular_users[i], stat.entity_id))
                        # Trigger update to entity stats
                        self.call_task(self.updateEntityStatsAsync, {'entityId': stat.entity_id})
                        continue
                    stampPreviews.append(stampPreview)
                entityStampPreviews[stat.entity_id] = stampPreviews

        # Results
        result = []
        for score, entity in scoredEntities:
            # Update previews
            if entity.entity_id in entityStampPreviews:
                previews = Previews()
                previews.stamps = entityStampPreviews[entity.entity_id]
                entity.previews = previews
            result.append(entity)

        return result

    def getGuide(self, guideRequest, authUserId):
        if guideRequest.scope == 'me' and authUserId is not None:
            return self.getPersonalGuide(guideRequest, authUserId)

        if guideRequest.scope == 'inbox' and authUserId is not None:
            return self.getUserGuide(guideRequest, authUserId)

        if guideRequest.scope == 'popular':
            return self.getTastemakerGuide(guideRequest)

        raise StampedInputError("Invalid scope for guide: %s" % guideRequest.scope)

    def searchGuide(self, guideSearchRequest, authUserId):
        if guideSearchRequest.scope == 'inbox' and authUserId is not None:
            stampIds = self._getScopeStampIds(scope='inbox', authUserId=authUserId)
        elif guideSearchRequest.scope == 'popular':
            stampIds = None
        elif guideSearchRequest.scope == 'me':
            ### TODO: Return actual search across my todos. For now, just return nothing.
            return []
        else:
            raise StampedInputError("Invalid scope for guide: %s" % guideSearchRequest.scope)

        searchSlice             = SearchSlice()
        searchSlice.limit       = 100
        searchSlice.viewport    = guideSearchRequest.viewport
        searchSlice.query       = guideSearchRequest.query
        searchSlice.types       = self._mapGuideSectionToTypes(guideSearchRequest.section, guideSearchRequest.subsection)

        stamps = self._searchStampCollection(stampIds, searchSlice, authUserId=authUserId)

        entityIds = {}
        userIds = {}

        for stamp in stamps:
            userIds[stamp.user.user_id] = None
            if stamp.entity.entity_id in entityIds:
                continue
            entityIds[stamp.entity.entity_id] = None

        # Entities
        entities = self._entityDB.getEntities(entityIds.keys())

        for entity in entities:
            if entity.sources.tombstone_id is not None:
                # Convert to newer entity
                replacement = self._entityDB.getEntity(entity.sources.tombstone_id)
                entityIds[entity.entity_id] = replacement
                # Call async process to update references
                self.call_task(self.updateTombstonedEntityReferencesAsync, {'oldEntityId': entity.entity_id})
            else:
                entityIds[entity.entity_id] = entity

        # Users
        users = self._userDB.lookupUsers(list(userIds.keys()))

        for user in users:
            userIds[user.user_id] = user.minimize()

        # Build previews
        entityStampPreviews = {}
        for stamp in stamps:
            stampPreview = StampPreview()
            stampPreview.user = userIds[stamp.user.user_id]
            stampPreview.stamp_id = stamp.stamp_id

            if stamp.entity.entity_id in entityStampPreviews:
                entityStampPreviews[stamp.entity.entity_id].append(stampPreview)
            else:
                entityStampPreviews[stamp.entity.entity_id] = [ stampPreview ]

        # Results
        result = []
        seenEntities = set()
        for stamp in stamps:
            if stamp.entity.entity_id in seenEntities:
                continue
            entity = entityIds[stamp.entity.entity_id]
            seenEntities.add(stamp.entity.entity_id)

            previews = Previews()
            previews.stamps = entityStampPreviews[stamp.entity.entity_id]
            entity.previews = previews
            result.append(entity)

        return result

    def buildGuideAsync(self, authUserId):
        self._buildUserGuide(authUserId)

    def _buildUserGuide(self, authUserId):
        user = self._userDB.getUser(authUserId)
        now = datetime.datetime.utcnow()

        t0 = time.time()

        stampIds = self._collectionDB.getInboxStampIds(user.user_id)
        stampStats = self._stampStatsDB.getStatsForStamps(stampIds)
        stampStats = filter(lambda x: x.entity_id is not None and x.user_id is not None, stampStats)
        entityIds = list(set(map(lambda x: x.entity_id, stampStats)))
        entityStats = self._entityStatsDB.getStatsForEntities(entityIds)
        todos = set(self._todoDB.getTodoEntityIds(user.user_id))
        friendIds = self._friendshipDB.getFriends(user.user_id)

        t1 = time.time()

        sections = {}
        for entity in entityStats:
            if entity.types is not None:
                if entity.isType('restaurant') or entity.isType('bar') or entity.isType('cafe'):
                    section = 'food'
                elif entity.isType('track') or entity.isType('artist') or entity.isType('album'):
                    section = 'music'
                elif entity.isType('movie') or entity.isType('tv'):
                    section = 'film'
                elif entity.isType('book'):
                    section = 'book'
                elif entity.isType('app'):
                    section = 'app'
                else:
                    section = 'other'
                if section not in sections:
                    sections[section] = set()
                sections[section].add(entity)

        def entityScore(**kwargs):
            section = kwargs.pop('section', None)
            avgStampQuality = kwargs.pop('avgStampQuality', 0.5)
            avgStampPopularity = kwargs.pop('avgStampPopularity', 0)
            stampTimestamps = kwargs.pop('stampTimestamps', {})
            entityQuality = kwargs.pop('entityQuality', 0.5)
            entityId = kwargs.pop('entityId', None)
            
            result = 0

            # Remove personal stamp from timestamps if it exists
            try:
                personalStampAge = (time.mktime(now.timetuple()) - stampTimestamps.pop(user.user_id)) / 60 / 60 / 24
            except KeyError:
                personalStampAge = None
                
            stampAges = map((lambda x: (time.mktime(now.timetuple()) - x) / 60 / 60 / 24), stampTimestamps.values())
            
            #stampScore - Primary factor for rankings
            stampScore = 0
            for t in stampAges:
                if t < 10:
                    stampScore += 1 - (.05 / 10 * t)
                elif t < 90:
                    stampScore += 1.04375 - (.75 / 80 * t)
                elif t < 290:
                    stampScore += 0.29 - (.2 / 200 * t) 
            

            if section in ['book', 'app']:
                slope = 0
            elif section is 'film':
                slope = 0.55 / 60
            else:
                slope = 0.55 / 120

            #Personal stamp multiplier
            personalStampMultiplier = 1
            if personalStampAge is not None and section is not 'food':
                if personalStampAge < 60:
                    personalStampMultiplier = 0.2 + (slope * personalStampAge)
                else:
                    personalStampMultiplier = min(0.75, slope * personalStampAge)
                
            ### PERSONAL TODO LIST
            personalTodoScore = 0
            if user.user_id in todosMap[entityId]:
                personalTodoScore = 1

            result = (((2 * stampScore)  
                    + (0.2 * avgStampPopularity))
                    * (avgStampQuality)
                    * (entityQuality)
                    * (personalStampMultiplier)
                    + (2.5 * personalTodoScore))
            
            return result

        # Map entities to stamp stats and build todosMap
        stampPopularities = {}
        stampQualities = {}
        stampTimestamps = {}
        todosMap = {}
        stampStatsMap = {}

        for stat in stampStats:

            # Build stampStatsMap
            if stat.entity_id not in stampStatsMap:
                stampStatsMap[stat.entity_id] = []
            stampStatsMap[stat.entity_id].append(stat)

            # Build stampPopularities
            if stat.entity_id not in stampPopularities:
                stampPopularities[stat.entity_id] = []
            stampPopularities[stat.entity_id].append(min(5,stat.popularity)) 

            # Build stampQualities
            if stat.entity_id not in stampQualities:
                stampQualities[stat.entity_id] = []
            stampQualities[stat.entity_id].append(stat.quality)

            # Build stampTimestamps
            if stat.last_stamped is not None:
                t = time.mktime(stat.last_stamped.timetuple())
                if stat.entity_id not in stampTimestamps:
                    stampTimestamps[stat.entity_id] = {}
                try:
                    if t > stampTimestamps[stat.entity_id][stat.user_id]:
                        stampTimestamps[stat.entity_id][stat.user_id] = t
                except KeyError:
                    stampTimestamps[stat.entity_id][stat.user_id] = t

            # Build todosMap
            if stat.preview_todos is not None:
                if stat.entity_id not in todosMap:
                    todosMap[stat.entity_id] = set()
                for userId in stat.preview_todos:
                    if userId in friendIds or userId == user.user_id:
                        todosMap[stat.entity_id].add(userId)       

        guide = GuideCache()
        guide.user_id = user.user_id
        guide.timestamp = StatTimestamp()
        guide.timestamp.generated = now
        
        for section, entity_ids in sections.items():
            r = []
            for entity in sections[section]:
                
                avgQuality = 0.5
                if len(stampQualities[entity.entity_id]) > 0:
                    avgQuality = sum(stampQualities[entity.entity_id]) / len(stampQualities[entity.entity_id])

                avgPopularity = 0
                if len(stampPopularities[entity.entity_id]) > 0:
                    avgPopularity = sum(stampPopularities[entity.entity_id]) / len(stampPopularities[entity.entity_id])

                entityQuality = 0.5
                if entity.quality is not None:
                    entityQuality = entity.quality

                score = entityScore(section=section, avgStampQuality=avgQuality,
                                    avgStampPopularity=avgPopularity, stampTimestamps=stampTimestamps[entity.entity_id],
                                    entityQuality=entityQuality, entityId=entity.entity_id)
                
                coordinates = None
                if entity.lat is not None:
                    coordinates = Coordinates()
                    coordinates.lat = entity.lat
                    coordinates.lng = entity.lng
                r.append((entity.entity_id, score, entity.types, coordinates))
                if entity.entity_id in todos:
                    if entity.entity_id not in todosMap:
                        todosMap[entity.entity_id] = set()
                    todosMap[entity.entity_id].add(user.user_id)

            r.sort(key=itemgetter(1))
            r.reverse()
            cache = []
            for result in r[:1000]:
                item = GuideCacheItem()
                item.entity_id = result[0]
                item.score = result[1]
                if result[2] is None:
                    item.tags = ['other']
                else:
                    item.tags = result[2]
                if result[3] is not None:
                    item.coordinates = result[3]

                # Build preview for associated stamps
                if item.entity_id in stampStatsMap:
                    preview = []
                    for stat in stampStatsMap[item.entity_id]:
                        stampPreview = StampPreview()
                        stampPreview.stamp_id = stat.stamp_id
                        userPreview = UserMini()
                        userPreview.user_id = stat.user_id
                        stampPreview.user = userPreview
                        preview.append(stampPreview)
                    if len(preview) > 0:
                        item.stamps = preview

                if item.entity_id in todosMap:
                    userIds = list(todosMap[result[0]])
                    if len(userIds) > 0:
                        item.todo_user_ids = userIds

                cache.append(item)
            setattr(guide, section, cache)

        logs.info("Time to build guide: %s seconds" % (time.time() - t0))

        self._guideDB.updateGuide(guide)

        return guide


    def _testUserGuide(self, authUserId, coeffs):
        user = self._userDB.getUser(authUserId)
        now = datetime.datetime.utcnow()

        t0 = time.time()

        stampIds = self._collectionDB.getInboxStampIds(user.user_id)
        stamps = self._stampDB.getStamps(stampIds)
        stampStats = self._stampStatsDB.getStatsForStamps(stampIds)
        entityIds = list(set(map(lambda x: x.entity.entity_id, stamps)))
        entities = self._entityDB.getEntities(entityIds)
        todos = set(self._todoDB.getTodoEntityIds(user.user_id))
        friendIds = self._friendshipDB.getFriends(user.user_id)

        stampMap = {} # Map entityId to stamps
        statsMap = {} # Map stampId to stats
        todosMap = {} # Map entityId to userIds

        t1 = time.time()

        sections = {}
        for entity in entities:
            section = entity.category
            if section == 'place':
                if entity.isType('restaurant') or entity.isType('bar') or entity.isType('cafe'):
                    section = 'food'
                else:
                    section = 'other'
            if section not in sections:
                sections[section] = set()
            sections[section].add(entity)

        def entityScore(**kwargs):
            section = kwargs.pop('section', None)
            avgQuality = kwargs.pop('aggQuality', [])
            avgPopularity = kwargs.pop('aggPopularity', [])
            timestamps = kwargs.pop('timestamps', [])
            result = 0
            
            #Remove personal stamp from timestamps if it exists
            try:
                personal_timestamp = (time.mktime(now.timetuple()) - timestamps.pop(authUserId)) / 60 / 60 / 24
            except KeyError:
                personal_timestamp = None
                
            #timestamps is now a list of each friends' most recent stamp time in terms of days since stamped 
            timestamps = map((lambda x: (time.mktime(now.timetuple()) - x) / 60 / 60 / 24), timestamps.values())
            
            #stamp_score
            stamp_score = 0
            personal_stamp_score = 0
            for t in timestamps:
                if t < 10:
                    stamp_score += 1 - (.05 / 10 * t)
                elif t < 90:
                    stamp_score += 1.03125 - (.65 / 80 * t)
                elif t < 290:
                    stamp_score += .435 - (.3 / 200 * t)
            
            #Personal stamp score - higher is worse
            if personal_timestamp is not None:
                if personal_timestamp < 10:
                    personal_stamp_score = 1 - (.05 / 10 * personal_timestamp)
                elif personal_timestamp < 90:
                    personal_stamp_score = 1.03125 - (.65 / 80 * personal_timestamp)
                elif personal_timestamp < 290:
                    personal_stamp_score = .435 - (.3 / 200 * personal_timestamp)
            
            section_coefs = {
                            'food': 0,
                            'music': 1.0,
                            'film': 0.5,
                            'book': 10,
                            'app': 10
                            }
            
            #Magnify personal stamp score by number of stamps by other friends
            try:
                personal_stamp_score = coeffs[section] * personal_stamp_score * len(timestamps)
            except KeyError:
                personal_stamp_score = personal_stamp_score * len(timestamps)
                
            ### PERSONAL TODO LIST
            personal_todo_score = 0
            if entity.entity_id in todos:
                personal_todo_score = 1
            
            if len(timestamps) > 0:
                avgQuality = avgQuality / len(timestamps)
                avgPopularity = avgPopularity / len(timestamps)
            
            image_score = 1
            if entity.images is None:
                image_score = 0.01
            
            result = ( (coeffs['stamp'] * stamp_score) 
                        - (coeffs['personal_stamp'] * personal_stamp_score) 
                        + (coeffs['todo'] * personal_todo_score) 
                        + (coeffs['qual'] * avgQuality) 
                        + (coeffs['pop'] * avgPopularity) ) * (image_score)
            
            return result

        # Build stampMap
        for stamp in stamps:
            if stamp.entity.entity_id not in stampMap:
                stampMap[stamp.entity.entity_id] = set()
            stampMap[stamp.entity.entity_id].add(stamp)
                    
        # Build statsMap and todoMap
        for stat in stampStats:
            statsMap[stat.stamp_id] = stat
            if stat.preview_todos is not None:
                if stat.entity_id not in todosMap:
                    todosMap[stat.entity_id] = set()
                for userId in stat.preview_todos:
                    if userId in friendIds:
                        todosMap[stat.entity_id].add(userId)

        guide = GuideCache()
        guide.user_id = user.user_id
        guide.updated = now
        
        for section, entities in sections.items():
            r = []
            for entity in entities:
                aggQuality = 0
                aggPopularity = 0
                timestamps = {}
                for stamp in stampMap[entity.entity_id]:
                    if stamp.stamp_id in statsMap:
                        stat = statsMap[stamp.stamp_id]
                        if stat.quality is not None:
                            aggQuality += stat.quality
                        if stat.popularity is not None:
                            aggPopularity += min(10,stat.popularity)
                    else:
                        # TEMP: Use embedded stats for backwards compatibility
                        if stamp.stats.quality is not None:
                            aggQuality += stamp.stats.quality
                        if stamp.stats.popularity is not None:
                            aggPopularity += min(10,stamp.stats.popularity)
                    if stamp.timestamp.stamped is not None:
                        t = time.mktime(stamp.timestamp.stamped.timetuple())
                        try:
                            if t > timestamps[stamp.user.user_id]:
                                timestamps[stamp.user.user_id] = t
                        except KeyError:
                            timestamps[stamp.user.user_id] = t
                    elif stamp.timestamp.created is not None:
                        t = time.mktime(stamp.timestamp.created.timetuple())
                        try:
                            if t > timestamps[stamp.user.user_id]:
                                timestamps[stamp.user.user_id] = t
                        except KeyError:
                            timestamps[stamp.user.user_id] = t
                
                score = entityScore(section=section,aggQuality=aggQuality,aggPopularity=aggPopularity, timestamps=timestamps)
                coordinates = None
                if hasattr(entity, 'coordinates'):
                    coordinates = entity.coordinates
                r.append((entity.entity_id, score, entity.types, coordinates))
                if entity.entity_id in todos:
                    if entity.entity_id not in todosMap:
                        todosMap[entity.entity_id] = set()
                    todosMap[entity.entity_id].add(user.user_id)

            r.sort(key=itemgetter(1))
            r.reverse()
            cache = []
            for result in r[:1000]:
                item = GuideCacheItem()
                item.entity_id = result[0]
                item.score = result[1]
                item.tags = result[2]
                if result[3] is not None:
                    item.coordinates = result[3]
                if len(stampMap[result[0]]) > 0:
                    preview = []
                    for stamp in stampMap[result[0]]:
                        stampPreview = StampPreview()
                        stampPreview.stamp_id = stamp.stamp_id
                        userPreview = UserMini()
                        userPreview.user_id = stamp.user.user_id
                        stampPreview.user = userPreview
                        preview.append(stampPreview)
                    if len(preview) > 0:
                        item.stamps = preview
                if result[0] in todosMap:
                    userIds = list(todosMap[result[0]])
                    if len(userIds) > 0:
                        item.todo_user_ids = userIds
                cache.append(item)
            setattr(guide, section, cache)
            
        
        logs.info("Time to build guide: %s seconds" % (time.time() - t0))

        self._guideDB.updateGuide(guide)
            
        return guide
