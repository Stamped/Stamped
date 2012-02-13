#!/usr/bin/python

"""
Not finished
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'ExternalSourceController' ]

import Globals
from logs import log, report

try:
	from ASourceController	import ASourceController
	from datetime			import datetime
	from datetime			import timedelta
except:
	report()
	raise

class ExternalSourceController(ASourceController):

	def __init__(self):
		ASourceController.__init__(self)
		self.__resolve_groups = set(['factual','singleplatform'])
		self.__max_resolve_ages = {
			'factual': timedelta(30),
			'singleplatform': timedelta(30),
		}
		self.__resolve_source_priorities = {
			'factual': ['factual','singleplatform'],
			'singleplatform': ['factual'],
		}
		self.__resolve_timestamps = {
			'factual': ['factual_timestamp'],
			'singleplatform': ['singleplatform_timestamp'],
		}
		self.__resolve_sources = {
			'factual': ['factual_source'],
			'singleplatform': ['singleplatform_source'],
		}
		self.__resolve = {
			'ages':self.__max_resolve_ages,
			'priorities':self.__resolve_source_priorities,
			'timestamps':self.__resolve_timestamps,
			'sources':self.__resolve_sources,
			'groups':self.__resolve_groups,
		}
		self.__enrich = {
			'groups': set(['address']),
			'ages': {
				'address':timedelta(30)
			},
			'priorities': {
				'address':['factual']
			},
			'timestamps': {
				'address':['address_timestamp'],
			},
			'sources': {
				'address':['address_source'],
			},
		}

	def shouldResolve(self, group, source, entity,timestamp=None):
		if timestamp == None:
			timestamp = datetime.utcnow()
		return self.__genericShould(group, source, entity, timestamp, self.__resolve)
	
	def shouldEnrich(self, group, source, entity,timestamp=None):
		if timestamp == None:
			timestamp = datetime.utcnow()
		return self.__genericShould(group, source, entity, timestamp, self.__enrich)

	def shouldDecorate(self, group, source, entity,timestamp=None):
		"""
		Returns whether an EntitySource should create the named decoration group.

		The optional timestamp parameter can be used to indicate state data from the current source.
		"""
		return False

	def __genericShould(self, group, source, entity, timestamp, state):
		priorities = state['priorities']
		ages = state['ages']
		timestamps = state['timestamps']
		sources = state['sources']
		groups = state['groups']
		if group not in groups:
			return False
		if source in priorities[group]:
			old_source = self.__field(entity, sources[group])
			delta = self.__compare(old_source, source, priorities[group])
			if delta > 0:
				return True
			elif delta < 0:
				return False
			else:
				old_timestamp = self.__field(entity, timestamps[group])
				return self.__stale(old_timestamp, timestamp, ages[group])
		else:
			return False

	def __field(self, entity, path):
		cur = entity
		for k in path:
			if k in cur:
				cur = cur[k]
			else:
				return None
		return cur
	
	def __compare(self, old_source, new_source, priorities):
		if old_source is None:
			return 1000 #arbitrary largish positive number
		else:
			return priorities.index(old_source) - priorities.index(new_source)
	
	def __stale(self, old_timestamp, new_timestamp, max_age):
		if old_timestamp is None:
			return True
		else:
			return new_timestamp - old_timestamp > max_age
			
