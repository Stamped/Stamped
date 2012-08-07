#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from servers.httpapi.v0.helpers import *

stampExceptions = [
    (StampedAccountNotFoundError, 404, 'not_found', 'There was an error retrieving account information'),
    (StampedOutOfStampsError, 403, 'forbidden', 'No more stamps remaining'),
    (StampedNotLoggedInError, 401, 'bad_request', 'You must be logged in to perform this action.'),
    (StampedRemoveStampPermissionsError, 403, 'forbidden', 'Insufficient privileges to remove stamp'),
    (StampedViewStampPermissionsError, 403, "forbidden", "Insufficient privileges to view stamp"),
    (StampedAddCommentPermissionsError, 403, "forbidden", "Insufficient privileges to add comment"),
    (StampedRemoveCommentPermissionsError, 403, "forbidden", "Insufficient privileges to remove comment"),
    (StampedViewCommentPermissionsError, 403, "forbidden", "Insufficient privileges to view comment"),
    (StampedPermissionsError, 403, "forbidden", "Insufficient privileges to view stamp"),
    (StampedBlockedUserError, 403, 'forbidden', "User is blocked"),
]

stampShareExceptions = [
    (StampedMissingParametersError, 400, 'bad_request', 'Missing third party service name'),
    (StampedFacebookTokenError,     401, 'facebook_auth', "Facebook login failed. Please reauthorize your account."),
    (StampedLinkedAccountError,     401, 'invalid_credentials', "Missing credentials for linked account."),
    (StampedThirdPartyError,        400, 'third_party', "There was an error connecting to the third-party service."),
] + stampExceptions

def transformStamps(stamps):
    """
    Convert stamps to HTTPStamp and return as json-formatted HttpResponse
    """
    result = []
    
    if stamps is None:
        stamps = []
    
    for stamp in stamps:
        try:
            result.append(HTTPStamp().importStamp(stamp).dataExport())
        except:
            logs.warn(utils.getFormattedException())
    
    return transformOutput(result)


@require_http_methods(["POST"])
@handleHTTPRequest(http_schema=HTTPStampNew,
                   exceptions=stampExceptions)
def create(request, authUserId, data, **kwargs):
    entityRequest = {
        'entity_id' : data.pop('entity_id', None),
        'search_id' : data.pop('search_id', None),
    }
    
    if 'credits' in data and data['credits'] is not None:
        data['credits'] = data['credits'].split(',')
    
    stamp = stampedAPI.stamps.addStamp(authUserId, entityRequest, data)
    stamp = HTTPStamp().importStamp(stamp)
    
    return transformOutput(stamp.dataExport())


@require_http_methods(["POST"])
@handleHTTPRequest(http_schema=HTTPStampShare,
                   exceptions=stampShareExceptions)
def share(request, authUserId, http_schema, data, **kwargs):
    if http_schema.service_name is None:
        if 'service_name' not in kwargs:
            raise StampedMissingParametersError("Missing linked account service_name parameter")
        else:
            http_schema.service_name = kwargs['service_name']

    stamp = stampedAPI.stamps.shareStamp(authUserId, http_schema.stamp_id, http_schema.service_name, http_schema.temp_image_url)
    stamp = HTTPStamp().importStamp(stamp)
    return transformOutput(stamp.dataExport())


@require_http_methods(["POST"])
@handleHTTPRequest(http_schema=HTTPStampId, exceptions=stampExceptions)
def remove(request, authUserId, http_schema, **kwargs):
    stampedAPI.stamps.removeStamp(authUserId, http_schema.stamp_id)
    return transformOutput(True)


@require_http_methods(["GET"])
@handleHTTPRequest(requires_auth=False,
                  http_schema=HTTPStampRef,
                  exceptions=stampExceptions)
def show(request, authUserId, http_schema, uri, **kwargs):
    if authUserId is None:
        try:
            return getCache(uri, http_schema)
        except KeyError:
            pass
        except Exception as e:
            logs.warning("Failed to get cache: %s" % e)

    if http_schema.stamp_id is not None:
        stamp = stampedAPI.stamps.getStamp(http_schema.stamp_id, authUserId)
    else:
        stamp = stampedAPI.stamps.getStampFromUser(userId=http_schema.user_id, 
                                            stampNumber=http_schema.stamp_num)
    
    stamp = HTTPStamp().importStamp(stamp)
    
    result = transformOutput(stamp.dataExport())

    if authUserId is None:
        setCache(uri, http_schema, result, ttl=600)

    return result


# Collection
@require_http_methods(["GET"])
@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPTimeSlice,
                   conversion=HTTPTimeSlice.exportTimeSlice,
                   exceptions=stampExceptions)
