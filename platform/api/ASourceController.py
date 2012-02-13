#!/usr/bin/python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'ASourceController' ]

import Globals
from logs import log, report

try:
	from abc 		import ABCMeta, abstractmethod
except:
	report()
	raise

class ASourceController(object):
	"""
	Abstact base class for the controller interface expected by subclasses of AEntitySource.
	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def shouldResolve(self, group, source, entity,timestamp=None):
		"""
		Returns whether an EntitySource should write to the given id-field group.

		The optional timestamp parameter can be used to indicate state data from the current source.
		"""
		pass

	@abstractmethod
	def shouldEnrich(self, group, source, entity,timestamp=None):
		"""
		Returns whether an EntitySource should write to the given data-field group.

		The optional timestamp parameter can be used to indicate state data from the current source.
		"""
		pass

	@abstractmethod
	def shouldDecorate(self, group, source, entity,timestamp=None):
		"""
		Returns whether an EntitySource should create the named decoration group.

		The optional timestamp parameter can be used to indicate state data from the current source.
		"""
		pass

