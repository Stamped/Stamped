
import Globals
from crawler import EntitySinks
from db.mongodb.MongoEntity import MongoEntity

EntitySinks.registerSink("mongodb", MongoEntity)

