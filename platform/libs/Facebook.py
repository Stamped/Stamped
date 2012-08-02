#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import time
import urllib, json, urlparse
import logs, utils
import re
from errors import *
from libs.Request import service_request
from APIKeys import get_api_key
from datetime import datetime
import httplib2
from BeautifulSoup import BeautifulSoup



APP_ID          = get_api_key('facebook', 'app_id')
APP_SECRET      = get_api_key('facebook', 'app_secret')
APP_NAMESPACE   = get_api_key('facebook', 'app_namespace')

USER_ID = '100003940534060'
ACCESS_TOKEN = 'AAAEOIZBBUXisBAO4BgIokl8sBOlrBCpgyeo8NAp4NZCvQxuAEUYJzc2U7vIZC7hBcUhJmLES0u32kJFzNXffl3fK3AOHMpdlKe3ZBnlrMlpqI3GrIRcc'
#ACCESS_TOKEN = 'AAAEOIZBBUXisBABDTY6Tu1lbjCn5NKSlc3LmjrINERhegr83XvoTvXNPN4hpPTPoZChXyxyBRU55MKZCHVeQk42qJbusvp9jknH830l3QZDZD'
#ACCESS_TOKEN = 'AAAEOIZBBUXisBABDTY6Tu1lbjCn5NKSlc3LmjrINERhegr83XvoTvXNPN4hpPTPoZChXyxyBRU55MKZCHVeQk42qJbusvp9jknH830l3QZDZD'
#ACCESS_TOKEN = 'AAAEOIZBBUXisBACXZB77U7QEInB7dQ1VPN7cv5kNpFnvaLK1eBeZBxfBHZBPL6aZBTTa32xp2zHrdnjYBQH02VfP7qZCpDSWtqjvUgBv1UKPKbdyIWZAZCcv'

AUTH_USER_ID = '4ecab825112dea0cfe000293' # Mike's stamped user id

USER_ID = '1337040065'
#ACCESS_TOKEN = 'BAAEOIZBBUXisBAHnrWWvBGFOLHQYaubpSMZAUZAakJeVgiMiHu4LylwOpeMBG7XznbnEdRHNZA5AmMhVcnUedsHNqniyQw1FMZCjmZBWPumPZCc4fFjoV1iy0eZBrTZCHUqtmyM0pIZC791Q61m7d94SRi'
ACCESS_TOKEN = 'AAAEOIZBBUXisBAFC4pEYEpUYJlzM7FPq9m77m7k2k5wIrcZCmXSZC0TT1ri6VcMWV5acLBZAs6lHzdkFJrWHZASY4XbKTqUQZD'

DEFAULT_TIMEOUT = 15

