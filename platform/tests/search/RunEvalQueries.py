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
    def test_run_book_queries(self):
        bookQueries = [
                '1984',
                '1Q84 book',
                '1Q84',
                'amrar',
                'baking made easy',
                'bossypants',
                'd day cornelius ryan',
                'd day stephen ambrose',
                'embassytown china',
                'freakonomics',
                'freedom by jonathon franzen',
                'freedom jonathon franzen',
                'freedom',
                'lord of the flies',
                'of mice and men',
                'steve jobs biography',
                'the boy who harnessed the wind',
                'the fault in our stars',
                'the girl who kicked the hornet\'s nest',
                'the girl who played with fire',
                'the help',
                'the immortal life of henrietta lacks',
                'hamlet',
                # series names rather than book names
                'narnia',
                'lord of the rings',
                'berenstain bears',
                # title hint + name
                'moon heinlein',
                'america baudrillard',
                'ouroboros e.r. eddison',
                'snow malfi',
                'c++ scott myers' # yeah i know it's misspelled, that's the point
                ]
        self.__runQueries('book', bookQueries)

    @fixtureTest()
    def test_run_film_queries(self):
        filmQueries = [
                '1984',  # This one is a DISASTER.
                '90210',
                'LOST',
                'Le ragazze di Piazza di Spagna',
                'a-team',
                'ateam',
                'a team',
                'american idol',
                'animaniacs',
                'arrested development',
                'athf',
                'aqua teen hunger force',
                'avengers',
                'big bang theory',
                'breaking bad',
                'casablanca',
                'coupling',
                'dark angel',
                'deadwood',
                'dexter',
                'die hard',
                'drive (2011)',
                'drive',
                'family guy',
                'firefly',
                'footballer\'s wives',
                'friends',
                'futurama movie',
                'futurama',
                'game of thrones',
                'girl with the dragon tattoo',
                'godfather',
                'harry potter',
                'hotel babylon',
                'how i met your mother',
                'hunger games',
                'inception',
                'incredibles',
                'it\'s always sunny in philadelphia',
                'jeeves and wooster',
                'lord of the rings',
                'misfits',
                'mission impossible ghost protocol',
                'new girl',
                'raiders of the lost ark',
                'requiem',
                'requiem for a dream',
                'rome',
                'saturday night live',
                'south park',
                'superman',
                'spongebob squarepants',
                'spongebob',
                'star wars',
                'star wars tng',
                'star wars deep space nine',
                'star trek',
                'star trek wrath of khan',
                'taken',
                'teenage mutant ninja turtles II',
                'teenage mutant ninja turtles III',
                'teenage mutant ninja turtles',
                'the a-team',
                'the avengers',
                'the fifth element',
                'the godfather',
                'the hunger games',
                'the simpsons',
                'the sopranos',
                'the walking dead',
                'tomorrow never dies',
                'trailer park boys',
                'true grit',
                'two towers',
                'up all night',

                # Tests for title + corroborating detail
                'true grit john wayne',
                'true grit 2010',
                'true grit jeff bridges',
                'true grit coens brothers',
                'superman reeves',
                'superman brandon routh',
                'superman kirk alyn',
                'superman ii',
                'superman iii',
                'superman kevin spacey',
                ]
        self.__runQueries('film', filmQueries)

    @fixtureTest()
    def test_run_music_queries(self):
        musicQueries = [
                '1980 rehab graffiti the world',
                '1980 rehab',
                '21 adele',
                '2face idibia',
                '50 cent',
                'A.D.H.D. kendrick lamar',
                'Ai Se Eu Te Pego',
                'B.o.B',
                'Befehl von ganz unten album',
                'Deep Cuts',
                'I-Empire',
                'Kimi Ni Saku Hana',
                'LMFAO Sorry for Party Rocking',
                'MGMT',
                'S.C.I.E.N.C.E.',
                'Simple As...',
                'Sorry for Party Rocking LMFAO',
                'Sorry for Party Rocking',
                'Tuskegee Lionel Richie',
                'Tuskegee by Lionel Richie',
                'What\'s wrong is everyhere',
                'above & beyond bassnectar divergent spectrum',
                'adele 21',
                'afternoon youth lagoon hibernation',
                'american music by the violent femmes',
                'angelique kidjo',
                'april uprising to look like you',
                'astro lounge',
                'bangarang skrillex',
                'bis ans ende der welt',
                'born this way',
                'carly rae jepsen',
                'carrie underwood',
                'damn it feels good to be a gangsta',
                'david guetta',
                'deadmau5',
                'empire of the sun',
                'enema of the state',
                'eyelid movies',
                'flo rida',
                'flobot fight with tools handlebars',
                'good morning chamillionaire',
                'gotye',
                'graffiti the world 1980',
                'hail to the thief',
                'i follow rivers lykke li',
                'it won\'t snow where you\'re going',
                'it\'s never been like that',
                'jay z',
                'jay-z',
                'john butler to look like you',
                'justin bieber',
                'kanye power',
                'kanye west',
                'katy perry part of me',
                'katy perry',
                'kelly clarkson',
                'leider geil deichkind',
                'let it (edit remix) machinedrum',
                'lux aeterna',
                'm83 intro',
                'michel telo',
                'midnight city',
                'montanita ratatat',
                'mouthful of diamonds',
                'mozart',
                'musique automatique',
                'my name is stain shaka',
                'nicki minaj',
                'nothing but the beat david guetta',
                'olly murs',
                'oracular spectacular',
                'parte stroke 9',
                'passion pit',
                'play the b-sides',
                'rammstein',
                'ratat party with children',
                'ratatat classics montanita',
                'ratatat party with children',
                'red hot chili peppers',
                'rising sun exile',
                'rjd2',
                'somebody that i used to know',
                'starry eyed surprise bunkka',
                'stefanie heinzmann',
                'stereo total',
                'susan boyle',
                'the beatles',
                'the glitch mob',
                'the temper trap',
                'the young machines',
                'to look like you john butler trio april uprising',
                'toxicity',
                'usher',
                'viva wisconsin',
                'we belong together mariah carey',
                'without a sound',
                'wolfgang amadeus phoenix',
                'yelle',
                'young blood lynx',

                # tests for title of album or track + artist name
                'waylon the door is always open',
                'the door is always open jamey johnson',
                'dreaming my dreams with you waylon',
                'jamey johnson dreaming my dreams',
                'alison krauss dreaming my dreams with you',
                ]
        self.__runQueries('music', musicQueries)

    @fixtureTest()
    def test_run_place_queries(self):
        placeQueries = [
                ('A16', (37.806528, -122.406511)),
                ('Galata Balikcisi', (41.025593, 28.974618)),
                ('PDT', None),
                ('SXSW', (50.172962, 8.721237)),
                ('amber india', (37.765037, -122.412568)),
                ('apotheke', (29.984821, -95.338962)),
                ('australian bar', (50.121094, 8.673447)),
                ('azul tequila', (44.783160, -91.436092)),
                ('beer bistro', (43.654828, -79.375191)),
                ('benihana', (35.395640, 139.567383)),
                ('bourbon and branch', None),
                ('cincinnati zoo', (39.149059, -84.437150)),
                ('disney world', (28.344178, -81.575242)),
                ('el pomodoro', (20.727698, -103.437507)),
                ('empanada mama', (40.754632, -73.994261)),
                ('empire state building', (40.736, -73.989)),
                ('enoxel', (-23.596847, -46.688728)),
                ('evo pizza', (37.781697, -122.392146)),
                ('faramita', (25.084350, 121.556224)),
                ('galleria mall', (35.995347, -114.936936)),
                ('highline park', None),
                ('kyoto japanese sushi', (53.606024, -113.379279)),
                ('la victoria', (35.395640, 139.567383)),
                ('le poisson rouge', (40.734466, -73.990742)),
                ('mauds cafe', (54.593507, -5.925185)),
                ('mordisco', (41.386533, 2.128773)),
                ('nando\'s', (51.478148, -3.176642)),
                ('paddy\'s irish', (35.042481, -78.928133)),
                ('per se in nyc', (29.984821, -95.338962)),
                ('prospect sf', (37.806528, -122.406511)),
                ('rocket science lab', (18.393496, -66.006503)),
                ('sakura japanese restaurant', (39.625811, -77.773603)),
                ('sakura', (39.625811, -77.773603)),
                ('sizzle pie pizza', (45.524149, -122.682825)),
                ('times square', (39.481461, -6.373380)),
                ('venga empanadas', (37.806586,-122.406520)),
                ('veritas media', (41.386533, 2.128773)),
                ('zoka', (47.622030, -122.337103)),

                # Disambiguating hints in query.
                ('shake shack madison square park', (40.5, -74.6)),
                ('shake shack madison ave', (40.5, -74.6)),
                ('shake shack weston', (40.5, -74.6)),
                ('shake shack madison ave', (41.4, -73.3)), # This one is real close to Weston but we should really
                                                            # find the Madison Ave one because it's explicitly in the
                                                            # query.
                ('pepe\'s pizza yonkers', (41.4, -73.3)),
                ('pepe\'s manchester', (41.4, -73.3)),
                ('wendy\'s', (40.58, -74.64)),              # Should hit the one in Bridgewater, NJ because of the
                                                            # lat/lng.
                ('wendy\'s bridgewater 22', (41.4, -73.3))
            ]
        self.__runQueries('place', placeQueries)

    @fixtureTest()
    def test_run_app_queries(self):
        appQueries = [
                'Stamped',
                'Instagram',
                'doodle jump',
                'tiny wings',
                'flipboard',
                'facebook app',
                'facebook',
                'temple run',
                'pandora radio',
                ]
        self.__runQueries('app', appQueries)


    def __runQueries(self, category, queries):
        searcher = EntitySearch()

        def runSearch(query):
            if category == 'place':
                query, location = query
                readableQuery = (query + ' near ' + str(location)) if location else query
            else:
                location = None
                readableQuery = query
            results = searcher.searchEntitiesAndClusters(category, query, coords=location)
            return readableQuery, list(results)

        results = dict(runSearch(query) for query in queries)

        outputMessage = """
        /---------------------------------------------
        |    Search results written to:
        |      %s
        \\---------------------------------------------
        """
        with tempfile.NamedTemporaryFile(delete=False) as fout:
            pickle.dump(results, fout)
            print outputMessage % fout.name


if __name__ == '__main__':
    main()
