#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *
import logs

@handleHTTPRequest(http_schema=HTTPStampNew)
@require_http_methods(["POST"])
def create(request, authUserId, data, **kwargs):
    entityRequest = {
        'entity_id' : data.pop('entity_id', None),
        'search_id' : data.pop('search_id', None)
    }
    
    stamp = stampedAPI.addStamp(authUserId, entityRequest, data)
    stamp = HTTPStamp().importSchema(stamp)
    
    return transformOutput(stamp.exportSparse())


@handleHTTPRequest(http_schema=HTTPStampEdit)
@require_http_methods(["POST"])
def update(request, authUserId, http_schema, data, **kwargs):
    ### TEMP: Generate list of changes. Need to do something better eventually...
    del(data['stamp_id'])
    
    for k, v in data.iteritems():
        if v == '':
            data[k] = None
    
    stamp = stampedAPI.updateStamp(authUserId, http_schema.stamp_id, data)
    stamp = HTTPStamp().importSchema(stamp)
    
    return transformOutput(stamp.exportSparse())


@handleHTTPRequest(http_schema=HTTPStampImage, upload='image')
@require_http_methods(["POST"])
def update_image(request, authUserId, http_schema, **kwargs):
    ret   = stampedAPI.updateStampImage(authUserId, http_schema.stamp_id, 
                                        http_schema.image)
    stamp = HTTPStamp().importSchema(stamp)
    
    return transformOutput(stamp.exportSparse())


@handleHTTPRequest(http_schema=HTTPStampId)
@require_http_methods(["GET"])
def show(request, authUserId, http_schema, **kwargs):
    stamp = stampedAPI.getStamp(http_schema.stamp_id, authUserId)
    stamp = HTTPStamp().importSchema(stamp)
    
    return transformOutput(stamp.exportSparse())


@handleHTTPRequest(http_schema=HTTPStampId)
@require_http_methods(["POST"])
def remove(request, authUserId, http_schema, **kwargs):
    stamp = stampedAPI.removeStamp(authUserId, http_schema.stamp_id)
    stamp = HTTPStamp().importSchema(stamp)
    
    return transformOutput(stamp.exportSparse())


@handleHTTPRequest(http_schema=HTTPStampId)
@require_http_methods(["POST"])
def likesCreate(request, authUserId, http_schema, **kwargs):
    stamp = stampedAPI.addLike(authUserId, http_schema.stamp_id)
    stamp = HTTPStamp().importSchema(stamp)
    
    return transformOutput(stamp.exportSparse())


@handleHTTPRequest(http_schema=HTTPStampId)
@require_http_methods(["POST"])
def likesRemove(request, authUserId, http_schema, **kwargs):
    stamp = stampedAPI.removeLike(authUserId, http_schema.stamp_id)
    stamp = HTTPStamp().importSchema(stamp)
    
    return transformOutput(stamp.exportSparse())


@handleHTTPRequest(http_schema=HTTPStampId)
@require_http_methods(["GET"])
def likesShow(request, authUserId, http_schema, **kwargs):
    userIds = stampedAPI.getLikes(authUserId, http_schema.stamp_id)
    output  = { 'user_ids': userIds }
    
    return transformOutput(output)


