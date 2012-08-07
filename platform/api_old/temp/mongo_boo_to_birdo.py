
import pymongo, json, codecs, os, sys
from subprocess import Popen, PIPE

OLD_HOST        = "ec2-107-20-88-11.compute-1.amazonaws.com"
NEW_HOST        = "ec2-107-20-48-197.compute-1.amazonaws.com"

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

    convertActivity()
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

def convertActivity():
    activity_collection = new_database['activity']
    activity = activity_collection.find()

    for item in activity:

        if 'link_stamp_id' in item['link']:
            activity_collection.update(
                {'_id': item['_id']},
                {
                    '$set': {'link.linked_stamp_id': item['link']['link_stamp_id']},
                    '$unset': {'link.link_stamp_id': 1}
                }
            )

        if 'link_user_id' in item['link']:
            activity_collection.update(
                {'_id': item['_id']},
                {
                    '$set': {'link.linked_user_id': item['link']['link_user_id']},
                    '$unset': {'link.link_user_id': 1}
                }
            )

        if 'link_entity_id' in item['link']:
            activity_collection.update(
                {'_id': item['_id']},
                {
                    '$set': {'link.linked_entity_id': item['link']['link_entity_id']},
                    '$unset': {'link.link_entity_id': 1}
                }
            )

        if 'link_comment_id' in item['link']:
            activity_collection.update(
                {'_id': item['_id']},
                {
                    '$set': {'link.linked_comment_id': item['link']['link_comment_id']},
                    '$unset': {'link.link_comment_id': 1}
                }
            )

        if 'link_url' in item['link']:
            activity_collection.update(
                {'_id': item['_id']},
                {
                    '$set': {'link.linked_url': item['link']['link_url']},
                    '$unset': {'link.link_url': 1}
                }
            )

        if item['genre'] == 'restamp':
            activity_collection.update(
                {'_id': item['_id']},
                {'$set': {'benefit': 2}}
            )

def convertStamps():
    stamp_collection = new_database['stamps']
    stamps = stamp_collection.find()

    for stamp in stamps:

        if 'modified' not in stamp['timestamp']:
            stamp_collection.update(
                {'_id': stamp['_id']},
                {'$set': {'timestamp.modified': stamp['timestamp']['created']}}
            )

if __name__ == '__main__':  
    main()


