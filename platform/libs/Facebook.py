
import time
import urllib, urllib2, json, urlparse
import logs
import re
from errors import *

APP_ID          = '297022226980395'
APP_SECRET      = '17eb87d731f38bf68c7b40c45c35e52e'
APP_NAMESPACE   = 'stampedapp'

class Facebook(object):
    def __init__(self, app_id=APP_ID, app_secret=APP_SECRET, app_namespace=APP_NAMESPACE):
        self.app_id         = app_id
        self.app_secret     = app_secret
        self.app_namespace  = app_namespace
        pass

    def _get(self, accessToken, path, params=None, parse_json=True):
        if params is None:
            params = {}

        num_retries = 0
        max_retries = 5
        if accessToken is not None:
            params['access_token'] = accessToken

        while True:
            try:
                baseurl = ''
                if path[:8] != 'https://':
                    baseurl = 'https://graph.facebook.com/'
                url     = "%s%s" % (baseurl, path)
                if params != {}:
                    encoded_params  = urllib.urlencode(params)
                    url += "?%s" % encoded_params
                logs.info('url: %s' % url)
                if parse_json:
                    result  = json.load(urllib2.urlopen(url))
                else:
                    result = urllib2.urlopen(url).read()
                return result
            except urllib2.HTTPError as e:
                msg = e.message
                result = json.load(e)
                if 'error' in result:
                    if 'type' in result['error'] and result['error']['type'] == 'OAuthException':
                        # OAuth exception
                        msg = result['error']['message']

                logs.info('Facebook API Error: %s' % msg)
                num_retries += 1
                if num_retries > max_retries:
                    if e.code == 400:
                        raise StampedInputError('Facebook API 400 Error')
                    raise StampedUnavailableError('Facebook API Error')

                logs.info("Retrying (%s)" % (num_retries))
                time.sleep(0.5)
            except Exception as e:
                raise Exception('Error connecting to Facebook: %s' % e)

    def authorize(self, code, state):
        path = 'oauth/access_token'
        self._get(None,
            params= {
                'client_id'       : self.app_id,
                'client_secret'   : self.app_secret,
                'code'            : code
        })

    def getUserInfo(self, access_token):
        path = 'me'
        return self._get(
            access_token,
            path,
        )

    def getFriendIds(self, access_token):
        path = 'me/friends?access_token=%s' % access_token
        friends = []
        while True:
            print path
            result = self._get(None, path)
            friends.extend([ d['id'] for d in result['data']] )
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
            { 'client_id'       : client_id,
              'client_secret'   : client_secret,
              'grant_type'      : 'client_credentials'
            },
            parse_json=False,
        )
        r = re.search('access_token=([^&]*)', result)
        return r.group(1)

    def createTestUser(self, name, access_token, permissions=None, installed=True, method='post', locale='en_US', app_id=APP_ID):
        path = '%s/accounts/test-users' % app_id
        return self._get(
            access_token,
            path,
            { 'installed'           : installed,
              'name'                : name,
              'locale'              : locale,
              'permissions'         : permissions,
              'method'              : method,
            }
        )

    def deleteTestUser(self, access_token, test_user_id):
        # will return bool result with True == success
        path = test_user_id

        return self._get(
            access_token,
            path,
            { 'method'          : 'delete',
            },
            parse_json=False,
        )

__globalFacebook = None

def globalFacebook():
    global __globalFacebook

    if __globalFacebook is None:
        __globalFacebook = Facebook()

    return __globalFacebook


USER_ID = '100003940534060'
ACCESS_TOKEN = 'AAACEdEose0cBAFWCTyFkxAdiLCPBHMTmFZArw1sKUY3ji564jZB3aN46JQxtpiF80mUnwvrU4ZCZBOTPjcB2tgfRijBZBpgBc0t1OBi8tTqGOG58qzWba'
#ACCESS_TOKEN = 'AAACEdEose0cBAKDAU1Wuupi7IZA3c4nAQWQkf315HnxHB6aWUj6tG9Lt6iU2hW0arXFO9b2xkkN275ezc6jyci1ZCqhCK9WdH5a3YJpHqWxQTDmlAD'

def demo(method, user_id=USER_ID, access_token=ACCESS_TOKEN, **params):
    from pprint import pprint
    facebook = Facebook()

    if 'getUserInfo' in methods:            pprint(facebook.getUserInfo(access_token))
    if 'getAppAccessToken' in methods:      pprint(facebook.getAppAccessToken())
    if 'getFriendIds' in methods:             pprint(facebook.getFriendIds(access_token))

if __name__ == '__main__':
    import sys
    params = {}
    methods = 'getFriendIds'
    params['access_token'] = ACCESS_TOKEN
    if len(sys.argv) > 1:
        methods = [x.strip() for x in sys.argv[1].split(',')]
    if len(sys.argv) > 2:
        params = {}
        for arg in sys.argv[2:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    demo(methods, **params)

