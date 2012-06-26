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
from HTTPSchemas                    import *
from api.MongoStampedAPI            import globalMongoStampedAPI
from api.MongoStampedAuth           import MongoStampedAuth

from django.views.decorators.http   import require_http_methods
from django.utils.functional        import wraps
from django.http                    import HttpResponse

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

def handleHTTPRequest(requires_auth=True, 
                      requires_client=False,
                      http_schema=None,
                      conversion=None,
                      upload=None, 
                      parse_request_kwargs=None, 
                      parse_request=True):
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
                origin = ""
                
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
                params['authUserId'], params['authClientId'] = checkOAuth(request, required=requires_auth)
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
            
            except StampedHTTPError as e:
                if e.kind is None:
                    e.kind = 'stamped_error'

                logs.warning("%s Error (%s): %s" % (e.code, e.kind, e.msg))
                logs.warning(utils.getFormattedException())
                logs.error(e.code)

                error = {'error': e.kind}
                if e.msg is not None:
                    error['message'] = unicode(e.msg)

                return transformOutput(error, status=e.code)
            
            except StampedAuthError as e:
                logs.warning("401 Error: %s" % (e.msg))
                logs.warning(utils.getFormattedException())
                logs.error(401)

                error = {'error': e.msg}
                return transformOutput(error, status=401)
            
            except StampedInputError as e:
                logs.warning("400 Error: %s" % (e.msg))
                logs.warning(utils.getFormattedException())
                logs.error(400)
                
                error = {'error': 'invalid_request'}
                if e.msg is not None:
                    error['message'] = unicode(e.msg)
                return transformOutput(error, status=400)
            
            except StampedIllegalActionError as e:
                logs.warning("403 Error: %s" % (e.msg))
                logs.warning(utils.getFormattedException())
                logs.error(403)

                error = {'error': 'illegal_action'}
                if e.msg is not None:
                    error['message'] = unicode(e.msg)
                return transformOutput(error, status=403)
            
            except StampedPermissionsError as e:
                logs.warning("403 Error: %s" % (e.msg))
                logs.warning(utils.getFormattedException())
                logs.error(403)

                error = {'error': 'insufficient_privileges'}
                return transformOutput(error, status=403)
            
            except StampedDuplicationError as e:
                logs.warning("409 Error: %s" % (e.msg))
                logs.warning(utils.getFormattedException())
                logs.error(409)

                error = {'error': 'already_exists'}
                if e.msg is not None:
                    error['message'] = unicode(e.msg)
                return transformOutput(error, status=409)
            
            except StampedUnavailableError as e:
                logs.warning("404 Error: %s" % (e.msg))
                logs.warning(utils.getFormattedException())
                logs.error(404)

                error = {'error': 'not_found'}
                if e.msg is not None:
                    error['message'] = unicode(e.msg)
                return transformOutput(error, status=404)
            
            except Exception as e:
                logs.warning("500 Error: %s" % e)
                logs.warning(utils.getFormattedException())
                logs.error(500)

                error = {'error': 'internal server error'}
                return transformOutput(error, status=500)
            
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
        client_id       = request.POST['client_id']
        client_secret   = request.POST['client_secret']
    except Exception:
        if not required:
            return None 
        raise StampedInputError("Client credentials not included")
    
    ### Validate Client Credentials
    try:
        logs.client(client_id)
        if not stampedAuth.verifyClientCredentials(client_id, client_secret):
            raise 

        client = stampedAuth.getClientDetails(client_id)
        stampedAPI.setVersion(client.api_version)
        
        return client_id
    except Exception, e:
        logs.warning("Invalid client credentials (%s)" % e)
        raise StampedAuthError("access_denied", "Invalid client credentials")

def optionalOAuth(request):
    try:
        authUserId = checkOAuth(request)
    except Exception:
        authUserId = None
    
    return authUserId

def checkOAuth(request, required=True):
    ### Parse Request for Access Token
    try:
        if request.method == 'GET':
            oauth_token = request.GET['oauth_token']
        elif request.method == 'POST':
            oauth_token = request.POST['oauth_token']
        else:
            raise Exception
        
        logs.token(oauth_token)
    except Exception:
        if not required:
            return None, None 
        raise StampedInputError("Access token not found")
    
    ### Validate OAuth Access Token
    try:
        authenticated_user_id, client_id = stampedAuth.verifyAccessToken(oauth_token)
        if authenticated_user_id is None:
            raise StampedAuthError("invalid_request", "User not found")
        
        logs.user(authenticated_user_id)
        logs.client(client_id)
        
        client = stampedAuth.getClientDetails(client_id)
        stampedAPI.setVersion(client.api_version)
        
        return authenticated_user_id, client_id
    except StampedHTTPError:
        raise
    except Exception, e:
        logs.warning("Error: %s" % e)
        raise StampedAuthError("invalid_token", "Invalid access token")

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
            data[k] = v

        if not kwargs.get('allow_oauth_token', False):
            data.pop('oauth_token',   None)
        data.pop('client_id',     None)
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
        
        raise StampedHTTPError(400, kind="invalid_form")

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
        
        raise StampedHTTPError(400, kind="invalid_form")

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

