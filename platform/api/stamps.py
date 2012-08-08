#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

from api_old.Schemas import *
from api_old.S3ImageDB import S3ImageDB

import utils
import datetime
import time
import logs

from db.mongodb.MongoUserCollection import MongoUserCollection
from db.mongodb.MongoTodoCollection import MongoTodoCollection
from db.mongodb.MongoStampCollection import MongoStampCollection, MongoStampStatsCollection
from db.mongodb.MongoEntityCollection import MongoEntityCollection, MongoEntityStatsCollection
from db.mongodb.MongoCommentCollection import MongoCommentCollection
from db.mongodb.MongoAccountCollection import MongoAccountCollection
from db.mongodb.MongoActivityCollection import MongoActivityCollection
from db.mongodb.MongoFriendshipCollection import MongoFriendshipCollection

from utils import lazyProperty, LoggingThreadPool
from search.AutoCompleteIndex import normalizeTitle, loadIndexFromS3, emptyIndex, pushNewIndexToS3
from libs.Memcache import generateKeyFromDictionary

from api.module import APIObject
from api.entities import Entities
from api.users import Users
from api.accounts import Accounts
from api.activity import Activity
from api.linkedaccountapi import LinkedAccountAPI


CREDIT_BENEFIT  = 1 # Per credit


