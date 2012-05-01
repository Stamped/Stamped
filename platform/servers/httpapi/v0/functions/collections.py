#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

def transform_stamps(stamps):
    """
    Convert stamps to HTTPStamp or HTTPDeletedStamps and return as json-formatted HttpResponse
    """
    result = []
    for stamp in stamps:
        try:
            if 'deleted' in stamp:
                result.append(HTTPDeletedStamp().importSchema(stamp).exportSparse())
            else:
                result.append(HTTPStamp().importSchema(stamp).exportSparse())
        except:
            logs.warn(utils.getFormattedException())
    
    return transformOutput(result)

@handleHTTPRequest(http_schema=HTTPGenericCollectionSlice, schema=GenericCollectionSlice)
@require_http_methods(["GET"])
def inbox(request, authUserId, schema, **kwargs):
    stamps = stampedAPI.getInboxStamps(authUserId, schema)
    
    return transform_stamps(stamps)

@handleHTTPRequest(requires_auth=False, http_schema=HTTPUserCollectionSlice, schema=UserCollectionSlice)
@require_http_methods(["GET"])
def user(request, authUserId, schema, **kwargs):
    stamps = stampedAPI.getUserStamps(authUserId, schema)
    
    return transform_stamps(stamps)

@handleHTTPRequest(http_schema=HTTPUserCollectionSlice, schema=UserCollectionSlice)
@require_http_methods(["GET"])
def credit(request, authUserId, schema, **kwargs):
    stamps = stampedAPI.getCreditedStamps(authUserId, schema)
    
    return transform_stamps(stamps)

@handleHTTPRequest(http_schema=HTTPFriendsSlice, schema=FriendsSlice)
@require_http_methods(["GET"])
def friends(request, authUserId, schema, **kwargs):
    stamps = stampedAPI.getFriendsStamps(authUserId, schema)
    
    return transform_stamps(stamps)

@handleHTTPRequest(http_schema=HTTPGenericCollectionSlice, schema=GenericCollectionSlice)
@require_http_methods(["GET"])
def suggested(request, authUserId, schema, **kwargs):
    stamps = stampedAPI.getSuggestedStamps(authUserId, schema)
    
    return transform_stamps(stamps)

@handleHTTPRequest(http_schema=HTTPConsumptionSlice, schema=ConsumptionSlice)
@require_http_methods(["GET"])
def consumption(request, authUserId, schema, **kwargs):
    print('\nHIT CONSUMPTION\n')
    stamps = None
    if schema.scope == 'you':
        userCollSlice = schema.exportSchema(UserCollectionSlice())
        userCollSlice['user_id'] = authUserId
        stamps = stampedAPI.getUserStamps(authUserId, userCollSlice)
    elif schema.scope == 'friends':
        stamps = stampedAPI.getInboxStamps(authUserId, schema)
    elif schema.scope == 'fof':
        friendsSlice = schema.exportSchema(FriendsSlice())
        friendsSlice.distance = 2
        stamps = stampedAPI.getFriendsStamps(authUserId, friendsSlice)
    elif schema.scope == 'everyone':
        stamps = stampedAPI.getSuggestedStamps(authUserId, schema)
    else:
        raise NotImplementedError('Consumption call with undefined scope %s' % schema.scope)
    if stamps is None:
        raise Exception('consumption() expected list of stamps, received None')

    import pprint
    for stamp in stamps:
        pprint.pprint(stamp.entity)

    return transform_stamps(stamps)