from __future__ import absolute_import
import Globals
import BeautifulSoup
import urllib2
from os.path import join
from sys import argv
from datetime import *

def wget(url, filename):
    with open('/tmp/historical_albums/%s.html' % filename, 'w') as fout:
        print >> fout, urllib2.urlopen(url).read()

current_date = date(1970, 12, 26)
one_week = timedelta(7)
errors = []

while current_date < date.today():
    date_string = current_date.strftime('%Y%m%d')
    next_url = 'http://umdmusic.com/default.asp?Lang=English&Chart=E&ChDate=%s&ChMode=N' % date_string
    print 'Fetching page:', next_url

    try:
        wget(next_url, date_string)
    except Exception as e:
        errors.append((date_string, e))
    print 'Success!'
    current_date += one_week

print 'Errors:'
print errors

