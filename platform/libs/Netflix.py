__author__ = "Kirsten Jones <synedra@gmail.com>"
__version__ = "$Rev$"
__date_ = "$Date$"

import Globals
import sys
import os.path
import re
import oauth as oauth
import httplib
import time
import json
import utils
import logs

from errors                 import StampedHTTPError
from datetime           import datetime, timedelta
from RateLimiter        import RateLimiter
from urlparse           import urlparse
from xml.dom.minidom    import parseString

HOST              = 'api.netflix.com'
PORT              = '80'
REQUEST_TOKEN_URL = 'http://api.netflix.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'http://api.netflix.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api-user.netflix.com/oauth/login'


class NetflixError(Exception): pass

class NetflixUser(object):
    def __init__(self, user, client):
        self.requestTokenUrl = REQUEST_TOKEN_URL
        self.accessTokenUrl  = ACCESS_TOKEN_URL
        self.authorizationUrl = AUTHORIZATION_URL
        self.accessToken = oauth.OAuthToken( user['access']['key'], user['access']['secret'] )
        self.client = client
        self.data = None

    def getRequestToken(self):
        client = self.client
        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(client.consumer, http_url=self.requestTokenUrl)
        oauthRequest.sign_request(client.signature_method_hmac_sha1, client.consumer, None)
        client.connection.request(oauthRequest.http_method, self.requestTokenUrl, headers=oauthRequest.to_header())
        response = client.connection.getresponse()
        requestToken = oauth.OAuthToken.from_string(response.read())

        params = {'application_name': client.CONSUMER_NAME, 'oauth_consumer_key': client.CONSUMER_KEY}

        oauthRequest = oauth.OAuthRequest.from_token_and_callback(token=requestToken, callback=client.CONSUMER_CALLBACK,
              http_url=self.authorizationUrl, parameters=params)

        return ( requestToken, oauthRequest.to_url() )

    
    def getAccessToken(self, requestToken):
        client = self.client
        
        if not isinstance(requestToken, oauth.OAuthToken):
            requestToken = oauth.OAuthToken( requestToken['key'], requestToken['secret'] )
        
        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(  client.consumer,
                                    token=requestToken,
                                    http_url=self.accessTokenUrl)
        oauthRequest.sign_request(  client.signature_method_hmac_sha1,
                                    client.consumer,
                                    requestToken)
        client.connection.request(  oauthRequest.http_method,
                                    self.accessTokenUrl,
                                    headers=oauthRequest.to_header())
        response = client.connection.getresponse()
        accessToken = oauth.OAuthToken.from_string(response.read())
        return accessToken
    
    def getData(self):
        accessToken=self.accessToken

        if not isinstance(accessToken, oauth.OAuthToken):
            accessToken = oauth.OAuthToken( accessToken['key'], accessToken['secret'] )
        
        requestUrl = '/users/%s' % (accessToken.key)
        
        info = json.loads( self.client._getResource( requestUrl, token=accessToken ) )
        self.data = info['user']
        return self.data
        
    def getInfo(self,field):
        accessToken=self.accessToken
        
        if not self.data:
            self.getData()
            
        fields = []
        url = ''
        for link in self.data['link']:
                fields.append(link['title'])
                if link['title'] == field:
                    url = link['href']
                    
        if not url:
            errorString = "Invalid or missing field.  Acceptable fields for this object are:\n" + "\n".join(fields)
            raise Exception(errorString)        
        try:
            info = json.loads(self.client._getResource( url,token=accessToken ))
        except :
            return []
        else:
            return info
        
    def getRatings(self, discInfo=[], urls=[]):
        accessToken=self.accessToken
        
        if not isinstance(accessToken, oauth.OAuthToken):
            accessToken = oauth.OAuthToken( accessToken['key'], accessToken['secret'] )
        
        requestUrl = '/users/%s/ratings/title' % (accessToken.key)
        if not urls:
            if isinstance(discInfo,list):
                   for disc in discInfo:
                        urls.append(disc['id'])
            else:
                urls.append(discInfo['id'])
        parameters = { 'title_refs': ','.join(urls) }
        
        info = json.loads( self.client._getResource( requestUrl, parameters=parameters, token=accessToken ) )
        
        ret = {}
        for title in info['ratings']['ratings_item']:
                ratings = {
                        'average': title['average_rating'],
                        'predicted': title['predicted_rating'],
                }
                try:
                    ratings['user'] = title['user_rating']
                except:
                    pass
                
                ret[ title['title']['regular'] ] = ratings
        
        return ret

    def getRentalHistory(self,type=None,startIndex=None,maxResults=None,updatedMin=None):
        accessToken=self.accessToken
        parameters = {}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults
        if updatedMin:
            parameters['updated_min'] = updatedMin

        if not isinstance(accessToken, oauth.OAuthToken):
            accessToken = oauth.OAuthToken( accessToken['key'], accessToken['secret'] )

        if not type:
            requestUrl = '/users/%s/rental_history' % (accessToken.key)
        else:
            requestUrl = '/users/%s/rental_history/%s' % (accessToken.key,type)
        
        try:
            info = json.loads( self.client._getResource( requestUrl, parameters=parameters, token=accessToken ) )
        except:
            return {}
            
        return info
        
