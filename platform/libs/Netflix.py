__author__ = "Kirsten Jones <synedra@gmail.com>"
__version__ = "$Rev$"
__date_ = "$Date$"

import Globals
import sys
from libs import oauth as oauth
import json
import utils
import logs
from errors import *

from datetime               import datetime, timedelta
from libs.LRUCache          import lru_cache
from libs.CachedFunction    import cachedFn
from libs.CountedFunction   import countedFn
from libs.Request           import *
from APIKeys                import get_api_key

HOST              = 'api-public.netflix.com'
PORT              = '80'
REQUEST_TOKEN_URL = 'http://api-public.netflix.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'http://api-public.netflix.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api-public-user.netflix.com/oauth/login'

APP_NAME                = get_api_key('netflix', 'app_name')
API_KEY                 = get_api_key('netflix', 'api_key')
API_SECRET              = get_api_key('netflix', 'api_secret')

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

    def __http(self, verb, service, user_id=None, token=None, priority='low', **parameters):
        """
        Makes a request to the Netflix API
        """
        self.__checkBlacklistExpiration()

        #if a user is specified, and she is in the blacklist, return None
        if user_id is not None and self.__isUserBlacklisted(user_id):
            return None
        if service.startswith('http'):
            url = service
        else:
            if user_id is None:
                url = "http://%s/%s" % (HOST, service)
            else:
                url = "http://%s/users/%s/%s" % (HOST, user_id, service)
        parameters['output'] = 'json'

        oauthRequest = oauth.OAuthRequest.from_consumer_and_token(self.__consumer,
            http_url=url,
            parameters=parameters,
            token=token,
            http_method=verb)

        oauthRequest.sign_request(  self.__signature_method_hmac_sha1, self.__consumer, token)
        print oauthRequest.to_url()

        headers = {'Content-Type' :'application/x-www-form-urlencoded'} if verb =='POST' else {}
        params = oauthRequest.parameters
        logs.info(url)

        if verb == 'POST':
            response, content = service_request('netflix', verb, url, body=params, header=headers, priority=priority)
        else:
            response, content = service_request('netflix', verb, url, query_params=params, header=headers, priority=priority)

        # if the response is a 401 or 403, blacklist the user until the day expires
        if user_id is not None and response.status in (401, 403):
            if self.__addToBlacklistCount(user_id):
                logs.warning('Too many 401/403 responses.  User added to blacklist')

        if response.status < 300:
            return json.loads(content)
        else:
            logs.info('Failed with status code %s' % response['status'])
            try:
                failData = json.loads(content)['status']
                status = failData['status_code']
                subcode = failData.get('sub_code', None)
                message = failData['message']
            except:
                raise StampedThirdPartyError("Error parsing Netflix error response")

            # For the full list of possible status codes, see: http://developer.netflix.com/docs/HTTP_Status_Codes
            if status == 401:
                raise StampedThirdPartyInvalidCredentialsError(message)
            elif status == 412 and subcode == 710:
                return True
            else:
                raise StampedThirdPartyError(message)

    def __get(self, service, user_id=None, token=None, priority='low', **parameters):
        return self.__http('GET', service, user_id, token, priority, **parameters)

    def __post(self, service, user_id=None, token=None, priority='low', **parameters):
        return self.__http('POST', service, user_id, token, priority, **parameters)

    def __delete(self, service, user_id=None, token=None, priority='low', **parameters):
        return self.__http('DELETE', service, user_id, token, priority, **parameters)
    
    def __asList(self, elmt):
        if isinstance(elmt, list):
            return elmt
        elif elmt == None:
            return []
        return [elmt]

    def _getFromLinks(self, links, key, search, returnKey):
        """
        Search a netflix 'link' list of dicts for a given substring in a given key.  If it is found, provide the value
         of the returnKey in that dict
        """
        for item in links:
            if item[key].find(search) != -1:
                return item[returnKey]
        return None

    # note: these decorators add tiered caching to this function, such that
    # results will be cached locally with a very small LRU cache of 64 items
    # and also cached in Mongo or Memcached with the standard TTL of 7 days.
    @countedFn('Netflix (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn()
    @countedFn('Netflix (after caching)')
    def autocomplete(self, term, priority='high'):
        results = self.__get(
            service         = 'catalog/titles/autocomplete',
            term            = term,
            priority        = priority,
        )
        autocomplete = results.pop('autocomplete', None)
        if autocomplete is None or 'autocomplete_item' not in self.__asList(autocomplete)[0]:
            return []

        completions = []
        for title in self.__asList(self.__asList(autocomplete)[0]['autocomplete_item']):
            completions.append( { 'completion' : title['title']['short'] } )
        return completions


    # note: these decorators add tiered caching to this function, such that
    # results will be cached locally with a very small LRU cache of 64 items
    # and also cached in Mongo or Memcached with the standard TTL of 7 days.
    @countedFn('Netflix (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn()
    @countedFn('Netflix (after caching)')
    def searchTitles(self, title, start=0, count=100, priority='low'):
        """
        Searches the netflix catalog for titles with a given search string.
        returns the json result as a dict
        """
        results = self.__get(
                        service         = 'catalog/titles',
                        term            = title,
                        start_index     = start,
                        max_results     = count,
                        priority        = priority,
                        expand          ='synopsis,cast,directors,formats,delivery_formats'
                    )
        return results.get('catalog_titles', None)

    # note: these decorators add tiered caching to this function, such that
    # results will be cached locally with a very small LRU cache of 64 items
    # and also cached in Mongo or Memcached with the standard TTL of 7 days.
    @countedFn('Netflix (before caching)')
    @lru_cache(maxsize=64)
    @cachedFn()
    @countedFn('Netflix (after caching)')
    def getTitleDetails(self, netflix_id, priority='low'):
        results = self.__get(
            service         = netflix_id,
            expand          = 'synopsis,cast,directors,formats,delivery_formats',
            priority        = priority,
        )
        return results.get('catalog_title', None)

    def getInstantQueue(self, user_id, user_token, user_secret, start=0, count=100, priority='low'):
        """
        Returns a list of netflix ids for the user id
        """
        token = oauth.OAuthToken(user_token, user_secret)
        results = self.__get(
                            'users/' + user_id + '/queues/instant',
                            token                   = token,
                            start_index             = start,
                            max_results             = count,
                            priority                = priority,
                        )
        queue = []
        for item in self.__asList(results.get('queue', None).get('queue_item', None)):
            netflix_id = self._getFromLinks(self.__asList(item['link']), 'rel', 'catalog/title', 'href')
            queue.append(netflix_id)

        return results.get('queue', None)

    def getRentalHistory(self, user_id, user_token, user_secret, start=0, count=100, priority='low'):
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
            priority                = priority,
        )
        if results is None:
            return None
        recent = []
        for item in self.__asList(results['rental_history']['rental_history_item']):
            date = datetime.fromtimestamp(item['watched_date'])
            netflix_id = self._getFromLinks(self.__asList(item['link']), 'rel', 'catalog/title', 'href')
            if netflix_id is not None:
                recent.append( (date, {'netflix_id': netflix_id}) )
        return recent

    def getRecommendations(self, user_id, user_token, user_secret, start=0, count=100, priority='low'):
        """
        Returns a list of netflix_ids
        """
        token = oauth.OAuthToken(user_token, user_secret)
        results = self.__get(
            'users/' + user_id + '/recommendations',
            token                   = token,
            start_index             = start,
            max_results             = count,
            priority                = priority,
        )
        recs = self.__asList(results['recommendations']['recommendation'])
        return [self._getFromLinks(self.__asList(x['link']), 'rel', 'catalog/title', 'href') for x in recs]

    def _getETag(self, user_id, user_token, user_secret, netflix_id):
        token = oauth.OAuthToken(user_token, user_secret)
        getresponse = self.__get(
            'queues/instant',
            title_ref               = netflix_id,
            user_id                 = user_id,
            token                   = token,
        )
        return getresponse["queue"]["etag"]

    def addToQueue(self, user_id, user_token, user_secret, netflix_id):
        """
        Returns a boolean (synchronously) if the operation succeeded
        """
        etag = self._getETag(user_id, user_token, user_secret, netflix_id)
        token = oauth.OAuthToken(user_token, user_secret)
        return self.__post(
            'queues/instant',
            title_ref               = netflix_id,
            position                = 1,
            etag                    = etag,
            user_id                 = user_id,
            token                   = token,
            priority                = 'high',
        )

    def getUserInfo(self, user_token, user_secret, priority='high'):
        token = oauth.OAuthToken(user_token, user_secret)
        userInfo = self.__get(
            'users/current',
            token           = token,
            priority        = priority,
        )
        userUrl = userInfo['resource']['link']['href']
        userId = userUrl[userUrl.rfind('/')+1:]
        return self.getUserInfoWithId(userId, user_token, user_secret)

    def getUserInfoWithId(self, user_id, user_token, user_secret, priority='high'):
        token = oauth.OAuthToken(user_token, user_secret)
        return self.__get(
            'users/%s' % user_id,
            token       = token,
            priority    = priority,
        )['user']

    def getUserRatings(self, user_id, user_token, user_secret, netflix_ids=None, priority='low'):
        # Returns a list of tuples (netflix_id, rating), where rating is an int value
        # netflix_ids should be a comma delimited list of titles to get the user ratings of (if they exist)
        # if no ids are provided, then we'll use the user's rental history
        if netflix_ids is None:
            netflix_ids = [x[1]['netflix_id'] for x in self.getRentalHistory(user_id, user_token, user_secret)]
        token = oauth.OAuthToken(user_token, user_secret)
        results = self.__get(
            'ratings/title',
            user_id                 = user_id,
            token                   = token,
            title_refs              = netflix_ids,
            priority                = priority,
        )
        ratings = []
        for x in self.__asList(results['ratings']['ratings_item']):
            if 'user_rating' not in x:
                continue
            ratings.append( ( self._getFromLinks(self.__asList(x['link']), 'rel', 'catalog/title', 'href') , x['user_rating']) )
        return ratings

    def getLoginUrl(self, stamped_oauth_token, netflixAddId=None):
        #request the oauth token and secret
        token_info = self.__get('oauth/request_token')
        token = oauth.OAuthToken(
            token_info['oauth_token'].encode('ascii'),
            token_info['oauth_token_secret'].encode('ascii'),
        )
        callback_url = utils.getDomain() + ('account/linked/netflix/login_callback.json?secret=%s&stamped_oauth_token=%s' %
                                             (token_info['oauth_token_secret'].encode('ascii'), stamped_oauth_token))
        if netflixAddId is not None:
            callback_url += "&netflix_add_id=%s" % netflixAddId
        token.set_callback(callback_url)

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
            priority                = 'high',
            #parameters              = { 'application_name': 'Stamped' },
        )
        return result

