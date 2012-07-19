
from collections import namedtuple
from sys import argv
from xml.parsers.expat import *

NetflixItem = namedtuple('NetflixItem', ['id', 'rating', 'title'])

class ParserHandlers(object):
    def __init__(self):
        self.parsed_items = []

    def handleCharacterData(self, data):
        self.__data = data

    def handleStartElement(self, name, attr):
        if name == 'title':
            self.__title = attr['regular']

    def handleEndElement(self, name):
        if name == 'id':
            self.__id = self.__data
            del self.__data
        if name == 'average_rating':
            self.__rating = float(self.__data)
            del self.__data
        if name == 'catalog_title':
            item = NetflixItem(self.__id, self.__rating, self.__title)
            del self.__id
            del self.__title
            self.__rating = 0
            if item.rating >= 3.7:
                print item


handler = ParserHandlers()
parser = ParserCreate()
parser.StartElementHandler = handler.handleStartElement
parser.EndElementHandler = handler.handleEndElement
parser.CharacterDataHandler = handler.handleCharacterData

with open(argv[1]) as fin:
    parser.ParseFile(fin)
