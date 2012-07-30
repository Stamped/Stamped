#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import copy, json, logs, urllib2, utils
import libs.ec2_utils
import datetime as dt

from errors                     import *

from api.HTTPSchemas            import *
from api.MongoStampedAPI        import globalMongoStampedAPI
from libs.Memcache              import globalMemcache, generateKeyFromDictionary

from servers.web2               import settings

from django.http                import HttpResponse, Http404
from django.shortcuts           import render_to_response
from django.template            import RequestContext
from django.utils.functional    import wraps

# initialize several useful globals
IS_PROD  = libs.ec2_utils.is_prod_stack()
#_baseurl = "https://api.stamped.com/v1"
_baseurl = "https://dev.stamped.com/v1"
#_baseurl = "https://ec2-50-19-40-37.compute-1.amazonaws.com/v1"
#_baseurl = "https://ec2-107-21-83-72.compute-1.amazonaws.com/v1"

# extract all of the settings from django's settings.py which begin with STAMPED_
# note that these settings will be included in the context of every rendered template.
STAMPED_SETTINGS = filter(lambda s: s.startswith('STAMPED_'), dir(settings))
STAMPED_SETTINGS = dict(map(lambda s: (s, eval('settings.%s' % s)), STAMPED_SETTINGS))

CLIENT_ID        = 'web-1.0.0'
CLIENT_SECRET    = '9lm4520o4m3718m3nmpn10h71nlbmui5'

