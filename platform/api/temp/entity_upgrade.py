#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from api.MongoStampedAPI import MongoStampedAPI
from api.HTTPSchemas import *
from api.Schemas import *
from pprint import pprint
from api.Entity import *

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

data = {
    "entity_id" : "4f3ec71d64c79428bb000014",
    "category" : "other",
    "subcategory" : "art_gallery",
    "title" : "RH Gallery",
    "titlel" : "rh gallery",
    "coordinates" : {
        "lat" : 40.71637,
        "lng" : -74.007706
    },
    "sources" : {
        "googlePlaces" : {
            "gid" : "d3f21d98ee61381fc290ae288892c55e56570a2e",
            "reference" : "CmRgAAAA06n-U04-LkzlutwfEaSBfJYKyArzEzm_7AFL9KU_alFdokBc1sPZSSewYvGqFWhS1tqbxef0GAQ9gwGTzs6ySFnt8dEHMcNX2cs0jeUt6-NjVw9g7CoxyOZbDscMLiSkEhD_Wh0-01sUPg5OGb2CPlXjGhQmlQU677u0o_jlDjzJSWvjKTthgw"
        }
    },
    "details" : {
        "contact" : {
            "site" : "http://www.rhgallery.com/",
            "phone_source" : "googleplaces",
            "phone" : "(646) 490-6355",
            "site_source" : "googleplaces",
        },
        "place" : {
            "neighborhood" : "137 Duane Street, New York",
            "address_region" : "NY",
            "address_locality" : "New York",
            "address" : "137 Duane Street, New York, NY 10013, United States",
            "address_components" : [
                {
                    "long_name" : "New York",
                    "types" : [
                        "locality",
                        "political"
                    ],
                    "short_name" : "New York"
                },
                {
                    "long_name" : "NY",
                    "types" : [
                        "administrative_area_level_1",
                        "political"
                    ],
                    "short_name" : "NY"
                },
                {
                    "long_name" : "US",
                    "types" : [
                        "country",
                        "political"
                    ],
                    "short_name" : "US"
                },
                {
                    "long_name" : "10013",
                    "types" : [
                        "postal_code"
                    ],
                    "short_name" : "10013"
                }
            ],
            "address_postcode" : "10013",
            "address_country" : "US",
            "address_source" : "googleplaces"
        }
    },
    "mangled_title" : "rh gallery",
    "mangled_title_source" : "format"
}


entity = upgradeEntityData(data)

print entity