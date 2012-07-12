import Globals
from datetime import datetime,timedelta

#Returns the date corresponding to v1 launch
def v1_init():
    return datetime(2011,11,21)

#Returns current time in UTC
def now():
    return datetime.utcnow()

#Returns current time in EST
def est():
    return datetime.utcnow() - timedelta(hours=4)

#Returns the beginning of a day (midnight) according to EST
def today():
    now = datetime.utcnow()
    if now.hour > 3:
        diff = timedelta(days=0,hours=now.hour-4,minutes=now.minute,seconds=now.second,microseconds=now.microsecond)
    else:
        diff = timedelta(days=0,hours= 20+now.hour,minutes=now.minute,seconds=now.second,microseconds=now.microsecond)
    return now - diff

#Exactly one full day prior to a given date
def dayAgo(date):
    return date - timedelta(days=1)

#Exactly one full week prior to a given date
def weekAgo(date):
    return date - timedelta(days=6)

#Exactly one full month prior to a given date
def monthAgo(date):
    if date.month > 1:
        monthAgo = datetime(date.year, date.month - 1, date.day,date.hour,date.minute,date.second,date.microsecond)
    else:
        monthAgo = datetime(date.year - 1, 12,date.day,date.hour,date.minute,date.second,date.microsecond)
    return monthAgo

def monthPast(date):
    if date.month < 12:
        monthPast = datetime(date.year, date.month + 1, date.day,date.hour,date.minute,date.second,date.microsecond)
    else:
        monthPast = datetime(date.year + 1, 1,date.day,date.hour,date.minute,date.second,date.microsecond)
    return monthPast

#Increments to the beginning of the next month
def incrMonth(date):
    if date.month == 12:
        incrMonth = datetime(date.year +1, 1,1)
    else:
        incrMonth = datetime(date.year,date.month+1,1)
    return incrMonth