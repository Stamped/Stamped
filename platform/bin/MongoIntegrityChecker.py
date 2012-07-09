#!/usr/bin/env python

__author__    = 'Stamped (dev@stamped.com)'
__version__   = '1.0'
__copyright__ = 'Copyright (c) 2011-2012 Stamped.com'
__license__   = 'TODO'

import Globals
import logs

from api.db.mongodb.MongoInboxStampsCollection 			import MongoInboxStampsCollection

collections = [
	MongoInboxStampsCollection
]

for collection in collections:
	db = collection()
	for i in db._collection.find(fields=['_id']):
		try:
			result = db.checkIntegrity(i['_id'], noop=True)
		except NotImplementedError:
			print 'COLLECTION NOT IMPLEMENTED: %s' % collection.__name__
			break
		except Exception:
			result = False
		print i['_id'], result

