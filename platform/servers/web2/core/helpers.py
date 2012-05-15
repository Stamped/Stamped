#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import copy, json, logs, urllib2, utils
import libs.ec2_utils
import datetime as dt
import settings

from MongoStampedAPI            import globalMongoStampedAPI
from HTTPSchemas                import *
from errors                     import *

from django.http                import HttpResponse
from django.shortcuts           import render_to_response
from django.template            import RequestContext
from django.utils.functional    import wraps

# initialize several useful globals
IS_PROD  = libs.ec2_utils.is_prod_stack()
_baseurl = "https://dev.stamped.com/v0"

# extract all of the settings from django's settings.py which begin with STAMPED_
# note that these settings will be included in the context of every rendered template.
STAMPED_SETTINGS = filter(lambda s: s.startswith('STAMPED_'), dir(settings))
STAMPED_SETTINGS = dict(map(lambda s: (s, eval('settings.%s' % s)), STAMPED_SETTINGS))

class StampedAPIProxy(object):
    
    def __init__(self):
        self._prod = IS_PROD
        self.api = globalMongoStampedAPI()
    
    def getUser(self, **params):
        if self._prod:
            raise NotImplementedError
        else:
            return self._handle_get("users/show.json", params)
    
    def getUserStamps(self, **params):
        if self._prod:
            raise NotImplementedError
        else:
            return self._handle_get("collections/user.json", params)
    
    def getFriends(self, **params):
        if self._prod:
            raise NotImplementedError
        else:
            response = self._handle_get("friendships/friends.json", params)
            
            if 'user_ids' in response and len(response['user_ids']) > 0:
                # TODO: this only returns max 100 at a time
                return self._handle_post("users/lookup.json", {
                    'user_ids' : ",".join(response['user_ids']), 
                });
            else:
                return []
    
    def getFollowers(self, **params):
        if self._prod:
            raise NotImplementedError
        else:
            response = self._handle_get("friendships/followers.json", params)
            
            if 'user_ids' in response and len(response['user_ids']) > 0:
                # TODO: this only returns max 100 at a time
                return self._handle_post("users/lookup.json", {
                    'user_ids' : ",".join(response['user_ids']), 
                });
            else:
                return []
    
    def _handle_local_get(self, func, params):
        pass
    
    def _handle_get(self, path, data):
        params = urllib.urlencode(data)
        url    = "%s/%s?%s" % (_baseurl, path, params)
        
        if not IS_PROD:
            utils.log("GET:  %s" % url)
        
        raw = urllib2.urlopen(url).read()
        return json.loads(raw)
    
    def _handle_post(self, path, data):
        params = urllib.urlencode(data)
        url    = "%s/%s" % (_baseurl, path)
        
        if not IS_PROD:
            utils.log("POST: %s" % url)
            utils.log(pformat(params))
        
        raw = urllib2.urlopen(url, params).read()
        return json.loads(raw)

stampedAPIProxy = StampedAPIProxy()