class Stamps(APIObject):

    def __init__(self):
        APIObject.__init__(self)

    @lazyProperty
    def _userDB(self):
        return MongoUserCollection()

    @lazyProperty
    def _todoDB(self):
        return MongoTodoCollection()
    
    @lazyProperty
    def _stampDB(self):
        return MongoStampCollection()

    @lazyProperty
    def _entityDB(self):
        return MongoEntityCollection()
    
    @lazyProperty
    def _commentDB(self):
        return MongoCommentCollection()
    
    @lazyProperty
    def _accountDB(self):
        return MongoAccountCollection()
    
    @lazyProperty
    def _activityDB(self):
        return MongoActivityCollection()

    @lazyProperty
    def _friendshipDB(self):
        return MongoFriendshipCollection()
    
    @lazyProperty
    def _stampStatsDB(self):
        return MongoStampStatsCollection()

    @lazyProperty
    def _entityStatsDB(self):
        return MongoEntityStatsCollection()
    

    ### RESTRUCTURE TODO
    @lazyProperty
    def _imageDB(self):
        return S3ImageDB()


    @lazyProperty
    def _entities(self):
        return Entities()

    @lazyProperty
    def _users(self):
        return Users()

    @lazyProperty
    def _accounts(self):
        return Accounts()

    @lazyProperty
    def _activity(self):
        return Activity()

    @lazyProperty
    def _linked_account_api(self):
        return LinkedAccountAPI()


    @lazyProperty
    def _user_regex(self):
        return re.compile(r'(?<![a-zA-Z0-9_])@([a-zA-Z0-9+_]{1,20})(?![a-zA-Z0-9_])', re.IGNORECASE)

    def extractMentions(self, text):
        if text is None:
            return set()

        screenNames = set()

        # Extract screen names with regex
        for user in self._user_regex.finditer(text):
            screenNames.add(str(user.groups()[0]).lower())

        # Match screen names to users
        users = self._userDB.lookupUsers(screenNames=list(screenNames))
        validScreenNames = set(map(lambda x: str(x.screen_name).lower(), users))

        # Log any invalid screen names
        if len(screenNames) > len(validScreenNames):
            logs.warning("Mentioned screen names not found: %s" % screenNames.difference(validScreenNames))
            logs.debug("Text: %s" % text)

        return validScreenNames

    def _extractCredit(self, creditData, entityId, stampOwner=None):
        creditedUserIds = set()
        credit = []

        if creditData is not None and isinstance(creditData, list):
            ### TODO: Filter out non-ASCII data for credit
            creditedScreenNames = []
            for creditedScreenName in creditData:
                if utils.validate_screen_name(creditedScreenName):
                    creditedScreenNames.append(creditedScreenName)

            creditedUsers = self._userDB.lookupUsers(None, creditedScreenNames)

            for creditedUser in creditedUsers:
                userId = creditedUser.user_id
                # User cannot give themselves credit!
                if stampOwner is not None and userId == stampOwner:
                    continue
                # User can't give credit to the same person twice
                if userId in creditedUserIds:
                    continue

                result              = StampPreview()
                result.user         = creditedUser.minimize()

                # Assign credit
                creditedStamp = self._stampDB.getStampFromUserEntity(userId, entityId)
                if creditedStamp is not None:
                    result.stamp_id = creditedStamp.stamp_id

                credit.append(result)
                creditedUserIds.add(userId)

        ### TODO: How do we handle credited users that have not yet joined?
        if len(credit) > 0:
            return credit

        return []

    def enrichStampObjects(self, stampObjects, **kwargs):
        t0 = time.time()
        t1 = t0

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

        stats = self.getStampStats(stampIds.keys())

        logs.debug('Time for getStatsForStamps: %s' % (time.time() - t1))
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
            entities = self._entityDB.getEntityMinis(list(missingEntityIds))
        else:
            entities = self._entityDB.getEntities(list(missingEntityIds))

        for entity in entities:
            if entity.sources.tombstone_id is not None:
                # Convert to newer entity
                replacement = self._entityDB.getEntityMini(entity.sources.tombstone_id)
                entityIds[entity.entity_id] = replacement
                # Call async process to update references
                self.call_task(self.updateTombstonedEntityReferencesAsync, {'oldEntityId': entity.entity_id})
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
        underlyingStamps = self._stampDB.getStamps(list(allUnderlyingStampIds))

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

        comments = self._commentDB.getComments(list(allCommentIds))

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
        users = self._userDB.getUserMinis(list(missingUserIds))

        for user in users:
            userIds[user.user_id] = user

        logs.debug('Time for getUserMinis: %s' % (time.time() - t1))
        t1 = time.time()


        if authUserId:
            ### TODO: Intelligent matching with stampId
            # Todos
            todos = self._todoDB.getTodoEntityIds(authUserId)

            ### TODO: Intelligent matching with stampId
            # Likes
            likes = self._stampDB.getUserLikes(authUserId)

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
                                    logs.warning("Key error for user (user_id = %s)" % userId)
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

                else:
                    self.call_task(self.updateStampStatsAsync, {'stampId': stamp.stamp_id})

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

    def getStampBadges(self, stamp):
        userId = stamp.user.user_id
        entityId = stamp.entity.entity_id
        badges  = []

        if stamp.stats.stamp_num == 1:
            badge           = Badge()
            badge.user_id   = userId
            badge.genre     = "user_first_stamp"
            badges.append(badge)

        try:
            stats = self._entityStatsDB.getEntityStats(entityId)
            if stats.num_stamps == 0:
                badge           = Badge()
                badge.user_id   = userId
                badge.genre     = "entity_first_stamp"
                badges.append(badge)

        except StampedUnavailableError:
            # This can happen if the stamp has just been created and it's a new entity
            pass

        return badges

    def addStamp(self, authUserId, entityRequest, data):
        user        = self._userDB.getUser(authUserId)
        entity      = self._entities.getEntityFromRequest(entityRequest)

        entityIds   = { entity.entity_id : entity }

        blurbData   = data.pop('blurb',  None)
        creditData  = data.pop('credits', None)

        imageData   = data.pop('image',  None)
        imageUrl    = data.pop('temp_image_url',    None)
        imageWidth  = data.pop('temp_image_width',  None)
        imageHeight = data.pop('temp_image_height', None)

        now         = datetime.datetime.utcnow()

        # Check if the user has already stamped this entity
        stampExists = self._stampDB.checkStamp(user.user_id, entity.entity_id)

        # Check to make sure the user has stamps left
        if not stampExists and user.stats.num_stamps_left <= 0:
            raise StampedOutOfStampsError("No more stamps remaining")

        # Build content
        content = StampContent()
        content.content_id = utils.generateUid()
        timestamp = BasicTimestamp()
        timestamp.created = now  #time.gmtime(utils.timestampFromUid(content.content_id))
        content.timestamp = timestamp
        if blurbData is not None:
            content.blurb = blurbData.strip()

        ### TODO: Verify external image exists via head request?

        # Create the stamp or get the stamp object so we can use its stamp_id for image filenames
        if stampExists:
            stamp = self._stampDB.getStampFromUserEntity(user.user_id, entity.entity_id)
        else:
            stamp = Stamp()

        # Update content if stamp exists
        if stampExists:
            stamp.timestamp.stamped     = now
            stamp.timestamp.modified    = now
            stamp.stats.num_blurbs      = stamp.stats.num_blurbs + 1 if stamp.stats.num_blurbs is not None else 2

            contents                    = list(stamp.contents)
            contents.append(content)
            stamp.contents              = contents

            # Extract credit
            if creditData is not None:
                newCredits = self._extractCredit(creditData, entity.entity_id, stampOwner=authUserId)
                if stamp.credits is None:
                    stamp.credits = newCredits
                else:
                    creditedUserIds = set()
                    credits = list(stamp.credits)
                    for credit in stamp.credits:
                        creditedUserIds.add(credit.user.user_id)
                    for credit in newCredits:
                        if credit.user.user_id not in creditedUserIds:
                            credits.append(credit)
                            creditedUserIds.add(credit.user.user_id)
                    stamp.credits = credits

            stamp = self._stampDB.updateStamp(stamp)

        # Build new stamp
        else:
            stamp.entity                = entity
            stamp.contents              = [ content ]

            userMini                    = UserMini()
            userMini.user_id            = user.user_id
            stamp.user                  = userMini

            stats                       = StampStatsSchema()
            stats.num_blurbs            = 1
            stats.stamp_num             = user.stats.num_stamps_total + 1
            stamp.stats                 = stats

            timestamp                   = StampTimestamp()
            timestamp.created           = now
            timestamp.stamped           = now
            timestamp.modified          = now
            stamp.timestamp             = timestamp

            stamp.badges                = self.getStampBadges(stamp)

            # Extract credit
            if creditData is not None:
                stamp.credits = self._extractCredit(creditData, entity.entity_id, stampOwner=authUserId)

            stamp = self._stampDB.addStamp(stamp)

        if imageUrl is not None:
            payload = {
                'imageUrl': imageUrl,
                'stampId': stamp.stamp_id,
                'contentId': content.content_id,
            }
            self.call_task(self.addResizedStampImagesAsync, payload)

        # Enrich linked user, entity, todos, etc. within the stamp
        ### TODO: Pass userIds (need to scrape existing credited users)
        stamp = self.enrichStampObjects(stamp, authUserId=authUserId, entityIds=entityIds)
        logs.debug('Stamp exists: %s' % stampExists)

        if not stampExists:
            # Add a reference to the stamp in the user's collection
            self._stampDB.addUserStampReference(user.user_id, stamp.stamp_id)
            self._stampDB.addInboxStampReference([ user.user_id ], stamp.stamp_id)

            # Update user stats
            self._userDB.updateUserStats(authUserId, 'num_stamps',       increment=1)
            self._userDB.updateUserStats(authUserId, 'num_stamps_left',  increment=-1)
            self._userDB.updateUserStats(authUserId, 'num_stamps_total', increment=1)
            distribution = self._users.getUserStampDistribution(authUserId)
            self._userDB.updateDistribution(authUserId, distribution)

        # Generate activity and stamp pointers
        payload = {
            'authUserId': user.user_id,
            'stampId': stamp.stamp_id,
            'imageUrl': imageUrl,
            'stampExists': stampExists,
        }
        self.call_task(self.addStampAsync, payload)
        
        return stamp
    
    def addStampAsync(self, authUserId, stampId, imageUrl, stampExists=False):
        # TODO(geoff): refactor retry logic to a common place.
        delay = 1
        while True:
            try:
                stamp   = self._stampDB.getStamp(stampId)
                entity  = self._entityDB.getEntity(stamp.entity.entity_id)
                break
            except StampedDocumentNotFoundError:
                if delay > 60:
                    raise
                time.sleep(delay)
                delay *= 2

        if not stampExists:
            # Add references to the stamp in all relevant inboxes
            followers = self._friendshipDB.getFollowers(authUserId)
            self._stampDB.addInboxStampReference(followers, stampId)

            # If stamped entity is on the to do list, mark as complete
            try:
                self._todoDB.completeTodo(entity.entity_id, authUserId)
                if entity.entity_id != stamp.entity.entity_id:
                    self._todoDB.completeTodo(stamp.entity.entity_id, authUserId)
            except Exception:
                pass
        
        creditedUserIds = set()
        # Give credit
        if stamp.credits is not None and len(stamp.credits) > 0:
            for item in stamp.credits:
                if item.user.user_id == authUserId:
                    continue

                # Check if the user has been given credit previously
                if self._stampDB.checkCredit(item.user.user_id, stamp):
                    continue

                # Assign credit
                self._stampDB.giveCredit(item.user.user_id, stamp.stamp_id, stamp.user.user_id)
                creditedUserIds.add(item.user.user_id)

                # Update credited user stats
                self._userDB.updateUserStats(item.user.user_id, 'num_credits',     increment=1)
                self._userDB.updateUserStats(item.user.user_id, 'num_stamps_left', increment=CREDIT_BENEFIT)

                # Update stamp stats if stamp exists
                creditedStamp = self._stampDB.getStampFromUserEntity(item.user.user_id, entity.entity_id)
                if creditedStamp is not None:
                    self.call_task(self.updateStampStatsAsync, {'stampId': creditedStamp.stamp_id})

        # Note: No activity should be generated for the user creating the stamp

        # Add activity for credited users
        if len(creditedUserIds) > 0:
            self._activity.addCreditActivity(authUserId, list(creditedUserIds), stamp.stamp_id, CREDIT_BENEFIT)
        # Add activity for mentioned users
        blurb = stamp.contents[-1].blurb
        if blurb is not None:
            mentionedUserIds = set()
            mentions = self.extractMentions(blurb)
            if len(mentions) > 0:
                mentionedUsers = self._userDB.lookupUsers(screenNames=list(mentions))
                for user in mentionedUsers:
                    if user.user_id != authUserId and user.user_id not in creditedUserIds:
                        mentionedUserIds.add(user.user_id)
            if len(mentionedUserIds) > 0:
                self._activity.addMentionActivity(authUserId, list(mentionedUserIds), stamp.stamp_id)
        # Update entity stats
        self.call_task(self._entities.updateEntityStatsAsync, {'entityId': stamp.entity.entity_id})

        # Update stamp stats
        self.call_task(self.updateStampStatsAsync, {'stampId': stamp.stamp_id})

        # Post to Facebook Open Graph if enabled
        if not stampExists:
            share_settings = self._accounts.getOpenGraphShareSettings(authUserId)
            if share_settings is not None and share_settings.share_stamps:
                payload = {
                    'auth_user_id': authUserId,
                    'stamp_id': stamp.stamp_id, 
                    'image_url': imageUrl,
                }
                self.call_task(self._linked_account_api.post_og_async, payload)
    
    def addResizedStampImagesAsync(self, imageUrl, stampId, contentId):
        assert imageUrl is not None, "stamp image url unavailable!"

        maxSize = (960, 960)
        supportedSizes   = {
            'ios1x'  : (200, None),
            'ios2x'  : (400, None),
            'web'    : (580, None),
            'mobile' : (572, None),
            }

        retry_count = 0
        max_retries = 5
        while True:
            try:
                # Get stamp using stampId
                stamp = self._stampDB.getStamp(stampId)

                # Find the blurb using the contentId to generate an imageId
                for i, c in enumerate(stamp.contents):
                    if c.content_id == contentId:
                        imageId = "%s-%s" % (stamp.stamp_id, int(time.mktime(c.timestamp.created.timetuple())))
                        contentsKey = i
                        break
                else:
                    raise StampedInputError('Could not find stamp blurb for image resizing')

                # Generate image
                sizes = self._imageDB.addResizedStampImages(imageUrl, imageId, maxSize, supportedSizes)
                break
            except (StampedInputError, StampedDocumentNotFoundError, urllib2.HTTPError):
                pass

            retry_count += 1
            if retry_count > max_retries:
                msg = "Unable to connect to add stamp image after %d retries (url=%s, stamp=%s)" % \
                    (max_retries, imageUrl, stampId)
                logs.warning(msg)
                raise 
            time.sleep(5)


        sizes.sort(key=lambda x: x.height, reverse=True)
        image = ImageSchema()
        image.sizes = sizes

        # Update stamp contents with sizes
        contents = list(stamp.contents)
        contents[contentsKey].images = [ image ] # Note: assumes only one image can exist
        stamp.contents = contents
        self._stampDB.updateStamp(stamp)


    def shareStamp(self, authUserId, stampId, serviceName, imageUrl):
        stamp = self.getStamp(stampId)
        account = self.getAccount(authUserId)

        if serviceName == 'facebook':
            if account.linked is None or account.linked.facebook is None \
                or account.linked.facebook.token is None or account.linked.facebook.linked_user_id is None:
                raise StampedLinkedAccountError('Cannot share stamp on facebook, missing necessary linked account information.')
            self._facebook.postToNewsFeed(account.linked.facebook.linked_user_id,
                                          account.linked.facebook.token,
                                          stamp.contents[-1].blurb,
                                          imageUrl)
        else:
            raise StampedNoSharingForLinkedAccountError("Sharing is not implemented for service: %s" % serviceName)
        return stamp

    def updateStamp(self, authUserId, stampId, data):
        raise NotImplementedError

    def removeStamp(self, authUserId, stampId):
        try:
            stamp = self._stampDB.getStamp(stampId)
        except StampedDocumentNotFoundError:
            logs.info("Stamp has already been deleted")
            return True
        
        # Verify user has permission to delete
        if stamp.user.user_id != authUserId:
            raise StampedRemoveStampPermissionsError("Insufficient privileges to remove stamp")

        og_action_id = stamp.og_action_id

        # Remove stamp
        self._stampDB.removeStamp(stamp.stamp_id)
        
        payload = {
            'authUserId': authUserId,
            'stampId': stampId,
            'entityId': stamp.entity.entity_id,
            'credits': stamp.credits,
            'og_action_id': og_action_id,
        }
        self.call_task(self.removeStampAsync, payload)
                
        return True
    
    def _should_regenerate_collage(self, stamp_num):
        # NOTE (travis): disabling collage regeneration for v2 launch triage
        return False
        #return (stamp_num in stamp_num_collage_regeneration)
    
    def removeStampAsync(self, authUserId, stampId, entityId, credits=None, og_action_id=None):
        # Remove from user collection
        self._stampDB.removeUserStampReference(authUserId, stampId)

        ### TODO: Remove from inboxes? Or let integrity checker do that?

        # Remove from stats
        self._stampStatsDB.removeStampStats(stampId)

        ### TODO: Remove from activity? To do? Anything else?

        # Remove comments
        ### TODO: Make this more efficient?
        commentIds = self._commentDB.getCommentIds(stampId)
        for commentId in commentIds:
            # Remove comment
            self._commentDB.removeComment(commentId)

        # Remove activity
        self._activityDB.removeActivityForStamp(stampId)

        # Remove as todo if necessary
        try:
            self._todoDB.completeTodo(entityId, authUserId, complete=False)
        except Exception as e:
            logs.warning(e)

        ### TODO: Remove reference in other people's todos

        # Update user stats
        ### TODO: Do an actual count / update?
        self._userDB.updateUserStats(authUserId, 'num_stamps',      increment=-1)
        self._userDB.updateUserStats(authUserId, 'num_stamps_left', increment=1)

        ### RESTRUCTURE TODO
        distribution = self._users.getUserStampDistribution(authUserId)
        self._userDB.updateDistribution(authUserId, distribution)

        # Update credit stats if credit given
        if credits is not None and len(credits) > 0:
            for item in credits:
                # Only run if user is flagged as credited
                if item.user.user_id is None:
                    continue

                # Assign credit
                self._stampDB.removeCredit(item.user.user_id, stampId, authUserId)

                # Update credited user stats
                self._userDB.updateUserStats(item.user.user_id, 'num_credits', increment=-1)

        # Update entity stats
        self.call_task(self._entities.updateEntityStatsAsync, {'entityId': entityId})

        # Remove OG activity item, if it was created, and if the user still has a linked FB account
        if og_action_id is not None and self._accounts.getOpenGraphShareSettings(authUserId) is not None:
            payload = {
                'auth_user_id': authUserId,
                'og_action_id': og_action_id,
            }
            self.call_task(self._linked_account_api.remove_og_async, payload)

    def getStamp(self, stampId, authUserId=None, enrich=True):
        stamp = self._stampDB.getStamp(stampId)
        if enrich:
            stamp = self.enrichStampObjects(stamp, authUserId=authUserId)

        return stamp

    def getStampFromUser(self, screenName=None, stampNumber=None, userId=None):
        if userId is None:
            userId = self._userDB.getUserByScreenName(screenName).user_id

        stamp = self._stampDB.getStampFromUserStampNum(userId, stampNumber)
        stamp = self.enrichStampObjects(stamp)

        # TODO: if authUserId == stamp.user.user_id, then the privacy should be disregarded
        if stamp.user.privacy == True:
            raise StampedViewStampPermissionsError("Insufficient privileges to view stamp")

        return stamp

    def getStampStats(self, stampIds):
        if isinstance(stampIds, basestring):
            # One stampId
            try:
                stat = self._stampStatsDB.getStampStats(stampIds)
            except (StampedUnavailableError, KeyError):
                stat = None
            return stat

        else:
            # Multiple stampIds
            statsList = self._stampStatsDB.getStatsForStamps(stampIds)
            statsDict = {}
            for stat in statsList:
                statsDict[stat.stamp_id] = stat
            return statsDict

    def updateStampStatsAsync(self, stampId):
        try:
            stamp = self._stampDB.getStamp(stampId)
        except StampedDocumentNotFoundError:
            logs.warning("Stamp not found: %s" % stampId)
            ### TODO: Will returning None cause problems?
            return None

        stats                   = StampStats()
        stats.stamp_id          = stampId
        stats.user_id           = stamp.user.user_id

        MAX_PREVIEW             = 10
        stats.last_stamped      = stamp.timestamp.stamped

        likes                   = self._stampDB.getStampLikes(stampId)
        stats.num_likes         = len(likes)
        likes                   = likes[-MAX_PREVIEW:]
        likes.reverse()
        stats.preview_likes     = likes

        """
        Note: To-Do preview objects are composed of two sources: users that have to-do'd the entity from
        the stamp directly ("direct" to-dos) and users that are following you but have also to-do'd the entity
        ("indirect" to-dos). Direct to-dos are guaranteed and will always show up on the stamp. Indirect to-dos
        are recalculated frequently based on your follower list and can change over time.
        """
        todos                   = self._todoDB.getTodosFromStampId(stamp.stamp_id)
        followers               = self._friendshipDB.getFollowers(stamp.user.user_id)
        followerTodos           = self._todoDB.getTodosFromUsersForEntity(followers, stamp.entity.entity_id, limit=100)
        existingTodos           = set(todos)
        for todo in followerTodos:
            if len(todos) >= 100:
                break
            if todo not in existingTodos:
                todos.append(todo)
                existingTodos.add(todo)
        stats.num_todos         = len(todos)
        stats.preview_todos     = todos[:MAX_PREVIEW]

        creditStamps            = self._stampDB.getCreditedStamps(stamp.user.user_id, stamp.entity.entity_id, limit=100)
        stats.num_credits       = len(creditStamps)
        stats.preview_credits   = map(lambda x: x.stamp_id, creditStamps[:MAX_PREVIEW])

        comments                = self._commentDB.getCommentsForStamp(stampId, limit=100)
        stats.num_comments      = len(comments)
        stats.preview_comments  = map(lambda x: x.comment_id, comments[:MAX_PREVIEW])

        entity                  = self._entityDB.getEntity(stamp.entity.entity_id)
        stats.entity_id         = entity.entity_id
        stats.kind              = entity.kind
        stats.types             = entity.types

        if entity.kind == 'place' and entity.coordinates is not None:
            stats.lat           = entity.coordinates.lat
            stats.lng           = entity.coordinates.lng

        if entity.sources.tombstone_id is not None:
            # Call async process to update references
            self.call_task(self.updateTombstonedEntityReferencesAsync, {'oldEntityId': entity.entity_id})

        # Stamp popularity - Unbounded score
        popularity = (2 * stats.num_likes) + stats.num_todos + (stats.num_comments / 2.0) + (2 * stats.num_credits)
        #TODO: Add in number of activity_items with the given stamp id 
        
        stats.popularity = float(popularity)

        # Stamp Quality - Score out of 1... 0.5 by default 

        quality = 0.5 

        # -0.2 for no blurb, +0 for <20 chars, +0.1 for 20-50 chars, + 0.16 for 50-100 chars, +0.19 for 100+ chars
        
        blurb = ""
        for content in stamp.contents:
            blurb = "%s%s" % (blurb,content.blurb)
        
        if len(blurb) > 100:
            quality += 0.19
        elif len(blurb) > 50:
            quality += 0.13
        elif len(blurb) > 20:
            quality += 0.1
        elif len(blurb) == 0:
            quality -= 0.2

        # +0.2 for image in the stamp
        for content in stamp.contents:
            if content.images is not None:
                quality += 0.2
                break
        
        # +0.05 if stamp has at least one credit
        if stats.num_credits > 0:
            quality += 0.05


        # +0.02 if blurb has at least one mention in it
        mentions = utils.findMentions(blurb)
        for mention in mentions:
            quality += 0.02
            break
            
        # +0.02 if blurb has at least one url link in it
        urls = utils.findUrls(blurb)
        for url in urls:
            quality += 0.02
            break
        
        # +0.2 if blurb has at least one quote in it 
        if '"' in blurb:
            quality += 0.02

        stats.quality = quality
        
        

        score = max(quality, float(quality * popularity))
        stats.score = score

        self._stampStatsDB.updateStampStats(stats)

        return stats

    # TODO: Move this helper function to a more centralizated location?






    def _getStampCollection(self, stampIds, timeSlice, authUserId=None):

        if timeSlice.limit is None or timeSlice.limit <= 0 or timeSlice.limit > 50:
            timeSlice.limit = 50

        # Add one second to timeSlice.before to make the query inclusive of the timestamp passed
        if timeSlice.before is not None:
            timeSlice.before = timeSlice.before + datetime.timedelta(seconds=1)

        # Buffer of 10 additional stamps
        limit = timeSlice.limit
        timeSlice.limit = limit + 10

        t0 = time.time()
        stampData = self._stampDB.getStampCollectionSlice(stampIds, timeSlice)
        logs.debug('Time for _getStampCollectionSlice: %s' % (time.time() - t0))

        stamps = self._enrichStampObjects(stampData, authUserId=authUserId, mini=True)
        stamps = stamps[:limit]

        if len(stampData) >= limit and len(stamps) < limit:
            logs.warning("TOO MANY STAMPS FILTERED OUT! %s, %s" % (len(stamps), limit))

        return stamps

    def _searchStampCollection(self, stampIds, searchSlice, authUserId=None):

        if searchSlice.limit is None or searchSlice.limit <= 0 or searchSlice.limit > 50:
            searchSlice.limit = 50

        # Buffer of 10 additional stamps
        limit = searchSlice.limit
        searchSlice.limit = limit + 10

        t0 = time.time()
        stampData = self._stampDB.searchStampCollectionSlice(stampIds, searchSlice)
        logs.debug('Time for _searchStampCollectionSlice: %s' % (time.time() - t0))

        stamps = self._enrichStampObjects(stampData, authUserId=authUserId)
        stamps = stamps[:limit]

        if len(stampData) >= limit and len(stamps) < limit:
            logs.warning("TOO MANY STAMPS FILTERED OUT! %s, %s" % (len(stamps), limit))

        return stamps

    def _getScopeStampIds(self, scope=None, userId=None, authUserId=None):
        """
        If not logged in return "popular" results. Also, allow scope to be set to "popular" if
        not logged in or to user stamps; otherwise, raise exception.
        """

        if scope == 'credit':
            if userId is not None:
                return self._collectionDB.getUserCreditStampIds(userId)
            elif authUserId is not None:
                return self._collectionDB.getUserCreditStampIds(authUserId)
            else:
                raise StampedInputError("User required")

        if scope == 'user':
            if userId is not None:
                return self._collectionDB.getUserStampIds(userId)
            raise StampedInputError("User required")

        if userId is not None and scope is not None:
            raise StampedInputError("Invalid scope combination")

        if userId is not None:
            self._collectionDB.getUserStampIds(userId)

        if scope == 'popular':
            return None

        if authUserId is None:
            raise StampedNotLoggedInError("Must be logged in to view %s" % scope)

        if scope == 'me':
            return self._collectionDB.getUserStampIds(authUserId)

        if scope == 'inbox':
            return self._collectionDB.getInboxStampIds(authUserId)

        if scope == 'friends':
            raise NotImplementedError()

        raise StampedInputError("Unknown scope: %s" % scope)

    def getStampCollection(self, timeSlice, authUserId=None):
        # Special-case "tastemakers"
        if timeSlice.scope == 'popular':
            limit = timeSlice.limit
            if limit <= 0:
                limit = 20

            start = datetime.datetime.utcnow() - datetime.timedelta(hours=3)
            if timeSlice.before is not None:
                start = timeSlice.before

            key = str("fn::StampedAPI.getStampCollection::%s" % generateKeyFromDictionary(timeSlice.dataExport()))

            try:
                stampIds = self._cache[key]

            except KeyError:
                # Start with any whitelisted stamp ids
                stampIds = self._stampDB.getWhitelistedTastemakerStampIds()

                # stampIds = []
                # daysOffset = 0
                # while len(stampIds) < limit and daysOffset < 7:
                #     """
                #     Loop through daily passes to get a full limit's worth of stamps. If a given 24-hour period doesn't
                #     have enough stamps, it should check the previous day, with a max of one week.
                #     """
                #     before = start - datetime.timedelta(hours=(24*daysOffset))
                #     since = before - datetime.timedelta(hours=24)
                #     stampIds += self._stampStatsDB.getPopularStampIds(since=since, before=before, limit=limit, minScore=3)
                #     daysOffset += 1
                # stampIds = stampIds[:limit]
                try:
                    self._cache.set(key, stampIds, time=(60*30))
                except Exception as e:
                    logs.warning("Unable to set cache for tastemakers: %s" % e)

        else:
            stampIds = self._getScopeStampIds(timeSlice.scope, timeSlice.user_id, authUserId)

        return self._getStampCollection(stampIds, timeSlice, authUserId=authUserId)

    def searchStampCollection(self, searchSlice, authUserId=None):
        t0 = time.time()
        stampIds    = self._getScopeStampIds(searchSlice.scope, searchSlice.user_id, authUserId)
        logs.debug('Time for _getScopeStampIds: %s' % (time.time() - t0))

        return self._searchStampCollection(stampIds, searchSlice, authUserId=authUserId)