class NetflixCatalog(object):
    def __init__(self,client):
        self.client = client
    
    def searchTitles(self, term,startIndex=None,maxResults=None):
       requestUrl = '/catalog/titles'
       parameters = {'term': term}
       if startIndex:
           parameters['start_index'] = startIndex
       if maxResults:
           parameters['max_results'] = maxResults
       info = json.loads( self.client._getResource( requestUrl, parameters=parameters))

       return info['catalog_titles']['catalog_title']

    def searchStringTitles(self, term,startIndex=None,maxResults=None):
       requestUrl = '/catalog/titles/autocomplete'
       parameters = {'term': term}
       if startIndex:
           parameters['start_index'] = startIndex
       if maxResults:
           parameters['max_results'] = maxResults

       info = json.loads( self.client._getResource( requestUrl, parameters=parameters))
       print json.dumps(info)
       return info['autocomplete']['autocomplete_item']
    
    def getTitle(self, url):
       requestUrl = url
       info = simplejson.loads( self.client._getResource( requestUrl ))
       return info

    def searchPeople(self, term,startIndex=None,maxResults=None):
       requestUrl = '/catalog/people'
       parameters = {'term': term, 'expand': 'filmography','max_results':'15','start_index':0}
       if startIndex:
           parameters['start_index'] = startIndex
       if maxResults:
           parameters['max_results'] = maxResults

       try:
           info = json.loads( self.client._getResource( requestUrl, parameters=parameters))
       except:
           return []

       return info['people']['person']

    def getPerson(self,url):
        requestUrl = url
        try:
            info = json.loads( self.client._getResource( requestUrl ))
        except:
            return {}
        return info       

