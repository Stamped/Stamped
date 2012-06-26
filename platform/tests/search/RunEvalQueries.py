#!/usr/bin/env python

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

import Globals
import pickle
import tempfile

from search.EntitySearch import EntitySearch
from tests.framework.FixtureTest import *

class RunEvalQueries(AStampedFixtureTestCase):
    @fixtureTest()
    def test_run_quries(self):
        bookQueries = [
                'book 1Q84 book',
                'book 1Q84',
                'book amrar',
                'book baking made easy',
                'book bossypants',
                'book embassytown china',
                'book freakonomics',
                'book freedom by jonathon franzen',
                'book freedom jonathon franzen',
                'book freedom',
                'book lord of the flies',
                'book of mice and men',
                'book steve jobs biography',
                'book the boy who harnessed the wind',
                'book the fault in our stars',
                'book the girl who kicked the hornet\'s nest',
                'book the girl who played with fire',
                'book the help',
                'book the immortal life of henrietta lacks',
                ]
        filmQueries = [
                'film 90210',
                'film LOST',
                'film Le ragazze di Piazza di Spagna',
                'film american idol',
                'film arrested development',
                'film big bang theory',
                'film breaking bad',
                'film coupling',
                'film dark angel',
                'film dexter',
                'film die hard',
                'film drive (2011)',
                'film drive',
                'film family guy',
                'film firefly',
                'film footballer\'s wives',
                'film friends',
                'film futurama movie',
                'film futurama',
                'film game of thrones',
                'film godfather',
                'film hotel babylon',
                'film how i met your mother',
                'film hunger games',
                'film inception',
                'film it\'s always sunny in philadelphia',
                'film jeeves and wooster',
                'film misfits',
                'film mission impossible ghost protocol',
                'film new girl',
                'film raiders of the lost ark',
                'film saturday night live',
                'film south park',
                'film spongebob squarepants',
                'film spongebob',
                'film teenage mutant ninja turtles II',
                'film teenage mutant ninja turtles III',
                'film teenage mutant ninja turtles',
                'film the fifth element',
                'film the godfather',
                'film the hunger games',
                'film the simpsons',
                'film the sopranos',
                'film the walking dead',
                'film tomorrow never dies',
                'film trailer park boys',
                'film up all night',
                ]
        musicQueries = [
                'music 1980 rehab graffiti the world',
                'music 1980 rehab',
                'music 21 adele',
                'music 2face idibia',
                'music 50 cent',
                'music A.D.H.D. kendrick lamar',
                'music Ai Se Eu Te Pego',
                'music B.o.B',
                'music Befehl von ganz unten album',
                'music Deep Cuts',
                'music I-Empire',
                'music Kimi Ni Saku Hana',
                'music LMFAO Sorry for Party Rocking',
                'music MGMT',
                'music S.C.I.E.N.C.E.',
                'music Simple As...',
                'music Sorry for Party Rocking LMFAO',
                'music Sorry for Party Rocking',
                'music Tuskegee Lionel Richie',
                'music Tuskegee by Lionel Richie',
                'music What\'s wrong is everyhere',
                'music above & beyond bassnectar divergent spectrum',
                'music adele 21',
                'music afternoon youth lagoon hibernation',
                'music american music by the violent femmes',
                'music angelique kidjo',
                'music april uprising to look like you',
                'music astro lounge',
                'music bangarang skrillex',
                'music bis ans ende der welt',
                'music born this way',
                'music carly rae jepsen',
                'music carrie underwood',
                'music damn it feels good to be a gangsta',
                'music david guetta',
                'music deadmau5',
                'music empire of the sun',
                'music enema of the state',
                'music eyelid movies',
                'music flo rida',
                'music flobot fight with tools handlebars',
                'music good morning chamillionaire',
                'music gotye',
                'music graffiti the world 1980',
                'music hail to the thief',
                'music i follow rivers lykke li',
                'music it won\'t snow where you\'re going',
                'music it\'s never been like that',
                'music jay z',
                'music jay-z',
                'music john butler to look like you',
                'music justin bieber',
                'music kanye power',
                'music kanye west',
                'music katy perry part of me',
                'music katy perry',
                'music kelly clarkson',
                'music leider geil deichkind',
                'music let it (edit remix) machinedrum',
                'music lux aeterna',
                'music m83 intro',
                'music michel telo',
                'music midnight city',
                'music montanita ratatat',
                'music mouthful of diamonds',
                'music mozart',
                'music musique automatique',
                'music my name is stain shaka',
                'music nicki minaj',
                'music nothing but the beat david guetta',
                'music olly murs',
                'music oracular spectacular',
                'music parte stroke 9',
                'music passion pit',
                'music play the b-sides',
                'music rammstein',
                'music ratat party with children',
                'music ratatat classics montanita',
                'music ratatat party with children',
                'music red hot chili peppers',
                'music rising sun exile',
                'music rjd2',
                'music somebody that i used to know',
                'music starry eyed surprise bunkka',
                'music stefanie heinzmann',
                'music stereo total',
                'music susan boyle',
                'music the beatles',
                'music the glitch mob',
                'music the temper trap',
                'music the young machines',
                'music to look like you john butler trio april uprising',
                'music toxicity',
                'music usher',
                'music viva wisconsin',
                'music we belong together mariah carey',
                'music without a sound',
                'music wolfgang amadeus phoenix',
                'music yelle',
                'music young blood lynx',
                ]
        placeQueries = [
                ('place A16', (37.806528, -122.406511)),
                ('place Galata Balikcisi', (41.025593, 28.974618)),
                ('place PDT', None),
                ('place SXSW', (50.172962, 8.721237)),
                ('place amber india', (37.765037, -122.412568)),
                ('place apotheke', (29.984821, -95.338962)),
                ('place australian bar', (50.121094, 8.673447)),
                ('place azul tequila', (44.783160, -91.436092)),
                ('place beer bistro', (43.654828, -79.375191)),
                ('place benihana', (35.395640, 139.567383)),
                ('place bourbon and branch', None),
                ('place cincinnati zoo', (39.149059, -84.437150)),
                ('place disney world', (28.344178, -81.575242)),
                ('place el pomodoro', (20.727698, -103.437507)),
                ('place empanada mama', (40.754632, -73.994261)),
                ('place empire state building', (40.736, -73.989)),
                ('place enoxel', (-23.596847, -46.688728)),
                ('place evo pizza', (37.781697, -122.392146)),
                ('place faramita', (25.084350, 121.556224)),
                ('place galleria mall', (35.995347, -114.936936)),
                ('place highline park', None),
                ('place kyoto japanese sushi', (53.606024, -113.379279)),
                ('place la victoria', (35.395640, 139.567383)),
                ('place le poisson rouge', (40.734466, -73.990742)),
                ('place mauds cafe', (54.593507, -5.925185)),
                ('place mordisco', (41.386533, 2.128773)),
                ('place nando\'s', (51.478148, -3.176642)),
                ('place paddy\'s irish', (35.042481, -78.928133)),
                ('place per se in nyc', (29.984821, -95.338962)),
                ('place prospect sf', (37.806528, -122.406511)),
                ('place rocket science lab', (18.393496, -66.006503)),
                ('place sakura japanese restaurant', (39.625811, -77.773603)),
                ('place sakura', (39.625811, -77.773603)),
                ('place sizzle pie pizza', (45.524149, -122.682825)),
                ('place times square', (39.481461, -6.373380)),
                ('place venga empanadas', (37.806586,-122.406520)),
                ('place veritas media', (41.386533, 2.128773)),
                ('place zoka', (47.622030, -122.337103)),
            ]

        searcher = EntitySearch()
        bookResults = {query : self.__runSearch(query, searcher) for query in bookQueries}
        filmResults = {query : self.__runSearch(query, searcher) for query in filmQueries}
        musicResults = {query : self.__runSearch(query, searcher) for query in musicQueries}

        placeResults = {}
        for query, location in placeQueries:
            formattedQuery = query + ' near ' + str(location) if location else query
            placeResults[formattedQuery] = self.__runSearch(query, searcher, location)

        outputMessage = """
        /---------------------------------------------
        |    Search results written:
        |      books: %s
        |      films: %s
        |      music: %s
        |      places: %s
        \\---------------------------------------------
        """
        print outputMessage % (
                self.__dumpResults(bookResults),
                self.__dumpResults(filmResults),
                self.__dumpResults(musicResults),
                self.__dumpResults(placeResults))


    def __dumpResults(self, results):
        with tempfile.NamedTemporaryFile(delete=False) as fout:
            pickle.dump(results, fout)
            return fout.name

    def __runSearch(self, query, searcher, location=None):
        tokens = query.split()
        assert len(tokens) > 1
        results = searcher.searchEntitiesAndClusters(tokens[0], ' '.join(tokens[1:]), coords=location)
        return [(entity.dataExport(), cluster) for entity, cluster in results]


if __name__ == '__main__':
    main()
