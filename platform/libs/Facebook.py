

APP_ID          = '297022226980395'
APP_SECRET      = '17eb87d731f38bf68c7b40c45c35e52e'
APP_NAMESPACE   = 'stampedapp'

class Facebook(object):
    def __init__(self, app_id=APP_ID, app_secret=APP_SECRET, app_namespace=APP_NAMESPACE):
        self.app_id         = app_id
        self.app_secret     = app_secret
        self.app_namespace  = app_namespace
        pass

    def _get(accessToken, path, params=None):
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
                result  = json.load(urllib2.urlopen(url))

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

    def authorize(code, state):
        path = 'oauth/access_token'
        self._get(None,
            params= {
                'client_id'       : self.app_id,
                'client_secret'   : self.app_secret,
                'code'            : code
        })

__globalFacebook = None

def globalFacebook():
    global __globalFacebook

    if __globalFacebook is None:
        __globalFacebook = Facebook()

    return __globalFacebook


MIKE_ID = '100003940534060'

def demo(method, user_id=USER_ID, user_token=OAUTH_TOKEN, user_secret=OAUTH_TOKEN_SECRET, netflix_id=BIGLEB_ID, **params):
    from pprint import pprint
    netflix = Netflix()

    user_id = MIKE_ID
    if 'netflix_id' in params:  netflix_id  = params['netflix_id']
    if 'title' in params:       title       = params['title']

    if 'searchTitles' in methods:         pprint( netflix.searchTitles(title) )
    if 'getTitleDetails' in methods:      pprint( netflix.getTitleDetails(netflix_id) )
    if 'getRentalHistory' in methods:     pprint( netflix.getRentalHistory(user_id, user_token, user_secret) )
    if 'getRecommendations' in methods:   pprint( netflix.getRecommendations(user_id, user_token, user_secret) )
    if 'getUserRatings' in methods:       pprint( netflix.getUserRatings(user_id, user_token, user_secret, netflix_id) )
    if 'addToQueue' in methods:           pprint( netflix.addToQueue(user_id, user_token, user_secret, netflix_id) )

if __name__ == '__main__':
    import sys
    params = {}
    methods = 'getTitleDetails'
    params['title'] = 'ghostbusters'
    if len(sys.argv) > 1:
        methods = [x.strip() for x in sys.argv[1].split(',')]
    if len(sys.argv) > 2:
        params = {}
        for arg in sys.argv[2:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    demo(methods, **params)

