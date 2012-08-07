
import pymongo, json, codecs, os, sys
from subprocess import Popen, PIPE

# base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.insert(0, base)

# import Globals
# from Schemas import *

OLD_HOST        = "ec2-50-17-124-56.compute-1.amazonaws.com"
NEW_HOST        = "ec2-50-17-36-190.compute-1.amazonaws.com"

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
        
        if collection == 'activity':
            mongoExportJSON('activityold')
            convertActivity()
            mongoImportJSON('activity')

            rmExportFile = "rm -rf /stamped/tmp/stamped/%s.json" % 'activity'
            rmImportFile = "rm -rf /stamped/tmp/stamped/%s.json" % 'activityold'
            cmd = "%s && %s" % (rmExportFile, rmImportFile)
            pp = Popen(cmd, shell=True, stdout=PIPE)
            pp.wait()

            print 'COMPLETE'
        
        elif collection == 'users':
            mongoExportJSON('users')
            convertUsers()
            mongoImportJSON('users')

            rmExportFile = "rm -rf /stamped/tmp/stamped/%s.json" % 'users'
            rmImportFile = "rm -rf /stamped/tmp/stamped/%s.json" % 'users'
            cmd = "%s && %s" % (rmExportFile, rmImportFile)
            pp = Popen(cmd, shell=True, stdout=PIPE)
            pp.wait()

            print 'COMPLETE'
        
        elif collection in ['stamps', 'comments']:
            mongoExportJSON(collection)
            convertUserData(collection)
            mongoImportJSON(collection)

            rmExportFile = "rm -rf /stamped/tmp/stamped/%s.json" % collection
            rmImportFile = "rm -rf /stamped/tmp/stamped/%s.json" % collection
            cmd = "%s && %s" % (rmExportFile, rmImportFile)
            pp = Popen(cmd, shell=True, stdout=PIPE)
            pp.wait()

            print 'COMPLETE'

        # elif collection in ['entities', 'places']:
        #     print 'SKIPPED'
        
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

def convertActivity():

    f = codecs.open('/stamped/tmp/stamped/activityold.json', 'rU', 'utf-8')
    o = codecs.open('/stamped/tmp/stamped/activity_out.json', 'w', 'utf-8')
    for line in f:
        data = json.loads(line)

        if 'link' in data:
            json.dump(data, o)
            o.write("\n")
        
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
            activity['link']['link_comment_id'] = data['comment']['comment_id']
            activity['link']['link_stamp_id'] = data['comment']['stamp_id']
        elif 'stamp' in data:
            activity['link'] = {}
            activity['link']['link_stamp_id'] = data['stamp']['stamp_id']
        elif 'user' in data:
            activity['link'] = {}
            activity['link']['link_user_id'] = data['user']['user_id']

        activity['user'] = {
            'user_id': data['user']['user_id']
        }

        activity['_id']         = data['_id']
        activity['genre']       = data['genre']
        activity['timestamp']   = data['timestamp']

        json.dump(activity, o)
        o.write("\n")

    f.close()
    o.close()

def convertUserData(collection):

    f = codecs.open('/stamped/tmp/stamped/%s.json' % collection, 'rU', 'utf-8')
    o = codecs.open('/stamped/tmp/stamped/%s_out.json' % collection, 'w', 'utf-8')
    for line in f:
        data = json.loads(line)
        
        del(data['user']['profile_image'])
        del(data['user']['display_name'])
        del(data['user']['screen_name'])
        del(data['user']['color_primary'])
        del(data['user']['color_secondary'])
        del(data['user']['privacy'])

        if collection == 'stamps':
            if 'credit' in data and len(data['credit']) > 0:
                for i in xrange(len(data['credit'])):
                    if 'display_name' in data['credit'][i]:
                        del(data['credit'][i]['profile_image'])
                        del(data['credit'][i]['display_name'])
                        del(data['credit'][i]['color_primary'])
                        del(data['credit'][i]['color_secondary'])
                        del(data['credit'][i]['privacy'])
            if 'mentions' in data and len(data['mentions']) > 0:
                for i in xrange(len(data['mentions'])):
                    if 'display_name' in data['mentions'][i]:
                        del(data['mentions'][i]['display_name'])
            if 'image' in data:
                del(data['image'])

        if collection == 'comments':
            if 'mentions' in data and len(data['mentions']) > 0:
                for i in xrange(len(data['mentions'])):
                    if 'display_name' in data['mentions'][i]:
                        del(data['mentions'][i]['display_name'])

        json.dump(data, o)
        o.write("\n")

    f.close()
    o.close()

def convertUsers():

    f = codecs.open('/stamped/tmp/stamped/users.json', 'rU', 'utf-8')
    o = codecs.open('/stamped/tmp/stamped/users_out.json', 'w', 'utf-8')
    for line in f:
        data = json.loads(line)

        num_stamps_left = 100
        if 'num_credits' in data['stats']:
            num_stamps_left = num_stamps_left + int(data['stats']['num_credits']) * 2
        if 'num_stamps' in data['stats']:
            num_stamps_left = num_stamps_left - int(data['stats']['num_stamps'])
        data['stats']['num_stamps_left'] = num_stamps_left
        
        data['name'] = '%s %s' % (data['first_name'], data['last_name'])
        data['screen_name_lower'] = (data['screen_name']).lower()
        del(data['profile_image'])
        del(data['display_name'])
        del(data['first_name'])
        del(data['last_name'])

        json.dump(data, o)
        o.write("\n")

    f.close()
    o.close()


if __name__ == '__main__':  
    main()


