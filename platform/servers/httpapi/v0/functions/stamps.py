#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from servers.httpapi.v0.helpers import *

exceptions = [
    (StampedAccountNotFoundError, 404, 'not_found', 'There was an error retrieving account information'),
    (StampedOutOfStampsError, 403, 'forbidden', 'No more stamps remaining'),
    (StampedNotLoggedInError, 401, 'bad_request', 'You must be logged in to perform this action.'),
    (StampedRemoveStampPermissionsError, 403, 'forbidden', 'Insufficient privileges to remove stamp'),
    (StampedViewStampPermissionsError, 403, "forbidden", "Insufficient privileges to view stamp"),
    (StampedAddCommentPermissionsError, 403, "forbidden", "Insufficient privileges to add comment"),
    (StampedRemoveCommentPermissionsError, 403, "forbidden", "Insufficient privileges to remove comment"),
    (StampedViewCommentPermissionsError, 403, "forbidden", "Insufficient privileges to view comment"),
    (StampedBlockedUserError, 403, 'forbidden', "User is blocked"),
]

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

@handleHTTPRequest(http_schema=HTTPStampNew,
                   exceptions=exceptions)
@require_http_methods(["POST"])
def create(request, authUserId, data, **kwargs):
    entityRequest = {
        'entity_id' : data.pop('entity_id', None),
        'search_id' : data.pop('search_id', None),
    }
    
    if 'credits' in data and data['credits'] is not None:
        data['credits'] = data['credits'].split(',')
    
    stamp = stampedAPI.addStamp(authUserId, entityRequest, data)
    stamp = HTTPStamp().importStamp(stamp)
    
    return transformOutput(stamp.dataExport())

exceptions_share = [
    (StampedMissingParametersError, StampedHTTPError(400, 'bad_request', 'Missing third party service name')),
    (StampedFacebookTokenError, StampedHTTPError(401, 'facebook_auth', "Facebook login failed. Please reauthorize your account.")),
]
@handleHTTPRequest(http_schema=HTTPStampShare,
                   exceptions=exceptions + exceptions_share)
@require_http_methods(["POST"])
def share(request, authUserId, http_schema, data, **kwargs):
    if http_schema.service_name is None:
        if 'service_name' not in kwargs:
            raise StampedMissingParametersError("Missing linked account service_name parameter")
        else:
            http_schema.service_name = kwargs['service_name']

    try:
        stamp = stampedAPI.shareStamp(authUserId, http_schema.stamp_id, http_schema.service_name, http_schema.temp_image_url)
    except StampedLinkedAccountError:
        raise StampedHTTPError(401, "Missing credentials for linked account")
    except StampedThirdPartyError:
        raise StampedHTTPError(400, "There was an error connecting to the third-party service")

    stamp = HTTPStamp().importStamp(stamp)
    return transformOutput(stamp.dataExport())


@require_http_methods(["POST"])
@handleHTTPRequest(http_schema=HTTPStampId, exceptions=exceptions)
def remove(request, authUserId, http_schema, **kwargs):
    stampedAPI.removeStamp(authUserId, http_schema.stamp_id)
    return transformOutput(True)


exceptions_show = [ (StampedPermissionsError, StampedHTTPError(403, "forbidden", "Insufficient privileges to view stamp")) ]
@handleHTTPRequest(requires_auth=False,
                  http_schema=HTTPStampRef,
                  exceptions=exceptions + exceptions_show)
@require_http_methods(["GET"])
def show(request, authUserId, http_schema, **kwargs):
    if http_schema.stamp_id is not None:
        stamp = stampedAPI.getStamp(http_schema.stamp_id, authUserId)
    else:
        stamp = stampedAPI.getStampFromUser(userId=http_schema.user_id, 
                                            stampNumber=http_schema.stamp_num)
    
    stamp = HTTPStamp().importStamp(stamp)
    
    return transformOutput(stamp.dataExport())


# Collection
@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPTimeSlice,
                   conversion=HTTPTimeSlice.exportTimeSlice,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def collection(request, authUserId, schema, **kwargs):
    stamps = stampedAPI.getStampCollection(schema, authUserId)
    return transformStamps(stamps)


# Search
@handleHTTPRequest(http_schema=HTTPSearchSlice,
                  conversion=HTTPSearchSlice.exportSearchSlice,
                  exceptions=exceptions)
@require_http_methods(["GET"])
def search(request, authUserId, schema, **kwargs):
    stamps = stampedAPI.searchStampCollection(schema, authUserId)
    return transformStamps(stamps)


# Guide
@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPGuideRequest,
                   conversion=HTTPGuideRequest.exportGuideRequest,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def guide(request, authUserId, schema, **kwargs):
    entities = stampedAPI.getGuide(schema, authUserId)
    result = []

    for entity in entities:
        try:
            result.append(HTTPEntity().importEntity(entity).dataExport())
        except Exception:
            raise
            # logs.warning(utils.getFormattedException())

    return transformOutput(result)


# Search Guide
@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPGuideSearchRequest,
                   conversion=HTTPGuideSearchRequest.exportGuideSearchRequest,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def searchGuide(request, authUserId, schema, **kwargs):
    entities = stampedAPI.searchGuide(schema, authUserId)
    result = []

    for entity in entities:
        try:
            result.append(HTTPEntity().importEntity(entity).dataExport())
        except Exception:
            raise
            # logs.warning(utils.getFormattedException())

    return transformOutput(result)


@handleHTTPRequest(http_schema=HTTPStampId,
                   exceptions=exceptions)
@require_http_methods(["POST"])
def likesCreate(request, authUserId, http_schema, **kwargs):
    stamp = stampedAPI.addLike(authUserId, http_schema.stamp_id)
    stamp = HTTPStamp().importStamp(stamp)

    return transformOutput(stamp.dataExport())


@handleHTTPRequest(http_schema=HTTPStampId,
                   exceptions=exceptions)
@require_http_methods(["POST"])
def likesRemove(request, authUserId, http_schema, **kwargs):
    stamp = stampedAPI.removeLike(authUserId, http_schema.stamp_id)
    stamp = HTTPStamp().importStamp(stamp)
    
    return transformOutput(stamp.dataExport())


@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPStampId,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def likesShow(request, authUserId, http_schema, **kwargs):
    ### TODO: Add paging
    userIds = stampedAPI.getLikes(authUserId, http_schema.stamp_id)
    output  = { 'user_ids': userIds }
    
    return transformOutput(output)


@handleHTTPRequest(requires_auth=False,
                   http_schema=HTTPStampId,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def todosShow(request, authUserId, http_schema, **kwargs):
    ### TODO: Add paging
    userIds = stampedAPI.getStampTodos(authUserId, http_schema.stamp_id)
    output  = { 'user_ids': userIds }
    
    return transformOutput(output)


