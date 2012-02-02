#!/usr/bin/python

"""
Interface for Factual API

Important attributes of a place entity:

factual_id - the unique entity identifier
name - the full or partial name in the case of resolve
postcode - zipcode string (i.e. '15237')
country - short code (i.e. 'US' )
address - street portion of address (i.e. '4864 McKnight Rd')
locality - city (i.e. 'Pittsburgh' )
region - state code (i.e. 'PA' )
tel - telephone number (i.e. '(412) 765-3200')
latitude - float (i.e. 40.525447)
longitude - float (i.e. -80.005443)


Crosswalk:
Crosswalk attempts to map ids and URIs from one service to
the ids and URIs of other services. For a complete list
of associated services visit:
http://developer.factual.com/display/docs/Places+API+-+Supported+Crosswalk+Services
For the purposes of this module, you might be most intersted in the following services (namespaces):

allmenus
bitehunter
facebook
foursquare
menuism
menumob
menuplatform
openmenu
opentable
singleplatform
twitter_place
urbanspoon
yahoolocal
yelp

"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import utils
import json
import urllib
import sys
from SinglePlatform import StampedSinglePlatform
from pprint import pprint

_API_Key = "SlSXpgbiMJEUqzYYQAYttqNqqb30254tAUQIOyjs0w9C2RKh7yPzOETd4uziASDv"
#_API_V3_Key = "p7kwKMFUSyVi64FxnqWmeSDEI41kzE3vNWmwY9Zi"
_API_V3_Key = 'xdNC1Jb03oXouZvIoGNjOFb122lhPax8DN1a1I8P'
_limit = 50

class Factual(object):
    """
    Factual API Wrapper
    """
    def __init__(self,key=_API_Key,v3_key=_API_V3_Key):
        self.__key = key
        self.__v3_key = v3_key
        self.__singleplatform = StampedSinglePlatform()
    
    def resolve(self, data,limit=_limit):
        """
        Use Resolve service to match entities to limited attributes, including partial names.
        
        Accepts a JSON compatible object such as: {'name':'ino','locality':'New York'}

        returns a JSON like object which includes the usual attributes and 'similarity'

        which indicates the quality of the match. Resolve does not require much information
        and will operate on partial names.
        """
        string = json.dumps(data)
        r = self.__factual('resolve',limit=limit,values=urllib.quote(string))
        if r != None and len(r) > limit:
            r = r[:limit]
        return r
        
    def places(self, data,limit=_limit):
        """
        A stricter search than resolve. Seems to only produce entities which exactly match the given fields (at least for name).
        """
        string = urllib.quote(json.dumps(data))
        return self.__factual('read',limit=limit,filters=string)
        
    def crosswalk_id(self,factual_id,namespace=None,limit=_limit):
        """
        Use Crosswalk service to find urls and ids that match the given entity.
        
        If namespace is provided, it limits the scope of the search to that service.

        It appears that there are not necessarilly crosswalk results for every factual_id.

        Regardless of the options, every entry in the result will contain the following fields:
        
        factual_id - the given id
        namespace - the namespace of entry (i.e. 'singleplatform')
        namespace_id - the string id within the namespace (i.e. 'ino') or '' if unknown/non-existant
        url - the url associated with the entity or '' (i.e. 'http://www.menuism.com/restaurants/ino-new-york-253388')
        """
        args = {'limit':limit,'factual_id':factual_id}
        if namespace != None:
            args['only'] = namespace
        return self.__factual('crosswalk',**args)
    
    def crosswalk_external(self,space,space_id,namespace=None,limit=_limit):
        """
        Use Crosswalk service to find urls and ids that match the given external entity.
        
        If namespace is provided, it limits the scope of the search to that service.
        Regardless of the options, every entry in the result will contain the following fields:
        
        factual_id - the given id
        namespace - the namespace of entry (i.e. 'singleplatform')
        namespace_id - the string id within the namespace (i.e. 'ino') or '' if unknown/non-existant
        url - the url associated with the entity or '' (i.e. 'http://www.menuism.com/restaurants/ino-new-york-253388')
        """
        args = {'limit':limit,'namespace':space,'namespace_id':space_id}
        if namespace != None:
            args['only'] = namespace
        return self.__factual('crosswalk',**args)
        
    def crossref_id(self,factual_id,limit=_limit):
        """
        Use Crossref service to find urls that pertain to the given entity.
        """
        return self.__factual('crossref',factual_id=factual_id,limit=limit)
        
    def crossref_url(self,url,limit=_limit):
        """
        User Crossref service to find the entities related/mentioned at the given url.
        """
        return self.__factual('crossref',url=urllib.quote(url),limit=limit)
    
    def restaurant(self,factual_id):
        """
        Get Factual restaurant data for a given factual_id.
        """
        string = json.dumps({'factual_id':factual_id})
        result = self.__factual('restaurants-us','t',filters=urllib.quote(string))
        if result:
            return result[0]
        else:
            return None

    def entity(self,factual_id):
        """
        STUB Create a Stamped entity from a factual_id.
        """
        pass

    def factual_from_entity(self,entity):
        """
        STUB Get the factual_id (if any) associated with the given entity.
        """
        pass
    
    def factual_from_singleplatform(self,singleplatform_id):
        """
        STUB Get the factual_id (if any) associated with the given singleplatform ID.
        """
        pass
    
    def singleplatform(self,factual_id):
        """
        Get singleplatform id from factual_id

        Returns id or None if not known.
        """
        singleplatform_info = self.crosswalk_id(factual_id,namespace='singleplatform')
        sp_id = None
        if singleplatform_info and 'namespace_id' in singleplatform_info[0]:
            sp_id = singleplatform_info[0]['namespace_id']
        if sp_id:
            return sp_id
        else:
            return None

    def menu(self,factual_id):
        """
        Get menu for a factual_id

        Currently only supports singleplatform and returns singleplatform menu verbatim.
        """
        sp_id = self.singleplatform(factual_id)
        if sp_id:
            m = self.__singleplatform.get_menu(sp_id)
            return m
        else:
            return None

    def __factual(self,service,prefix='places',**args):
        if 'KEY' not in args:
            args['KEY'] = self.__v3_key
        pairs = [ '%s=%s' % (k,v) for k,v in args.items() ]
        url =  "http://api.v3.factual.com/%s/%s?%s" % (prefix,service,'&'.join(pairs))
        return self.__query(url)

    def __query(self,url):
        response = utils.getFile(url)
        m = json.loads(response)
        try:
            return m['response']['data']
        except:
            return None
            
def demo():
    """
    Interactive feature demo for the Factual class.
    Follow the prompts to test out features for different inputs.
    Refer to the 
    """
    sys.stdout.write('Use default attributes (non-empty for false): ')
    use_defaults = sys.stdin.readline().strip()
    d = {}
    if not use_defaults:
        sys.stdout.write('Enter a name (or partial name): ')
        d['name'] = sys.stdin.readline().strip()
        sys.stdout.write('Enter a city: ')
        d['locality'] = sys.stdin.readline().strip()
    else:
        while True:
            sys.stdout.write('Enter key (or empty to finish): ')
            key = sys.stdin.readline().strip()
            if not key:
                break
            sys.stdout.write('Enter value: ')
            d[key] = sys.stdin.readline().strip()
    sys.stdout.write('Enter maximum number of results: ')
    limit = int(sys.stdin.readline().strip())
    f = Factual()
    results = f.resolve(d,limit=limit)
    print("Top "+str(len(results))+" results:")
    for i in results:
        pprint(i)
    sys.stdout.write('Choose an item (by index): ')
    index = int(sys.stdin.readline().strip())
    item = results[index]
    sys.stdout.write('Limit to namespace (blank for no namespace): ')
    namespace = sys.stdin.readline().strip()
    sys.stdout.write('Enter maximum number of crosswalk results: ')
    limit = int(sys.stdin.readline().strip())
    if namespace == '':
        namespace = None
    results = f.crosswalk_id(item['factual_id'],namespace,limit)
    print("Top "+str(len(results))+" crosswalk results:")
    for i in results:
        pprint(i)
    sys.stdout.write('Choose an item (by index): ')
    index = int(sys.stdin.readline().strip())
    item2 = results[index]
    sys.stdout.write('Enter maximum number of reverse crosswalk results: ')
    limit = int(sys.stdin.readline().strip())
    sys.stdout.write('Limit to namespace (blank for no namespace): ')
    namespace = sys.stdin.readline().strip()
    if namespace == '':
        namespace = None
    results = f.crosswalk_external(item2['namespace'],item2['namespace_id'],namespace,limit)
    print("Top "+str(len(results))+" reverse crosswalk results:")
    for i in results:
        pprint(i)
    sys.stdout.write('Enter maximum number of crossref results: ')
    limit = int(sys.stdin.readline().strip())
    results = f.crossref_id(item['factual_id'],limit)
    print("Top "+str(len(results))+" crossref results:")
    for i in results:
        pprint(i)
        
    sys.stdout.write('Enter a url for reverse crossref: ')
    url = sys.stdin.readline().strip()
    sys.stdout.write('Enter maximum number of crossref results: ')
    limit = int(sys.stdin.readline().strip())
    
    results = f.crossref_url(url,limit)
    print("Top "+str(len(results))+" reverse crossref results:")
    for i in results:
        pprint(i)
    print("Finished")

if __name__ == '__main__':
    demo()
    
    
