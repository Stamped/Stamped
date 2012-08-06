from __future__ import absolute_import

import pymongo, json, codecs, os, sys, bson
from subprocess import Popen, PIPE

OLD_HOST        = "ec2-107-20-48-197.compute-1.amazonaws.com"
NEW_HOST        = "ec2-174-129-76-168.compute-1.amazonaws.com"

old_connection  = pymongo.Connection(OLD_HOST, 27017)
new_connection  = pymongo.Connection(NEW_HOST, 27017)

old_database    = old_connection['stamped']
new_database    = new_connection['stamped']

collections     = old_database.collection_names()

if not os.path.isdir('/stamped/tmp/stamped/'):
   os.makedirs('/stamped/tmp/stamped')

def main():
    for collection in collections:
        print 'RUN %s' % collection

        if collection == 'tempentities':
            print 'PASS'
        
        else:
            mongoExportImport(collection)
            print 'COMPLETE'

        print 

    convertUsers()
    convertActivity()


def mongoExportImport(collection):

    cmdExport = "mongodump --db stamped --collection %s --host %s --out /stamped/tmp" % \
                (collection, OLD_HOST)
    cmdImport = "mongorestore --db stamped --collection %s --host %s /stamped/tmp/stamped/%s.bson" % \
                (collection, NEW_HOST, collection)

    out = open("/stamped/tmp/convert_%s.log" % collection, "w")
    cmd = "%s && %s && rm -rf /stamped/tmp/stamped/%s.bson" % \
            (cmdExport, cmdImport, collection)
    pp  = Popen(cmd, shell=True, stdout=out, stderr=out)
    pp.wait()

def mongoExportJSON(collection):
    collection = collection.lower()
    cmdExport = "mongoexport --db stamped --collection %s --host %s --out /stamped/tmp/stamped/%s.json" % \
                (collection, OLD_HOST, collection)
    pp = Popen(cmdExport, shell=True, stdout=PIPE)
    pp.wait()

def mongoImportJSON(collection):
    collection = collection.lower()
    cmdImport = "mongoimport --db stamped --collection %s --host %s /stamped/tmp/stamped/%s_out.json" % \
                (collection, NEW_HOST, collection)
    pp = Popen(cmdImport, shell=True, stdout=PIPE)
    pp.wait()


def convertUsers():
    user_collection = new_database['users']
    users = user_collection.find()

    for user in users:

        if 'name_lower' not in user:
            name = user['name'].lower()
            user_collection.update(
                {'_id': user['_id']},
                {'$set': {'name_lower': name}}
            )

        if 'image_cache' not in user['timestamp']:
            user_collection.update(
                {'_id': user['_id']},
                {'$set': {'timestamp.image_cache': user['timestamp']['created']}}
            )


def convertActivity():
    activity_collection = new_database['activity']
    user_activity_collection = new_database['useractivity']

    user_activity = user_activity_collection.find()

    for user in user_activity:        
        if len(user['_id']) < 24:
            continue

        for activityId in user['ref_ids']:
            item = activity_collection.find_one({'_id': bson.objectid.ObjectId(activityId)})
            
            if item:
                del(item['_id'])
                item['recipient_id'] = user['_id']

                if 'link' in item and 'linked_friend_id' in item['link']:
                    del(item['link']['linked_friend_id'])

                activity_collection.insert(item)


    new_database['activity'].remove({'recipient_id': {'$exists': False}})

if __name__ == '__main__':  
    main()

