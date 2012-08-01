





item = {
    'activity_id'   : # Required
    'verb'          : # Required
    'subject'       : # Optional ("Welcome to Stamped")
    'recipient'     : # Optional (to-do an entity)
    'objects'       : { # ?? 
        'stamp_id'
        'user_id'
        'entity_id'
        'todo_id' #?
    }

    'timestamp'     : # Required
    'benefit'       : # If necessary

    'header'        :
    'body'          :
    'footer'        : 
}




grouped = {
    'activity_id'
    'verb'
    'subjects'
    'objects'
    'timestamp'
    'benefit'
    'header'
    'body'
    'footer'
}





item = {
    'activity_id'   : # Required
    'verb'          : # Required
    'subject'       : # Optional ("Welcome to Stamped")
    'objects'       : { # ?? 
        'stamp_id'      : 
        'user_id'       : 
        'entity_id'     : 
        'comment_id'    : 
    }
    'source'        : # Optional (actions)

    'timestamp'     : # Required
    'benefit'       : # If necessary

    'header'        : 
    'body'          : 
    'footer'        : 
}



# LINKS
- Per user / item
- Overwrite timestamp


# OBJECTS
- Per item
- Default timestamp

Mike added a todo for The Dark Knight via Kevin & Robby
Bart commented on Lulu Lemon via Ryan
Paul listented to Flight of the Conchords via Kevin
Geoff added The NY Times as a to-do
Robby followed Landon
Welcome to Stamped 2.0
Please reset your Facebook token


Robby   credit      The Dark Knight     Kevin
Robby   credit      The Dark Knight     Bart 

Bart    to-do       Path                Paul
Bart    to-do       Path                Kevin 

Robby   like        Path                Paul




            UNIVERSAL NEWS          PERSONAL NEWS
todo    ->  group on entity_id      group on entity_id / date
follow  ->  group on user_id        group on date
like    ->  group on stamp_id       group on stamp_id / date
comment ->  no group                no group 
friend  ->  N/A                     no group 
credit  ->  N/A                     group on stamp_id
action  ->  N/A                     group on stamp_id 


activityIds = find({'user_id': authUserId})
friendIds = self._friendshipDB.getFriends(authUserId)

personalQuery = {'_id': {'$in': activityIds}}
personalItems = self._activityDB._collection.find(personalQuery)

universalQuery = {'subject': {'$in': friendIds}, 'verb': {'$in': ['todo', 'follow', 'like', 'comment']}}
universalItems = self._activityDB._collection.find(universalQuery)

def buildActivityKeys(items):
    keys = {}
    sortedKeys = []
    for item in items:
        # Generate unique key
        key = '%s::%s' % (item.verb, item.activity_id)

        # Generate grouped key
        if item.verb == 'todo':
            key = 'todo::%s::%s' % (item.entity_id, item.timestamp.created.isodate()[:10])
            
        elif item.verb == 'follow':
            key = 'follow::%s::%s' % (item.user_id, item.timestamp.created.isodate()[:10])

        elif item.verb == 'like' or item.verb == 'credit' or item.verb.startswith('action_'):
            key = '%s::%s::%s' % (item.verb, item.stamp_id, item.timestamp.created.isodate()[:10])

        elif item.verb in set(['comment', 'reply', 'mention']):
            if item.comment_id is not None:
                key = 'comment::%s' % item.comment_id
            else:
                key = 'mention::%s' % item.stamp_id

        # Apply keys
        if key in keys:
            # Existing item
            if 'subjects' in keys[key] and item.subject not in keys[key]['subjects']:
                keys[key]['subjects'].append[item.subject]
            else:
                logs.warning("Missing subjects! %s" % item)
        else:
            # New item
            keys[key] = item 
            sortedKeys.append(key)

    return keys, sortedKeys

personalKeys, sortedPersonalKeys = buildActivityKeys(personalItems)
universalKeys, sortedUniversalKeys = buildActivityKeys(universalItems)

mark = str(int(time.time() * 1000000))

sort = 9999
personalResult = []
for key in sortedPersonalKeys:
    item = personalKeys[key]
    item.sort = ("%s|%s" % (mark, str(sort).zfill(4))).zfill(22)
    personalResult.append(item)
    sort -= 1

sort = 9999
universalResult = []
for key in sortedUniversalKeys:
    if key not in personalKeys:
        item = universalKeys[key]
        item.sort = ("%s|%s" % (mark, str(sort).zfill(4))).zfill(22)
        universalResult.append(item)
        sort -= 1





