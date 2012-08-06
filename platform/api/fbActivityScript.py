from __future__ import absolute_import
import Globals
from time import sleep
from MongoStampedAPI import MongoStampedAPI
from errors import StampedFacebookTokenError

api = MongoStampedAPI()
fb = api._facebook

testedUsers = set()
failedUsers = set()

users = api._accountDB._collection.find(
        { {'linked.facebook.extended_timestamp' : {'$exists' : 0}} }
)

for u in users:



    user_id = u['_id']
    token = u['linked']['facebook']['token']
    print('updating user_id: %s  token: %s' % (user_id, token))
    try:
        api.updateFBPermissionsAsync(user_id, token)
    except StampedFacebookTokenError:
        print('### Invalid token for user: %s' % user_id)
        failedUsers.add(user_id)
        acct = api.getAccount(user_id)
        linked = acct.linked.facebook
        linked.token = None
        api._accountDB.updateLinkedAccount(user_id, linked)
    except Exception as e:
        print('### EXCEPTION: %s' % e)
        failedUsers.add(user_id)
        continue
    testedUsers.add(user_id)
    sleep(1)

print('Failed Users')
for u in failedUsers:
    print(u)

print('Succeeded Users')
for u in testedUsers:
    print(u)

print('Number of Failed Users: %s' % failedUsers.count())
print('Number of Succeeded Users: %s' % testedUsers.count())