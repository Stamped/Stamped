#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
from crawler.sources.dumps import CSVUtils, FactualUtils
import os, time

from gevent.pool import Pool
from crawler.AEntitySource import AExternalDumpEntitySource
from Schemas import Entity

__all__ = [ "FactualUSRestaurantsDump" ]

class FactualUSRestaurantsDump(AExternalDumpEntitySource):
    """
        Factual US Restaurants importer
    """
    
    DUMP_FILE_PREFIX      = os.path.dirname(os.path.abspath(__file__)) + "/data/factual/"
    DUMP_FILE_NAME        = "US_Restaurants_V2"
    DUMP_FILE_SUFFIX      = ".csv"
    DUMP_FILE_TEST_SUFFIX = ".test"
    DUMP_FILE = DUMP_FILE_PREFIX + DUMP_FILE_NAME + DUMP_FILE_SUFFIX
    DUMP_FILE_TEST = DUMP_FILE_PREFIX + DUMP_FILE_NAME + DUMP_FILE_TEST_SUFFIX + DUMP_FILE_SUFFIX
    
    NAME = "Factual US Restaurants"
    TYPES = set([ 'restaurant' ])
    
    _map = {
        'Factual ID' : 'faid', 
        'name' : 'title', 
        'tel' : 'phone', 
        'fax' : 'fax', 
        'website' : 'site', 
        'email' : 'email', 
        'latitude' : 'lat', 
        'longitude' : 'lng', 
        'parking' : 'parking', 
        'link_to_menu' : 'menuLink', 
        'alcohol' : 'alcohol', 
        #'breakfast' : None, 
        #'lunch' : None, 
        #'dinner' : None, 
        #'good_for_kids' : 'lng', 
        #'childrens_menu' : 'lng', 
        'takeout' : 'takeout', 
        'delivery' : 'delivery', 
        'kosher' : 'kosher', 
        #'halal' : None, 
        #'vegan_or_vegetarian' : None, 
        #'gluten_free_options' : None, 
        #'healthy_options' : None, 
        #'low_fat_options' : None, 
        #'low_salt_options' : None, 
        #'organic_options' : None, 
        'wheelchair_access' : 'wheelchairAccess', 
        'hours' : 'hoursOfOperation', 
        #'open_24_hours' : None, 
        'price' : 'price', 
        #'link_to_image' : 'lng', 
        'chef' : 'chef', 
        'owner' : 'owner', 
        #'founded' : 'founded', 
        'reservations' : 'acceptsReservations', 
        #'cash_only' : 'lng', 
        'catering' : 'catering', 
        'private_room' : 'privatePartyFacilities', 
        'bar' : 'bar', 
        'link_to_reviews' : 'reviewLinks', 
        #'category' : None, 
    }
    
    def __init__(self):
        AExternalDumpEntitySource.__init__(self, self.NAME, self.TYPES, 512)
        
        if Globals.options.test:
            self._dumpFile = self.DUMP_FILE_TEST
        else:
            self._dumpFile = self.DUMP_FILE
    
    def getMaxNumEntities(self):
        csvFile  = open(self._dumpFile, 'rb')
        numLines = max(0, utils.getNumLines(csvFile) - 1)
        csvFile.close()
        
        return numLines
    
    def _run(self):
        csvFile  = open(self._dumpFile, 'rb')
        numLines = max(0, utils.getNumLines(csvFile) - 1)
        if Globals.options.limit:
            numLines = max(0, min(Globals.options.limit, numLines - Globals.options.offset))
        
        utils.log("[%s] parsing %d entities from '%s'" % \
            (self.NAME, numLines, self.DUMP_FILE_NAME))
        
        reader = CSVUtils.UnicodeReader(csvFile)
        pool   = Pool(512)
        count  = 0
        offset = 0
        self.numCollapsed = 0
        
        for row in reader:
            if offset < Globals.options.offset:
                offset += 1
                continue
            
            if Globals.options.limit and count >= Globals.options.limit:
                break
            
            pool.spawn(self._parseEntity, row, count)
            count += 1
            
            if numLines > 100 and (count % (numLines / 100)) == 0:
                utils.log("[%s] done parsing %s" % \
                    (self.NAME, utils.getStatusStr(count, numLines)))
                time.sleep(0.1)
        
        Globals.options.offset = 0
        if Globals.options.limit:
            Globals.options.limit = max(0, Globals.options.limit - count)
        
        pool.join()
        self._output.put(StopIteration)
        csvFile.close()
        
        utils.log("[%s] finished parsing %d entities (%d collapsed)" % (self.NAME, count, self.numCollapsed))
        #for name in self.seen:
        #    num = self.seen[name]
        #    if num > 5:
        #        print "%s) %d" % (name, num)
        #import sys
        #sys.exit(1)
    
    def _parseEntity(self, row, count):
        #utils.log("[%s] parsing entity %d" % (self, count))
        
        name = row['name'].lower().strip()
        collapsed = False
        
        if name in to_collapse:
            if to_collapse[name]:
                self.numCollapsed += 1
                return
            
            to_collapse[name] = True
            collapsed = True
        
        # record how many times we've encountered each restaurant
        #if not hasattr(self, 'seen'):
        #    self.seen = {}
        #if name in self.seen:
        #    self.seen[name] += 1
        #else:
        #    self.seen[name] = 1
        
        entity = Entity()
        entity.subcategory = "restaurant"
        entity.factual = {
            'table' : 'US_Restaurants_V2.csv'
        }
        
        if not collapsed:
            address = FactualUtils.parseAddress(row)
            if address is not None:
                entity.address = address
        
        for srcKey, destKey in self._map.iteritems():
            if srcKey in row and row[srcKey]:
                entity[destKey] = row[srcKey]
        
        self._output.put(entity)

