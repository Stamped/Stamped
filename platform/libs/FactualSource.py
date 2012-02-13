#!/usr/bin/python

"""
Not finished
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'FactualSource' ]

import Globals
from logs import log, report

try:
	from AExternalSource	import AExternalSource
	from libs.Factual		import Factual
	from utils				import lazyProperty
	from datetime			import datetime
	from functools			import partial
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

class FactualSource(AExternalSource):
	"""
	Data-Source wrapper for Factual services.
	"""
	def __init__(self):
		AExternalSource.__init__(self)
		self.__address_fields = {
		    ('address_street',):_ppath('address'),
		    ('address_street_ext',):_ppath('address_extended'),
		    ('address_locality',):_ppath('locality'),
		    ('address_region',):_ppath('region'),
		    ('address_postcode',):_ppath('postcode'),
		    ('address_country',):_ppath('country'),
		}

	@lazyProperty
	def __factual(self):
		return Factual()

	def resolveEntity(self, entity, controller):
		"""
		Attempt to fill populate id fields based on seed data.

		Returns True if the entity was modified.
		"""
		result = False
		factual_id = entity['factual_id']
		if controller.shouldResolve('factual','factual',entity):
			factual_id = self.__factual.factual_from_entity(entity)
			entity['factual_id'] = factual_id
			entity['factual_timestamp'] = datetime.utcnow()
			entity['factual_source'] = 'factual'
			result = True
		if factual_id is not None and controller.shouldResolve('singleplatform','factual',entity):
			singleplatform_id = self.__factual.singleplatform(factual_id)
			entity['singleplatform_id'] = singleplatform_id
			entity['singleplatform_timestamp'] = datetime.utcnow()
			entity['singleplatform_source'] = 'factual'
			result = True
		return result
	
	def enrichEntity(self, entity, controller):
		"""
		Attempt to populate data fields based on id data.

		Returns True if the entity was modified.
		"""
		result = False
		factual_id = entity['factual_id']
		data = None
		if factual_id is not None and controller.shouldEnrich('address','factual',entity):
			data = self.__factual.data(factual_id,entity=entity)
			self.writeFields(entity, data, self.__address_fields)
			entity['address_source'] = 'factual'
			entity['address_timestamp'] = datetime.utcnow()
			result = True
		return result

	def decorateEntity(self, entity, controller):
		"""
		Hook for creating/updating external resouces associated with an entity, writing to decorator-specific entity fields if necessary.

		Returns True if the entity was modified.
		"""
		return False

	@property
	def sourceName(self):
		"""
		Returns the name of this source as would be used with a SourceController.
		"""
		return 'factual'
	

