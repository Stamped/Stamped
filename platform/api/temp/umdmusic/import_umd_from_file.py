
import Globals
from api.MongoStampedAPI import globalMongoStampedAPI
from resolve.UMDSource import *
from resolve.StampedSource import StampedSource
import datetime
from sys import argv

api = globalMongoStampedAPI()
stampedSource = StampedSource(api)
with open(argv[1]) as fileIn:
    for line in fileIn:
        data = eval(line)
        proxy = UMDAlbum(data)
        api.mergeProxyIntoDb(proxy, stampedSource)
        