class Facebook(object):
    def __init__(self, app_id=APP_ID, app_secret=APP_SECRET, app_namespace=APP_NAMESPACE):
        self.app_id         = app_id
        self.app_secret     = app_secret
        self.app_namespace  = app_namespace
        pass

    def _http(self, method, accessToken, path, priority='high', parse_json=True, **params):
        if params is None:
            params = {}

        num_retries = 0
        max_retries = 5
        if accessToken is not None:
            params['access_token'] = accessToken
        if method != 'get':
            params['method'] = method

        data = None

        baseurl = ''
        if path[:8] != 'https://':
            baseurl = 'https://graph.facebook.com/'
        url     = "%s%s" % (baseurl, path)

        if method == 'get':
            response, content = service_request('facebook', method, url, query_params=params, priority=priority, timeout=DEFAULT_TIMEOUT)
        else:
            print('body: %s  url: %s' % (params, url))
            response, content = service_request('facebook', method, url, body=params, priority=priority, timeout=DEFAULT_TIMEOUT)
        if parse_json:
            result = json.loads(content)
        else:
            result = content

        if int(response.status) >= 400:
            result = json.loads(content)
            logs.info('result: %s' % result)

            msg = None
            code = None
            if 'error' in result:
                msg = result['error']['message']
                if 'code' in result['error']:
                    code = result['error']['code']
                    if code == 190:
                        raise StampedFacebookTokenError('Invalid Facebook token')
                    elif code == 200:
                        raise StampedFacebookPermissionsError(msg)
                    elif code == 3501:
                        raise StampedFacebookUniqueActionAlreadyTakenOnObject('OG Action already exists for object')
                    elif code == 1611118:
                        raise StampedFacebookOGImageSizeError(msg)
                if 'type' in result['error'] and result['error']['type'] == 'OAuthException':
                    # OAuth exception
                    pass

            logs.info('Facebook API Error: status: %s  code: %s  message: %s' % (response.status, code, msg))

            raise StampedThirdPartyError('Facebook API Error: %s' % msg)

            #logs.info("Retrying (%s)" % (num_retries))
            #time.sleep(0.5)
        return result

    def _get(self, accessToken, path, priority='high', **params):
        return self._http('get', accessToken, path, priority, **params)

    def _post(self, accessToken, path, priority='high', **params):
        return self._http('post', accessToken, path, priority, **params)

    def _delete(self, accessToken, path, priority='high', **params):
        return self._http('delete', accessToken, path, priority, **params)

    def authorize(self, code, state):
        path = 'oauth/access_token'
        self._get(
            None,
            client_id       = self.app_id,
            client_secret   = self.app_secret,
            code            = code,
        )

    def getUserInfo(self, access_token, user_id='me'):
        path = user_id
        fields = 'id,email,bio,name,username,third_party_id'
        return self._get(
            access_token,
            path,
            fields=fields
        )

    def getUserPermissions(self, access_token, user_id='me'):
        path = '%s/permissions' % user_id
        result = self._get(access_token, path)
        if 'data' in result and len(result['data'] > 0):
            return result['data'][0]
        else:
            return []

    def getFriendIds(self, access_token):
        path = 'me/friends'

        friends = []
        while True:
            print path
            result = self._get(access_token, path)
            access_token = None
            friends.extend([ d['id'] for d in result['data']] )
            if 'paging' in result and 'next' in result['paging']:
                path = result['paging']['next']
                url = urlparse.urlparse(result['paging']['next'])
                params = dict([part.split('=') for part in url[4].split('&')])
                if 'offset' in params and int(params['offset']) == len(friends):
                    continue
            break
        return friends

    def getFriendData(self, access_token, offset=0, limit=30):
        path = 'me/friends'
        logs.info('#### offset: %s  limit: %s' % (offset, limit))

        #May want to order by name using FQL:
        #http://developers.facebook.com/tools/explorer?fql=SELECT%20uid%2C%20name%20FROM%20user%20WHERE%20uid%20IN%20(SELECT%20uid2%20FROM%20friend%20WHERE%20uid1%20%3D%20me())%20ORDER%20BY%20last_name

        friends = []
        while True:
            print path
            result = self._get(access_token, path, limit=limit, offset=offset, fields='id,name,picture')
            access_token = None
            logs.info('### result: %s' % result)
            for d in result['data']:
                friends.append(
                    {
                        'user_id' : d['id'],
                        'name' : d['name'],
                        'image_url' : d['picture'],
                    }
                )