# TODO (travis): move StampedAPIProxy to its own file!
class StampedAPIProxy(object):
    
    def __init__(self):
        self._prod = IS_PROD
        self._ec2  = utils.is_ec2()
        
        self.api    = globalMongoStampedAPI()
        self._cache = globalMemcache()
    
    def _try_get_cache(self, key):
        try:
            return self._cache[key]
        except KeyError:
            pass
        
        return None
    
    def _try_set_cache(self, key, value, ttl=600):
        try:
            self._cache.set(key, value, time=ttl)
        except Exception as e:
            logs.warning("Unable to set cache: %s" % e)
        
        return value
    
    def _export(self, d):
        for k, v in d.iteritems():
            if isinstance(v, datetime.datetime):
                d[k] = v.isoformat()
            elif isinstance(v, dict):
                d[k] = self._export(v)
        
        return d
    
    def checkAccount(self, email):
        if self._ec2:
            user = self.api.checkAccount(email)
            
            return HTTPUser().importUser(user).dataExport()
        else:
            return self._handle_post("account/check.json", {
                'login'         : email, 
                'client_id'     : CLIENT_ID, 
                'client_secret' : CLIENT_SECRET, 
            })
    
    def getAccountByScreenName(self, screen_name):
        if self._ec2:
            key = str("web::getAccountByScreenName::%s" % screen_name)
            
            ret = self._try_get_cache(key)
            if ret is not None:
                return ret
            
            ret = self._export(self.api.getAccountByScreenName(screen_name).dataExport())
            return self._try_set_cache(key, ret, 600 * 3)
        else:
            return self._handle_get("users/show.json", { 'screen_name' : screen_name })
    
    def getAccount(self, user_id):
        if self._ec2:
            key = str("web::getAccount::%s" % user_id)
            
            ret = self._try_get_cache(key)
            if ret is not None:
                return ret
            
            ret = self._export(self.api.getAccount(user_id).dataExport())
            return self._try_set_cache(key, ret, 600 * 3)
        else:
            return self._handle_get("users/show.json", { 'user_id' : user_id })
    
    def updateAlerts(self, user_id, on, off):
        if self._ec2:
            return self.api.updateAlerts(user_id, on, off)
        else:
            raise NotImplementedError
    
    def getUser(self, params):
        if self._ec2:
            key = str("web::getUser::%s" % generateKeyFromDictionary(params))
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            user = self.api.getUser(HTTPUserId().dataImport(params), None)
            ret  = HTTPUser().importUser(user).dataExport()
            
            return self._try_set_cache(key, ret)
        else:
            return self._handle_get("users/show.json", params)
    
    def getUserStamps(self, params):
        params['scope'] = 'user'
        
        if self._ec2:
            key = str("web::getUserStamps::%s" % generateKeyFromDictionary(params))
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            ts  = HTTPTimeSlice.exportTimeSlice(HTTPTimeSlice().dataImport(params))
            ret = self._transform_stamps(self.api.getStampCollection(ts, None))
            
            return self._try_set_cache(key, ret)
        else:
            return self._handle_get("stamps/collection.json", params)
    
    def _transform_stamps(self, stamps):
        if stamps is None:
            stamps = []
        
        ret = []
        
        for stamp in stamps:
            try:
                ret.append(HTTPStamp().importStamp(stamp).dataExport())
            except Exception:
                logs.warn(utils.getFormattedException())
        
        return ret
    
    def _transform_users(self, users):
        output = []
        
        for user in users:
            output.append(HTTPUser().importUser(user).dataExport())
        
        return output
    
    def getFriends(self, user_id, limit=None):
        if self._ec2:
            key = str("web::getFriends::user_id=%s" % user_id)
            if limit is not None:
                key = str("%s,%s" % (key, limit))
            
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            ret = self._transform_users(self.api.getEnrichedFriends(user_id, limit))
            return self._try_set_cache(key, ret)
        else:
            params = { 'user_id' : user_id }
            
            return self._get_users("friendships/friends.json", params, limit)
    
    def getFollowers(self, user_id, limit=None):
        if self._ec2:
            key = str("web::getFollowers::user_id=%s" % user_id)
            if limit is not None:
                key = str("%s,%s" % (key, limit))
            
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            ret = self._transform_users(self.api.getEnrichedFollowers(user_id, limit))
            return self._try_set_cache(key, ret)
        else:
            params = { 'user_id' : user_id }
            
            return self._get_users("friendships/followers.json", params, limit)
    
    def getLikes(self, stamp_id, limit=None):
        if self._ec2:
            key = str("web::getLikes::stamp_id=%s" % stamp_id)
            if limit is not None:
                key = str("%s,%s" % (key, limit))
            
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            user_ids = self.api.getLikes(None, stamp_id)
            ret = self._transform_users(self.api.getUsers(user_ids, None, None))
            
            return self._try_set_cache(key, ret)
        else:
            params = { 'stamp_id' : stamp_id }
            
            return self._get_users("stamps/likes/show.json", params, limit)
    
    def getTodos(self, stamp_id, limit=None):
        if self._ec2:
            key = str("web::getTodos::stamp_id=%s" % stamp_id)
            if limit is not None:
                key = str("%s,%s" % (key, limit))
            
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            user_ids = self.api.getStampTodos(None, stamp_id)
            ret = self._transform_users(self.api.getUsers(user_ids, None, None))
            
            return self._try_set_cache(key, ret)
        else:
            params = { 'stamp_id' : stamp_id }
            
            return self._get_users("stamps/todos/show.json", params, limit)
    
    def _get_users(self, path, params, limit=None):
        response = self._handle_get(path, params)
        
        if 'user_ids' in response and len(response['user_ids']) > 0:
            if limit is not None:
                response['user_ids'] = response['user_ids'][:limit]
            
            # TODO: PAGING -- this only returns max 100 at a time
            return self._handle_post("users/lookup.json", {
                'user_ids' : ",".join(response['user_ids']), 
            })
        else:
            return []
    
    def getStampFromUser(self, user_id, stamp_num):
        if self._ec2:
            key = str("web::getStampFromUser::user_id=%s,stamp_num=%s" % (user_id, stamp_num))
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            stamp  = self.api.getStampFromUser(userId=user_id, stampNumber=stamp_num)
            ret = HTTPStamp().importStamp(stamp).dataExport()
            
            return self._try_set_cache(key, ret)
        else:
            return self._handle_get("stamps/show.json", {
                'user_id'   : user_id, 
                'stamp_num' : stamp_num, 
            })
    
    def getEntity(self, entity_id):
        if self._ec2:
            key = str("web::getEntity::entity_id=%s" % entity_id)
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            entity = self.api.getEntity(HTTPEntityIdSearchId().dataImport({'entity_id' : entity_id}), None)
            ret = HTTPEntity().importEntity(entity, None).dataExport()
            
            return self._try_set_cache(key, ret)
        else:
            return self._handle_get("entities/show.json", {
                'entity_id' : entity_id
            })
    
    def getEntityMenu(self, entity_id):
        if self._ec2:
            key = str("web::getEntityMenu::entity_id=%s" % entity_id)
            ret = self._try_get_cache(key)
            
            if ret is not None:
                return ret
            
            menu   = self.api.getMenu(entity_id)
            ret = HTTPMenu().importMenu(menu).dataExport()
            
            return self._try_set_cache(key, ret)
        else:
            return self._handle_get("entities/menu.json", {
                'entity_id' : entity_id
            })
    
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
                 ignore_extra_params=False, 
                 parse_request_kwargs=None, 
                 parse_django_kwargs=True):
    def decorator(fn):
        # NOTE (travis): if you hit this assertion, you're likely using the 
        # handleHTTPRequest incorrectly.
        assert callable(fn)
        
        @wraps(fn)
        def _wrapper(request, *args, **kwargs):
            import servers.web2.error.views as web_error
            
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
                    
                    result = parse_request(request, schema(), django_kwargs, overflow=ignore_extra_params, **parse_kwargs)
                    subkwargs['schema'] = result
                
                response = fn(request, *args, **subkwargs)
                logs.info("End request: Success")
                
                if utils.is_ec2():
                    response['Expires'] = (dt.datetime.utcnow() + dt.timedelta(minutes=60)).ctime()
                    response['Cache-Control'] = 'max-age=600'
                else:
                    # disable caching for local development / debugging
                    response['Expires'] = (dt.datetime.utcnow() - dt.timedelta(minutes=10)).ctime()
                    response['Cache-Control'] = 'max-age=0'
                
                return response
            
            except urllib2.HTTPError, e:
                logs.warning("%s Error: %s" % (e.code, e))
                logs.warning(utils.getFormattedException())
                
                if e.code == 404:
                    return web_error.error_404(request)
                elif e.code >= 500:
                    return web_error.error_500(request)
                
                raise # invoke django's default 500 handler
                #response = HttpResponse("%s" % e, status=e.code)
                #logs.error(response.status_code)
                #return response
            
            except StampedHTTPError as e:
                logs.warning("%s Error: %s" % (e.code, e.msg))
                logs.warning(utils.getFormattedException())
                
                raise # invoke django's default 500 handler
                #response = HttpResponse(e.msg, status=e.code)
                #logs.error(response.status_code)
                #return response
            
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
                
                return web_error.error_404(request)
                
                #response = HttpResponse("not_found", status=404)
                #logs.error(response.status_code)
                #return response
            
            except Exception as e:
                logs.warning("500 Error: %s" % e)
                logs.warning(utils.getFormattedException())
                utils.printException()
                
                logs.error(500)
                raise # invoke django's default 500 handler
                #response = HttpResponse("internal server error", status=500)
                #return response
            
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
    
    #utils.log(pprint.pformat(context))
    return render_to_response(template, context, **kwargs)

