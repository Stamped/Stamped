
import time
import urllib, json, urlparse
import logs, utils
import re
from errors import *
from libs.Request import *


APP_ID          = '297022226980395'
APP_SECRET      = '17eb87d731f38bf68c7b40c45c35e52e'
APP_NAMESPACE   = 'stampedapp'

USER_ID = '100003940534060'
ACCESS_TOKEN = 'AAAEOIZBBUXisBADc0xvUq2cVvQs3vDvGQ57g0oTjahwKaEjCZAFI3Uot8suKSvqLI9LyvDVL5Qg9CmuqJOHSMTT1cgDXk5uj7ODE8CsAZDZD'
#ACCESS_TOKEN = 'AAAEOIZBBUXisBABDTY6Tu1lbjCn5NKSlc3LmjrINERhegr83XvoTvXNPN4hpPTPoZChXyxyBRU55MKZCHVeQk42qJbusvp9jknH830l3QZDZD'
#ACCESS_TOKEN = 'AAAEOIZBBUXisBABDTY6Tu1lbjCn5NKSlc3LmjrINERhegr83XvoTvXNPN4hpPTPoZChXyxyBRU55MKZCHVeQk42qJbusvp9jknH830l3QZDZD'
#ACCESS_TOKEN = 'AAAEOIZBBUXisBACXZB77U7QEInB7dQ1VPN7cv5kNpFnvaLK1eBeZBxfBHZBPL6aZBTTa32xp2zHrdnjYBQH02VfP7qZCpDSWtqjvUgBv1UKPKbdyIWZAZCcv'

ACCESS_TOKEN = 'AAAEOIZBBUXisBABDTY6Tu1lbjCn5NKSlc3LmjrINERhegr83XvoTvXNPN4hpPTPoZChXyxyBRU55MKZCHVeQk42qJbusvp9jknH830l3QZDZD'

class Facebook(object):
    def __init__(self, app_id=APP_ID, app_secret=APP_SECRET, app_namespace=APP_NAMESPACE):
        self.app_id         = app_id
        self.app_secret     = app_secret
        self.app_namespace  = app_namespace
        pass

    def _http(self, method, accessToken, path, parse_json=True, **params):
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
            response, content = service_request('facebook', method, url, query_params=params)
        else:
            response, content = service_request('facebook', method, url, body=params)
        if parse_json:
            result = json.loads(content)
        else:
            result = content

        if int(response.status) >= 400:
            result = json.loads(content)
            logs.info('result: %s' % result)

            msg = None
            if 'error' in result:
                if 'code' in result['error']:
                    code = result['error']['code']
                    if code == 190:
                        raise StampedFacebookTokenError('Invalid Facebook token')
                if 'type' in result['error'] and result['error']['type'] == 'OAuthException':
                    # OAuth exception
                    pass
                msg = result['error']['message']

            logs.info('Facebook API Error: code: %s  message: %s' % (response.status, msg))

            raise StampedThirdPartyError('Facebook API Error')

            #logs.info("Retrying (%s)" % (num_retries))
            #time.sleep(0.5)
        return result

    def _get(self, accessToken, path, **params):
        return self._http('get', accessToken, path, **params)

    def _post(self, accessToken, path, **params):
        return self._http('post', accessToken, path, **params)

    def _delete(self, accessToken, path, **params):
        return self._http('delete', accessToken, path, **params)

    def authorize(self, code, state):
        path = 'oauth/access_token'
        self._get(
            None,
            client_id       = self.app_id,
            client_secret   = self.app_secret,
            code            = code,
        )

    def getUserInfo(self, access_token):
        path = 'me'
        return self._get(access_token, path)

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
        redirect_uri = 'https://dev.stamped.com/v0/account/linked/facebook/login_callback.json'
        path = "oauth/access_token"
        result = self._get(
            None,
            path,
            client_id       = client_id,
            client_secret   = client_secret,
            code            = code,
            redirect_uri    = redirect_uri,
        )

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

    def postToOpenGraph(self, action, access_token, object_type, object_url, message=None, imageUrl=None):
        logs.info('### access_token: %s  object_type: %s  object_url: %s' % (access_token, object_type, object_url))
        path = "me/stampedapp:%s" % action
        args = {}
        args[object_type] = object_url
        if message is not None:
            args['message'] = message
        if imageUrl is not None:
            args['image[0][url]'] = imageUrl
            args['image[0][user_generated]'] = "true"
        return self._post(
            access_token,
            path,
            **args
        )

    def deleteFromOpenGraph(self, action, access_token, object_type, object_url, message=None, imageUrl=None):
        logs.info('### access_token: %s  object_type: %s  object_url: %s' % (access_token, object_type, object_url))
        path = "me/stampedapp:%s" % action
        args = {}
        args[object_type] = object_url
        if message is not None:
            args['message'] = message
        if imageUrl is not None:
            args['image'] = imageUrl
        return self._post(
            access_token,
            path,
            **args
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
            **params
        )

__globalFacebook = None

def globalFacebook():
    global __globalFacebook

    if __globalFacebook is None:
        __globalFacebook = Facebook()

    return __globalFacebook



def demo(method, user_id=USER_ID, access_token=ACCESS_TOKEN, **params):
    from pprint import pprint
    facebook = Facebook()

    if 'getUserInfo' in methods:            pprint(facebook.getUserInfo(access_token))
    if 'getAppAccessToken' in methods:      pprint(facebook.getAppAccessToken())
    if 'getFriendIds' in methods:           pprint(facebook.getFriendIds(access_token))
    if 'getFriendData' in methods:          pprint(facebook.getFriendData(access_token))
    if 'postToNewsFeed' in methods:         pprint(facebook.postToNewsFeed(user_id, access_token,
                                                   message="Test news feed item.",
                                                   picture="http://static.stamped.com/users/ml.jpg"))
    if 'postToOpenGraph' in methods:        pprint(facebook.postToOpenGraph('stamp', access_token,
                                                   'movie', 'http://ec2-23-22-98-51.compute-1.amazonaws.com/ml/s/10',
                                                   message="Test message", imageUrl='http://static.stamped.com/users/ml.jpg'))
    if 'getOpenGraphActivity' in methods:   pprint(facebook.getOpenGraphActivity(access_token))
    if 'getTestUsers' in methods:           pprint(facebook.getTestUsers())
    if 'clearTestUsers' in methods:         pprint(facebook.clearTestUsers())

if __name__ == '__main__':
    import sys
    params = {}
    methods = 'getTestUsers'
    params['access_token'] = ACCESS_TOKEN
    if len(sys.argv) > 1:
        methods = [x.strip() for x in sys.argv[1].split(',')]
    if len(sys.argv) > 2:
        params = {}
        for arg in sys.argv[2:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    demo(methods, **params)

