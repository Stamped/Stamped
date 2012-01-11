#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest
@require_http_methods(["POST"])
def create(request):
    authUserId  = checkOAuth(request)

    schema      = parseRequest(HTTPCommentNew(), request)
    stampId     = schema.stamp_id
    blurb       = schema.blurb

    comment     = stampedAPI.addComment(authUserId, stampId, blurb)
    comment     = HTTPComment().importSchema(comment)

    return transformOutput(comment.exportSparse())


@handleHTTPRequest
@require_http_methods(["POST"])
def remove(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPCommentId(), request)

    comment     = stampedAPI.removeComment(authUserId, schema.comment_id)
    comment     = HTTPComment().importSchema(comment)
    
    return transformOutput(comment.exportSparse())


@handleHTTPRequest
@require_http_methods(["GET"])
def show(request):
    authUserId  = checkOAuth(request)
    schema      = parseRequest(HTTPCommentSlice(), request)

    data        = schema.exportSparse()
    del(data['stamp_id'])

    comments    = stampedAPI.getComments(schema.stamp_id, authUserId, **data)

    result = []
    for comment in comments:
        result.append(HTTPComment().importSchema(comment).exportSparse())
    
    result = sorted(result, key=lambda k: k['created'])

    return transformOutput(result)


