#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from MongoStampedAPI import MongoStampedAPI
from HTTPSchemas import *
from Schemas import *
from pprint import pprint
from Entity import *

stampedAPI = MongoStampedAPI()

data = {
    "entity_id": "4eedb08b06007d0f1f00004f",
    "subcategory" : "book",
    "title" : "The Devil in the White City: Murder, Magic & Madness and the Fair that Changed America (Illinois)",
    "image" : "http://ecx.images-amazon.com/images/I/51BJMQK2YSL._SL160_.jpg",
    "popularity" : 2,
    "titlel" : "the devil in the white city: murder, magic & madness and the fair that changed america (illinois)",
    "sources" : {
        "amazon" : {
            "asin" : "0739303406",
            "amazon_link" : "http://www.amazon.com/Devil-White-City-Madness-Illinois/dp/0739303406/ref=pd_zg_rss_ts_b_2269_2"
        }
    },
    "details" : {
        "book" : {
            "author" : "Erik Larson"
        }
    }
}

entity = upgradeEntityData(data)

print entity