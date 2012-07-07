import Globals
from datetime import datetime,timedelta

def v1_init():
    return datetime(2011,11,21)

def now():
    return datetime.utcnow()

def est():
    return datetime.utcnow() - timedelta(hours=4)

def today():
    now = datetime.utcnow()
    if now.hour > 3:
        diff = timedelta(days=0,hours=now.hour-4,minutes=now.minute,seconds=now.second,microseconds=now.microsecond)
    else:
        diff = timedelta(days=0,hours= 20+now.hour,minutes=now.minute,seconds=now.second,microseconds=now.microsecond)
    return now - diff

def dayAgo(date):
    return date - timedelta(days=1)

def weekAgo(date):
    return date - timedelta(days=6)

def monthAgo(date):
    if date.month > 1:
        monthAgo = datetime(date.year, date.month - 1, date.day,date.hour,date.minute,date.second,date.microsecond)
    else:
        monthAgo = datetime(date.year - 1, 12,date.day,date.hour,date.minute,date.second,date.microsecond)
    return monthAgo