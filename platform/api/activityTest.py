

import Globals
import logs, time
from HTTPSchemas import *
from Schemas import *
from MongoStampedAPI import MongoStampedAPI

stampedAPI = MongoStampedAPI()

authUserId = '4ecab825112dea0cfe000293'
scope = 'friends'
limit = 100
offset = 0

activity = stampedAPI.getActivity(authUserId, scope, limit=limit, offset=offset)

print('### len activity: %s' % len(activity))
print(activity[0])

t0 = time.time()
t1 = t0
result = []
for item in activity:
    t1 = time.time()
    result.append(HTTPActivity().importEnrichedActivity(item).dataExport())
    print('time for importEnrichedActivity: %s' % (time.time() - t1))
print('TOTAL time for importEnrichedActivity loop: %s' % (time.time() - t1))
