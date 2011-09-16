#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from httpapi.v0.helpers import *
import logs

@handleHTTPRequest
@require_http_methods(["POST"])
def create(request):
    authUserId  = checkOAuth(request)
    schema      = parseFileUpload(HTTPStampNew(), request, 'image')
    
    if schema.search_id:
        entityId = stampedAPI._convertSearchId(schema.search_id)
    elif schema.entity_id:
        entityId = schema.entity_id
    else:
        raise InputError
    
    data        = schema.exportSparse()
    data.pop('entity_id', None)
    data.pop('search_id', None)
    
    stamp       = stampedAPI.addStamp(authUserId, entityId, data)
    logs.info('STAMP: %s' % stamp)
    stamp       = HTTPStamp().importSchema(stamp)
    
    return transformOutput(stamp.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def update(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPStampEdit(), request)

    ### TEMP: Generate list of changes. Need to do something better eventually...
    data        = schema.exportSparse()
    del(data['stamp_id'])

    for k, v in data.iteritems():
        if v == '':
            data[k] = None
    
    stamp       = stampedAPI.updateStamp(authUserId, schema.stamp_id, data)
    stamp       = HTTPStamp().importSchema(stamp)

    return transformOutput(stamp.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def update_image(request):
    authUserId  = checkOAuth(request)
    schema      = parseFileUpload(HTTPStampImage(), request, 'image')
    
    ret         = stampedAPI.updateStampImage(authUserId, schema.stamp_id, \
                                                schema.image)

    stamp       = HTTPStamp().importSchema(stamp)

    return transformOutput(stamp.exportSparse())


@handleHTTPRequest
@require_http_methods(["GET"])
def show(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPStampId(), request)

    stamp       = stampedAPI.getStamp(schema.stamp_id, authUserId)
    stamp       = HTTPStamp().importSchema(stamp)
    
    return transformOutput(stamp.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def remove(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPStampId(), request)

    stamp       = stampedAPI.removeStamp(authUserId, schema.stamp_id)
    stamp       = HTTPStamp().importSchema(stamp)
    
    return transformOutput(stamp.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def likesCreate(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPStampId(), request)

    stamp       = stampedAPI.addLike(authUserId, schema.stamp_id)
    stamp       = HTTPStamp().importSchema(stamp)
    
    return transformOutput(stamp.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def likesRemove(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPStampId(), request)

    stamp       = stampedAPI.removeLike(authUserId, schema.stamp_id)
    stamp       = HTTPStamp().importSchema(stamp)
    
    return transformOutput(stamp.exportSparse())


