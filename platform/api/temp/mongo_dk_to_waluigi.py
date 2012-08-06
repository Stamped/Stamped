from __future__ import absolute_import

import pymongo, json, codecs, os, sys, bson, unicodedata
from subprocess import Popen, PIPE

OLD_HOST        = "ec2-174-129-76-168.compute-1.amazonaws.com"
NEW_HOST        = "ec2-184-73-40-130.compute-1.amazonaws.com"

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

        if collection == 'logs':
            print 'PASS'
        
        else:
            mongoExportImport(collection)
            print 'COMPLETE'

        print 

    convertEntities()
    updateUserFavEntities()
    updateUsers()


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
    entity_collection = new_database['entities']
    entities = entity_collection.find()

    for entity in entities:

        if 'titlel' in entity:
            titlel = entity['titlel']
            new = unicodedata.normalize('NFKD', unicode(titlel)).encode('ascii', 'ignore')

            if titlel != new:
                entity_collection.update(
                    {'_id': entity['_id']},
                    {'$set': {'titlel': new}}
                )
                print 'OLD: %30s     NEW: %s' % (titlel, new)
        else:
            print '-' * 40
            print 'SKIPPED: %s (%s)' % (entity['_id'], entity['title'])    
            print '-' * 40

def updateUserFavEntities():
    user_collection = new_database['users']
    fav_collection = new_database['favorites']
    userfav_collection = new_database['userfaventities']
    users = user_collection.find()
    for user in users:
        userfavorites = fav_collection.find({'user_id': str(user['_id'])})
        favs = []
        for v in userfavorites:
            favs.append(str(v['_id']))
        userfav_collection.update(
            {'_id': str(user['_id'])},
            {'$set': {'ref_ids': favs}}
        )

def updateUsers():
    user_collection = new_database['users']
    users = user_collection.find()

    for user in users:
        user_collection.update(
        {'_id': user['_id']},
        {'$set': {  
            "alerts" : { 
                "ios_alert_comment" : True, 
                "ios_alert_follow" : True, 
                "ios_alert_reply" : True, 
                "ios_alert_fav" : True, 
                "ios_alert_credit" : True, 
                "ios_alert_mention" : True, 
                "ios_alert_like" : True, 
                "email_alert_credit" : False, 
                "email_alert_reply" : False, 
                "email_alert_like" : False, 
                "email_alert_comment" : False, 
                "email_alert_mention" : False, 
                "email_alert_follow" : False, 
                "email_alert_fav" : False 
            }
        }})

## TODO:
# Update notification settings

if __name__ == '__main__':  
    main()

