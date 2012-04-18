#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Helper utilities for API functions.

DOCUMENTED SAMPLE PATH MODULE
MULTIPLE USES from functions/account.py
"""
__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import stamped
import os, json, utils, random, time, hashlib, logs

from errors                         import *
from HTTPSchemas                    import *
from api.MongoStampedAPI            import MongoStampedAPI
from api.MongoStampedAuth           import MongoStampedAuth

from django.views.decorators.http   import require_http_methods
from django.utils.functional        import wraps
from django.http                    import HttpResponse

VALID_ORIGINS = [
    'http://stamped.com',
    'http://api.stamped.com', 
    'http://www.stamped.com',
    'http://dev.stamped.com',
    'http://localhost:19000',
    'http://localhost:18000',
]

t1 = time.time()

stampedAPI  = MongoStampedAPI()
stampedAuth = MongoStampedAuth()

t2 = time.time()
duration = (t2 - t1) * 1.0
logs.info("INIT: %s sec" % duration)

if duration > 2:
    logs.warning("LONG INIT: %s sec" % duration)

def handleHTTPRequest(fn):
    @wraps(fn)
    def handleHTTPRequest(request, *args, **kwargs):
        try:
            try:
                valid_origin = request.META['HTTP_ORIGIN'] if request.META['HTTP_ORIGIN'] in VALID_ORIGINS else None
            except:
                valid_origin = None

            if request.method == 'OPTIONS' and valid_origin is not None:
                response = HttpResponse()
                response['Access-Control-Allow-Origin'] = valid_origin
                response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                response['Access-Control-Max-Age'] = 1000
                response['Access-Control-Allow-Headers'] = '*'
                return response

            logs.begin(
                saveLog=stampedAPI._logsDB.saveLog,
                saveStat=stampedAPI._statsDB.addStat,
                requestData=request,
                nodeName=stampedAPI.node_name,
            )
            logs.info("%s %s" % (request.method, request.path))
            ret = fn(request, *args, **kwargs)
            logs.info("End request: Success")

            if valid_origin is not None and isinstance(ret, HttpResponse):
                ret['Access-Control-Allow-Origin'] = valid_origin
                ret['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
                ret['Access-Control-Max-Age'] = 1000
                ret['Access-Control-Allow-Headers'] = '*'

            return ret
        
        except StampedHTTPError as e:
            logs.warning("%s Error: %s (%s)" % (e.code, e.msg, e.desc))
            response = HttpResponse(e.msg, status=e.code)
            logs.error(response.status_code)
            return response
        
        except StampedAuthError as e:
            logs.warning("401 Error: %s" % (e.msg))
            response = HttpResponse(e.msg, status=401)
            logs.auth(e.msg)
            return response
        
        except StampedInputError as e:
            logs.warning("400 Error: %s" % (e.msg))
            response = HttpResponse("invalid_request", status=400)
            logs.error(response.status_code)
            return response
        
        except StampedIllegalActionError as e:
            logs.warning("403 Error: %s" % (e.msg))
            response = HttpResponse("illegal_action", status=403)
            logs.error(response.status_code)
            return response
        
        except StampedPermissionsError as e:
            logs.warning("403 Error: %s" % (e.msg))
            response = HttpResponse("insufficient_privileges", status=403)
            logs.error(response.status_code)
            return response
        
        except StampedDuplicationError as e:
            logs.warning("409 Error: %s" % (e.msg))
            response = HttpResponse("already_exists", status=409)
            logs.error(response.status_code)
            return response
        
        except StampedUnavailableError as e:
            logs.warning("404 Error: %s" % (e.msg))
            response = HttpResponse("not_found", status=404)
            logs.error(response.status_code)
            return response
        
        except Exception as e:
            logs.warning("500 Error: %s" % e)
            logs.warning(utils.getFormattedException())
            response = HttpResponse("internal server error", status=500)
            logs.error(response.status_code)
            return response
        
        finally:
            try:
                logs.save()
            except:
                pass
    
    return handleHTTPRequest

def checkClient(request):
    ### Parse Request for Client Credentials
    try:
        client_id       = request.POST['client_id']
        client_secret   = request.POST['client_secret']
    except:
        msg = "Client credentials not included"
        logs.warning(msg)
        raise StampedHTTPError("invalid_request", 401, msg)
    
    ### Validate Client Credentials
    try:
        logs.client(client_id)
        if not stampedAuth.verifyClientCredentials(client_id, client_secret):
            raise

        client = stampedAuth.getClientDetails(client_id)
        stampedAPI.setVersion(client.api_version)
        
        return client_id
    except:
        msg = "Invalid client credentials"
        logs.warning(msg)
        raise StampedHTTPError("access_denied", 401, msg)

def optionalOAuth(request):
    try:
        authUserId = checkOAuth(request)
    except:
        authUserId = None
    
    return authUserId

def checkOAuth(request):
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
        msg = "Access token not found"
        logs.warning(msg)
        raise StampedHTTPError("invalid_request", 401, msg)
    
    ### Validate OAuth Access Token
    try:
        authenticated_user_id, client_id = stampedAuth.verifyAccessToken(oauth_token)
        if authenticated_user_id == None:
            raise
        
        logs.user(authenticated_user_id)
        logs.client(client_id)

        client = stampedAuth.getClientDetails(client_id)
        stampedAPI.setVersion(client.api_version)

        return authenticated_user_id, client_id
    except StampedHTTPError:
        raise
    except Exception:
        msg = "Invalid access token"
        logs.warning(msg)
        raise StampedAuthError("invalid_token", msg)

def parseRequest(schema, request, **kwargs):
    ### Parse Request
    try:
        if request.method == 'GET':
            rawData = request.GET
        elif request.method == 'POST':
            rawData = request.POST
        else:
            raise
        
        # Build the dict because django sucks
        data = {}
        for k, v in rawData.iteritems():
            data[k] = v
        
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
        
        schema.importData(data)
        
        logs.debug("Parsed request data")
        return schema
    
    except Exception as e:
        msg = "Unable to parse form (%s)" % e
        logs.warning(msg)
        utils.printException()
        
        raise StampedHTTPError("invalid_form", 400)

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
        
        data.pop('oauth_token', None)
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
        
        schema.importData(data)
        
        logs.debug("Parsed request data")
        return schema
    except Exception as e:
        msg = "Unable to parse form (%s)" % e
        logs.warning(msg)
        utils.printException()
        
        raise StampedHTTPError("invalid_form", 400)

def transformOutput(value, **kwargs):
    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    kwargs.setdefault('mimetype', 'application/json')
    
    output_json = json.dumps(value, sort_keys=True)
    output = HttpResponse(output_json, **kwargs)

    logs.output(output_json)
    
    return output

