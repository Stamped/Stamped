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
import time
import logs

from db.userdb import UserDB
from db.stampdb import StampDB
from db.commentdb import CommentDB
from db.activitydb import ActivityDB
from db.friendshipdb import FriendshipDB

from utils import lazyProperty, LoggingThreadPool

from api.helpers import APIObject
from api.stampapi import StampAPI
from api.activityapi import ActivityAPI


class CommentAPI(APIObject):

    def __init__(self):
        APIObject.__init__(self)

    @lazyProperty
    def _userDB(self):
        return UserDB()
    
    @lazyProperty
    def _stampDB(self):
        return StampDB()
    
    @lazyProperty
    def _commentDB(self):
        return CommentDB()
    
    @lazyProperty
    def _activityDB(self):
        return ActivityDB()
    
    @lazyProperty
    def _friendshipDB(self):
        return FriendshipDB()

    @lazyProperty
    def _stamps(self):
        return StampAPI()

    @lazyProperty
    def _activity(self):
        return ActivityAPI()


    def addComment(self, authUserId, stampId, blurb):
        user    = self._userDB.getUser(authUserId)
        stamp   = self._stampDB.getStamp(stampId)
        stamp   = self._stamps.enrichStampObjects(stamp, authUserId=authUserId)

        # Verify user has the ability to comment on the stamp
        friendship              = Friendship()
        friendship.user_id      = stamp.user.user_id
        friendship.friend_id    = user.user_id

        # Check if stamp is private; if so, must be a follower
        if stamp.user.privacy == True:
            if not self._friendshipDB.checkFriendship(friendship):
                raise StampedAddCommentPermissionsError("Insufficient privileges to add comment")

        # Check if block exists between user and stamp owner
        if self._friendshipDB.blockExists(friendship) == True:
            raise StampedBlockedUserError("Block exists")

        # Build comment
        comment                     = Comment()
        comment.stamp_id            = stamp.stamp_id
        comment.blurb               = blurb

        userMini                    = UserMini()
        userMini.user_id            = user.user_id
        comment.user                = userMini

        timestamp                   = BasicTimestamp()
        timestamp.created           = datetime.datetime.utcnow()
        comment.timestamp           = timestamp

        # Add the comment data to the database
        comment = self._commentDB.addComment(comment)

        # Add full user object back
        comment.user = user.minimize()

        # Call async process
        payload = {
            'authUserId': user.user_id,
            'stampId': stampId,
            'commentId': comment.comment_id,
        }
        self.call_task(self.addCommentAsync, payload)

        return comment

    def addCommentAsync(self, authUserId, stampId, commentId):
        delay = 1
        while True:
            try:
                comment = self._commentDB.getComment(commentId)
                stamp   = self._stampDB.getStamp(stampId)
                stamp   = self._stamps.enrichStampObjects(stamp, authUserId=authUserId)
                break
            except StampedDocumentNotFoundError:
                if delay > 60:
                    raise
                time.sleep(delay)
                delay *= 2

        # Add activity for mentioned users
        mentionedUserIds = set()
        ### RESTRUCTURE TODO
        mentions = self._stamps.extractMentions(comment.blurb)
        if len(mentions) > 0:
            mentionedUsers = self._userDB.lookupUsers(screenNames=list(mentions))
            for user in mentionedUsers:
                if user.user_id != authUserId:
                    mentionedUserIds.add(user.user_id)
        if len(mentionedUserIds) > 0:
            self._activity.addMentionActivity(authUserId, list(mentionedUserIds), stamp.stamp_id, comment.comment_id)

        # Add activity for stamp owner
        commentedUserIds = set()
        if stamp.user.user_id not in mentionedUserIds and stamp.user.user_id != authUserId:
            commentedUserIds.add(stamp.user.user_id)
        self._activity.addCommentActivity(authUserId, list(commentedUserIds), stamp.stamp_id, comment.comment_id)

        repliedUserIds = set()
        # Add activity for previous commenters
        for prevComment in self._commentDB.getCommentsForStamp(stamp.stamp_id, limit=20):
            repliedUserId = prevComment.user.user_id

            if repliedUserId not in commentedUserIds.union(mentionedUserIds).union(repliedUserIds) \
                and repliedUserId != authUserId:

                # Check if block exists between user and previous commenter
                friendship              = Friendship()
                friendship.user_id      = authUserId
                friendship.friend_id    = repliedUserId

                if self._friendshipDB.blockExists(friendship) == False:
                    repliedUserIds.add(repliedUserId)

        if len(repliedUserIds) > 0:
            self._activity.addReplyActivity(authUserId, list(repliedUserIds), stamp.stamp_id, comment.comment_id)

        # Update stamp stats
        self.call_task(self._stamps.updateStampStatsAsync, {'stampId': stamp.stamp_id})

    def removeComment(self, authUserId, commentId):
        comment = self._commentDB.getComment(commentId)

        # Only comment owner and stamp owner can delete comment
        if comment.user.user_id != authUserId:
            stamp = self._stampDB.getStamp(comment.stamp_id)
            if stamp.user.user_id != authUserId:
                raise StampedRemoveCommentPermissionsError("Insufficient privileges to remove comment")

        # Remove comment
        self._commentDB.removeComment(comment.comment_id)

        # Remove activity?
        self._activityDB.removeCommentActivity(authUserId, comment.comment_id)

        # Update stamp stats
        self.call_task(self._stamps.updateStampStatsAsync, {'stampId': comment.stamp_id})

        return True

    def getComments(self, stampId, authUserId, before=None, limit=20, offset=0):
        stamp = self._stampDB.getStamp(stampId)

        # Check privacy of stamp
        if stamp.user.privacy == True:
            friendship              = Friendship()
            friendship.user_id      = stamp.user.user_id
            friendship.friend_id    = authUserId

            if not self._friendshipDB.checkFriendship(friendship):
                raise StampedViewCommentPermissionsError("Insufficient privileges to view comments")

        commentData = self._commentDB.getCommentsForStamp(stamp.stamp_id, before=before, limit=limit, offset=offset)

        # Get user objects
        userIds = {}
        for comment in commentData:
            userIds[comment.user.user_id] = 1

        users = self._userDB.lookupUsers(userIds.keys(), None)

        for user in users:
            userIds[user.user_id] = user.minimize()

        comments = []
        for comment in commentData:
            if userIds[comment.user.user_id] == 1:
                msg = 'Unable to get user_id %s for comment_id %s' % (comment.user.user_id, comment.comment_id)
                logs.warning(msg)
            else:
                comment.user = userIds[comment.user.user_id]
                comments.append(comment)

        return comments


