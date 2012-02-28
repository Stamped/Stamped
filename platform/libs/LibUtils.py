#!/usr/bin/python

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

__all__ = [ 'states', 'months', 'parseDateString' ]

import Globals
from logs import log, report

try:
    import re
except:
    report()
    raise

states = {
    "Alabama":"AL",
    "Alaska":"AK",
    "American Samoa":"AS",
    "Arizona":"AZ",
    "Arkansas":"AR",
    "Armed Forces Europe":"AE",
    "Armed Forces Pacific":"AP",
    "Armed Forces the Americas":"AA",
    "California":"CA",
    "Colorado":"CO",
    "Connecticut":"CT",
    "Delaware":"DE",
    "District of Columbia":"DC",
    "Federated States of Micronesia":"FM",
    "Florida":"FL",
    "Georgia":"GA",
    "Guam":"GU",
    "Hawaii":"HI",
    "Idaho":"ID",
    "Illinois":"IL",
    "Indiana":"IN",
    "Iowa":"IA",
    "Kansas":"KS",
    "Kentucky":"KY",
    "Louisiana":"LA",
    "Maine":"ME",
    "Marshall Islands":"MH",
    "Maryland":"MD",
    "Massachusetts":"MA",
    "Michigan":"MI",
    "Minnesota":"MN",
    "Mississippi":"MS",
    "Missouri":"MO",
    "Montana":"MT",
    "Nebraska":"NE",
    "Nevada":"NV",
    "New Hampshire":"NH",
    "New Jersey":"NJ",
    "New Mexico":"NM",
    "New York":"NY",
    "North Carolina":"NC",
    "North Dakota":"ND",
    "Northern Mariana Islands":"MP",
    "Ohio":"OH",
    "Oklahoma":"OK",
    "Oregon":"OR",
    "Pennsylvania":"PA",
    "Puerto Rico":"PR",
    "Rhode Island":"RI",
    "South Carolina":"SC",
    "South Dakota":"SD",
    "Tennessee":"TN",
    "Texas":"TX",
    "Utah":"UT",
    "Vermont":"VT",
    "Virgin Islands, U.S.":"VI",
    "Virginia":"VA",
    "Washington":"WA",
    "West Virginia":"WV",
    "Wisconsin":"WI",
    "Wyoming":"WY"
}

months = {
    'January':1,
    'February':2,
    'March':3,
    'April':4,
    'May':5,
    'June':6,
    'July':7,
    'August':8,
    'September':9,
    'October':10,
    'November':11,
    'December':12,
}

def parseDateString(date):
    if date is not None:
        new_date = None
        match = re.match(r'^(\d\d\d\d) (\d\d) (\d\d)$',date)
        if match is not None:
            try:
                return datetime(int(match.group(1)),int(match.group(2)),int(match.group(3)))
            except ValueError:
                pass
            except TypeError:
                pass
        match = re.match(r'^(\w+) (\d+), (\d\d\d\d)$',date)
        if match is not None:
            try:
                month = match.group(1)
                if month in months:
                    return datetime(int(match.group(3)),months[month],int(match.group(2)))
            except ValueError:
                pass
            except TypeError:
                pass
        #sample 2012-02-10
        match = re.match(r'^(\d\d\d\d)-(\d\d)-(\d\d)$',date)
        if match is not None:
            try:
                return datetime(int(match.group(1)),int(match.group(2)),int(match.group(3)))
            except ValueError:
                pass
            except TypeError:
                pass
        #sample 2009-05-29T07:00:00Z
        match = re.match(r'^(\d\d\d\d)-(\d\d)-(\d\d)\w+\d\d:\d\d:\d\d\w+$',date)
        if match is not None:
            try:
                return datetime(int(match.group(1)),int(match.group(2)),int(match.group(3)))
            except ValueError:
                pass
            except TypeError:
                pass
    return None