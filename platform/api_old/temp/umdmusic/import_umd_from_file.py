
import Globals
from api_old.MongoStampedAPI import globalMongoStampedAPI
from resolve.UMDSource import *
from resolve.StampedSource import StampedSource
import datetime
from sys import argv

api = globalMongoStampedAPI()
stampedSource = StampedSource(api)
if len(argv) != 3 or argv[1] not in ('track', 'album'):
    raise Exception('Usage:  import_umd_from_file.py <track or album> <filename>')
umdClass = UMDTrack if argv[1]=='track' else UMDAlbum
with open(argv[2]) as fileIn:
    for line in fileIn:
        data = eval(line)
        proxy = umdClass(data)
        api.mergeProxyIntoDb(proxy, stampedSource)
