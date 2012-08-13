#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from api_old.Schemas import *

import utils
import datetime
import logs

from db.tododb import TodoDB
from db.userdb import UserDB
from db.stampdb import StampDB
from db.entitydb import EntityDB
from db.friendshipdb import FriendshipDB

from utils import lazyProperty, LoggingThreadPool
from search.AutoCompleteIndex import normalizeTitle, loadIndexFromS3, emptyIndex, pushNewIndexToS3
from resolve.merge import Merge

from api.helpers import APIObject

class EntityAPI(APIObject):

    def __init__(self):
        APIObject.__init__(self)

        self.__autocomplete = emptyIndex()
        self.__autocomplete_last_loaded = datetime.datetime.now()
        if utils.is_ec2():
            self.reloadAutoCompleteIndex()

    @lazyProperty
    def _todoDB(self):
        return TodoDB()

    @lazyProperty
    def _userDB(self):
        return UserDB()
    
    @lazyProperty
    def _stampDB(self):
        return StampDB()

    @lazyProperty
    def _entityDB(self):
        return EntityDB()

    @lazyProperty
    def _friendshipDB(self):
        return FriendshipDB()

    @lazyProperty
    def _merge(self):
        return Merge()


    def getEntityFromRequest(self, entityRequest):
        if isinstance(entityRequest, Schema):
            entityRequest = entityRequest.dataExport()

        entityId    = entityRequest.pop('entity_id', None)
        searchId    = entityRequest.pop('search_id', None)

        if entityId is None and searchId is None:
            raise StampedMissingParametersError("Required field missing (entity_id or search_id)")

        if entityId is None:
            entityId = searchId

        return self._getEntity(entityId)

    def _getEntity(self, entityId):
        if entityId is not None and entityId.startswith('T_'):
            ### RESTRUCTURE TODO: Where does this go? Temporarily raise
            raise NotImplementedError
            entityId = self._merge.convertSearchId(entityId)
            return self._entityDB.getEntity(entityId, forcePrimary=True)
        else:
            ### RESTRUCTURE TODO: Where does this go?
            # self.mergeEntityId(entityId)
            return self._entityDB.getEntity(entityId)

    def addEntity(self, entity):
        timestamp = BasicTimestamp()
        timestamp.created = datetime.datetime.utcnow()
        entity.timestamp = timestamp
        entity = self._entityDB.addEntity(entity)
        return entity

    def getEntity(self, entityRequest, authUserId=None):
        entity = self.getEntityFromRequest(entityRequest)

        if entity.isType('artist') and entity.albums is not None:
            albumIds = {}
            for album in entity.albums:
                if album.entity_id is not None:
                    albumIds[album.entity_id] = None
            try:
                albums = self._entityDB.getEntities(albumIds.keys())
            except Exception:
                logs.warning("Unable to get albums for keys: %s" % albumIds.keys())
                albums = []

            for album in albums:
                albumIds[album.entity_id] = album.minimize()

            enrichedAlbums = []
            for album in entity.albums:
                if album.entity_id is not None and album.entity_id in albumIds and albumIds[album.entity_id] is not None:
                    enrichedAlbums.append(albumIds[album.entity_id])
                else:
                    enrichedAlbums.append(album)

            entity.albums = enrichedAlbums

        ### TODO: Check if user has access to this entity?
        return entity

    def updateCustomEntity(self, authUserId, entityId, data):
        ### TODO: Reexamine how updates are done
        entity = self._entityDB.getEntity(entityId)

        # Check if user has access to this entity
        if entity.generated_by != authUserId or entity.generated_by is None:
            raise StampedEntityUpdatePermissionError("Insufficient privileges to update custom entity")

        # Try to import as a full entity
        for k, v in data.iteritems():
            entity[k] = v

        entity.timestamp.modified = datetime.datetime.utcnow()
        self._entityDB.updateEntity(entity)

        return entity

    def updateEntity(self, data, auth):
        entity = self._entityDB.getEntity(data['entity_id'])

        # Assert that it's the same one (i.e. hasn't been tombstoned)
        if entity.entity_id != data['entity_id']:
            raise StampedTombstonedEntityError('Cannot update entity %s - old entity has been tombstoned' % entity.entity_id)

        # Try to import as a full entity
        for k, v in data.iteritems():
            entity[k] = v

        entity.timestamp.modified = datetime.datetime.utcnow()
        self._entityDB.updateEntity(entity)

        return entity

    def removeEntity(self, entityId):
        return self._entityDB.removeEntity(entityId)

    def removeCustomEntity(self, authUserId, entityId):
        entity = self._entityDB.getEntity(entityId)

        self._entityDB.removeCustomEntity(entityId, authUserId)

        return entity

    @lazyProperty
    def _oldEntitySearch(self):
        from resolve.EntitySearch import EntitySearch
        return EntitySearch()

    @lazyProperty
    def _newEntitySearch(self):
        from search.EntitySearch import EntitySearch
        return EntitySearch()

    def searchEntities(self,
                       query,
                       coords=None,
                       authUserId=None,
                       category=None):

        coordsAsTuple = None if coords is None else (coords.lat, coords.lng)
        entities = self._newEntitySearch.searchEntities(category, query, limit=10, coords=coordsAsTuple)

        results = []
        numToStore = 5

        if category != 'place':
            # The 'place' search engines -- especially Google -- return these shitty half-assed results with nowhere
            # near enough detail to be useful for a user, so we definitely want to do a full lookup on those.
            for entity in entities[:numToStore]:
                self._entityDB.writeSearchEntity(entity)

        for entity in entities:
            distance = None
            try:
                if coords is not None and entity.coordinates is not None:
                    a = (coords.lat, coords.lng)
                    b = (entity.coordinates.lat, entity.coordinates.lng)
                    distance = abs(utils.get_spherical_distance(a, b) * 3959)
            except Exception:
                pass

            results.append((entity, distance))

        return results

    def _orderedUnique(self, theList):
        known = set()
        newlist = []

        for d in theList:
            if d in known: continue
            newlist.append(d)
            known.add(d)

        return newlist

    def getEntityAutoSuggestions(self, query, category, coordinates=None, authUserId=None):
        if datetime.datetime.now() - self.__autocomplete_last_loaded > datetime.timedelta(1):
            self.__autocomplete_last_loaded = datetime.datetime.now()
            self.reloadAutoCompleteIndex()
        if category == 'place':
            if coordinates is None:
                latLng = None
            else:
                latLng = [ coordinates.lat, coordinates.lng ]
            results = self._googlePlaces.getAutocompleteResults(latLng, query, {'radius': 500, 'types' : 'establishment'},
                priority='high')
            #make list of names from results, remove duplicate entries, limit to 10
            if results is None:
                return []
            names = self._orderedUnique([place['terms'][0]['value'] for place in results])[:10]
            completions = []
            for name in names:
                completions.append( { 'completion' : name } )
            return completions

        return [{'completion' : name} for name in self.__autocomplete[category][normalizeTitle(unicode(query))]]

    def reloadAutoCompleteIndex(self, retries=5, delay=0):
        def setIndex(greenlet):
            try:
                self.__autocomplete = greenlet.get()
            except Exception as e:
                if retries:
                    self.reloadAutoCompleteIndex(retries-1, delay*2+1)
                else:
                    email = {
                        'from' : 'Stamped <noreply@stamped.com>',
                        'to' : 'dev@stamped.com',
                        'subject' : 'Error while reloading autocomplete index on ' + self.node_name,
                        'body' : '<pre>%s</pre>' % str(e),
                    }
                    utils.sendEmail(email, format='html')
        gevent.spawn_later(delay, loadIndexFromS3).link(setIndex)

    def updateAutoCompleteIndexAsync(self):
        pushNewIndexToS3()

    def getSuggestedEntities(self, authUserId, category, subcategory=None, coordinates=None, limit=10):
        if category == 'place':
            return self._suggestedEntities.getSuggestedEntities(authUserId,
                                                                category=category,
                                                                subcategory=subcategory,
                                                                coords=coordinates,
                                                                limit=limit)

        groups = []
        if category == 'book':
            entityIds = [
                '4e57b45941ad8514cb00013b', # Steve Jobs
                '4ecaf331fc905f14cc000005', # Fifty Shades of Grey 
                '4fe3342e9713961a5e000b5b', # Gone Girl 
                '4fff6529967d717a14000041', # Bared to You 
                '5010b4a67b815764dee6d0b1', # Wild 
                '4e57ac4a41ad85147e00007a', # Unbroken 
                '4e57aca741ad85147e00153f', # A Game of Thrones
                '4e57ac5841ad85147e000425', # The Hunger Games
            ]
            groups.append(('Suggestions', entityIds))

        elif category == 'film':
            entityIds = [
                '500dd5fe7b81571916b7b258', # Dark Knight Rises 
                '501c520a7b81574f65c592b9', # Total Recall 
                '4e9cbd8cfe4a1d7bd2000070', # Game of Thrones 
                '5010504453b48c4c5a103cf9', # The Bourne Legacy 
                '4e9fb96dfe4a1d1cbe0000f5', # Breaking Bad 
                '4f835f34d56d835c6e000572', # 21 Jump Street 
                '5010504d81353510f980b0f6', # The Campaign 
                '4ea269a3fe4a1d2a4100027e', # Modern Family 
            ]
            groups.append(('Suggestions', entityIds))

        elif category == 'music':
            # Songs
            entityIds = [
                '5018ab0753b48c16ab87aa8d', # Home by Phillip Phillips 
                '5010466c7b8157477c65e47b', # Whistle Flo Rida 
                '5023e56403666c43872de48b', # I Will Wait by Mumford and Sons 
                '50103afb53b48c49b7d3813d', # Some Nights by Fun. 
                '501041a253b48c49b7d38263', # Sweetlife by Frank Ocean
            ]
            groups.append(('Songs', entityIds))

            # Albums
            entityIds = [
                '5023e59f03666c43822de3e4', # Babel by Mumford and Sons 
                '4faa7152591fa4535a0009c2', # Some Nights by Fun. 
                '4fb4fe40591fa462ec0000c5', # Believe by Justin Bieber 
                '500f52c47b815738449589ec', # Gossamer by Passion Pit 
            ]
            groups.append(('Albums', entityIds))

            # Artists
            entityIds = [
                '4ecad83f4820c5024c00049e', # Mumford and Sons 
                '4eb3001b41ad855d53000ac8', # Katy Perry 
                '4ee0233c54533e75460010e1', # Justin Bieber 
                '4eb8700441ad850b6200004f', # Maroon 5 
                '4f0d595b06007d1bb700001f', # The Wanted 
            ]
            groups.append(('Artists', entityIds))

        elif category == 'app':
            # Free
            entityIds = [
                '4edac94056f8685d87000bec', # Angry Birds 
                '4efa2c666e33431b71000cf2', # Instagram 
                '4edac5d1e32a3a08d400000b', # Temple Run 
                '4ed44c9482750f30b70002fd', # Pinterest 
                '4ed44c3f82750f30b7000196', # Spotify 
            ]
            groups.append(('Free', entityIds))

            # Paid
            entityIds = [
                '4ed480e456f86859c20023bd', # Words with Friends 
                '4f13f96f54533e5c89001a5c', # Instapaper 
                '4edad3d7e32a3a08d4000048', # The Sims 3 
                '5010c8a47b81576a00657433', # Where’s my Perry 
            ]
            groups.append(('Paid', entityIds))

        result = []
        for group in groups:
            name = group[0]
            entityIds = group[1]
            entities = self._entityDB.getEntities(entityIds)
            entities.sort(key=lambda x: entityIds.index(x.entity_id))

            result.append({'name': name, 'entities': entities })
            
        return result

    def getMenu(self, entityId):
        menu = self._entityDB.getMenu(entityId)
        if menu is None:
            try:
                self.mergeEntityId(entityId)
                menu = self._entityDB.getMenu(entityId)
            except Exception:
                pass
        if menu is None:
            raise StampedMenuUnavailableError()
        else:
            return menu

    def completeAction(self, authUserId, **kwargs):
        kwargs['authUserId'] = authUserId
        self.call_task(self.completeActionAsync, kwargs)
        return True

    def completeActionAsync(self, authUserId, **kwargs):
        action      = kwargs.pop('action', None)
        source      = kwargs.pop('source', None)
        sourceId    = kwargs.pop('source_id', None)
        entityId    = kwargs.pop('entity_id', None)
        userId      = kwargs.pop('user_id', None)
        stampId     = kwargs.pop('stamp_id', None)

        actions = set([
            'listen',
            'playlist',
            'download',
            'reserve',
            'menu',
            'buy',
            'watch',
            'tickets',
            'queue',
        ])

        # For now, only complete the action if it's associated with an entity and a stamp
        if stampId is not None:
            stamp   = self._stampDB.getStamp(stampId)
            # user    = self._userDB.getUser(stamp.user.user_id)
            entity  = self._entityDB.getEntity(stamp.entity.entity_id)

            if action in actions and authUserId != stamp.user.user_id:
                self._addActionCompleteActivity(authUserId, action, source, stamp.stamp_id, stamp.user.user_id)

        return True

    def entityStampedBy(self, entityId, authUserId=None, limit=100):
        try:
            stats = self._entityDB.getEntityStats(entityId)
        except StampedUnavailableError:
            stats = self.updateEntityStatsAsync(entityId)

        userIds = {}

        # Get popular stamp data
        popularUserIds = map(str, stats.popular_users[:limit])
        popularStamps = self._stampDB.getStampsFromUsersForEntity(popularUserIds, entityId)
        popularStamps.sort(key=lambda x: popularUserIds.index(x.user.user_id))

        # Get friend stamp data
        if authUserId is not None:
            friendUserIds = self._friendshipDB.getFriends(authUserId)
            friendStamps = self._stampDB.getStampsFromUsersForEntity(friendUserIds, entityId)

        # Build user list
        for stamp in popularStamps:
            userIds[stamp.user.user_id] = None
        if authUserId is not None:
            for stamp in friendStamps:
                userIds[stamp.user.user_id] = None

        users = self._userDB.lookupUsers(userIds.keys())
        for user in users:
            userIds[user.user_id] = user.minimize()

        # Populate popular stamps
        stampedby = StampedBy()

        stampPreviewList = []
        for stamp in popularStamps:
            preview = StampPreview()
            preview.stamp_id = stamp.stamp_id
            preview.user = userIds[stamp.user.user_id]
            if preview.user is not None:
                stampPreviewList.append(preview)

        allUsers            = StampedByGroup()
        allUsers.stamps     = stampPreviewList
        allUsers.count      = stats.num_stamps
        stampedby.all       = allUsers

        # Populate friend stamps
        if authUserId is not None:
            stampPreviewList = []
            for stamp in friendStamps:
                preview = StampPreview()
                preview.stamp_id = stamp.stamp_id
                preview.user = userIds[stamp.user.user_id]
                stampPreviewList.append(preview)

            friendUsers         = StampedByGroup()
            friendUsers.stamps  = stampPreviewList
            friendUsers.count   = len(friendStamps)
            stampedby.friends   = friendUsers

        return stampedby

    def updateEntityStatsAsync(self, entityId):
        try:
            entity = self._entityDB.getEntity(entityId)
        except StampedDocumentNotFoundError:
            logs.warning("Entity not found: %s" % entityId)
            return 

        if entity.sources.tombstone_id is not None:
            # Call async process to update references
            self.call_task(self.updateTombstonedEntityReferencesAsync, {'oldEntityId': entity.entity_id})

        numStamps = self._stampDB.countStampsForEntity(entityId)
        popularStampIds = self._stampDB.getPopularStampIds(entityId=entityId, limit=1000)

        # If for some reason popularStampIds doesn't include all stamps, recalculate them
        if numStamps < 1000 and len(popularStampIds) < numStamps:
            logs.warning("Recalculating stamp stats for entityId=%s" % entityId)
            allStampIds = self._stampDB.getStampIdsForEntity(entityId)
            for stampId in allStampIds:
                if stampId not in popularStampIds:
                    ### RESTRUCTURE TODO: Figure out async tasks...
                    pass
                    # stat = self.updateStampStatsAsync(stampId)
            popularStampIds = self._stampDB.getPopularStampIds(entityId=entityId, limit=1000)

        popularStamps = self._stampDB.getStamps(popularStampIds)
        popularStamps.sort(key=lambda x: popularStampIds.index(x.stamp_id))
        popularStampIds = map(lambda x: x.stamp_id, popularStamps)
        popularUserIds = map(lambda x: x.user.user_id, popularStamps)
        popularStampStats = self._stampDB.getStatsForStamps(popularStampIds)

        if len(popularStampIds) != len(popularUserIds):
            logs.warning("%s: Length of popularStampIds doesn't equal length of popularUserIds" % entityId)
            raise Exception

        numTodos = self._todoDB.countTodosFromEntityId(entityId)
        
        aggStampScore = 0

        for stampStat in popularStampStats:
            if stampStat.score is not None:
                aggStampScore += stampStat.score

        popularity = (1 * numTodos) + (1 * aggStampScore)

        # Entity Quality is a mixture of having an image and having enrichment
        if entity.kind == 'other':
            quality = 0.1
        else:
            quality = 0.6
        
            # Check if entity has an image (places don't matter)
            if entity.kind != 'place':
                if entity.images is None:
                    quality -= 0.3

            # Places
            if entity.kind == 'place':
                if entity.sources.googleplaces_id is None:
                    quality -= 0.3
                if entity.formatted_address is None:
                    quality -= 0.1
                if entity.sources.singleplatform_id is not None:
                    quality += 0.2
                if entity.sources.opentable_id is not None:
                    quality += 0.1


            # Music 
            if entity.isType('track') or entity.isType('album') or entity.isType('artist'):
                
                if entity.sources.itunes_id is None:
                    quality -= 0.3
                if entity.sources.spotify_id is not None: 
                    quality += 0.15
                if entity.sources.rdio_id is not None:
                    quality += 0.15

                if entity.isType('track'):
                    if entity.artists is None:
                        quality -= 0.1
                    if entity.albums is None:
                        quality -= 0.05

                elif entity.isType('artist'):
                    if entity.tracks is None:
                        quality -= 0.1
                    if entity.albums is None:
                        quality -= 0.05

                elif entity.isType('album'):
                    if entity.artists is None:
                        quality -= 0.1
                    if entity.tracks is None:
                        quality -= 0.1

            # Movies and TV
            if entity.isType('movie'):

                if entity.sources.tmdb_id is None:
                    quality -= 0.3
                if entity.sources.itunes_id is not None:
                    quality += 0.2
                if entity.sources.netflix_id is not None:
                    quality += 0.1

            if entity.isType('tv'):
                if entity.sources.thetvdb_id is None:
                    quality -= 0.15
                if entity.sources.netflix_id is not None:
                    quality += 0.2

            # Books
            if entity.isType('book'):

                if entity.sources.amazon_id is None:
                    quality -= 0.2
                if entity.sources.itunes_id is not None:
                    quality += 0.1

            # Apps
            if entity.isType('app'):

                if entity.sources.itunes_url is None:
                    quality -= 0.4
                else:
                    quality += 0.1


        if quality > 1.0:
            logs.warning("Quality score greater than 1 for entity %s" % entityId)
            quality = 1.0

        score = max(quality, quality * popularity)

        stats = EntityStats()
        stats.entity_id = entity.entity_id
        stats.num_stamps = numStamps
        stats.popular_users = popularUserIds
        stats.popular_stamps = popularStampIds
        stats.popularity = popularity
        stats.quality = quality
        stats.score = score
        stats.kind = entity.kind
        stats.types = entity.types
        if entity.kind == 'place' and entity.coordinates is not None:
            stats.lat = entity.coordinates.lat
            stats.lng = entity.coordinates.lng
        self._entityDB.saveEntityStats(stats)

        return stats

    def updateTombstonedEntityReferencesAsync(self, oldEntityId):
        """
        Basic function to update all references to an entity_id that has been tombstoned.
        """
        oldEntity = self._entityDB.getEntity(oldEntityId)
        if oldEntity.sources.tombstone_id is None:
            logs.info("Short circuit: tombstone_id is 'None' for entity %s" % oldEntityId)
            return
        
        newEntity = self._entityDB.getEntity(oldEntity.sources.tombstone_id)
        newEntityId = newEntity.entity_id
        newEntityMini = newEntity.minimize()

        # Stamps
        stampIds = self._stampDB.getStampIdsForEntity(oldEntityId)
        for stampId in stampIds:
            self._stampDB.updateStampEntity(stampId, newEntityMini)
            r = self.updateStampStatsAsync(stampId)

        # Todos
        todoIds = self._todoDB.getTodoIdsFromEntityId(oldEntityId)
        for todoId in todoIds:
            self._todoDB.updateTodoEntity(todoId, newEntityMini)

        self.updateEntityStatsAsync(newEntityId)
