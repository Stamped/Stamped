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

def yesterday(date):
    return date - timedelta(days=1)

def weekAgo(date):
    return date - timedelta(days=6)
