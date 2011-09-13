#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Stamped (dev@stamped.com)"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2011 Stamped.com"
__license__ = "TODO"

import init
import os, json, utils, random, time, hashlib, logs

from errors import *
from HTTPSchemas import *
from api.MongoStampedAPI import MongoStampedAPI
from api.MongoStampedAuth import MongoStampedAuth
from django.http import HttpResponse
from django.utils.functional import wraps
from django.views.decorators.http import require_http_methods

stampedAPI  = MongoStampedAPI()
stampedAuth = MongoStampedAuth()

def handleHTTPRequest(fn):
    @wraps(fn)
    def handleHTTPRequest(request, *args, **kwargs):
        try:
            print
            print
            logs.begin(stampedAPI._logsDB.addLog)
            logs.request(request)
            logs.info("%s %s" % (request.method, request.path))
            ret = fn(request, *args, **kwargs)
            logs.info("End request: Success")
            return ret

        except StampedHTTPError as e:
            logs.warning("%s Error: %s (%s)" % (e.code, e.msg, e.desc))
            response = HttpResponse(e.msg)
            response.status_code = e.code
            logs.error(response.status_code)
            return response

        except IllegalActionError as e:
            logs.warning("403 Error: %s" % (e.msg))
            response = HttpResponse("illegal_action")
            response.status_code = 403
            logs.error(response.status_code)
            return response

        except InsufficientPrivilegesError as e:
            logs.warning("403 Error: %s" % (e.msg))
            response = HttpResponse("insufficient_privileges")
            response.status_code = 403
            logs.error(response.status_code)
            return response

        except InputError as e:
            logs.warning("400 Error: %s" % (e.msg))
            response = HttpResponse("invalid_request")
            response.status_code = 400
            logs.error(response.status_code)
            return response

        except Exception as e:
            logs.warning("500 Error: %s" % e)
            utils.printException()
            
            response = HttpResponse("error")
            response.status_code = 500
            logs.error(response.status_code)
            return response

        finally:
            logs.save()

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
        return client_id
    except:
        msg = "Invalid client credentials"
        logs.warning(msg)
        raise StampedHTTPError("access_denied", 401, msg)

def checkOAuth(request):
    ### Parse Request for Access Token
    try:
        if request.method == 'GET':
            oauth_token = request.GET['oauth_token']
        elif request.method == 'POST':
            oauth_token = request.POST['oauth_token']
        else:
            raise
        logs.token(oauth_token)
    except:
        msg = "Access token not included"
        logs.warning(msg)
        raise StampedHTTPError("invalid_request", 401, msg)
    
    ### Validate OAuth Access Token
    try:
        authenticated_user_id = stampedAuth.verifyAccessToken(oauth_token)
        if authenticated_user_id == None:
            raise
        logs.user(authenticated_user_id)
        return authenticated_user_id
    except StampedHTTPError:
        raise
    except Exception:
        msg = "Invalid access token"
        logs.warning(msg)
        raise StampedHTTPError("invalid_token", 401, msg)

def parseRequest(schema, request):
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
        if 'password' in logData:
            logData['password'] = '*****'
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
        
        raise StampedHTTPError("bad_request", 400)

def parseFileUpload(schema, request, fileName='image'):
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
            max_size = 1048576 # 1 mb in bytes
            
            if f.size > max_size:
                msg = "Uploaded file is too large (%s) (max size is %d)" % (f.size, max_size)
                logs.warning(msg)
                raise Exception(msg)
            
            data[fileName] = f.read()
            logs.attachment(fileName, f.size)
        
        data.pop('oauth_token', None)
        data.pop('client_id', None)
        data.pop('client_secret', None)
            
        logs.form(data)
        
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
        
        raise StampedHTTPError("bad_request", 400)

def transformOutput(value, **kwargs):
    kwargs.setdefault('content_type', 'text/javascript; charset=UTF-8')
    kwargs.setdefault('mimetype', 'application/json')
    
    output_json = json.dumps(value, sort_keys=True)
    output = HttpResponse(output_json, **kwargs)
    
    # pretty_output = json.dumps(value, sort_keys=True, indent=2)
    logs.output(output_json)
    
    return output