class NetflixUserQueue(object):
    def __init__(self,user):
        self.user = user
        self.client = user.client
        self.tag = None

    def getContents(self, sort=None, startIndex=None, maxResults=None, updatedMin=None):
        parameters={}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults
        if updatedMin:
            parameters['updated_min'] = updatedMin
        if sort and sort in ('queue_sequence','date_added','alphabetical'):
            parameters['sort'] = sort
        
        requestUrl = '/users/%s/queues' % (self.user.accessToken.key)
        try:
            info = json.loads(self.client._getResource( requestUrl, parameters=parameters, token=self.user.accessToken ))
        except :
            return []
        else:
            return info
            
    def getAvailable(self, sort=None, startIndex=None, maxResults=None, updatedMin=None,type='disc'):
        parameters={}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults
        if updatedMin:
            parameters['updated_min'] = updatedMin
        if sort and sort in ('queue_sequence','date_added','alphabetical'):
            parameters['sort'] = sort

        requestUrl = '/users/%s/queues/%s/available' % (self.user.accessToken.key,type)
        try:
            info = json.loads(self.client._getResource( requestUrl, parameters=parameters, token=self.user.accessToken ))
        except :
            return []
        else:
            return info

    def getSaved(self, sort=None, startIndex=None, maxResults=None, updatedMin=None,type='disc'):
        parameters={}
        if startIndex:
            parameters['start_index'] = startIndex
        if maxResults:
            parameters['max_results'] = maxResults
        if updatedMin:
            parameters['updated_min'] = updatedMin
        if sort and sort in ('queue_sequence','date_added','alphabetical'):
            parameters['sort'] = sort

        requestUrl = '/users/%s/queues/%s/saved' % (self.user.accessToken.key,type)
        try:
            info = json.loads(self.client._getResource( requestUrl, parameters=parameters, token=self.user.accessToken ))
        except :
            return []
        else:
            return info

    def addTitle(self, discInfo=[], urls=[],type='disc',position=None):
        accessToken=self.user.accessToken
        parameters={}
        if position:
            parameters['position'] = position
            
        if not isinstance(accessToken, oauth.OAuthToken):
            accessToken = oauth.OAuthToken( accessToken['key'], accessToken['secret'] )

        requestUrl = '/users/%s/queues/disc' % (accessToken.key)
        if not urls:
            for disc in discInfo:
                urls.append( disc['id'] )
        parameters = { 'title_ref': ','.join(urls) }

        if not self.tag:
            response = self.client._getResource( requestUrl, token=accessToken )
            response = json.loads(response)
            self.tag = response["queue"]["etag"]
        parameters['etag'] = self.tag
        response = self.client._postResource( requestUrl, token=accessToken, parameters=parameters )
        return response

    def removeTitle(self, id, type='disc'):
        accessToken=self.user.accessToken
        entryID = None
        parameters={}
        if not isinstance(accessToken, oauth.OAuthToken):
            accessToken = oauth.OAuthToken( accessToken['key'], accessToken['secret'] )

        # First, we gotta find the entry to delete
        queueparams = {'max_results' : 500}
        requestUrl = '/users/%s/queues/disc' % (accessToken.key)
        response = self.client._getResource( requestUrl, token=accessToken,parameters=queueparams )
        print "Response is " + response
        response = json.loads(response)
        titles = response["queue"]["queue_item"]
        
        for disc in titles:
            discID = os.path.basename(urlparse(disc['id']).path)
            if discID == id:
                entryID = disc['id']

        if not entryID:
            return
        firstResponse = self.client._getResource( entryID, token=accessToken, parameters=parameters )
        
        response = self.client._deleteResource( entryID, token=accessToken )
        return response

class NetflixDisc(object):
    def __init__(self,discInfo,client):
        self.info = discInfo
        self.client = client
    
    def getInfo(self,field):
        fields = []
        url = ''
        for link in self.info['link']:
                fields.append(link['title'])
                if link['title'] == field:
                    url = link['href']
        if not url:
            errorString = "Invalid or missing field.  Acceptable fields for this object are:\n" + "\n".join(fields)
            raise Exception(errorString)        
        try:
            info = json.loads(self.client._getResource( url ))
        except :
            return []
        else:
            return info

APP_NAME   = 'Stamped'
API_KEY    = 'nr5nzej56j3smjra6vtybbvw'
API_SECRET = 'H5A633JsYk'

