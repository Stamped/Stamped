#!/u()sr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

from servers.httpapi.v0.helpers import *

exceptions = [
    (StampedActivityMissingRecipientError, 400, "bad_request", "There was an error adding the activity item."),
]

@handleHTTPRequest(http_schema=HTTPTodoNew, exceptions=exceptions)
@require_http_methods(["POST"])
def create(request, authUserId, http_schema, **kwargs):

    raise StampedDeprecatedError()

#    stampId  = http_schema.stamp_id
#    entityRequest = {
#        'entity_id': http_schema.entity_id,
#        'search_id': http_schema.search_id,
#        }
#
#    todo = stampedAPI.addTodo(authUserId, entityRequest, stampId)
#    todo = HTTPTodo().importTodo(todo)
#
#    return transformOutput(todo.dataExport())

@handleHTTPRequest(http_schema=HTTPTodoComplete, exceptions=exceptions)
@require_http_methods(["POST"])
def complete(request, authUserId, http_schema, **kwargs):

    raise StampedDeprecatedError()

#    todo = stampedAPI.completeTodo(authUserId, http_schema.entity_id, http_schema.complete)
#    todo = HTTPTodo().importTodo(todo)
#    return transformOutput(todo.dataExport())

@handleHTTPRequest(http_schema=HTTPEntityId, exceptions=exceptions)
@require_http_methods(["POST"])
def remove(request, authUserId, http_schema, **kwargs):

    raise StampedDeprecatedError()

#    stampedAPI.removeTodo(authUserId, http_schema.entity_id)
#
#    return transformOutput(True)

@handleHTTPRequest(http_schema=HTTPTodoTimeSlice,
                   conversion=HTTPTodoTimeSlice.exportTimeSlice,
                   exceptions=exceptions)
@require_http_methods(["GET"])
def collection(request, authUserId, schema, **kwargs):
    todos = stampedAPI.getTodos(authUserId, schema)

    result = []
    for todo in todos:
        result.append(HTTPTodo().importTodo(todo).dataExport())

    return transformOutput(result)

