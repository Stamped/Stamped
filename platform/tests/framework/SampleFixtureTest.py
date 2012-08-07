#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from tests.framework.FixtureTest import *
from tests.StampedTestUtils import *
import datetime
from libs.MongoCache import mongoCachedFn
from db.mongodb.MongoEntityCollection import MongoEntityCollection
from db.mongodb.MongoUserCollection import MongoUserCollection

@mongoCachedFn(memberFn=False)
def myCachedFn():
    return str(datetime.datetime.now() + datetime.timedelta(1))

def generate_john_doe():
    from api_old.Schemas import PersonEntity
    person = PersonEntity()
    person.schema_version = 12
    person.title = 'John Doe'
    person.timestamp.created = datetime.datetime.now()
    MongoEntityCollection().addEntity(person)

class SampleFixtureTestCase(AStampedTestCase):
    @fixtureTest()
    def test_api_caching_only(self):
        print "Result of myCachedFn() is", myCachedFn()

    ENTITY_STRING = '{"entities":[{"category": "food", "subtitle": "food", "subcategory": "restaurant", "title": "1550 Hyde Cafe", "titlel": "1550 hyde cafe", "coordinates": {"lat": 37.79530099999999, "lng": -122.418152}, "sources": {"sfmag": {}, "googlePlaces": {"gid": "3701ff773e73de24d78482896bfedd8c2f440698", "reference": "CoQBcQAAAAz4jPLR_OgUmZC0KRgDwdY0SrQcOKQMSorVCVI8DSihnhTqOpRzd4RFHXvAU4a3_GAQ_UU9SnV_41joDvS5k94k77Q1ClnBTz4KjpWWXnEpnL1ya9rsJL3KRSFVDJkjLnm5ZNl7GSIP6Lol_XCAUOwidg9Q7knapEBOQxDTBGmhEhDuer6ZRXAz5wRllga9GLZlGhSiHFHU45mOTFGZ7BkaYPELo5XaYQ"}}, "details": {"contact": {"phone": "(415) 931-3474"}, "place": {"address_components": [{"long_name": "1509", "short_name": "1509", "types": ["street_number"]}, {"long_name": "Hyde Street", "short_name": "Hyde Street", "types": ["route"]}, {"long_name": "San Francisco", "short_name": "San Francisco", "types": ["locality", "political"]}, {"long_name": "San Francisco", "short_name": "San Francisco", "types": ["administrative_area_level_2", "political"]}, {"long_name": "CA", "short_name": "CA", "types": ["administrative_area_level_1", "political"]}, {"long_name": "US", "short_name": "US", "types": ["country", "political"]}, {"long_name": "94109", "short_name": "94109", "types": ["postal_code"]}], "neighborhood": "Hyde Street, San Francisco", "address": "1550 Hyde St., San Francisco, CA"}}, "_id": {"$oid": "4e4c67f226f05a2ba9000002"}}]}'
    @fixtureTest(fixtureText=ENTITY_STRING)
    def test_db_fixture_string(self):
        # For this test, there is just hard-coded fixture text with no regenerate function, so we will always just get
        # this string.
        entityCollection = MongoEntityCollection()
        entity = entityCollection.getEntity("4e4c67f226f05a2ba9000002")
        print "The entity I got is:\n\n", entity, "\n\n"

    # Not a fixture tests, but coexists with them without a problem.
    def test_simple(self):
        print "Simple, non-fixture test"

    @fixtureTest(generateLocalDbFn=generate_john_doe)
    def test_db_fixture_gen_fn(self):
        entityResults = list(MongoEntityCollection()._collection.find({'title':'John Doe'}))
        self.assertEquals(1, len(entityResults))
        print "The entity I got back is:\n", entityResults[0]

    @fixtureTest(generateLocalDbQueries=[('entities', {'title':'They Might Be Giants'}),
                                         ('users', {'screen_name':'robby'})])
    def test_db_queries(self):
        allEntities = list(MongoEntityCollection()._collection.find())
        self.assertTrue(len(allEntities) >= 2)
        self.assertTrue(len(allEntities) < 10)
        self.assertTrue(all(entity['title'] == 'They Might Be Giants' for entity in allEntities))
        # Just to show that this doesn't fuck anything up for future runs of the test, other tests, etc.
        MongoEntityCollection()._collection._collection.drop()
        # It's empty now!
        self.assertEqual(len(list(MongoEntityCollection()._collection.find())), 0)

        allScreenNames = list(MongoUserCollection(None)._getAllScreenNames())
        self.assertEqual(len(allScreenNames), 1)
        self.assertEqual(allScreenNames[0], 'robby')
        user = MongoUserCollection(None).getUserByScreenName('robby')
        self.assertEqual(user.name, 'Robby Stein')

    @fixtureTest()
    def test_no_db_data(self):
        self.assertEqual(len(list(MongoEntityCollection()._collection.find())), 0)

if __name__ == '__main__':
    _verbose = True
    main()
