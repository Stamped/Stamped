
import time
import urllib, urllib2, json
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
                baseurl = 'https://graph.facebook.com/'
                encoded_params  = urllib.urlencode(params)
                url     = "%s%s?%s" % (baseurl, path, encoded_params)
                if parse_json:
                    result  = json.load(urllib2.urlopen(url))
                else:
                    result = urllib2.urlopen(url).read()

                if 'error' in result:
                    if 'type' in result['error'] and result['error']['type'] == 'OAuthException':
                        # OAuth exception
                        raise
                    raise

                return result

            except urllib2.HTTPError as e:
                logs.warning('Facebook API Error: %s' % e)
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
            params= {
                'access_token'            : access_token
            })

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
              'access_token'        : access_token,
            }
        )

    def deleteTestUser(self, access_token, test_user_id):
        # will return bool result with True == success
        path = test_user_id

        return self._get(
            access_token,
            path,
            { 'method'          : 'delete',
              'access_token'    : access_token,
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

def demo(method, user_id=USER_ID, access_token=ACCESS_TOKEN, **params):
    from pprint import pprint
    facebook = Facebook()

#    if 'netflix_id' in params:  netflix_id  = params['netflix_id']
#    if 'title' in params:       title       = params['title']

    if 'getUserInfo' in methods:            pprint(facebook.getUserInfo(access_token))
    if 'getAppAccessToken' in methods:      pprint(facebook.getAppAccessToken())

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

