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
        self._local = utils.is_ec2()
        self.api = globalMongoStampedAPI()
    
    def getUser(self, **params):
        if self._local:
            raise NotImplementedError
        else:
            return self._handle_get("users/show.json", params)
    
    def getUserStamps(self, **params):
        if self._local:
            raise NotImplementedError
        else:
            return self._handle_get("collections/user.json", params)
    
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

def stamped_view(f):
    @wraps(f)
    def _wrapper(request, *args, **kwargs):
        try:
            logs.begin(saveLog=stampedAPIProxy.api._logsDB.saveLog,
                       saveStat=stampedAPIProxy.api._statsDB.addStat,
                       requestData=request,
                       nodeName=stampedAPIProxy.api.node_name)
            logs.info("%s %s" % (request.method, request.path))
            
            response = f(request, *args, **kwargs)
            logs.info("End request: Success")
            
            response['Expires'] = (dt.datetime.utcnow() + dt.timedelta(minutes=10)).ctime()
            response['Cache-Control'] = 'max-age=600'
            
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

def stamped_render(request, template, context, **kwargs):
    # augment template context with global django / stamped settings
    kwargs['context_instance'] = kwargs.get('context_instance', RequestContext(request))
    
    context = copy.copy(context)
    context.update(STAMPED_SETTINGS)
    
    return render_to_response(template, context, **kwargs)