class NetflixClient(object):
    
    def __init__(self, name=APP_NAME, key=API_KEY, secret=API_SECRET, callback='',verbose=False):
        self.connection = httplib.HTTPConnection("%s:%s" % (HOST, PORT))
        self.server = HOST
        self.verbose = verbose
        self.user = None
        self.catalog = NetflixCatalog(self)
        
        self.CONSUMER_NAME=name
        self.CONSUMER_KEY=key
        self.CONSUMER_SECRET=secret
        self.CONSUMER_CALLBACK=callback
        self.consumer = oauth.OAuthConsumer(self.CONSUMER_KEY, self.CONSUMER_SECRET)
        self.signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
    
    # note: these decorators add tiered caching to this function, such that 
    # results will be cached locally with a very small LRU cache of 64 items 
    # and also cached remotely via memcached with a TTL of 7 days
    #@lru_cache(maxsize=64)
    #@memcached_function(time=7*24*60*60)
    def _getResource(self, url, token=None, parameters={}):
        if not re.match('http',url):
            url = "http://%s%s" % (HOST, url)
        parameters['output'] = 'json'
        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
                                http_url=url,
                                parameters=parameters,
                                token=token)
        oauthRequest.sign_request(  self.signature_method_hmac_sha1,
                                self.consumer,
                                token)
        if (self.verbose):
                print oauthRequest.to_url()
        self.connection.request('GET', oauthRequest.to_url())
        response = self.connection.getresponse()
        return response.read()
    
    def _postResource(self, url, token=None, parameters=None):
        if not re.match('http',url):
            url = "http://%s%s" % (HOST, url)
        
        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(  self.consumer,
                                http_url=url,
                                parameters=parameters,
                                token=token,
                                http_method='POST')
        oauthRequest.sign_request(self.signature_method_hmac_sha1, self.consumer, token)
        
        if (self.verbose):
                print "POSTING TO" + oauthRequest.to_url()
        
        headers = {'Content-Type' :'application/x-www-form-urlencoded'}
        self.connection.request('POST', url, body=oauthRequest.to_postdata(), headers=headers)
        response = self.connection.getresponse()
        return response.read()
        
    def _deleteResource(self, url, token=None, parameters=None):
        if not re.match('http',url):
            url = "http://%s%s" % (HOST, url)
        
        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(  self.consumer,
                                http_url=url,
                                parameters=parameters,
                                token=token,
                                http_method='DELETE')
        oauthRequest.sign_request(self.signature_method_hmac_sha1, self.consumer, token)

        if (self.verbose):
                print "DELETING FROM" + oauthRequest.to_url()

        self.connection.request('DELETE', oauthRequest.to_url())
        response = self.connection.getresponse()
        return response.read()

"""
HOST              = 'api.netflix.com'
PORT              = '80'
REQUEST_TOKEN_URL = 'http://api.netflix.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'http://api.netflix.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api-user.netflix.com/oauth/login'
"""