def get_stamped_context(context, preload=None):
    context = copy.copy(context)
    
    context["DEBUG"]   = settings.DEBUG
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

def parse_request(request, schema, django_kwargs, overflow, **kwargs):
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
        
        schema.dataImport(data, overflow=overflow)
        return schema
    except Exception as e:
        msg = "Invalid form (%s): %s vs %s" % (e, pformat(data), schema)
        logs.warning(msg)
        logs.warning(utils.getFormattedException())
        
        raise StampedHTTPError("invalid_form", 400, msg)

def format_url(url_format, schema, diff = None):
    import string
    formatter = string.Formatter()
    
    data = schema.dataExport()
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

def is_static_profile_image(url):
    return url.lower().strip() == 'http://static.stamped.com/users/default.jpg'

def get_body_classes(base, schema):
    has_category    = False
    has_subcategory = False
    body_classes    = base
    
    try:
        has_category    = (schema.category is not None)
        has_subcategory = (schema.subcategory is not None)
    except:
        pass
    
    if has_category:
        body_classes += " %s" % schema.category
    else:
        body_classes += " default"
    
    if has_subcategory:
        body_classes += " %s" % schema.subcategory
    
    return body_classes

# ensure friends and followers are randomly shuffled s.t. different users will 
# appear every page refresh, with preferential treatment always going to users 
# who have customized their profile image away from the default.
def shuffle_split_users(users):
    has_image        = (lambda a: a.get('image_url', None) is not None)
    has_custom_image = (lambda a: has_image(a) and not is_static_profile_image(a['image_url']))
    
    # find all users who have a custom profile image
    a0 = filter(has_custom_image, users)
    
    # find all users who have the default profile image
    a1 = filter(lambda a: not has_custom_image(a), users)
    
    # shuffle them both independently
    a0 = utils.shuffle(a0)
    a1 = utils.shuffle(a1)
    
    # and combine the results s.t. all users with custom profile images precede 
    # all those without custom profile images
    a0.extend(a1)
    
    return a0

def transform_output(value, **kwargs):
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

def convert_stamp(stamp):
    for i in xrange(len(stamp['contents'])):
        content = stamp['contents'][i]
        if 'blurb_references' in content and 'blurb' in content:
            content['blurb'] = convert_blurb(content['blurb'], content['blurb_references'])
    
    return stamp

def convert_blurb(blurb, references=None):
    prevIndex = 0
    result = []
    
    if references is not None:
        for reference in references:
            bgn = reference['indices'][0]
            end = reference['indices'][1]
            
            # Append previous section
            result.append(blurb[prevIndex:bgn]) 
            
            # Build this section
            if reference['action']['type'] == 'link':
                result.append("<a href='%s'>%s</a>" % (reference['action']['sources'][0]['link'], blurb[bgn:end]))
            elif reference['action']['type'] == 'stamped_view_screen_name':
                result.append("<class='mention'>%s</class>" % (blurb[bgn:end]))
            
            prevIndex = end
    
    if len(blurb) > prevIndex:
        result.append(blurb[prevIndex:])
    
    result = ''.join(result)
    result = result.replace('\n', '<br>')
    result = result.replace('  ', '&nbsp;&nbsp;')
    
    return result