#            friends.extend([ d for d in result['data']] )
            if 'paging' in result and 'next' in result['paging']:
                path = result['paging']['next']
                url = urlparse.urlparse(result['paging']['next'])
                params = dict([part.split('=') for part in url[4].split('&')])
                if 'offset' in params and int(params['offset']) == len(friends):
                    continue
            break
        return friends

    # see: http://developers.facebook.com/docs/opengraph/using-app-tokens/
    def getAppAccessToken(self, client_id=APP_ID, client_secret=APP_SECRET):
        path = 'oauth/access_token'
        result = self._get(
            None,
            path,
            parse_json      = False,
            client_id       = client_id,
            client_secret   = client_secret,
            grant_type      = 'client_credentials',
        )
        r = re.search('access_token=([^&]*)', result)
        return r.group(1)

    def getUserAccessToken(self, code, client_id=APP_ID, client_secret=APP_SECRET):
        logs.info('### getUserAccessToken called # client_id: %s, client_secret: %s, code: %s' % (client_id, client_secret, code))
        redirect_uri = utils.getDomain() + 'account/linked/facebook/login_callback.json'
        path = "oauth/access_token"
        result = self._get(
            None,
            path,
            parse_json      = False,
            client_id       = client_id,
            client_secret   = client_secret,
            code            = code,
            redirect_uri    = redirect_uri,
        )
        r = re.search('access_token=([^&]*)', result)
        token = r.group(1)
        r = re.search(r'expires=([^&]*)', result)
        expires = None
        if r is not None:
            expires = r.group(1)
            #expires = datetime.fromtimestamp(time.time() + int(expires))
        return token, expires

    def extendAccessToken(self, access_token, client_id=APP_ID, client_secret=APP_SECRET):
        path = "oauth/access_token"
        result = self._get(
            None,
            path,
            parse_json      = False,
            client_id       = client_id,
            client_secret   = client_secret,
            grant_type      = 'fb_exchange_token',
            fb_exchange_token = access_token,
        )
        r = re.search(r'access_token=([^&]*)', result)
        token = r.group(1)
        r = re.search(r'expires=([^&]*)', result)
        expires = None
        if r is not None:
            expires = r.group(1)
            expires = datetime.fromtimestamp(time.time() + int(expires))
        return token, expires


    def createTestUser(self, name, access_token, permissions=None, installed=True, locale='en_US', app_id=APP_ID):
        path = '%s/accounts/test-users' % app_id
        return self._post(
            access_token,
            path,
            installed            = installed,
            name                 = name,
            locale               = locale,
            permission           = permissions,
        )

    def createTestUserFriendship(self, user_a_id, user_a_token, user_b_id, user_b_token):
        # Create friend request from user a to user b
        path = '%s/friends/%s' % (user_a_id, user_b_id)
        self._post(user_a_token, path)

        # Confirm the request
        path = '%s/friends/%s' % (user_b_id, user_a_id)
        self._post(user_b_token, path)

    def deleteTestUser(self, access_token, test_user_id):
        # will return bool result with True == success
        path = test_user_id
        return self._delete(access_token, path)

    def getTestUsers(self, app_id=APP_ID, app_secret=APP_SECRET, app_access_token=None):
        if app_access_token is None:
            app_access_token = self.getAppAccessToken(app_id, app_secret)
        path = "%s/accounts/test-users" % app_id
        return self._get(app_access_token, path)

    def clearTestUsers(self, app_id=APP_ID, app_secret=APP_SECRET, app_access_token=None):
        if app_access_token is None:
            app_access_token = self.getAppAccessToken(app_id, app_secret)
        path = "%s/accounts/test-users" % app_id
        while True:
            result = self._get(app_access_token, path, limit=50)
            users = result['data']
            for user in users:
                assert(self.deleteTestUser(app_access_token, user['id']))
            if 'paging' in result and 'next' in result['paging']:
                path = result['paging']['next']
                url = urlparse.urlparse(result['paging']['next'])
                params = dict([part.split('=') for part in url[4].split('&')])
                if len(users) == 50:
                    continue
#                if 'offset' in params and int(params['offset']) == len(users):
#                    continue
            break

    def getOpenGraphActivity(self, access_token):
        path = "me/stampedapp:stamp"
        return self._get(
            access_token,
            path,
        )

    def postToOpenGraph(self, fb_user_id, action, access_token, object_type, object_url, message=None, imageUrl=None):
        logs.info('### access_token: %s  object_type: %s  object_url: %s' % (access_token, object_type, object_url))

        http = httplib2.Http()
        response, content = http.request(object_url, 'GET')
        soup = BeautifulSoup(content)
        logs.info('### meta tags:\n%s' % soup.findAll('meta', property=True))

        args = {}
        if action == 'like':
            path = "%s/og.likes" % fb_user_id
            args['object'] = object_url
        elif action == 'follow':
            path = "me/og.follows"
            args['profile'] = object_url
        else:
            args[object_type] = object_url
            path = "me/stampedapp:%s" % action
        if message is not None:
            args['message'] = message
        if imageUrl is not None:
            args['image[0][url]'] = imageUrl
            args['image[0][user_generated]'] = "true"
        return self._post(
            access_token,
            path,
            priority='low',
            **args
        )

    def deleteFromOpenGraph(self, action_instance_id, access_token):
        path = str(action_instance_id)
        return self._delete(
            access_token,
            path,
            priority='low',
        )

    def getNewsFeed(self, user_id, access_token):
        path = '%s/feed' % user_id
        self._get(
            access_token,
            path,
        )

    def postToNewsFeed(self, user_id, access_token, message, picture=None):
        path = '%s/feed' % user_id
        params = {}
        if picture is not None:
            params['picture'] = picture
        if message is not None:
            params['message'] = message
        self._post(
            access_token,
            path,
            priority='low',
            **params
        )

    def getLoginUrl(self, authUserId, callbackToken):