def collection(request, authUserId, http_schema, schema, uri, **kwargs):
    if authUserId is None:
        try:
            return getCache(uri, http_schema)
        except KeyError:
            pass
        except Exception as e:
            logs.warning("Failed to get cache: %s" % e)

    stamps = stampedAPI.stamps.getStampCollection(schema, authUserId)

    result = transformStamps(stamps)

    if authUserId is None:
        setCache(uri, http_schema, result, ttl=600)

    return result


# Search
@require_http_methods(["GET"])
@handleHTTPRequest(http_schema=HTTPSearchSlice,
                  conversion=HTTPSearchSlice.exportSearchSlice,
                  exceptions=stampExceptions)
def search(request, authUserId, http_schema, schema, uri, **kwargs):
    if authUserId is None or http_schema.scope == 'popular':
        try:
            return getCache(uri, http_schema)
        except KeyError:
            pass
        except Exception as e:
            logs.warning("Failed to get cache: %s" % e)

    stamps = stampedAPI.stamps.searchStampCollection(schema, authUserId)

    result = transformStamps(stamps)

    if authUserId is None or http_schema.scope == 'popular':
        setCache(uri, http_schema, result, ttl=600)

    return result


# Guide
@require_http_methods(["GET"])
@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPGuideRequest,
                   conversion=HTTPGuideRequest.exportGuideRequest,
                   exceptions=stampExceptions)
def guide(request, authUserId, http_schema, schema, uri, **kwargs):
    if http_schema.scope == 'popular':
        try:
            return getCache(uri, http_schema)
        except KeyError:
            pass
        except Exception as e:
            logs.warning("Failed to get cache: %s" % e)
    # TODO: Remove this try/catch and address underlying issue that arises when entitystats and stampstats are out of sync
    try:
        entities = stampedAPI.guides.getGuide(schema, authUserId)
    except Exception as e:
        logs.warning('Failed to build guide: %s' % e)
        entities = []
    result = []

    for entity in entities:
        try:
            result.append(HTTPEntity().importEntity(entity).dataExport())
        except Exception:
            logs.warning(utils.getFormattedException())
            raise

    result = transformOutput(result)

    if http_schema.scope == 'popular':
        setCache(uri, http_schema, result, ttl=600)

    return result


# Search Guide
@require_http_methods(["GET"])
@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPGuideSearchRequest,
                   conversion=HTTPGuideSearchRequest.exportGuideSearchRequest,
                   exceptions=stampExceptions)
def searchGuide(request, authUserId, http_schema, schema, uri, **kwargs):
    if http_schema.scope == 'popular':
        try:
            return getCache(uri, http_schema)
        except KeyError:
            pass
        except Exception as e:
            logs.warning("Failed to get cache: %s" % e)
            
    entities = stampedAPI.guides.searchGuide(schema, authUserId)
    result = []

    for entity in entities:
        try:
            result.append(HTTPEntity().importEntity(entity).dataExport())
        except Exception:
            logs.warning(utils.getFormattedException())
            raise

    result = transformOutput(result)

    if http_schema.scope == 'popular':
        setCache(uri, http_schema, result, ttl=600)

    return result


@require_http_methods(["POST"])
@handleHTTPRequest(http_schema=HTTPStampId,
                   exceptions=stampExceptions)
def likesCreate(request, authUserId, http_schema, **kwargs):
    stamp = stampedAPI.likes.addLike(authUserId, http_schema.stamp_id)
    stamp = HTTPStamp().importStamp(stamp)

    return transformOutput(stamp.dataExport())


@require_http_methods(["POST"])
@handleHTTPRequest(http_schema=HTTPStampId,
                   exceptions=stampExceptions)
def likesRemove(request, authUserId, http_schema, **kwargs):
    stamp = stampedAPI.likes.removeLike(authUserId, http_schema.stamp_id)
    stamp = HTTPStamp().importStamp(stamp)
    
    return transformOutput(stamp.dataExport())


@require_http_methods(["GET"])
@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPStampId,
                   exceptions=stampExceptions)
def likesShow(request, authUserId, http_schema, **kwargs):
    ### TODO: Add paging
    userIds = stampedAPI.likes.getLikes(authUserId, http_schema.stamp_id)
    output  = { 'user_ids': userIds }
    
    return transformOutput(output)


@require_http_methods(["GET"])
@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPStampId,
                   exceptions=stampExceptions)
def todosShow(request, authUserId, http_schema, **kwargs):
    ### TODO: Add paging
    userIds = stampedAPI.stamps.getStampTodos(authUserId, http_schema.stamp_id)
    output  = { 'user_ids': userIds }
    
    return transformOutput(output)


