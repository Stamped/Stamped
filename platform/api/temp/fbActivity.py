import Globals
from time import sleep
from MongoStampedAPI import MongoStampedAPI

api = MongoStampedAPI()

testedUsers = set()
failedUsers = set()

limit = 10000000
if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])


users = list(api._accountDB._collection.find({'linked.facebook.extended_timestamp' : {'$exists' : 0}}))
print('%s accounts found for update.  Updating %s' % (len(users), limit))

if len(users) > limit:
    users = users[:limit]

for u in users:
    user_id = u['_id']
    print('updating user_id: %s' % user_id)
    try:
        api._addFBLoginActivity(user_id)
        testedUsers.add(user_id)
    except Exception as e:
        print('### Failed for user: %s  Exception: %s' % (user_id, e))
        failedUsers.add(user_id)


print('Failed Users')
for u in failedUsers:
    print(u)

print('Succeeded Users')
for u in testedUsers:
    print(u)

print('Number of Failed Users: %s' % len(failedUsers))
print('Number of Succeeded Users: %s' % len(testedUsers))



