from __future__ import absolute_import
import Globals
import utils
from MongoStampedAPI import MongoStampedAPI

api = MongoStampedAPI()

joey_id = '4f729e99b951fe20740007e1'

#Builds a guide side by side without factoring in the lottery randomness 
def generateSXS(user_id,section=None):
    
    coeffs = {
              'food' : 0,
              'music' : 1.0,
              'film' : .5,
              'book' : 10,
              'app' : 10,
              'stamp' : 5,
              'personal_stamp' : 0,
              'todo' : 4,
              'qual' : 2,
              'pop' : 3
              
              }
    control = api._buildUserGuide(user_id)
    experiment = api._testUserGuide(user_id, coeffs)
        
        
    if section is not None:
        control = getattr(control,section)
        experiment = getattr(experiment,section)
        
    print "%60s %60s\n" % ("Control", "Experiment")

    for i in range (0,40):
        c = str(control[i].entity_id)
        e = str(experiment[i].entity_id)
        print "%60s %60s" % (api._entityDB.getEntity(c).title, api._entityDB.getEntity(e).title)
        
        
        
    