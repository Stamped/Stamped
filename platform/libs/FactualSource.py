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

try
	from AExternalSource	import AExternalSource
	from libs.Factual		import Factual
	from utils				import lazyProperty
except:
	report()
	raise

class FactualSource(AEntitySource):
	"""
	Data-Source wrapper for Factual services.
	"""
	def __init__(self):
		pass

	@lazyProperty
	def __factual(self):
		return Factual()

	def resolveEntity(self, entity, controller):
		"""
		Attempt to fill populate id fields based on seed data.

		Returns True if the entity was modified.
		"""
		if controller.shouldResolve('factual','factual',entity):
			pass
			#TODO
		return False
	
	def enrichEntity(self, entity, controller):
		"""
		Attempt to populate data fields based on id data.

		Returns True if the entity was modified.
		"""
		return False

	def decorateEntity(self, entity, controller):
		"""
		Hook for creating/updating external resouces associated with an entity, writing to decorator-specific entity fields if necessary.

		Returns True if the entity was modified.
		"""
		return False