#        callback_url = utils.getDomain() + ('account/linked/facebook/login_callback.json?secret=%s&stamped_oauth_token=%s' %
#                                            (token_info['oauth_token_secret'].encode('ascii'), stamped_oauth_token))
        callback_url = utils.getDomain() + 'account/linked/facebook/login_callback.json'
        permissions = 'user_about_me,user_location,email,publish_stream,publish_actions'
        #unique = datetime.now().strftime("%H:%M:%S.%f")
        path = "https://www.facebook.com/dialog/oauth?" \
               "client_id=%s" \
               "&redirect_uri=%s" \
               "&scope=%s" \
               "&state=%s" % \
               (APP_ID, callback_url, permissions, callbackToken)

        return path
#        print path
#        response, content = service_request('facebook', 'GET', path)
#        print(response)
#        print(content)
#        return content


__globalFacebook = None

def globalFacebook():
    global __globalFacebook

    if __globalFacebook is None:
        __globalFacebook = Facebook()

    return __globalFacebook


CODE = 'AQCKon1gU-jv8gYtZnXHYjjK-tG63ZbW9EFo-Vk5AAGgPfYua4Rr_g_Z2BTqUOMeqpt1wja1pCJL-dg5Fogo6VIWcJeHiBoNVqUSsHMok-fjXXogJ2qyANmw8xqWw51qz5XJdPHqCAgRCXYgRA5HC8vnQHw8AojNyudbKKdGOxCuudgXDbpAv2E0Nl9jlzpc2RnH1M_Ixcdy622-QNUYX2Sw'

def demo(method, user_id=USER_ID, access_token=ACCESS_TOKEN, **params):
    from pprint import pprint
    facebook = Facebook()

    if 'getUserInfo' in methods:            pprint(facebook.getUserInfo(access_token))
    if 'getLoginUrl' in methods:            pprint(facebook.getLoginUrl(AUTH_USER_ID))
    if 'extendAccessToken' in methods:      pprint(facebook.extendAccessToken(access_token))
    if 'getUserAccessToken' in methods:     pprint(facebook.getUserAccessToken(CODE))
    if 'getUserPermissions' in methods:     pprint(facebook.getUserPermissions(access_token))
    if 'getAppAccessToken' in methods:      pprint(facebook.getAppAccessToken())
    if 'getFriendIds' in methods:           pprint(facebook.getFriendIds(access_token))
    if 'getFriendData' in methods:          pprint(facebook.getFriendData(access_token))
    if 'postToNewsFeed' in methods:         pprint(facebook.postToNewsFeed(user_id, access_token,
                                                   message="Test news feed item.",
                                                   picture="http://static.stamped.com/users/ml.jpg"))
    if 'postToOpenGraph' in methods:        pprint(facebook.postToOpenGraph('12345', 'todo', access_token,
                                                   'app', 'http://stamped.com/JSinatra/s/37',
                                                   message="Test message", imageUrl='http://static.stamped.com/users/ml.jpg'))
    if 'getOpenGraphActivity' in methods:   pprint(facebook.getOpenGraphActivity(access_token))
    if 'getTestUsers' in methods:           pprint(facebook.getTestUsers())
    if 'clearTestUsers' in methods:         pprint(facebook.clearTestUsers())

if __name__ == '__main__':
    import sys
    params = {}
    methods = 'getUserInfo'
    params['access_token'] = ACCESS_TOKEN
    if len(sys.argv) > 1:
        methods = [x.strip() for x in sys.argv[1].split(',')]
    if len(sys.argv) > 2:
        params = {}
        for arg in sys.argv[2:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    demo(methods, **params)