from crawler import EntitySources
EntitySources.registerSource('factualUSRestaurants', FactualUSRestaurantsDump)

to_collapse = {
    "fuddruckers" : False, 
    "d'angelo grilled sandwiches" : False, 
    "pizza factory" : False, 
    "mexico lindo" : False, 
    "penn station east coast subs" : False, 
    "dennys" : False, 
    "au bon pain" : False, 
    "whataburger restaurants" : False, 
    "larry's giant subs" : False, 
    "firehouse sub" : False, 
    "huddle house" : False, 
    "lenny's sub shop" : False, 
    "crown fried chicken" : False, 
    "magic wok" : False, 
    "ils wayport" : False, 
    "charley's grilled subs" : False, 
    "china king buffet" : False, 
    "hungry howies pizza" : False, 
    "carvel" : False, 
    "perkins restaurant and bakery" : False, 
    "panera bread" : False, 
    "cousins subs" : False, 
    "steak 'n ale" : False, 
    "friendly's" : False, 
    "mcdonald's" : False, 
    "caribou coffee company" : False, 
    "krispy kreme" : False, 
    "monical's pizza" : False, 
    "maid-rite" : False, 
    "jersey mike's subs" : False, 
    "american deli" : False, 
    "pollo tropical" : False, 
    "orange julius" : False, 
    "rally's hamburgers" : False, 
    "joe's pizza" : False, 
    "pizza time" : False, 
    "bruster's real ice cream" : False, 
    "chili's" : False, 
    "shanghai restaurant" : False, 
    "chopsticks" : False, 
    "noodles & company" : False, 
    "tony roma's" : False, 
    "peet's coffee and tea" : False, 
    "china city" : False, 
    "taste of india" : False, 
    "la mexicana" : False, 
    "chuck e cheese's" : False, 
    "hometown buffet" : False, 
    "johnny rockets" : False, 
    "five guys burgers & fries" : False, 
    "taco casa" : False, 
    "camille's sidewalk cafe" : False, 
    "simple simon's pizza" : False, 
    "primo pizza" : False, 
    "mr goodcents subs and pastas" : False, 
    "bennigan\xe2s" : False, # note, this is an extended ascii apostrophe
    "mr gatti's" : False, 
    "mazzio's pizza" : False, 
    "hong kong kitchen" : False, 
    "lone star steakhouse and saloon" : False, 
    "krystal" : False, 
    "straw hat pizza" : False, 
    "tonys pizza" : False, 
    "grand buffet" : False, 
    "peking restaurant" : False, 
    "rallys hamburgers" : False, 
    "rosati's pizza" : False, 
    "china king restaurant" : False, 
    "jimmy's pizza" : False, 
    "taco loco" : False, 
    "sarku japan" : False, 
    "cosi" : False, 
    "in-n-out burger" : False, 
    "joe's crab shack" : False, 
    "angelo's pizza" : False, 
    "skyline chili" : False, 
    "cafe" : False, 
    "taqueria jalisco" : False, 
    "cottage inn pizza" : False, 
    "lunch box" : False, 
    "sonic drive-in" : False, 
    "golden corral" : False, 
    "subway" : False, 
    "grandy's" : False, 
    "church's fried chicken" : False, 
    "panda chinese restaurant" : False, 
    "peter piper pizza" : False, 
    "dunn bros coffee" : False, 
    "panda express" : False, 
    "manchu wok" : False, 
    "wing zone" : False, 
    "alberto's mexican food" : False, 
    "peking chinese restaurant" : False, 
    "chick-fil-a" : False, 
    "buca di beppo" : False, 
    "bojangles' famous chicken 'n biscuits" : False, 
    "captain d's seafood restaurants" : False, 
    "mazatlan mexican restaurant" : False, 
    "grill depot" : False, 
    "cheesecake factory" : False, 
    "roma pizza" : False, 
    "taco mayo" : False, 
    "qdoba mexican grill" : False, 
    "qdoba" : False, 
    "ponderosa steak house" : False, 
    "thai house" : False, 
    "fatburger" : False, 
    "applebee's" : False, 
    "luby's" : False, 
    "coffee bean and tea leaf" : False, 
    "olive garden" : False, 
    "sweet tomatoes" : False, 
    "bellacino's pizza and grinders" : False, 
    "new york fried chicken" : False, 
    "snappy tomato pizza" : False, 
    "china wok" : False, 
    "l&l hawaiian barbecue" : False, 
    "hunan chinese restaurant" : False, 
    "rally's" : False, 
    "pizza express" : False, 
    "first wok" : False, 
    "old chicago" : False, 
    "wendy's" : False, 
    "baja fresh" : False, 
    "ryan's family steak house" : False, 
    "togo's" : False, 
    "carrows" : False, 
    "grill" : False, 
    "erbert & gerbert's" : False, 
    "brown's chicken & pasta" : False, 
    "sunshine cafe" : False, 
    "which wich" : False, 
    "no 1 chinese restaurant" : False, 
    "roadhouse grill" : False, 
    "mcalister's deli" : False, 
    "great wall restaurant" : False, 
    "corner cafe" : False, 
    "tropical smoothie cafe" : False, 
    "ruth's chris steak house" : False, 
    "smoothie king" : False, 
    "souper salad" : False, 
    "imo's pizza" : False, 
    "churchs chicken" : False, 
    "round table pizza" : False, 
    "hunan garden" : False, 
    "shoney's restaurant" : False, 
    "murphy's deli" : False, 
    "mr jim's pizza" : False, 
    "china kitchen" : False, 
    "wingstop" : False, 
    "checkers" : False, 
    "china buffet" : False, 
    "city cafe" : False, 
    "red robin" : False, 
    "fleming's prime steakhouse & wine bar" : False, 
    "black-eyed pea restaurant" : False, 
    "auntie anne's" : False, 
    "marble slab creamery" : False, 
    "golden china restaurant" : False, 
    "jets pizza" : False, 
    "coffee shop" : False, 
    "red brick pizza" : False, 
    "wings to go" : False, 
    "wendys" : False, 
    "taste of china" : False, 
    "friendly's ice cream shop" : False, 
    "office" : False, 
    "el tapatio" : False, 
    "western sizzlin steak house" : False, 
    "blimpie" : False, 
    "pei wei" : False, 
    "jimmy johns" : False, 
    "honeybaked ham" : False, 
    "bonefish grill" : False, 
    "fosters freeze" : False, 
    "mrs winners chicken and biscuits" : False, 
    "on the border mexican grill and cantina" : False, 
    "thai kitchen" : False, 
    "famous dave's" : False, 
    "culvers" : False, 
    "captain ds seafood" : False, 
    "outback steakhouse" : False, 
    "kfc" : False, 
    "las margaritas" : False, 
    "golden wok" : False, 
    "starbucks" : False, 
    "daily grind" : False, 
    "mellow mushroom" : False, 
    "sbarro" : False, 
    "mi ranchito" : False, 
    "pizza ranch" : False, 
    "moes southwest grill" : False, 
    "daphne's greek cafe" : False, 
    "steak escape" : False, 
    "moe's southwest grill" : False, 
    "black angus steakhouse" : False, 
    "shari's restaurant" : False, 
    "el chico" : False, 
    "roly poly sandwiches" : False, 
    "great steak & potato co" : False, 
    "hong kong express" : False, 
    "jason's deli" : False, 
    "meals on wheels" : False, 
    "braum's" : False, 
    "jade garden" : False, 
    "village inn" : False, 
    "coco's bakery" : False, 
    "ruby tuesday" : False, 
    "china town" : False, 
    "bakers square restaurant and pie" : False, 
    "taco john's" : False, 
    "carl's jr." : False, 
    "it's a grind coffee house" : False, 
    "la hacienda mexican restaurant" : False, 
    "chinatown restaurant" : False, 
    "dickey's barbecue pit" : False, 
    "great wall chinese restaurant" : False, 
    "tim hortons" : False, 
    "holiday inn" : False, 
    "east of chicago pizza" : False, 
    "whataburger" : False, 
    "panda house" : False, 
    "pick up stix" : False, 
    "buck's pizza" : False, 
    "old country buffet" : False, 
    "wing street" : False, 
    "village cafe" : False, 
    "hometown pizza" : False, 
    "bertucci's" : False, 
    "new china buffet" : False, 
    "mr hero" : False, 
    "texas roadhouse" : False, 
    "waffle house" : False, 
    "california pizza kitchen" : False, 
    "boston market" : False, 
    "caseys carry out pizza" : False, 
    "tcby" : False, 
    "golden dragon restaurant" : False, 
    "new china" : False, 
    "noble romans pizza" : False, 
    "el rodeo" : False, 
    "logan's roadhouse" : False, 
    "plaza cafe" : False, 
    "china cafe" : False, 
    "breadeaux pizza" : False, 
    "z pizza" : False, 
    "rita's water ice" : False, 
    "casey's general store" : False, 
    "del taco" : False, 
    "long john silver's" : False, 
    "chinatown express" : False, 
    "panda buffet" : False, 
    "taco bueno" : False, 
    "village inn restaurant" : False, 
    "diner" : False, 
    "baskin-robbins" : False, 
    "gold star chili" : False, 
    "romano's macaroni grill" : False, 
    "las palmas mexican restaurant" : False, 
    "sonny's real pit bar-b-q" : False, 
    "buffalo wild wings" : False, 
    "wok n roll" : False, 
    "china wok restaurant" : False, 
    "panda restaurant" : False, 
    "rubio's fresh mexican grill" : False, 
    "cancun mexican restaurant" : False, 
    "carrabba's italian grill" : False, 
    "taco time" : False, 
    "maggie moo's" : False, 
    "sunrise cafe" : False, 
    "ryan's grill buffet and bakery" : False, 
    "house of pizza" : False, 
    "chinese kitchen" : False, 
    "carvel ice cream and bakery" : False, 
    "dq grill and chill" : False, 
    "red lobster" : False, 
    "pei wei asian diner" : False, 
    "main street pizza" : False, 
    "saladworks" : False, 
    "monterrey mexican restaurant" : False, 
    "arctic circle restaurant" : False, 
    "the melting pot" : False, 
    "acapulco mexican restaurant" : False, 
    "china moon" : False, 
    "mimi's cafe" : False, 
    "popeyes chicken and biscuits" : False, 
    "golden china" : False, 
    "village pizza" : False, 
    "dairy queen" : False, 
    "chipotle mexican grill" : False, 
    "ben and jerry's" : False, 
    "beef o'brady's" : False, 
    "taco tico" : False, 
    "hong kong chinese restaurant" : False, 
    "papa johns pizza" : False, 
    "pizza plus" : False, 
    "benihana" : False, 
    "el torito" : False, 
    "la salsa fresh mexican grill" : False, 
    "china garden" : False, 
    "dippin' dots" : False, 
    "restaurants" : False, 
    "papa murphys take n bake" : False, 
    "juice it up" : False, 
    "haagen-dazs" : False, 
    "elephant bar" : False, 
    "pizza pan" : False, 
    "donatos pizza" : False, 
    "hooters" : False, 
    "cracker barrel" : False, 
    "pizza palace" : False, 
    "roly poly" : False, 
    "new china restaurant" : False, 
    "schlotzskys deli" : False, 
    "el pollo loco" : False, 
    "carvel ice cream" : False, 
    "china express" : False, 
    "bruegger's" : False, 
    "pizza place" : False, 
    "china palace" : False, 
    "chicken express" : False, 
    "garden cafe" : False, 
    "pizza patron" : False, 
    "china dragon" : False, 
    "little caesars pizza" : False, 
    "villa pizza" : False, 
    "oriental express" : False, 
    "chevy's fresh mex restaurants" : False, 
    "hong kong buffet" : False, 
    "pizza house" : False, 
    "coffee beanery" : False, 
    "dragon express" : False, 
    "super suppers" : False, 
    "port of subs" : False, 
    "pizza inn" : False, 
    "king buffet" : False, 
    "ponderosa" : False, 
    "rice garden" : False, 
    "jet's pizza" : False, 
    "subway sandwiches and salads" : False, 
    "mario's pizza" : False, 
    "hunan restaurant" : False, 
    "our place" : False, 
    "china palace restaurant" : False, 
    "new york pizzeria" : False, 
    "country cafe" : False, 
    "original italian pizza" : False, 
    "dominos pizza" : False, 
    "beef o bradys" : False, 
    "la fiesta" : False, 
    "tgi fridays" : False, 
    "mancino's pizza and grinders" : False, 
    "asian buffet" : False, 
    "potbelly sandwich works" : False, 
    "buffalo wings and rings" : False, 
    "arbys" : False, 
    "king wok" : False, 
    "krystal company the" : False, 
    "china star restaurant" : False, 
    "o'charley's" : False, 
    "peking house" : False, 
    "ninety nine restaurant" : False, 
    "giovanni's pizza" : False, 
    "papa gino's" : False, 
    "golden dragon" : False, 
    "tony's pizza" : False, 
    "sizzler restaurants" : False, 
    "country kitchen" : False, 
    "cici's pizza" : False, 
    "china house restaurant" : False, 
    "chinese gourmet express" : False, 
    "china taste" : False, 
    "ryans family steak house" : False, 
    "happy garden" : False, 
    "super china buffet" : False, 
    "kennedy fried chicken" : False, 
    "super buffet" : False, 
    "mr pizza" : False, 
    "number one chinese restaurant" : False, 
    "quiznos" : False, 
    "steak 'n shake" : False, 
    "hot wok" : False, 
    "little tokyo" : False, 
    "china one" : False, 
    "wingstreet" : False, 
    "pizza man" : False, 
    "las palmas" : False, 
    "vocelli pizza" : False, 
    "great wall" : False, 
    "courtyard cafe" : False, 
    "philly connection" : False, 
    "shoney's" : False, 
    "gatti's pizza" : False, 
    "bella pizza" : False, 
    "taco johns" : False, 
    "china garden restaurant" : False, 
    "china chef" : False, 
    "taco del mar" : False, 
    "panda garden" : False, 
    "mountain mike's pizza" : False, 
    "original pancake house" : False, 
    "p. f. chang's china bistro" : False, 
    "brothers pizza" : False, 
    "houlihan's" : False, 
    "carvel ice cream bakery" : False, 
    "jamba juice" : False, 
    "cheddar's restaurant" : False, 
    "longhorn steakhouse" : False, 
    "golden chick" : False, 
    "fox's pizza den" : False, 
    "happy wok" : False, 
    "pizza pro" : False, 
    "back yard burgers" : False, 
    "la fiesta mexican restaurant" : False, 
    "great wraps" : False, 
    "la hacienda" : False, 
    "lee's famous recipe chicken" : False, 
    "number 1 chinese restaurant" : False, 
    "china inn restaurant" : False, 
    "shane's rib shack" : False, 
    "fazoli's" : False, 
    "d'angelo sandwich shops" : False, 
    "bob evans" : False, 
    "roberto's taco shop" : False, 
    "cheeburger cheeburger" : False, 
    "white castle" : False, 
    "bamboo garden" : False, 
    "china gourmet" : False, 
    "figaro's pizza" : False, 
    "main street cafe" : False, 
    "taco bell" : False, 
    "shoneys restaurant" : False, 
    "china king" : False, 
    "caribou coffee" : False, 
    "hot stuff pizza" : False, 
    "hong kong restaurant" : False, 
    "ledo pizza" : False, 
    "tgi friday's" : False, 
    "cinnabon" : False, 
    "einstein bros. bagels" : False, 
    "pizza hut" : False, 
    "hard rock cafe" : False, 
    "ihop" : False, 
    "china 1" : False, 
    "guadalajara mexican restaurant" : False, 
    "sal's pizza" : False, 
    "wienerschnitzel" : False, 
    "corner bakery cafe" : False, 
    "deli" : False, 
    "foxs pizza den" : False, 
    "new york pizza" : False, 
    "cold stone creamery" : False, 
    "sizzler" : False, 
    "jerry's subs and pizza" : False, 
    "sub shop" : False, 
    "pizza guys" : False, 
    "figaros pizza" : False, 
    "chuck e cheeses" : False, 
    "pizza" : False, 
    "hong kong" : False, 
    "melting pot restaurant" : False, 
    "fiesta mexicana" : False, 
    "marco's pizza" : False, 
    "captain d's seafood kitchen" : False, 
    "mountain mikes pizza" : False, 
    "sub station ii" : False, 
    "red robin gourmet burgers" : False, 
    "restaurant depot" : False, 
    "dunkin donuts" : False, 
    "pizza shack" : False, 
    "biggby coffee" : False, 
    "cheeseburger in paradise" : False, 
    "big boy restaurant" : False, 
    "china house" : False, 
    "courthouse cafe" : False, 
    "zaxby's" : False, 
    "atlanta bread company" : False, 
    "china restaurant" : False, 
    "china star" : False, 
    "jack in the box" : False, 
    "coffee house" : False, 
    "tastee freez" : False, 
    "dog house" : False, 
    "tapioca express" : False, 
    "extreme pizza" : False, 
    "noble roman's" : False, 
    "pita pit" : False, 
    "a&w restaurant" : False, 
    "hardees" : False, 
    "taco cabana" : False, 
    "godfathers pizza" : False, 
    "pizza king" : False, 
    "uno chicago grill" : False, 
    "burger king" : False, 
}

