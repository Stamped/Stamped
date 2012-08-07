from BeautifulSoup import BeautifulSoup
from sys import argv
from datetime import *
import os

with open(argv[1]) as fin:
    content = fin.read()

filebase = os.path.basename(argv[1])[:-5]
popular_date = datetime.strptime(filebase, '%Y%m%d')

rank = 1
soup = BeautifulSoup(content)
table_rows = soup.findAll('tr')
for row in table_rows:
    if row.td.text == 'ThisWeek':
        nextSiblings = row.nextSiblingGenerator()
        for trash, song_row in zip(nextSiblings, nextSiblings):
            if song_row:
                song_info = list(song_row.findAll('td'))[2]
                song_name = song_info.b.text
                artist = song_info.b.next.next.next
                data = {
                        'rank' : rank,
                        'name' : song_name,
                        'artist' : artist,
                        'last_popular' : popular_date,
                        }
                print repr(data)
                rank += 1
