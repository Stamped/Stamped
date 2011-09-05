#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest
@require_http_methods(["POST"])
def create(request):
    authUserId  = checkOAuth(request)

    schema      = parseRequest(HTTPStampNew(), request)
    entityId    = schema.entity_id
    data        = schema.exportSparse()
    del(data['entity_id'])

    stamp       = stampedAPI.addStamp(authUserId, entityId, data)
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
    schema      = parseRequest(HTTPStampImage(), request)
    
    ret         = stampedAPI.updateStampImage(authUserId, schema.stamp_id, \
                                                schema.image)
                                                
    stamp       = HTTPStamp().importSchema(stamp)

    return transformOutput(stamp.exportSparse())
    
    # suffix      = '.jpg'
    
    # images = { }
    # prefixes = {
    #     'fast' : 'static.stamped.com/', 
    #     'slow' : 'http://stamped.com.static.images.s3.amazonaws.com/', 
    # }
    
    # for k, prefix in prefixes.iteritems():
    #     prefix = "%s/stamps/%s" % (prefix, schema.stamp_id)
    #     value  = []
        
    #     value.append("%s%s" % (prefix, suffix))
    #     images[k] = value
    
    # output      = { 'stamp_id': schema.stamp_id, 'images': images, }
    
    # return transformOutput(output)


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


