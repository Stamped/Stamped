#!/usr/bin/env python
"""
    Helper utilities for API functions.
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import stamped
import os, json, utils, random, time, hashlib, logs
import libs.ec2_utils

from pprint                         import pformat
from errors                         import *
from api.HTTPSchemas                import *
from api.MongoStampedAPI            import globalMongoStampedAPI
from api.MongoStampedAuth           import MongoStampedAuth

from django.views.decorators.http   import require_http_methods
from django.utils.functional        import wraps
from django.http                    import HttpResponse

from datetime                       import datetime

IS_PROD = libs.ec2_utils.is_prod_stack()

# TODO (travis): VALID_ORIGINS should be dependent on IS_PROD to be 100% as 
# restrictive as possible.
# TODO: (travis): does localhost as a valid origin mean any computer's localhost is valid? methinks yes...
# TODO: (travis): should https also be a valid origin prefix?

VALID_ORIGINS = [
    'http://stamped.com', 
    'http://api.stamped.com', 
    'http://www.stamped.com', 
    'http://dev.stamped.com', 
    'http://ec2-23-22-98-51.compute-1.amazonaws.com', # peach.api0 as of 5/20/2012 (travis - testing web)
]

if not IS_PROD:
    VALID_ORIGINS.extend([
        'http://localhost:19000', 
        'http://localhost:18000', 
        'http://localhost:8000', 
    ])

t1 = time.time()

# TODO (travis): use single global stamped API instance
# e.g., there are MongoStampedAPIs instantiated throughout the codebase => refactor
stampedAPI  = globalMongoStampedAPI()
stampedAuth = MongoStampedAuth()

t2 = time.time()
duration = (t2 - t1) * 1.0
logs.info("INIT: %s sec" % duration)

if duration > 2:
    logs.warning("LONG INIT: %s sec" % duration)

defaultExceptions = [
    (StampedDocumentNotFoundError,      404,    'not_found',            'There was a problem retrieving the requested data'),
    (StampedAuthError,                  401,    'invalid_credentials',  'There was an error during authentication'),
    (StampedInputError,                 400,    'invalid_request',      'An error occurred. Please try again later.'),
    (StampedIllegalActionError,         403,    'invalid_request',      'An error occurred. Please try again later.'),
    (StampedMissingParametersError,     400,    'invalid_request',      'An error occurred. Please try again later'),
    (StampedPermissionsError,           403,    'forbidden',            'Insufficient privileges'),
    (StampedDuplicationError,           409,    'already_exists',       'An error occurred. Please try again later'),
    (StampedUnavailableError,           404,    'not_found',            'Not found'),
    (SchemaException,                   400,    'invalid_request',      'Invalid form'),
    (StampedInternalError,              500,    'internal',             'An error occurred. Please try again later'),
]


def handleStampedExceptions(e, handlers=None):
    if isinstance(e, StampedHTTPError):
        exceptions =  [(StampedHTTPError, e.code, e.kind, e.msg)]
    elif handlers is not None:
        exceptions = handlers + defaultExceptions
    else:
        exceptions = defaultExceptions

    for (exception, code, kind, msg) in exceptions:
        if isinstance(e, exception):
            logs.warning("%s Error (%s): %s" % (code, kind, msg))
            logs.warning(utils.getFormattedException())
            logs.error(code)

            kind = kind
            if kind is None:
                kind = 'stamped_error'

            message = msg
            if message is None and e.msg is not None:
                message = e.msg

            error = {}
            error['error'] = kind
            if message is not None:
                error['message'] = unicode(message)

            return transformOutput(error, status=code)
    else:
        error = {
            'error' :   'stamped_error',
            'message' : "An error occurred. Please try again later.",
        }
        logs.warning("500 Error: %s" % e)
        logs.warning(utils.getFormattedException())
        logs.error(500)

        # Email dev if a 500 occurs
        if libs.ec2_utils.is_ec2():
            try:
                email = {}
                email['from'] = 'Stamped <noreply@stamped.com>'
                email['to'] = 'dev@stamped.com'
                email['subject'] = '%s - 500 Error - %s' % (stampedAPI.node_name, datetime.utcnow().isoformat())
                email['body'] = logs.getHtmlFormattedLog()
                utils.sendEmail(email, format='html')
            except Exception as e:
                logs.warning('UNABLE TO SEND EMAIL: %s')

        return transformOutput(error, status=500)

def handleHTTPRequest(requires_auth=True, 
                      requires_client=False,
                      http_schema=None,
                      conversion=None,
                      upload=None, 
                      parse_request_kwargs=None, 
                      parse_request=True,
                      exceptions=None):
    """
        handleHTTPRequest is Stamped API's main HTTP API function decorator, taking 
        care of oauth, client, and request validation, optionally parsing the input 
        GET or POST data against a target http_schema, logging, and error handling, 
        including catching all top-level exceptions and converting them to their 
        HTTP error equivalents. handleHTTPRequest also handles gracefully responding 
        to cross-domain requests from a set of pre-defined, priveleged domains.
        
        Note that this decorator injects one or more of the following attributes 
        into the wrapped function's keyword arguments (so all wrapped API functions 
        must accept **kwargs):
        
            * http_schema  - if http_schema is specified, the input GET or POST data 
                             will be parsed against this schema and the resulting 
                             validated schema instance will be contained in http_schema.
                             note: if 'upload' is specified, parseFileUpload will be 
                             used instead of parseRequest (uploads also require POST).
                             
            * schema       - if schema is specified, the http_schema will be exported 
                             to an instance of the given schema type.
                             
            * data         - if no schema is specified, data will contain the parsed 
                             http_schema data exported sparsely to a dict.
                             
            * authUserId   - the user id of the authenticated user; will be None if 
                             oauth validation failed (note that to enable 
                             unauthenticated access to an API function, you must set 
                             requires_auth to False).
                             
            * authClientId - the client id of the authenticated client; will be None if 
                             oauth validation failed (note that to enable 
                             unauthenticated access to an API function, you must set 
                             requires_auth to False).
                             
            * client_id    - the client id of the unauthenticated client (circumventing 
                             oauth). note that if an unauthenticated API function wishes 
                             to require a valid client_id and client_secret, it must 
                             set requires_client to True.
    """
    def decorator(fn):
        # NOTE (travis): if you hit this assertion, you're likely using the 
        # handleHTTPRequest incorrectly.
        assert callable(fn)
        
        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            try:
                origin = None
                
                try:
                    origin = request.META['HTTP_ORIGIN']
                    valid_origin = origin
                    assert valid_origin in VALID_ORIGINS
                except Exception:
                    valid_origin = None
                
                def _add_cors_headers(response):
                    response['Access-Control-Allow-Origin']  = valid_origin
                    response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                    response['Access-Control-Max-Age']       = 1000
                    response['Access-Control-Allow-Headers'] = '*'
                    return response
                
                # allow API to gracefully handle cross-domain requests from trusted origins
                if request.method == 'OPTIONS' and valid_origin is not None:
                    return _add_cors_headers(HttpResponse())
                
                logs.begin(saveLog=stampedAPI._logsDB.saveLog,
                           saveStat=stampedAPI._statsDB.addStat,
                           requestData=request,
                           nodeName=stampedAPI.node_name)
                logs.info("%s %s" % (request.method, request.path))

                if valid_origin is None:
                    if origin is not None:
                        logs.warning("Invalid origin: %s" % origin)
                    else:
                        logs.debug("Origin not included")
                
                params = {}
                params['authUserId'], params['authClientId'] = checkOAuthWithRequest(request, required=requires_auth)
                params['client_id'] = checkClient(request, required=requires_client)
                
                if parse_request:
                    parse_kwargs = parse_request_kwargs or {}

                    if upload is not None:
                        if http_schema is None:
                            raise Exception("ERROR: handleHTTPRequest requires http_schema if upload is provided")
                        
                        params['http_schema']   = parseFileUpload(http_schema(), request, upload, **parse_kwargs)
                    elif http_schema is not None:
                        params['http_schema']   = parseRequest(http_schema(), request, **parse_kwargs)
                    else:
                        params['http_schema']   = parseRequest(None, request, **parse_kwargs)
                    
                    if conversion is not None:
                        params['schema']        = conversion(params['http_schema'])
                    elif http_schema is not None:
                        params['data']          = params['http_schema'].dataExport()
                
                kwargs.update(params)
                ret = fn(request, *args, **kwargs)
                logs.info("End request: Success")
                
                if valid_origin and isinstance(ret, HttpResponse):
                    _add_cors_headers(ret)
                
                return ret

            except Exception as e:
                return handleStampedExceptions(e, exceptions)
            finally:
                try:
                    logs.save()
                except Exception:
                    print 'Unable to save logs'
                    import traceback
                    traceback.print_exc()
                    logs.warning(traceback.format_exc())

        return wrapper
    return decorator



def handleHTTPCallbackRequest(
        http_schema=None,
        conversion=None,
        parse_request_kwargs=None,
        parse_request=True,
        exceptions=None):

    def decorator(fn):
        # NOTE (travis): if you hit this assertion, you're likely using the
        # handleHTTPRequest incorrectly.
        assert callable(fn)

        @wraps(fn)
        def wrapper(request, *args, **kwargs):
            try:
                logs.begin(saveLog=stampedAPI._logsDB.saveLog,
                    saveStat=stampedAPI._statsDB.addStat,
                    requestData=request,
                    nodeName=stampedAPI.node_name)
                logs.info("%s %s" % (request.method, request.path))

                params = {}
                oauth_token = None

                if 'stamped_oauth_token' in request.GET:
                    oauth_token = request.GET['stamped_oauth_token']
                elif 'stamped_oauth_token' in request.POST:
                    oauth_token = request.POST['stamped_oauth_token']
                elif 'oauth_token' in request.GET:
                    oauth_token = request.GET['oauth_token']
                elif 'oauth_token' in request.POST:
                    oauth_token = request.POST['oauth_token']
                else:
                    raise StampedInputError("Access token not found")

                params['authUserId'], params['authClientId'] = checkOAuth(oauth_token, required=False)

                if parse_request:
                    parse_kwargs = parse_request_kwargs or { 'allow_oauth_token' : True }

                    if http_schema is not None:
                        params['http_schema']   = parseRequest(http_schema(), request, **parse_kwargs)
                    else:
                        params['http_schema']   = parseRequest(None, request, **parse_kwargs)

                    if conversion is not None:
                        params['schema']        = conversion(params['http_schema'])
                    elif http_schema is not None:
                        params['data']          = params['http_schema'].dataExport()

                kwargs.update(params)
                ret = fn(request, *args, **kwargs)
                logs.info("End request: Success")

                return ret

            except Exception as e:
                handleStampedExceptions(e, exceptions)
            finally:
                try:
                    logs.save()
                except Exception:
                    print 'Unable to save logs'

        return wrapper
    return decorator

def checkClient(request, required=True):
    ### Parse Request for Client Credentials
    try:
        if request.method == 'GET':
            clientId        = request.GET['client_id']
            clientSecret    = request.GET['client_secret']
        elif request.method == 'POST':
            clientId        = request.POST['client_id']
            clientSecret    = request.POST['client_secret']
    except Exception:
        if not required:
            return None 
        raise StampedHTTPError(400, "invalid_request")
    
    ### Validate Client Credentials
    try:
        logs.client(clientId)
        stampedAuth.verifyClientCredentials(clientId, clientSecret)

        client = stampedAuth.getClientDetails(clientId)
        stampedAPI.setVersion(client.api_version)
        
        return clientId
    except StampedInvalidClientError:
        raise StampedHTTPError(400, "invalid_client")

def optionalOAuth(request):
    try:
        authUserId = checkOAuthWithRequest(request)
    except Exception:
        authUserId = None
    
    return authUserId

def checkOAuthWithRequest(request, required=True):
    ### Parse Request for Access Token
    try:
        if request.method == 'GET':
            oauth_token = request.GET['oauth_token']
        elif request.method == 'POST':
            oauth_token = request.POST['oauth_token']
        else:
            raise StampedHTTPError(400, "invalid_request")
    except Exception:
        if not required:
            return None, None
        raise StampedHTTPError(400, "invalid_request")

    return checkOAuth(oauth_token, required)

def checkOAuth(oauth_token, required=True):
    logs.token(oauth_token)

    ### Validate OAuth Access Token
    try:
        authenticated_user_id, client_id = stampedAuth.verifyAccessToken(oauth_token)
        if authenticated_user_id is None:
            raise StampedAuthUserNotFoundError("User not found")
        
        logs.user(authenticated_user_id)
        logs.client(client_id)
        
        client = stampedAuth.getClientDetails(client_id)
        stampedAPI.setVersion(client.api_version)
        
        return authenticated_user_id, client_id

    except StampedAuthUserNotFoundError:
        raise StampedHTTPError(401, "access_denied", "User not found")
    except StampedInvalidAuthTokenError:
        raise StampedHTTPError(401, "invalid_token")
    except Exception, e:
        logs.warning("Error: %s" % e)
        raise StampedHTTPError(401, "invalid_token")

def parseRequest(schema, request, **kwargs):
    data = { }
    
    ### Parse Request
    try:
        if request.method == 'GET':
            rawData = request.GET
        elif request.method == 'POST':
            rawData = request.POST
        else:
            raise

        # Build the dict because django sucks
        for k, v in rawData.iteritems():
            if v == '':
                v = None
            data[k] = v

        if not kwargs.get('allow_oauth_token', False):
            data.pop('oauth_token', None)
        data.pop('client_id', None)
        data.pop('client_secret', None)
        
        logData = data.copy()
        
        obfuscate = kwargs.pop('obfuscate', [])
        obfuscate.append('password')
        for item in obfuscate:
            if item in logData:
                logData[item] = '*****'
        logs.form(logData)
        
        if schema is None:
            if len(data) > 0:
                raise
            return
        
        schema.dataImport(data)
        schema.validate()
        
        logs.debug("Parsed request data")
        return schema
    
    except Exception as e:
        msg = "Invalid form (%s): %s vs %s" % (e, pformat(data), schema)
        logs.warning(msg)
        logs.warning(utils.getFormattedException())
        raise e

def parseFileUpload(schema, request, fileName='image', **kwargs):
    ### Parse Request
    try:
        if request.method != 'POST':
            raise
        rawData = request.POST
        
        # Build the dict because django sucks
        data = {}
        for k, v in rawData.iteritems():
            data[k] = v
        
        # Extract file
        if fileName in request.FILES:
            f = request.FILES[fileName]
            max_size = 1048576 # 1 MB
            
            if f.size > max_size:
                msg = "Uploaded file is too large (%s) (max size is %d)" % (f.size, max_size)
                logs.warning(msg)
                raise Exception(msg)
            
            data[fileName] = f.read()
            logs.attachment(fileName, f.size)

        if not kwargs.get('allow_oauth_token', False):
            data.pop('oauth_token',   None)
        data.pop('client_id', None)
        data.pop('client_secret', None)
        
        logData = data.copy()
        
        obfuscate = kwargs.pop('obfuscate', [])
        obfuscate.append('password')
        for item in obfuscate:
            if item in logData:
                logData[item] = '*****'
        if fileName in logData:
            logData[fileName] = 'FILE (SIZE: %s)' % f.size
        logs.form(logData)
        
        if schema == None:
            if len(data) > 0:
                raise
            return
        
        schema.dataImport(data)
        schema.validate()
        
        logs.debug("Parsed request data")
        return schema
    except Exception as e:
        msg = "Unable to parse form (%s)" % e
        logs.warning(msg)
        utils.printException()
        raise e

def transformOutput(value, **kwargs):
    """
    Serialize object to json and return it as an HttpResponse object
    """
    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    kwargs.setdefault('mimetype', 'application/json')

    if isinstance(value, bool):
        value = { 'result' : value }
    
    output_json = json.dumps(value, sort_keys=not IS_PROD)
    output      = HttpResponse(output_json, **kwargs)
    
    logs.output(output_json)
    return output

