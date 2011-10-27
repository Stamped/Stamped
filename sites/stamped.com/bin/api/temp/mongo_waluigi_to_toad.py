
import pymongo, json, codecs, os, sys, bson, unicodedata
from subprocess import Popen, PIPE

OLD_HOST        = "ec2-184-73-40-130.compute-1.amazonaws.com"
NEW_HOST        = "ec2-107-22-0-49.compute-1.amazonaws.com"

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
    # entities = entity_collection.find({'sources.apple.export_date': '1311152428052'})
    entities = entity_collection.find({'details.media.track_length': {'$exists': True}})

    for entity in entities:

        if 'details' in entity and 'media' in entity['details'] and 'track_length' in entity['details']['media']:
            track_length = entity['details']['media']['track_length']
            if track_length:
                try:
                    new = int(float(track_length))
                    if 'sources' in entity and 'apple' in entity['sources'] and 'export_date' in entity['sources']['apple']:
                        new = int(round(int(float(track_length)) / 1000.0))
                    
                    entity_collection.update(
                        {'_id': entity['_id']},
                        {'$set': {'details.media.track_length': new}}
                    )
                    print '%60s (%s -> %s)' % (entity['title'], track_length, new)
                except Exception as e:
                    print 'SKIPPED: %s (%s)' % (entity['title'], e)

if __name__ == '__main__':  
    main()

