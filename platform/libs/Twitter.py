
import time
import urllib, urllib2, json, httplib2
import logs
import re
from errors import *
import oauth as oauth

TWITTER_CONSUMER_KEY    = 'kn1DLi7xqC6mb5PPwyXw'
TWITTER_CONSUMER_SECRET = 'AdfyB0oMQqdImMYUif0jGdvJ8nUh6bR1ZKopbwiCmyU'

class Twitter(object):
    def __init__(self, consumer_key=TWITTER_CONSUMER_KEY, consumer_secret=TWITTER_CONSUMER_SECRET):
        self.__consumer_key         = consumer_key
        self.__consumer_secret      = consumer_secret
        self.__consumer             = oauth.OAuthConsumer(self.__consumer_key, self.__consumer_secret)
        self.__signature_method     = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.__httpObj              = httplib2.Http()

    def __http(self, verb, service, user_token=None, user_secret=None, **params):

        baseurl = 'https://api.twitter.com/'
        encoded_params  = urllib.urlencode(params)
        url     = "%s%s?%s" % (baseurl, service, encoded_params)

        # Generate the oauth token from the user_token and user_secret
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

        headers = oauthRequest.to_header()
#        body = oauthRequest.to_postdata() if verb == 'POST' else None
        body = None
        logs.info(url)

        # Send the http request
        response, content = self.__httpObj.request(url, method=verb, body=body, headers=headers)

        print content
        result = json.loads(content)
        if 'error' in result:
            raise StampedInputError('Twitter API Fail: %s' % result['error'])
        return result

    def __get(self, service, user_token, user_secret, **params):
        return self.__http('GET', service, user_token, user_secret, **params)

    def __post(self, service, user_token, user_secret, **params):
        return self.__http('POST', service, user_token, user_secret, **params)

    def verifyCredentials(self, user_token, user_secret):
        print ('calling verifyCredentials with user_token: %s  user_secret: %s' % (user_token, user_secret))
        result = self.__get(
            'account/verify_credentials.json',
            user_token,
            user_secret,
        )
        # id is returned as an int, but we'll use it as a string for consistency
        result['id'] = str(result['id'])
        return result

__globalTwitter = None

def globalTwitter():
    global __globalTwitter

    if __globalTwitter is None:
        __globalTwitter = Twitter()

    return __globalTwitter


#TEST_OAUTH_TOKEN             = '87947182-2hCG8J8WY3sHod3DTDX474vSaBXZbWsCGgGR7Yo'
#TEST_OAUTH_TOKEN_SECRET      = 'CXRhlwRULHpEckEfZ3HFH8aMBjIQ7NuDRhgseuww'

#TODO: Get a test account instead of using my personal account here!
TEST_OAUTH_TOKEN_SECRET     = 'NpWLdSOrvHrtTpy2SALH4Ty1T5QUWdMZQhAMcW6Jp4'
TEST_OAUTH_TOKEN            = '558345111-gsOAXPBGrvjOaWNmTyCtivPcEoH6yHVh627IynHU'

def demo(method, user_token=TEST_OAUTH_TOKEN, user_secret=TEST_OAUTH_TOKEN_SECRET, **params):
    from pprint import pprint
    twitter = Twitter()

    import utils

    if 'user_token' in params:              user_token  = params['user_token']
    if 'user_secret' in params:             user_secret = params['user_secret']

    #headers = utils.getTwitter('https://api.twitter.com/account/verify_credentials.json', user_token, user_secret)
    if 'verifyCredentials' in methods:      pprint(twitter.verifyCredentials(user_token, user_secret))

if __name__ == '__main__':
    import sys
    params = {}
    methods = 'verifyCredentials'
    if len(sys.argv) > 1:
        methods = [x.strip() for x in sys.argv[1].split(',')]
    if len(sys.argv) > 2:
        params = {}
        for arg in sys.argv[2:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    demo(methods, **params)

