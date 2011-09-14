
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
        
        else:
            mongoExportImport(collection)
            print 'COMPLETE'

        print 


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

if __name__ == '__main__':  
    main()


