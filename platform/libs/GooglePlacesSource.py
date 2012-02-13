#!/usr/bin/python

"""
Not finished
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'GooglePlacesSource' ]

import Globals
from logs import log, report

try:
	from AExternalSource		import AExternalSource
	from crawler.GooglePlaces 	import GooglePlaces
	from utils					import lazyProperty
	from datetime				import datetime
	from functools				import partial
	from LibUtils				import states
except:
	report()
	raise

def _path(path,data):
    cur = data
    for k in path:
        if k in cur:
            cur = cur[k]
        else:
            return None
    return cur

def _ppath(*args):
    return partial(_path,args)

def _constant_helper(value,not_used):
	return value

def _constant(value):
	return partial(_constant_helper,value)

class GooglePlacesSource(AExternalSource):
	"""
	Data-Source wrapper for Google Places.
	"""
	def __init__(self):
		AExternalSource.__init__(self)
	@lazyProperty
	def __places(self):
		return GooglePlaces()

	def resolveEntity(self, entity, controller):
		return False
	
	def enrichEntity(self, entity, controller):
		result = False
		if controller.shouldEnrich('address','googleplaces',entity) and 'lng' in entity and 'lat' in entity and 'title' in entity:
			gdata = self.__places.getSearchResultsByLatLng((entity['lat'],entity['lng']),{'name':entity['title']})
			if gdata is not None and len(gdata) > 0:
				gdatum = gdata[0]
				if 'reference' in gdatum:
					ref = gdatum['reference']
					details = self.__places.getPlaceDetails(ref)
					if details is not None:
						reformatted = self.__reformat(details)
						self.writeFields(entity, None, reformatted)
						entity['address_source'] = 'googleplaces'
						entity['address_timestamp'] = datetime.utcnow()
						result = True
		return result

	def decorateEntity(self, entity, controller):
		return False

	@property
	def sourceName(self):
		return 'googleplaces'

	def __reformat(self, results):
		data = {
			'address_street':None,
			'address_street_ext':None,
			'address_locality':None,
			'address_region':None,
			'address_postcode':None,
			'address_country':None,
		}
		number = None
		route = None
		if 'address_components' in results:
			for comp in results['address_components']:
				if 'types' in comp and 'long_name' in comp:
					name = comp['long_name']
					types = comp['types']
					if 'administrative_area_level_1' in types:
						#TODO consider country checking
						if name in states:
							name = states[name]
						data['address_region'] = name
					elif 'country' in types:
						data['address_country'] = name
					elif 'postal_code' in types:
						data['address_postcode'] = name
					elif 'locality' in types:
						data['address_locality'] = name
					elif 'street_number' in types:
						number = name
					elif 'route' in types:
						route = name
		if 'address_components' in results:
			for comp in results['address_components']:
				if 'types' in comp and 'long_name' in comp:
					name = comp['long_name']
					types = comp['types']
					if 'sublocality' in types and data['address_locality'] is None:
						data['address_locality'] = name
		if route is not None and number is not None:
			data['address_street'] = "%s %s" % (number, route)
		data = { tuple(k.split('.')):_constant(v) for k,v in data.items() }
		return data
	

