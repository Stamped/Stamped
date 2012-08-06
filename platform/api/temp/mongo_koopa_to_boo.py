from __future__ import absolute_import

import pymongo, json, codecs, os, sys
from subprocess import Popen, PIPE

OLD_HOST        = "ec2-50-17-36-190.compute-1.amazonaws.com"
NEW_HOST        = "ec2-107-20-88-11.compute-1.amazonaws.com"

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

        if collection == 'entities':
            mongoExportImport(collection)
            convertEntities()
            print 'COMPLETE'

        elif collection == 'tempentities':
            print 'PASS'
        
        else:
            mongoExportImport(collection)
            print 'COMPLETE'

        print 

    convertStamps()


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

def convertEntities():
    collection = new_database['entities']
    entities = collection.find({'sources.userGenerated.user_id': {'$exists': True}})

    for entity in entities:
        collection.update(
            {'_id': entity['_id']}, 
            {
                '$set': {
                    'sources.userGenerated.generated_by': entity['sources']['userGenerated']['user_id'],
                },
                '$unset': {
                    'sources.userGenerated.user_id': 1
                }
            })

def convertStamps():
    stamp_collection = new_database['stamps']
    user_collection = new_database['users']
    users = user_collection.find()

    for user in users:

        stamps = stamp_collection.find({'user.user_id': str(user['_id'])}).sort('_id', pymongo.ASCENDING)
        count = 0
        for stamp in stamps:
            count += 1
            stamp_collection.update(
                {'_id': stamp['_id']},
                {'$set': {'stats.stamp_num': count}}
            )

        user_collection.update(
            {'_id': user['_id']},
            {'$set': {'stats.num_stamps_total': count}}
        )
        if 'color_primary' in user:
            user_collection.update(
                {'_id': user['_id']},
                {'$set': {'color_primary': user['color_primary'].upper()}}
            )
        if 'color_secondary' in user:
            user_collection.update(
                {'_id': user['_id']},
                {'$set': {'color_secondary': user['color_secondary'].upper()}}
            )
        if user['screen_name_lower'] == 'ed':
            user_collection.update(
                {'_id': user['_id']},
                {'$set': {'screen_name_lower': 'edmuki'}}
            )
            user_collection.update(
                {'_id': user['_id']},
                {'$set': {'screen_name': 'edmuki'}}
            )
                

if __name__ == '__main__':  
    main()


