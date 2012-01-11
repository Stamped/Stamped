
import Globals
from crawler import EntitySinks
from db.mongodb.MongoEntityCollection import MongoEntityCollection

EntitySinks.registerSink("mongodb", MongoEntityCollection)

