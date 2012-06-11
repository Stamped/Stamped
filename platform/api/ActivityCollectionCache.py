#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


from ACollectionCache                           import ACollectionCache
from utils                                      import lazyProperty

class ActivityCollectionCache(ACollectionCache):

    def __init__(self, api, cacheBlockSize=50, cacheBufferSize=20):
        self.api = api
        ACollectionCache.__init__(self, 'activity')

    def _getFromDB(self, limit, before=None, **kwargs):
        final = False

        authUserId = kwargs['authUserId']

        params = {}
        if 'before' in kwargs and kwargs['before'] is not None:
            params['before'] = kwargs['before']
        params['limit'] = limit

        distance = kwargs.get('distance', 0)
        if distance > 0:
            params['verbs'] = ['comment', 'like', 'todo', 'restamp', 'follow']
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
                # Exclude the item if it is in the user's personal feed, unless it is a 'follow' item.  In that case,
                #  remove the user as an object and ensure there are still other users targeted by the item
                isInPersonalFeed = item.activity_id in overlappingActivityIds
                if isInPersonalFeed and item.verb in ['comment', 'like',  'todo', 'restamp' ]:
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

        return activityData, final