#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals

import math
from datetime import datetime,timedelta


"""
Time Functions 
"""

# Returns the date corresponding to v1 launch
def v1_init():
    return datetime(2011, 11, 21)

# Returns the date corresponding to v2 launch
def v2_init():
    return datetime(2012, 07, 26)

# Returns current time in UTC - use for all statistics calculations since all mongo and simpledb logs store timestamps in UTC)
def now():
    return datetime.utcnow()

# Returns current time in EST - USE FOR DISPLAY PURPOSES ONLY: Stats calculated up until est() will be missing data from the past couple of hours
def est():
    return datetime.today()

#  Returns 12:00 am eastern time for a given date/time, represented in UTC for statistics purposes
def estMidnight(date=None):
    if date is None:
        date = datetime.utcnow()
    
    offset = datetime.utcnow().hour - datetime.today().hour
    
    if date.hour >= offset:
        diff = timedelta(hours=(date.hour - offset), minutes=date.minute, seconds=date.second, microseconds=date.microsecond)
    else:
        diff = timedelta(hours=(24 - offset + date.hour), minutes=date.minute, seconds=date.second, microseconds=date.microsecond)
        
    return date - diff

#Exactly one full day prior to a given date
def dayBefore(date):
    return date - timedelta(days=1)

#Exactly one full week prior to a given date
def weekBefore(date):
    return date - timedelta(days=6)

#Exactly one full month prior to a given date
def monthBefore(date):
    if date.month > 1:
        try:
            monthAgo = datetime(date.year, date.month-1, date.day, date.hour, date.minute, date.second, date.microsecond)
        except ValueError: # Day out of range for previous month - default to first day of current month
            monthAgo = datetime(date.year, date.month, 1, date.hour, date.minute, date.second, date.microsecond) 
    else:
        monthAgo = datetime(date.year-1, 12, date.day, date.hour, date.minute, date.second, date.microsecond)
    return monthAgo

#Exactly one full month past a given date
def monthPast(date):
    if date.month < 12:
        try:
            monthPast = datetime(date.year, date.month+1, date.day, date.hour, date.minute, date.second, date.microsecond)
        except ValueError:
            monthPast = datetime(date.year, date.month+2, 1, date.hour, date.minute, date.second, date.microsecond)
    else:
        monthPast = datetime(date.year+1, 1, date.day, date.hour, date.minute, date.second, date.microsecond)
    return monthPast

#Increments to the first day of the next month
def incrMonth(date):
    if date.month == 12:
        incrMonth = datetime(date.year +1, 1, 1)
    else:
        incrMonth = datetime(date.year, date.month+1, 1)
    return incrMonth


"""
Math Functions 
"""

def percentile(numList,p):
    #Assumes numList is sorted
    k = (len(numList)-1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return numList[int(k)]
    d0 = numList[int(f)] * (c-k)
    d1 = numList[int(c)] * (k-f)
    return d0+d1