class Netflix(object):
    def __init__(self, name=APP_NAME, key=API_KEY, secret=API_SECRET):
        self.__name=name
        self.__key=key
        self.__secret=secret
        self.__consumer = oauth.OAuthConsumer(self.__key, self.__secret)
        self.__signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.__cpsLimiter = RateLimiter(cps=4, max_wait=15)          # 4 requests per second for all requests
        self.__cpdLimiter = RateLimiter(cpd=5000)

        # the blacklist contains a dict of users and their 401/403 count. When a threshold is reached, all requests
        # from that user will be ignored until the blacklist is cleared
        self.__blacklist = dict()#dict({USER_ID: 4})
        self.__blacklistClearDate = datetime.now()
        self.__blacklistLifespan = timedelta(days=2)
        self.__blacklistThreshold = 5

    def __checkBlacklistExpiration(self):
        if (datetime.now() - self.__blacklistClearDate) > self.__blacklistLifespan:
            self.__blacklist.clear()
            self.__blacklistClearDate = datetime.now()

    def __addToBlacklistCount(self, user_id):
        """
        Increments the blacklist counter for a given user, and returns a bool on whether the threshold is hit
        """
        count = self.__blacklist.setdefault(user_id, 0) + 1
        self.__blacklist[user_id] = count
        if (count >= self.__blacklistThreshold):
            text = "Netflix user_id: %s hit the blacklist threshold of %d 403/401 errors." % (user_id, self.__blacklistThreshold)
            logs.info(text)
            msg = {}
            msg['to'] = 'dev@stamped.com'
            msg['from'] = 'Stamped <noreply@stamped.com>'
            msg['subject'] = 'Netflix blacklist threshold reached'
            msg['body'] = text
            utils.sendEmail(msg)
            return True
        return False

    def __isUserBlacklisted(self, user_id):
        return self.__blacklist.get(user_id, 0) >= self.__blacklistThreshold

    def __http(self, verb, service, user_id=None, token=None, **parameters):
        """
        Makes a request to the Netflix API
        """
        self.__checkBlacklistExpiration()

        #if a user is specified, and she is in the blacklist, return None
        if user_id is not None and self.__isUserBlacklisted(user_id):
            return None
        connection = httplib.HTTPConnection("%s:%s" % (HOST, PORT))
        if service.startswith('http'):
            url = service
        else:
            if user_id is None:
                url = "http://%s/%s" % (HOST, service)
            else:
                url = "http://%s/users/%s/%s" % (HOST, user_id, service)
        parameters['output'] = 'json'
        # parameters['v'] = '1.5' # v1.5 isn't returning expanded information, so nevermind it
        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(self.__consumer,
            http_url=url,
            parameters=parameters,
            token=token,
            http_method=verb)

        oauthRequest.sign_request(  self.__signature_method_hmac_sha1, self.__consumer, token)
        print oauthRequest.to_url()

        headers = {'Content-Type' :'application/x-www-form-urlencoded'} if verb =='POST' else {}
        body = oauthRequest.to_postdata() if verb == 'POST' else None
        url = url if verb == 'POST' else oauthRequest.to_url()
        logs.info(url)

        with self.__cpsLimiter:
            # if we're not making a user-signed request, then we need to enforce the 5000 request per day limit
            if user_id is None:
                with self.__cpdLimiter:
                    connection.request(verb, url, body, headers)
                    response = connection.getresponse()
            else:
                connection.request(verb, url, body, headers)
                response = connection.getresponse()
                # if the response is a 401 or 403, blacklist the user until the day expires
                if response.status in (401,403):
                    if self.__addToBlacklistCount(user_id):
                        logs.warning('Too many 401/403 responses.  User added to blacklist')

        if response.status == 200:
            return json.loads(response.read())
        else:
            failData = json.loads(response.read())['status']
            raise StampedHTTPError('Netflix returned a failure response.  status: %d  sub_code %d.  %s' %
                           (failData['status_code'], failData['sub_code'], failData['message']), failData['status_code'])

    def get(self, service, user_id=None, token=None, **parameters):
        return self.__get(service, user_id, token, **parameters)

    def __get(self, service, user_id=None, token=None, **parameters):
        return self.__http('GET', service, user_id, token, **parameters)

    def __post(self, service, user_id=None, token=None, **parameters):
        return self.__http('POST', service, user_id, token, **parameters)

    def __delete(self, service, user_id=None, token=None, **parameters):
        return self.__http('DELETE', service, user_id, token, **parameters)

    def __asList(self, elmt):
        if isinstance(elmt, list):
            return elmt
        elif elmt == None:
            return []
        return [elmt]

    def getFromLinks(self, links, key, search, returnKey):
        """
        Search a netflix 'link' list of dicts for a given substring in a given key.  If it is found, provide the value
         of the returnKey in that dict
        """
        for item in links:
            if item[key].find(search) != -1:
                return item[returnKey]
        return None

    def searchTitles(self, title, start=0, count=100):
        """
        Searches the netflix catalog for titles with a given search string.
        returns the json result as a dict
        """
        results = self.__get(
                        service         = 'catalog/titles',
                        term            = title,
                        start_index     = start,
                        max_results     = count,
                        expand          ='synopsis,cast,directors,formats,delivery_formats'
                    )
        return results.get('catalog_titles', None)

    def getTitleDetails(self, netflix_id):
        results = self.__get(
            service         = netflix_id,
            expand          ='synopsis,cast,directors'
        )
        import pprint
        pprint.pprint (results)
        return results.get('catalog_titles', None)

    def getInstantQueue(self, user_id, user_token, user_secret, start=0, count=100):
        """
        Returns a list of netflix ids for the user identified by auth
        """
        token = oauth.OAuthToken(user_token, user_secret)
        results = self.__get(
                            'users/' + user_id + '/queues/instant',
                            token                   = token,
                            start_index             = start,
                            max_results             = count,
                        )
        queue = []
        for item in self.__asList(results.get('queue', None).get('queue_item', None)):
            netflix_id = self.getFromLinks(self.__asList(item['link']), 'rel', 'catalog/title', 'href')
            queue.append(netflix_id)

        return results.get('queue', None)

    def getRentalHistory(self, user_id, user_token, user_secret, start=0, count=100):
        """
        Returns a list of (date, {netflix_id:<ID>}) tuples for the user identified by auth
        """
        token = oauth.OAuthToken(user_token, user_secret)
        results = self.__get(
            'rental_history',
            user_id                 = user_id,
            token                   = token,
            start_index             = start,
            max_results             = count,
        )
        if results is None:
            return None
        recent = []
        for item in self.__asList(results['rental_history']['rental_history_item']):
            date = datetime.fromtimestamp(item['watched_date'])
            netflix_id = self.getFromLinks(self.__asList(item['link']), 'rel', 'catalog/title', 'href')
            if netflix_id is not None:
                recent.append( (date, {'netflix_id': netflix_id}) )
        return recent

    def getRecommendations(self, user_id, user_token, user_secret, start=0, count=100):
        token = oauth.OAuthToken(user_token, user_secret)
        results = self.get(
            'users/' + user_id + '/recommendations',
            token                   = token,
            start_index             = start,
            max_results             = count,
        )
        return results

    def getViewingHistory(self, user_id, user_token, user_secret, start=0, count=100):
        pass

    def getETag(self, user_id, user_token, user_secret):
        token = oauth.OAuthToken(user_token, user_secret)
        getresponse = self.__get(
            'queues/instant',
            title_ref               = netflix_id,
            #position                = 1,
            user_id                 = user_id,
            token                   = token,
        )
        return getresponse["queue"]["etag"]

    def addToQueue(self, user_id, user_token, user_secret, netflix_id):
        """
        Returns a boolean (synchronously) if the operation succeeded
        """
        etag = getETag(user_id, user_token, user_secret)
        token = oauth.OAuthToken(user_token, user_secret)
        return self.__post(
            'queues/instant',
            title_ref               = netflix_id,
            position                = 1,
            etag                    = etag,
            user_id                 = user_id,
            token                   = token,
        )

    def titlesByUserRating(self, rating, auth, start, count):
        """
        Returns a list of {netflix_id:<ID>}s
        """
        pass

    def suggestedTitlesForUser(self, auth):
        """
        Returns a list of {netflix_id:<ID>}s
        """
        pass

    def getLoginUrl(self, authUserId):
        #request the oauth token and secret
        token_info = self.__get('oauth/request_token')
        token = oauth.OAuthToken(
            token_info['oauth_token'].encode('ascii'),
            token_info['oauth_token_secret'].encode('ascii'),
        )
        token.set_callback('https://dev.stamped.com/v0/account/linked/netflix/login_callback.json?secret=%s&stamped_oauth_token='
                % (token_info['oauth_token_secret'].encode('ascii'), authUserId))

        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(self.__consumer,
            http_url = 'https://api-user.netflix.com/oauth/login',
            parameters = { 'application_name': 'Stamped' },
            token = token,
            http_method = 'GET')

        url = oauthRequest.to_url()
        return (token_info['oauth_token_secret'], url)

    def requestUserAuth(self, oauth_token, secret):
        token = oauth.OAuthToken(
            oauth_token,
            secret,
        )

        result = self.__get(
           'oauth/access_token',
            token                   = token,
            parameters              = { 'application_name': 'Stamped' },
        )
        return result

