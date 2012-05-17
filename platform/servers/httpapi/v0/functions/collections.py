#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from errors import StampedHTTPError
from httpapi.v0.helpers import *
import time

def transform_stamps(stamps):
    """
    Convert stamps to HTTPStamp or HTTPDeletedStamps and return as json-formatted HttpResponse
    """
    result = []
    for stamp in stamps:
        try:
            if 'deleted' in stamp:
                result.append(HTTPDeletedStamp().importSchema(stamp).dataExport())
            else:
                result.append(HTTPStamp().importSchema(stamp).dataExport())
        except:
            logs.warn(utils.getFormattedException())
    
    return transformOutput(result)

@handleHTTPRequest(http_schema=HTTPGenericCollectionSlice, schema=GenericCollectionSlice)
@require_http_methods(["GET"])
def inbox(request, authUserId, schema, **kwargs):
    before = time.time()
    stamps = stampedAPI.getInboxStamps(authUserId, schema)
    logs.info('api.getInboxStamps() duration: %d seconds' % (time.time()-before))
    return transform_stamps(stamps)

@handleHTTPRequest(requires_auth=False, http_schema=HTTPUserCollectionSlice, schema=UserCollectionSlice)
@require_http_methods(["GET"])
def user(request, authUserId, schema, **kwargs):
    before = time.time()
    stamps = stampedAPI.getUserStamps(authUserId, schema)
    logs.info('api.getUserStamps() duration: %d seconds' % (time.time()-before))
    return transform_stamps(stamps)

@handleHTTPRequest(http_schema=HTTPUserCollectionSlice, schema=UserCollectionSlice)
@require_http_methods(["GET"])
def credit(request, authUserId, schema, **kwargs):
    before = time.time()
    stamps = stampedAPI.getCreditedStamps(authUserId, schema)
    logs.info('api.getCreditedStamps() duration: %d seconds' % (time.time()-before))

    return transform_stamps(stamps)

@handleHTTPRequest(http_schema=HTTPFriendsSlice, schema=FriendsSlice)
@require_http_methods(["GET"])
def friends(request, authUserId, schema, **kwargs):
    import datetime
    #before = time.time()
    before = datetime.datetime.now()
    stamps = stampedAPI.getFriendsStamps(authUserId, schema)
    after = datetime.datetime.now()
    dur = after - before
    logs.info('api.getFriendsStamps() duration: %d.%d' % (dur.seconds, dur.microseconds))

    return transform_stamps(stamps)

@handleHTTPRequest(requires_auth=False, http_schema=HTTPGenericCollectionSlice, schema=GenericCollectionSlice)
@require_http_methods(["GET"])
def suggested(request, authUserId, schema, **kwargs):
    before = time.time()
    stamps = stampedAPI.getSuggestedStamps(authUserId, schema)
    logs.info('api.getSuggestedStamps() duration: %d seconds' % (time.time()-before))
    
    return transform_stamps(stamps)

@handleHTTPRequest(requires_auth=False, http_schema=HTTPConsumptionSlice, schema=ConsumptionSlice)
@require_http_methods(["GET"])
def consumption(request, authUserId, schema, **kwargs):
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
        raise StampedHTTPError('Consumption call with undefined scope %s' % schema.scope, 400)
    if stamps is None:
        raise StampedHTTPError('consumption() expected list of stamps, received None', 500)
    
    import pprint
    for stamp in stamps:
        pprint.pprint(stamp.entity)
    
    return transform_stamps(stamps)

