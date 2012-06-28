#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


import logs, time

from ACollectionCache                           import ACollectionCache
from utils                                      import lazyProperty

class ActivityCollectionCache(ACollectionCache):

    def __init__(self, api, cacheBlockSize=50, cacheBufferSize=20):
        self.api = api
        ACollectionCache.__init__(self, 'activity')

    def _getFromDB(self, limit, before=None, **kwargs):
        t0 = time.time()
        t1 = t0

        final = False

        authUserId = kwargs['authUserId']

        params = {}
        if before is not None:
            params['before'] = before
        params['limit'] = limit

        scope = kwargs.get('scope', 'me')
        if scope == 'friends':
            params['verbs'] = ['comment', 'like', 'todo', 'follow']
            friends = self.api._friendshipDB.getFriends(authUserId)
            activityData = []

            # Get activities where friends are a subject member
            dirtyActivityData = self.api._activityDB.getActivityForUsers(friends, **params)
            if len(dirtyActivityData) < limit:
                final = True
            activityItemIds = [item.activity_id for item in dirtyActivityData]
            # Find activity items for friends that also appear in personal feed
            personalActivityIds = self.api._activityDB.getActivityIdsForUser(authUserId, **params)
            overlappingActivityIds =  list(set(personalActivityIds).intersection(set(activityItemIds)))

            for item in dirtyActivityData:
                # Exclude the item if it is in the user's 0personal feed, unless it is a 'follow' item.  In that case,
                #  remove the user as an object and ensure there are still other users targeted by the item
                isInPersonalFeed = item.activity_id in overlappingActivityIds
                if isInPersonalFeed and item.verb in ['comment', 'like',  'todo', 'credit' ]:
                    continue
                elif isInPersonalFeed and item.verb in ['follow']:
                    assert(item.objects is not None and authUserId in item.objects.user_ids)
                    newUserIds = list(item.objects.user_ids)
                    newUserIds.remove(authUserId)
                    item.objects.user_ids = newUserIds
                    if len(item.objects.user_ids) == 0:
                        continue

                item.subjects = list(set(item.subjects).intersection(set(friends)))
                assert(len(item.subjects) > 0)
                activityData.append(item)
        else:
            activityData = self.api._activityDB.getActivity(authUserId, **params)
            if len(activityData) < limit:
                final = True

        logs.debug('Time for getFromDB: %s' % (time.time() - t1))
        t1 = time.time()

        return activityData, final

    def _pruneActivityItems(self, activityItems):
        prunedItems = []
        for item in activityItems:
        #            if item.verb == 'follow':
        #                continue
            prunedItems.append(item)
        return prunedItems