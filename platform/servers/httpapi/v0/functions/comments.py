#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from httpapi.v0.helpers import *

@handleHTTPRequest(http_schema=HTTPCommentNew)
@require_http_methods(["POST"])
def create(request, authUserId, http_schema, **kwargs):
    comment = stampedAPI.addComment(authUserId, http_schema.stamp_id, http_schema.blurb)
    comment = HTTPComment().importComment(comment)
    
    return transformOutput(comment.dataExport())


@handleHTTPRequest(http_schema=HTTPCommentId)
@require_http_methods(["POST"])
def remove(request, authUserId, http_schema, **kwargs):
    comment = stampedAPI.removeComment(authUserId, http_schema.comment_id)
    comment = HTTPComment().importComment(comment)
    
    return transformOutput(comment.dataExport())


@handleHTTPRequest(http_schema=HTTPCommentSlice)
@require_http_methods(["GET"])
def show(request, authUserId, http_schema, data, **kwargs):
    del(data['stamp_id'])

    comments = stampedAPI.getComments(http_schema.stamp_id, authUserId, **data)
    results  = []
    
    for comment in comments:
        results.append(HTTPComment().importComment(comment).dataExport())
    
    results = sorted(results, key=lambda k: k['created'])
    return transformOutput(results)

