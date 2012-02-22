#!/usr/bin/env python
import oauth2 as oauth
import urllib, cgi
import sys
import pprint
import json

def getAccess():
    # create the OAuth consumer credentials
    consumer = oauth.Consumer('bzj2pmrs283kepwbgu58aw47','xJSZwBZxFp')
     
    # make the initial request for the request token
    client = oauth.Client(consumer)
    response, content = client.request('http://api.rdio.com/oauth/request_token', 'POST', urllib.urlencode({'oauth_callback':'oob'}))
    parsed_content = dict(cgi.parse_qsl(content))
    request_token = oauth.Token(parsed_content['oauth_token'], parsed_content['oauth_token_secret'])
     
    # ask the user to authorize this application
    print 'Authorize this application at: %s?oauth_token=%s' % (parsed_content['login_url'], parsed_content['oauth_token'])
    oauth_verifier = raw_input('Enter the PIN / OAuth verifier: ').strip()
    # associate the verifier with the request token
    request_token.set_verifier(oauth_verifier)
     
    # upgrade the request token to an access token
    client = oauth.Client(consumer, request_token)
    response, content = client.request('http://api.rdio.com/oauth/access_token', 'POST')
    parsed_content = dict(cgi.parse_qsl(content))
    print(parsed_content)
    access_token = oauth.Token(parsed_content['oauth_token'], parsed_content['oauth_token_secret'])
    print access_token
    # make an authenticated API call
    client = oauth.Client(consumer, access_token)
    response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode({'method': 'currentUser'}))
    print response[1]

def useAccess(access_token,access_secret):
    # create the OAuth consumer credentials
    access_token = oauth.Token(access_token, access_secret)
    consumer = oauth.Consumer('bzj2pmrs283kepwbgu58aw47','xJSZwBZxFp')
     
    # make an authenticated API call
    client = oauth.Client(consumer, access_token)
    """
    track = 't4518120'
    response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode({
        'method': 'createPlaylist',
        'name':'Katy Perry Songs',
        'description':'Awesome Songs',
        'tracks':track,
    }))
    """
    response = client.request('http://api.rdio.com/1/', 'POST', urllib.urlencode({
        'method': 'getPlaylists',
    }))

    print response
    pprint.pprint(json.loads(response[1]))

if __name__ == '__main__':
    if len(sys.argv) < 3:
        getAccess()
    else:
        useAccess(sys.argv[1],sys.argv[2])