#    http://api.netflix.com/oauth/access_token?
#    oauth_consumer_key=YourConsumerKey&\
#    oauth_signature_method=HMAC-SHA1&\
#    oauth_timestamp=timestamp&\
#    oauth_token=YourAuthorizedToken&\
#    oauth_nonce=nonce&\
#    oauth_version=1.0&\
#    oauth_signature=YourSignature
        #oauthRequest.sign_request(  self.__signature_method_hmac_sha1, self.__consumer, token)

#        results = self.__get(
#            'https://api-user.netflix.com/oauth/login',
#            application_name        = 'Stamped',
#            token                   = token,
#        )

#        https://api-user.netflix.com/oauth/login?
#        application_name=Your+Application+Name&
#        oauth_callback=http%3A%2F%2Fyourserver.com%2Fyourpage&\
#        oauth_consumer_key=YourConsumerKey&\
#        oauth_token=YourToken

__globalNetflix = None

def globalNetflix():
    global __globalNetflix
    
    if __globalNetflix is None:
        __globalNetflix = Netflix()
    
    return __globalNetflix

USER_ID = 'BQAJAAEDEOSopz8_plL6unZkMNWPF0swuckE11EpXgKKIiGokw4c7bE5zMk2-HgDEBW6XUAs9ULWh3MSZJfAPT0tby6iNSqb'
OAUTH_TOKEN = 'BQAJAAEDEEA_ABseWJmlwCbPcFoxztwwARmaMLeLXt1TYXxQ_F-zSETr2voXtq6DNeSIqjLtt2fax66UyvP5IPs-gxET3CUX'
OAUTH_TOKEN_SECRET = 'K28wcUY4YjAM'