def stamped_view(schema=None, 
                 parse_request_kwargs=None, 
                 parse_django_kwargs=True):
    def decorator(fn):
        # NOTE (travis): if you hit this assertion, you're likely using the 
        # handleHTTPRequest incorrectly.
        assert callable(fn)
        
        @wraps(fn)
        def _wrapper(request, *args, **kwargs):
            try:
                logs.begin(saveLog=stampedAPIProxy.api._logsDB.saveLog,
                           saveStat=stampedAPIProxy.api._statsDB.addStat,
                           requestData=request,
                           nodeName=stampedAPIProxy.api.node_name)
                logs.info("%s %s" % (request.method, request.path))
                
                subkwargs = kwargs
                
                if schema is not None:
                    parse_kwargs  = parse_request_kwargs or {}
                    django_kwargs = {}
                    
                    if parse_django_kwargs:
                        django_kwargs = kwargs or {}
                        subkwargs = {}
                    
                    result = parse_request(request, schema(), django_kwargs, **parse_kwargs)
                    subkwargs['schema'] = result
                
                response = fn(request, *args, **subkwargs)
                logs.info("End request: Success")
                
                response['Expires'] = (dt.datetime.utcnow() + dt.timedelta(minutes=10)).ctime()
                response['Cache-Control'] = 'max-age=600'
                
                return response
            
            except urllib2.HTTPError, e:
                logs.warning("%s Error: %s" % (e.code, e))
                logs.warning(utils.getFormattedException())
                
                response = HttpResponse("%s" % e, status=e.code)
                logs.error(response.status_code)
                return response
            
            except StampedHTTPError as e:
                logs.warning("%s Error: %s (%s)" % (e.code, e.msg, e.desc))
                logs.warning(utils.getFormattedException())
                
                response = HttpResponse(e.msg, status=e.code)
                logs.error(response.status_code)
                return response
            
            except StampedAuthError as e:
                logs.warning("401 Error: %s" % (e.msg))
                logs.warning(utils.getFormattedException())
                
                response = HttpResponse(e.msg, status=401)
                logs.auth(e.msg)
                return response
            
            except StampedInputError as e:
                logs.warning("400 Error: %s" % (e.msg))
                logs.warning(utils.getFormattedException())
                
                response = HttpResponse("invalid_request", status=400)
                logs.error(response.status_code)
                return response
            
            except StampedIllegalActionError as e:
                logs.warning("403 Error: %s" % (e.msg))
                logs.warning(utils.getFormattedException())
                
                response = HttpResponse("illegal_action", status=403)
                logs.error(response.status_code)
                return response
            
            except StampedPermissionsError as e:
                logs.warning("403 Error: %s" % (e.msg))
                logs.warning(utils.getFormattedException())
                
                response = HttpResponse("insufficient_privileges", status=403)
                logs.error(response.status_code)
                return response
            
            except StampedDuplicationError as e:
                logs.warning("409 Error: %s" % (e.msg))
                logs.warning(utils.getFormattedException())
                
                response = HttpResponse("already_exists", status=409)
                logs.error(response.status_code)
                return response
            
            except StampedUnavailableError as e:
                logs.warning("404 Error: %s" % (e.msg))
                logs.warning(utils.getFormattedException())
                
                response = HttpResponse("not_found", status=404)
                logs.error(response.status_code)
                return response
            
            except Exception as e:
                logs.warning("500 Error: %s" % e)
                logs.warning(utils.getFormattedException())
                utils.printException()
                
                response = HttpResponse("internal server error", status=500)
                logs.error(response.status_code)
                return response
            
            finally:
                try:
                    logs.save()
                except:
                    pass

        return _wrapper
    return decorator

def stamped_render(request, template, context, **kwargs):
    # augment template context with global django / stamped settings
    kwargs['context_instance'] = kwargs.get('context_instance', RequestContext(request))
    
    preload = kwargs.pop('preload', None)
    context = get_stamped_context(context, preload)
    
    return render_to_response(template, context, **kwargs)

def get_stamped_context(context, preload=None):
    context = copy.copy(context)
    
    context["DEBUG"]   = not IS_PROD
    context["IS_PROD"] = IS_PROD
    
    # only preload global STAMPED_PRELOAD javscript variable if desired by the 
    # calling view
    if preload is None:
        ctx = context
    else:
        ctx = dict(((k, context[k]) for k in preload))
    
    json_context = json.dumps(ctx, sort_keys=not IS_PROD)
    stamped_preload = "var STAMPED_PRELOAD = %s;" % json_context
    
    context["STAMPED_PRELOAD_JS"] = stamped_preload
    context.update(STAMPED_SETTINGS)
    
    return context

def parse_request(request, schema, django_kwargs, **kwargs):
    data = { }
    
    try:
        if request.method == 'GET':
            rawData = request.GET
        elif request.method == 'POST':
            rawData = request.POST
        else:
            raise "invalid HTTP method '%s'" % request.method
        
        # Build the dict because django sucks
        for k, v in rawData.iteritems():
            data[k] = v
        
        for k, v in django_kwargs.iteritems():
            if k in data:
                msg = "duplicate django kwarg '%s' found in request %s data" % (k, request.method)
                raise msg
            
            data[k] = v
        
        logs.info("REQUEST: %s" % pformat(data))
        
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
        
        schema.importData(data)
        return schema
    except Exception as e:
        msg = "Invalid form (%s): %s vs %s" % (e, pformat(data), schema)
        logs.warning(msg)
        logs.warning(utils.getFormattedException())
        
        raise StampedHTTPError("invalid_form", 400, msg)

def format_url(url_format, schema, diff = None):
    import string
    formatter = string.Formatter()
    
    data = schema.exportSparse()
    url  = ""
    
    if diff is not None:
        for k, v in diff.iteritems():
            data[k] = v
    
    for chunk in formatter.parse(url_format):
        variable = chunk[1]
        value = ""
        
        if variable is not None:
            if variable in data:
                value = data[variable]
                del data[variable]
            else:
                value = schema[variable]
        
        url += "%s%s" % (chunk[0], value)
    
    if len(data) > 0:
        params = urllib.urlencode(data)
        
        if len(params) > 0:
            url = "%s?%s" % (url, params)
    
    return url

