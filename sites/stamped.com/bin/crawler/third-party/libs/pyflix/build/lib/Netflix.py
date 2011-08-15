__author__ = "Kirsten Jones <synedra@gmail.com>"
__version__ = "$Rev$"
__date_ = "$Date$"

import sys
import os.path
import re
import oauth.oauth as oauth
import httplib
import time
from xml.dom.minidom import parseString
import simplejson
from urlparse import urlparse

HOST 			  = 'api.netflix.com'
PORT              = '80'
REQUEST_TOKEN_URL = 'http://api.netflix.com/oauth/request_token'
ACCESS_TOKEN_URL  = 'http://api.netflix.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api-user.netflix.com/oauth/login'

class NetflixError(Exception): pass

class NetflixUser():
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
		oauthRequest = oauth.OAuthRequest.from_consumer_and_token(	client.consumer,
									token=requestToken,
									http_url=self.accessTokenUrl)
		oauthRequest.sign_request(	client.signature_method_hmac_sha1,
									client.consumer,
									requestToken)
		client.connection.request(	oauthRequest.http_method,
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
		
		info = simplejson.loads( self.client._getResource( requestUrl, token=accessToken ) )
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
			info = simplejson.loads(self.client._getResource( url,token=accessToken ))
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
		
		info = simplejson.loads( self.client._getResource( requestUrl, parameters=parameters, token=accessToken ) )
		
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
			info = simplejson.loads( self.client._getResource( requestUrl, parameters=parameters, token=accessToken ) )
		except:
			return {}
			
		return info
		
class NetflixCatalog():
	def __init__(self,client):
		self.client = client
	
	def searchTitles(self, term,startIndex=None,maxResults=None):
	   requestUrl = '/catalog/titles'
	   parameters = {'term': term}
	   if startIndex:
		   parameters['start_index'] = startIndex
	   if maxResults:
		   parameters['max_results'] = maxResults
	   info = simplejson.loads( self.client._getResource( requestUrl, parameters=parameters))

	   return info['catalog_titles']['catalog_title']

	def searchStringTitles(self, term,startIndex=None,maxResults=None):
	   requestUrl = '/catalog/titles/autocomplete'
	   parameters = {'term': term}
	   if startIndex:
		   parameters['start_index'] = startIndex
	   if maxResults:
		   parameters['max_results'] = maxResults

	   info = simplejson.loads( self.client._getResource( requestUrl, parameters=parameters))
	   print simplejson.dumps(info)
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
	   	   info = simplejson.loads( self.client._getResource( requestUrl, parameters=parameters))
	   except:
		   return []

	   return info['people']['person']

	def getPerson(self,url):
		requestUrl = url
		try:
			info = simplejson.loads( self.client._getResource( requestUrl ))
		except:
			return {}
		return info		  

class NetflixUserQueue:
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
			info = simplejson.loads(self.client._getResource( requestUrl, parameters=parameters, token=self.user.accessToken ))
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
			info = simplejson.loads(self.client._getResource( requestUrl, parameters=parameters, token=self.user.accessToken ))
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
			info = simplejson.loads(self.client._getResource( requestUrl, parameters=parameters, token=self.user.accessToken ))
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
			response = simplejson.loads(response)
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
		response = simplejson.loads(response)
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

class NetflixDisc:
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
			info = simplejson.loads(self.client._getResource( url ))
		except :
			return []
		else:
			return info
			
class NetflixClient:
	def __init__(self, name, key, secret, callback='',verbose=False):
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
	
	def _getResource(self, url, token=None, parameters={}):
		if not re.match('http',url):
			url = "http://%s%s" % (HOST, url)
		parameters['output'] = 'json'
		oauthRequest = oauth.OAuthRequest.from_consumer_and_token(self.consumer,
								http_url=url,
								parameters=parameters,
								token=token)
		oauthRequest.sign_request(	self.signature_method_hmac_sha1,
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
		
		oauthRequest = oauth.OAuthRequest.from_consumer_and_token(	self.consumer,
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
		
		oauthRequest = oauth.OAuthRequest.from_consumer_and_token(	self.consumer,
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
