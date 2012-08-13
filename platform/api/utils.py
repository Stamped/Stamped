#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import api.Globals

from api_old.Schemas import *

import utils
import datetime
import time
import logs

from db.userdb import UserDB
from db.likedb import LikeDB
from db.tododb import TodoDB
from db.stampdb import StampDB
from db.entitydb import EntityDB
from db.commentdb import CommentDB

def enrich_stamp_objects(stampObjects, **kwargs):

    t0 = time.time()
    t1 = t0

    # Define databases
    ### TODO: Make this lazy?
    _userDB = UserDB()
    _todoDB = TodoDB()
    _likeDB = LikeDB()
    _stampDB = StampDB()
    _entityDB = EntityDB()
    _commentDB = CommentDB()

    previewLength = kwargs.pop('previews', 10)
    mini        = kwargs.pop('mini', True)

    authUserId  = kwargs.pop('authUserId', None)
    entityIds   = kwargs.pop('entityIds', {})
    userIds     = kwargs.pop('userIds', {})

    singleStamp = False
    if not isinstance(stampObjects, list):
        singleStamp = True
        stampObjects = [stampObjects]

    stampIds = {}
    for stamp in stampObjects:
        stampIds[stamp.stamp_id] = stamp

    statsList = _stampDB.getStatsForStamps(stampIds.keys())
    stats = {}
    for stat in statsList:
        stats[stat.stamp_id] = stat

    t1 = time.time()

    """
    ENTITIES

    Enrich the underlying entity object for all stamps
    """
    allEntityIds = set()

    for stamp in stampObjects:
        allEntityIds.add(stamp.entity.entity_id)

    # Enrich missing entity ids
    missingEntityIds = allEntityIds.difference(set(entityIds.keys()))
    if mini:
        entities = _entityDB.getEntityMinis(list(missingEntityIds))
    else:
        entities = _entityDB.getEntities(list(missingEntityIds))

    for entity in entities:
        if entity.sources.tombstone_id is not None:
            # Convert to newer entity
            replacement = _entityDB.getEntityMini(entity.sources.tombstone_id)
            entityIds[entity.entity_id] = replacement
        else:
            entityIds[entity.entity_id] = entity

    logs.debug('Time for getEntities: %s' % (time.time() - t1))
    t1 = time.time()

    """
    STAMPS

    Enrich the underlying stamp objects for credit received
    """
    underlyingStampIds      = {}
    allUnderlyingStampIds   = set()

    for stat in stats.values():
        if stat.preview_credits is not None:
            for credit in stat.preview_credits[:previewLength]:
                allUnderlyingStampIds.add(credit)

    # Enrich underlying stamp ids
    underlyingStamps = _stampDB.getStamps(list(allUnderlyingStampIds))

    for stamp in underlyingStamps:
        underlyingStampIds[stamp.stamp_id] = stamp

    logs.debug('Time for getStamps: %s' % (time.time() - t1))
    t1 = time.time()

    """
    COMMENTS

    Pull in the comment objects for each stamp
    """
    allCommentIds   = set()
    commentIds      = {}

    for stat in stats.values():
        # Comments
        if stat.preview_comments is not None:
            for commentId in stat.preview_comments[:previewLength]:
                allCommentIds.add(commentId)

    comments = _commentDB.getComments(list(allCommentIds))

    for comment in comments:
        commentIds[comment.comment_id] = comment

    logs.debug('Time for getComments: %s' % (time.time() - t1))
    t1 = time.time()

    """
    USERS

    Enrich the underlying user objects. This includes:
    - Stamp owner
    - Likes
    - To-Dos
    - Credit received (restamps)
    - Credit given
    - Comments
    """
    allUserIds    = set()

    for stamp in stampObjects:
        # Stamp owner
        allUserIds.add(stamp.user.user_id)

        # Credit given
        if stamp.credits is not None:
            for credit in stamp.credits:
                allUserIds.add(credit.user.user_id)

    for k, v in commentIds.items():
        allUserIds.add(v.user.user_id)

    for stat in stats.values():
        # Likes
        if stat.preview_likes is not None:
            for like in stat.preview_likes[:previewLength]:
                allUserIds.add(like)

        # To-Dos
        if stat.preview_todos is not None:
            for todo in stat.preview_todos[:previewLength]:
                allUserIds.add(todo)

    for stampId, stamp in underlyingStampIds.iteritems():
        # Credit received
        allUserIds.add(stamp.user.user_id)

    # Enrich missing user ids
    missingUserIds = allUserIds.difference(set(userIds.keys()))
    users = _userDB.getUserMinis(list(missingUserIds))

    for user in users:
        userIds[user.user_id] = user

    logs.debug('Time for getUserMinis: %s' % (time.time() - t1))
    t1 = time.time()


    if authUserId:
        ### TODO: Intelligent matching with stampId
        # Todos
        todos = _todoDB.getTodoEntityIds(authUserId)

        ### TODO: Intelligent matching with stampId
        # Likes
        likes = _likeDB.get_for_user(authUserId)

        logs.debug('Time for authUserId queries: %s' % (time.time() - t1))
        t1 = time.time()

    """
    APPLY DATA
    """

    stamps = []

    for stamp in stampObjects:
        try:
            stamp.entity = entityIds[stamp.entity.entity_id]
            stamp.user = userIds[stamp.user.user_id]

            # Credit
            credits = []
            if stamp.credits is not None:
                for credit in stamp.credits:
                    try:
                        item = StampPreview()
                        item.user = userIds[str(credit.user.user_id)]
                        item.stamp_id = credit.stamp_id
                        credits.append(item)
                    except KeyError:
                        logs.warning("Key error for credit (stamp_id=%s, credit_id=%s)" % \
                            (stamp.stamp_id, credit.stamp_id))
                stamp.credits = credits

            # Previews
            previews = Previews()
            try:
                stat = stats[stamp.stamp_id]
            except KeyError:
                stat = None

            if stat is not None:
                # Comments
                commentPreviews = []
                if stat.preview_comments is not None:
                    for commentId in stat.preview_comments[:previewLength]:
                        try:
                            comment = commentIds[str(commentId)]
                            try:
                                comment.user = userIds[str(comment.user.user_id)]
                            except KeyError:
                                logs.warning("Key error for user (user_id = %s)" % comment.user.user_id)
                                raise
                            commentPreviews.append(comment)
                        except KeyError:
                            logs.warning("Key error for comment (comment_id = %s)" % commentId)
                            logs.debug("Stamp: %s" % stamp)
                            continue
                previews.comments = commentPreviews

                # Likes
                likePreviews = []
                if stat.preview_likes is not None:
                    for userId in stat.preview_likes[:previewLength]:
                        try:
                            likePreviews.append(userIds[str(userId)])
                        except KeyError:
                            logs.warning("Key error for like (user_id = %s)" % userId)
                            logs.debug("Stamp: %s" % stamp)
                            continue
                previews.likes = likePreviews

                # Todos
                todoPreviews = []
                if stat.preview_todos is not None:
                    for userId in stat.preview_todos[:previewLength]:
                        try:
                            todoPreviews.append(userIds[str(userId)])
                        except KeyError:
                            logs.warning("Key error for todo (user_id = %s)" % userId)
                            logs.debug("Stamp: %s" % stamp)
                            continue
                previews.todos = todoPreviews

                # Credits
                creditPreviews = []
                if stat.preview_credits is not None:
                    for i in stat.preview_credits[:previewLength]:
                        try:
                            credit = underlyingStampIds[str(i)]
                            stampPreview = StampPreview()
                            stampPreview.user = userIds[str(credit.user.user_id)]
                            stampPreview.stamp_id = i
                            creditPreviews.append(stampPreview)
                        except KeyError, e:
                            logs.warning("Key error for credit (stamp_id = %s)" % i)
                            logs.warning("Error: %s" % e)
                            continue
                previews.credits = creditPreviews

                # Stats
                stamp.stats.num_comments    = stat.num_comments 
                stamp.stats.num_todos       = stat.num_todos 
                stamp.stats.num_credit      = stat.num_credits
                stamp.stats.num_likes       = stat.num_likes 

            stamp.previews = previews

            # User-specific attributes
            if authUserId:
                if stamp.attributes is None:
                    stamp.attributes = StampAttributesSchema()

                # Mark as todo
                stamp.attributes.is_todo = stamp.entity.entity_id in todos

                # Mark as liked
                stamp.attributes.is_liked =  stamp.stamp_id in likes

            stamps.append(stamp)

        except KeyError, e:
            logs.warning("Fatal key error: %s" % e)
            logs.debug("Stamp: %s" % stamp)
            continue
        except Exception:
            raise

    logs.debug('Time for stamp iteration: %s' % (time.time() - t1))

    logs.debug('TOTAL TIME: %s' % (time.time() - t0))

    if singleStamp:
        return stamps[0]

    return stamps