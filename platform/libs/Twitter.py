
import Globals
import json, httplib2
import logs
from errors import *
import oauth as oauth

from libs.Request       import service_request
from APIKeys            import get_api_key

TWITTER_CONSUMER_KEY    = get_api_key('twitter', 'consumer_key')
TWITTER_CONSUMER_SECRET = get_api_key('twitter', 'consumer_secret')

class Twitter(object):
    def __init__(self, consumer_key=TWITTER_CONSUMER_KEY, consumer_secret=TWITTER_CONSUMER_SECRET):
        self.__consumer_key         = consumer_key
        self.__consumer_secret      = consumer_secret
        self.__consumer             = oauth.OAuthConsumer(self.__consumer_key, self.__consumer_secret)
        self.__signature_method     = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.__httpObj              = httplib2.Http()

    def __http(self, verb, service, user_token=None, user_secret=None, priority='high', **params):

        url = 'https://api.twitter.com/%s' % service

        # Generate the oauth token from the user_token and user_secret
        if user_token is not None and user_secret is not None:
            token = oauth.OAuthToken(
                user_token,
                user_secret,
            )

            # Prepare the oauth request
            oauthRequest = oauth.OAuthRequest.from_consumer_and_token(self.__consumer,
                http_url=url,
                parameters=params,
                token=token,
                http_method=verb)
            oauthRequest.sign_request(  self.__signature_method, self.__consumer, token)

            header = oauthRequest.to_header()
        else:
            header = None
        body = oauthRequest.to_postdata() if verb == 'POST' else None
        logs.debug(url)

        # Send the http request
        try:
            response, content = service_request('twitter', verb, url, query_params=params, body=body, header=header, priority=priority)
            result = json.loads(content)
        except Exception:
            logs.warning('Error connecting to Twitter')
            raise StampedThirdPartyError('There was an error connecting to Twitter')
        if 'error' in result:
            raise StampedInputError('Twitter API Fail: %s' % result['error'])
        elif 'errors' in result:
            errors = result['errors']
            # Internal Error
            if len(errors) == 1 and 'code' in errors[0] and errors[0]['code'] == 131:
                raise StampedThirdPartyInternalError('Twitter returned an internal error')
            raise StampedThirdPartyError('There was an error connecting to Twitter')
        return result

    def __get(self, service, user_token=None, user_secret=None, priority='high', **params):
        return self.__http('GET', service, user_token, user_secret, priority, **params)

    def __post(self, service, user_token=None, user_secret=None, priority='high', **params):
        return self.__http('POST', service, user_token, user_secret, priority, **params)

    def getUserInfo(self, user_token, user_secret):
        result = self.__get(
            '1/account/verify_credentials.json',
            str(user_token),
            str(user_secret),
        )
        if 'id' not in result:
            logs.info('')
            raise StampedThirdPartyError('An error occurred while retrieving user information from Twitter: %s ' % result)
        # id is returned as an int, but we'll use it as a string for consistency
        result['id'] = str(result['id'])
        return result

    def _getUserIds(self, user_token, user_secret, relationship):
        if relationship == 'friends':
            baseurl = '1/friends/ids.json'
        elif relationship == 'followers':
            baseurl = '1/followers/ids.json'
        else:
            raise StampedInputError("Invalid relationship parameter to getUserIds.  Must be 'friends' or 'followers'.")
        if user_token is None or user_secret is None:
            raise StampedInputError("Connecting to Twitter requires a valid key / secret")

        twitterIds = []
        cursor = -1

        while True:
            result = self.__get(baseurl, user_token, user_secret, cursor=cursor)
            print('### result: %s' % result)
            if 'ids' in result:
                twitterIds = twitterIds + result['ids']

            # Break if no cursor
            if 'next_cursor' not in result or result['next_cursor'] == 0:
                break
            cursor = result['next_cursor']
        twitterIds = map(lambda id: str(id), twitterIds)
        return twitterIds


    def getFriendData(self, user_token, user_secret, offset=0, limit=30):
        logs.info('### user_token %s   user_secret: %s' % (user_token, user_secret))
        if limit > 100:
            raise StampedInputError("Limit must be <= 100")
        ids = self._getUserIds(user_token, user_secret, 'friends')
        if offset >= len(ids):
            return []

        url = '1/users/lookup.json'
        friends = []

        idset = ','.join(ids[offset:offset+limit])
        results = self.__get(url, user_token, user_secret, user_id=idset)
        for result in results:
            try:
                friends.append(
                    {
                        'user_id'   : result['id'],
                        'name'      : result['name'],
                        'screen_name' : result['screen_name'],
                        'image_url' : result['profile_image_url'],
                    }
                )
            except TypeError as e:
                logs.warning("Unable to get twitter friends! Error: %s" % e)
                logs.info("Results: %s" % results)
                raise
        return friends


    def getFriendIds(self, user_token, user_secret):
        return self._getUserIds(user_token, user_secret, 'friends')

    def getFollowerIds(self, user_token, user_secret):
        return self._getUserIds(user_token, user_secret, 'followers')

    def createFriendship(self, user_token, user_secret, friend_screen_name):
        return self.__post('1/friendships/create.json', user_token, user_secret, screen_name = friend_screen_name)

    def destroyFriendship(self, user_token, user_secret, friend_screen_name):
        return self.__post('1/friendships/destroy.json', user_token, user_secret, screen_name = friend_screen_name)


__globalTwitter = None

def globalTwitter():
    global __globalTwitter

    if __globalTwitter is None:
        __globalTwitter = Twitter()

    return __globalTwitter


#TWITTER_USER_A0_TOKEN      = "595895658-K0PpPWPSBvEVYN46cZOJIQtljZczyoOSTXd68Bju"
#TWITTER_USER_A0_SECRET     = "ncDA2SHT0Tn02LRGJmx2LeoDioH7XsKemYk3ktrEyw"
TWITTER_USER_A0_TOKEN      = "558345111-gsOAXPBGrvjOaWNmTyCtivPcEoH6yHVh627IynHU"
TWITTER_USER_A0_SECRET     = "NpWLdSOrvHrtTpy2SALH4Ty1T5QUWdMZQhAMcW6Jp4"

#TWITTER_USER_A0_TOKEN      = "11131112-gJWVu3jAcXDy5ujuyFzD8C1NqU7sA2foMAlrA8RZs"
#TWITTER_USER_A0_SECRET     = "5X0o2biSxIMZpXBbslujtCB8xtGx4sRKekg0D86KM"

def demo(method, user_token=TWITTER_USER_A0_TOKEN, user_secret=TWITTER_USER_A0_SECRET, **params):
    from pprint import pprint
    twitter = Twitter()

    import utils

    if 'user_token' in params:              user_token  = params['user_token']
    if 'user_secret' in params:             user_secret = params['user_secret']

    #headers = utils.getTwitter('https://api.twitter.com/account/verify_credentials.json', user_token, user_secret)
    if 'getFriendData' in methods:          pprint(twitter.getFriendData(user_token, user_secret))
    if 'getUserInfo' in methods:            pprint(twitter.getUserInfo(user_token, user_secret))
    if 'getFriendIds' in methods:           pprint(twitter.getFriendIds(user_token, user_secret))
    if 'getFollowerIds' in methods:         pprint(twitter.getFollowerIds(user_token, user_secret))

if __name__ == '__main__':
    import sys
    params = {}
    methods = 'getUserInfo'
    if len(sys.argv) > 1:
        methods = [x.strip() for x in sys.argv[1].split(',')]
    if len(sys.argv) > 2:
        params = {}
        for arg in sys.argv[2:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    demo(methods, **params)