__globalNetflix = None

def globalNetflix():
    global __globalNetflix
    
    if __globalNetflix is None:
        __globalNetflix = Netflix()
    
    return __globalNetflix

USER_ID = 'BQAJAAEDEBt1T1psKyjyA2IphhT34icw3Nwze3KAkc232VbNA7apgZuLYhrDaHkY2dTHbhLCE1aBH2mxmhKYIbgy9mJZmHdy'
OAUTH_TOKEN = 'BQAJAAEDEDXdt6wgpbupNB2Tb9h-_hcwAdmYwRvmtwsUNtV96kMObcRjcEM4xT3Iy5rJcKY1pW3gQsQ7tGNsC3U_Bu3yuZVq'
OAUTH_TOKEN_SECRET = 'gxpc6dxp242x'




GHOSTBUSTERS2_ID = 'http://api-public.netflix.com/catalog/titles/movies/541027'
BIGLEB_ID = 'http://api-public.netflix.com/catalog/titles/movies/1181532'
INCEPTION_ID = 'http://api-public.netflix.com/catalog/titles/movies/70131314'
ARRESTED_DEV_ID = "http://api.netflix.com/catalog/titles/series/70140358"

def demo(method, user_id=USER_ID, user_token=OAUTH_TOKEN, user_secret=OAUTH_TOKEN_SECRET, netflix_id=ARRESTED_DEV_ID, **params):
    from pprint import pprint
    netflix = Netflix()

    title = 'arrested development'
    if 'netflix_id' in params:  netflix_id  = params['netflix_id']
    if 'title' in params:       title       = params['title']

    if 'autocomplete' in methods:         pprint( netflix.autocomplete(title) )
    if 'searchTitles' in methods:         pprint( netflix.searchTitles(title) )
    if 'getTitleDetails' in methods:      pprint( netflix.getTitleDetails(netflix_id) )
    if 'getUserInfo' in methods:          pprint( netflix.getUserInfo(user_token, user_secret) )
    if 'getUserInfoWithId' in methods:    pprint( netflix.getUserInfoWithId(user_id, user_token, user_secret) )
    if 'getRentalHistory' in methods:     pprint( netflix.getRentalHistory(user_id, user_token, user_secret) )
    if 'getRecommendations' in methods:   pprint( netflix.getRecommendations(user_id, user_token, user_secret) )
    if 'getUserRatings' in methods:       pprint( netflix.getUserRatings(user_id, user_token, user_secret, netflix_id) )
    if 'addToQueue' in methods:           pprint( netflix.addToQueue(user_id, user_token, user_secret, netflix_id) )

if __name__ == '__main__':
    import sys
    params = {}
    methods = 'autocomplete'
    params['title'] = 'arrested development'
    if len(sys.argv) > 1:
        methods = [x.strip() for x in sys.argv[1].split(',')]
    if len(sys.argv) > 2:
        params = {}
        for arg in sys.argv[2:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    demo(methods, **params)