HOPE_FLOATS_ID = 'http://api.netflix.com/catalog/titles/movies/11819509'
GHOSTBUSTERS2_ID = 'http://api.netflix.com/catalog/titles/movies/541027'
BIGLEB_ID = 'http://api.netflix.com/catalog/titles/movies/1181532'
INCEPTION_ID = 'http://api.netflix.com/catalog/titles/movies/70131314'

def demo(method, **params):
    import pprint
    netflix = Netflix()

    #request the oauth token and secret
#    token_info = netflix.get('oauth/request_token')
#    token = oauth.OAuthToken(
#        token_info['oauth_token'].encode('ascii'),
#        token_info['oauth_token_secret'].encode('ascii'),
#    )

    #result = netflix.getRentalHistory(USER_ID, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
    #result = netflix.addToQueue(USER_ID, OAUTH_TOKEN, OAUTH_TOKEN_SECRET, INCEPTION_ID)

    #url = netflix.getLoginUrl()
    response = netflix.requestUserAuth('wym773u9f5sn3j5hrp4pzctd', 'AJ8ZuZZYCRn5')
    #result = netflix.getInstantQueue(USER_ID, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

    #result = netflix.searchTitles("inception")

#    result = netflix.getTitleDetails(BIGLEB_ID)
#    result = netflix.get('http://api.netflix.com/catalog/titles/movies/1181532/format_availability')

#    result = netflix.__get('http://api.netflix.com/catalog/titles/movies/1181532/format_availability')

#    result = netflix.get('https://api-user.netflix.com/oauth/login', token=token, application_name='Stamped')
    #pprint.pprint(result)
    pprint.pprint(result)

if __name__ == '__main__':
    import sys
    method = 'search'
    params = {'term':'Katy Perry'}
    if len(sys.argv) > 1:
        method = sys.argv[1]
    if len(sys.argv) > 2:
        params = {}
        for arg in sys.argv[2:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    demo(method, **params)


