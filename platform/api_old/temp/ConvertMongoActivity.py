
import pymongo, copy

connection = pymongo.Connection("ec2-50-17-124-56.compute-1.amazonaws.com", 27017)
database = connection['stamped']
collection = database['activity']
newCollection = database['activity3']

oldData = collection.find()

for data in oldData:
	print 'OLD: %s' % data

	if 'link' in data:
		print 'PASS'
		print
		print 
		break

	activity = {}

	if 'comment' in data:
		activity['blurb'] = data['comment']['blurb']
	elif 'stamp' in data:
		activity['blurb'] = data['stamp']['blurb']
	else:
		activity['blurb'] = None

	if 'stamp' in data:
		activity['subject'] = data['stamp']['entity']['title']

	if 'comment' in data:
		activity['link'] = {}
		activity['link']['comment_id'] = data['comment']['comment_id']
		activity['link']['stamp_id'] = data['comment']['stamp_id']
	elif 'stamp' in data:
		activity['link'] = {}
		activity['link']['stamp_id'] = data['stamp']['stamp_id']
	elif 'user' in data:
		activity['link'] = {}
		activity['link']['user_id'] = data['user']['user_id']

	activity['user'] = {
		'color_primary': data['user']['color_primary'], 
		'color_secondary': data['user']['color_secondary'], 
		'screen_name': data['user']['screen_name'], 
		'privacy': data['user']['privacy'], 
		'user_id': data['user']['user_id']
	}

	activity['user'] 		= data['user'] 		 ### TEMP
	activity['_id'] 		= data['_id']
	activity['genre'] 		= data['genre']
	activity['timestamp'] 	= data['timestamp']

	print
	print 'NEW: %s' % activity
	newCollection.insert(activity)

	print
	print
	print


"""


'user': {
	u'color_primary': u'33B6DA', 
	u'color_secondary': u'006C89', 
	u'display_name': u'Kevin P.',  ###
	u'screen_name': u'kevin', 
	u'privacy': False, 
	u'profile_image': u'https://si0.twimg.com/profile_images/147088134/twitter_profile_reasonably_small.jpg',  ###
	u'user_id': u'4e570489ccc2175fcd000000'
}



[
{
	"activity_id": "4e5d3ade32a7ba8fa200002c", 
	"created": "2011-08-30 19:32:46.550000", 
	"genre": "mention", 
	"stamp": {
		"blurb": "Thanks @UserB!", 
		"created": "2011-08-30 19:32:46.536000", 
		"entity": {
			"category": "music", 
			"entity_id": "4e5d3ade32a7ba8fa200002a", 
			"subcategory": "artist", 
			"subtitle": "Hubristic Rapper", 
			"title": "Kanye West"
		}, 
		"mentions": [{"indices": [7, 13], "screen_name": "UserB", "user_id": "4e5d3ade32a7ba8fa200001f"}], 
		"stamp_id": "4e5d3ade32a7ba8fa200002b", 
		"user": {"privacy": false, "screen_name": "UserA", "user_id": "4e5d3ade32a7ba8fa200001e"}
	}, 
	"user": {
		"privacy": false, "screen_name": "UserA", "user_id": "4e5d3ade32a7ba8fa200001e"
	}
}, 
{
	"activity_id": "4e5d3ade32a7ba8fa2000025", 
	"comment": {
		"blurb": "Glad you liked it!", "comment_id": "4e5d3ade32a7ba8fa2000024", "created": "2011-08-30 19:32:46.355000", "stamp_id": "4e5d3ade32a7ba8fa2000021", 
		"user": {
			"privacy": false, "screen_name": "UserA", "user_id": "4e5d3ade32a7ba8fa200001e"
		}
	}, 
	"created": "2011-08-30 19:32:46.361000", 
	"genre": "reply", 
	"stamp": {
		"blurb": "Best restaurant in America", "created": "2011-08-30 19:32:46.287000", 
		"entity": {
			"category": "music", "entity_id": "4e5d3ade32a7ba8fa2000020", "subcategory": "artist", "subtitle": "Hubristic Rapper", "title": "Kanye West"
		}, 
		"stamp_id": "4e5d3ade32a7ba8fa2000021", 
		"user": {"privacy": false, "screen_name": "UserA", "user_id": "4e5d3ade32a7ba8fa200001e"}
	}, 
	"user": {"privacy": false, "screen_name": "UserA", "user_id": "4e5d3ade32a7ba8fa200001e"}
}
]
"""
