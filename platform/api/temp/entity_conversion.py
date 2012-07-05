
import Globals
from api.Schemas            import *
from Entity             import deriveTypeFromSubcategory
from bson.objectid      import ObjectId
from libs.LibUtils      import parseDateString
import datetime

# To Catch A Thief
old = {u'category': u'film', u'mangled_title_timestamp': datetime.datetime(2012, 3, 5, 22, 54, 52, 748000), u'subtitle': u'film', u'subcategory': u'movie', u'title': u'To Catch a Thief (1955)', u'desc_timestamp': datetime.datetime(2012, 3, 5, 17, 3, 16, 865000), u'subtitle_source': u'seed', u'titlel': u'to catch a thief (1955)', u'sources': {u'tmdb': {u'tmdb_source': u'tmdb', u'tmdb_timestamp': datetime.datetime(2012, 3, 27, 14, 52, 11, 100000), u'tmdb_id': u'381'}, u'apple': {u'view_url': u'http://itunes.apple.com/video/to-catch-a-thief-1955/id212048938?uo=5', u'export_date': u'1311152428052', u'aid': u'212048938'}, u'itunes_timestamp': datetime.datetime(2012, 3, 27, 14, 52, 11, 100000), u'stamped_timestamp': datetime.datetime(2012, 3, 27, 14, 52, 11, 100000), u'stamped_source': u'stamped', u'itunes_id': u'212048938', u'itunes_url': u'http://itunes.apple.com/us/movie/to-catch-a-thief-1955/id212048938?uo=4', u'itunes_source': u'itunes'}, u'details': {u'media': {u'itunes_release_date': u'2007 01 09', u'content_provider_name': u'Paramount', u'parental_advisory_id': u'0', u'search_terms': u'', u'genre_source': u'itunes', u'collection_display_name': u'', u'copyright': u'1955 Paramount Pictures', u'genre_timestamp': datetime.datetime(2012, 3, 1, 23, 3, 39, 734000), u'original_release_date': u'1955 08 03', u'release_date_source': u'format', u'artist_display_name': u'Alfred Hitchcock', u'title_version': u'', u'track_length_timestamp': datetime.datetime(2012, 3, 1, 22, 39, 47, 283000), u'track_length_source': u'seed', u'mpaa_rating_source': u'itunes', u'track_length': u'6402', u'p_line': u'', u'genre': u'Thriller', u'mpaa_rating_timestamp': datetime.datetime(2012, 3, 1, 23, 3, 39, 734000), u'artist_display_name_timestamp': datetime.datetime(2012, 3, 1, 22, 39, 47, 283000), u'artwork_url': u'http://a947.phobos.apple.com/us/r1000/028/Music/10/42/3b/dj.necnbton.170x170-75.jpg', u'release_date': datetime.datetime(1955, 8, 3, 0, 0), u'release_date_timestamp': datetime.datetime(2012, 3, 1, 22, 39, 47, 283000), u'mpaa_rating': u'NR', u'artist_display_name_source': u'seed'}, u'video': {u'episode_production_number': u'', u'director_source': u'tmdb', u'network_name': u'Paramount Pictures', u'studio_name': u'', u'cast_timestamp': datetime.datetime(2012, 3, 1, 23, 3, 39, 734000), u'director': u'Alfred Hitchcock', u'cast': u'Cary Grant, Grace Kelly, Jessie Royce Landis, Brigitte Auber, John Williams, Charles Vanel', u'director_timestamp': datetime.datetime(2012, 3, 1, 23, 3, 39, 734000), u'short_description': u'', u'cast_source': u'tmdb'}, u'artist': {}}, u'desc_source': u'itunes', u'subtitle_timestamp': datetime.datetime(2012, 3, 1, 22, 39, 47, 283000), u'desc': u'Cary Grant plays John Robie, reformed jewel thief who was once known as "The Cat," in this suspenseful Alfred Hitchcock classic thriller. Robie is suspected of a new rash of gem thefts in the luxury hotels of the French Riviera, and he must set out to clear himself. Meeting pampered heiress Frances (Grace Kelly), he sees a chance to bait the mysterious thief with her mother\'s (Jessie Royce Landis) fabulous jewels. His plan backfires, however, but France, who believes him guilty, proves her love by helping him escape. In a spine-tingling climax, the real criminal is exposed.', u'id': ObjectId('4e4c6804db6bbe2c1200011d'), u'mangled_title': u'to catch a thief', u'mangled_title_source': u'format'}

# The Artist
old = {u'category': u'film', u'subcategory': u'movie', u'title': u'The Artist', u'desc_timestamp': datetime.datetime(2012, 3, 1, 23, 31, 11, 573000), u'image': u'http://images.fandango.com/r86.4.4/ImageRenderer/375/375/images/no_image_375x375.jpg/140264/images/masterrepository/fandango/140264/the-artist-poster.jpg', u'mangled_title_timestamp': datetime.datetime(2012, 3, 7, 22, 29, 9, 725000), u'titlel': u'the artist', u'sources': {u'fandango': {u'f_url': u'http://www.qksrv.net/click-5348839-10576760?url=http%3a%2f%2fmobile.fandango.com%3fa%3d12169%3fpid=5348839%26m%3d140264', u'fid': u'140264'}, u'tmdb': {u'tmdb_source': u'tmdb', u'tmdb_timestamp': datetime.datetime(2012, 3, 7, 22, 58, 25, 206000), u'tmdb_id': u'74643'}, u'itunes_source': u'itunes', u'itunes_timestamp': datetime.datetime(2012, 3, 7, 22, 58, 25, 206000)}, u'details': {u'media': {u'track_length_timestamp': datetime.datetime(2012, 3, 1, 23, 31, 11, 573000), u'track_length_source': u'seed', u'genre_timestamp': datetime.datetime(2012, 3, 1, 23, 31, 11, 573000), u'mpaa_rating_source': u'seed', u'track_length': u'6000', u'original_release_date': u'tomorrow, November 25, 2011', u'mpaa_rating': u'PG-13', u'genre': u'Art House/Foreign, Comedy', u'genre_source': u'seed', u'mpaa_rating_timestamp': datetime.datetime(2012, 3, 1, 23, 31, 11, 573000)}, u'video': {u'director': u'Michel Hazanavicius', u'cast': u'Jean Dujardin, B\xe9r\xe9nice Bejo, John Goodman, James Cromwell, Penelope Ann Miller', u'cast_source': u'seed', u'cast_timestamp': datetime.datetime(2012, 3, 1, 23, 31, 11, 573000)}}, u'desc_source': u'seed', u'desc': u"In 1929, actor George Valentin (Jean Dujardin) is a bona fide matinee idol with many adoring fans. While working on his latest film, George finds himself falling in love with an ingenue named Peppy Miller (B\xe9r\xe9nice Bejo) and, what's more, it seems Peppy feels the same way. But George is reluctant to cheat on his wife with the beautiful young actress. The growing popularity of sound in movies further separates the potential lovers, as George's career begins to fade while Peppy's star rises.  Release Date:11/25/2011", u'id': ObjectId('4ecae65a366b3c15e7000005'), u'mangled_title': u'the artist', u'mangled_title_source': u'format'}

# Salumeria Rosi
old = {u'category': u'food', u'subtitle': u'food', u'subcategory': u'restaurant', u'title': u'Salumeria Rosi', u'image': u'http://www.opentable.com//img/restimages/27739.jpg', u'titlel': u'salumeria rosi', u'coordinates': {u'lat': 40.779421999999997, u'lng': -73.980835999999996}, u'sources': {u'googlePlaces': {u'googleplaces_id': u'CoQBcQAAAJvwB3u-hI0G8zEd0gNM59qKx-qvQ3s8YMeE81KK8PlSoK55KwNMB8i9X7DClCMp6o47WYBlMPa79g5bkTi3ltEHHLQOTR4AGzRDfwgXwzidp6mkyD4PtpKJ3DrNftFaU3HkfAci6QJ95PVCHvSUfUmKW4jD4bQPfohOsk3UzVkYEhDMaNzfoNjlqz6WPDa26FooGhT8V1blahnwsDEZcJufWAErb-PaOQ', u'gid': u'87464625989e92d20154014cf31f9e120b102304', u'googleplaces_source': u'googleplaces', u'reference': u'CnRmAAAAtjez-PLZ0-vaWPbgU4EpQQTKi8MlTWXb9Zv_yaovP3DO1GibpKgYZIjo-PIcIxVHW7-t8FGTvS-o5lPQBIFA6p6Wn4gUI4naQLNwh2nCfvXFRSZ8LHwtRq4e9J_lH5BSOGr04tK-AeJDMFbK_OV3XxIQy-0Bd2kaPEZ3sG9dFS45thoUM5RS8UU8gXolZPnQnCnHYn_35JM', u'googleplaces_timestamp': datetime.datetime(2012, 2, 27, 17, 51, 46, 793000)}, u'factual': {u'factual_source': u'factual', u'factual_timestamp': datetime.datetime(2012, 2, 27, 17, 51, 46, 793000), u'factual_id': u'35ce6d0d-61d5-4dfe-8159-5e716f207160'}, u'singleplatform': {u'singleplatform_timestamp': datetime.datetime(2012, 2, 27, 17, 51, 46, 793000), u'singleplatform_source': u'factual', u'singleplatform_id': u'salumeria-rosi'}, u'openTable': {u'reserveURL': u'529BDCCC', u'rid': u'27739', u'neighborhoodName': u'Upper West Side', u'countryID': u'US', u'metroName': u'New York / Tri-State Area'}, u'zagat': {u'zurl': u'http://www.zagat.comhttp://www.zagat.com/r/salumeria-rosi-parmacotto-manhattan'}}, u'details': {u'contact': {u'phone_timestamp': datetime.datetime(2012, 2, 27, 17, 51, 46, 793000), u'site': u'http://www.salumeriarosi.com/', u'hoursOfOperation': u'Salumi counter opens at 11:00am daily.Dining room is open continually from Noon to close.Sunday: Noon - 10:00pmMonday - Thursday: Noon - 11:00pmFriday & Saturday: Noon - 11:30pm', u'phone_source': u'googleplaces', u'phone': u'(212) 877-4801', u'site_source': u'factual', u'site_timestamp': datetime.datetime(2012, 2, 27, 17, 51, 46, 793000), u'email': u'info@salumeriarosi.com'}, u'place': {u'neighborhood': u'Amsterdam Avenue, New York', u'address_street': u'283 Amsterdam Ave', u'address_timestamp': datetime.datetime(2012, 2, 27, 17, 51, 46, 793000), u'address_region': u'NY', u'parking': u'Street Parking', u'address_locality': u'New York', u'crossStreet': u'73rd Street', u'address': u'283 Amsterdam Avenue, New York, NY 10023', u'address_components': [{u'long_name': u'283', u'short_name': u'283', u'types': [u'street_number']}, {u'long_name': u'Amsterdam Avenue', u'short_name': u'Amsterdam Avenue', u'types': [u'route']}, {u'long_name': u'New York', u'short_name': u'New York', u'types': [u'locality', u'political']}, {u'long_name': u'NY', u'short_name': u'NY', u'types': [u'administrative_area_level_1', u'political']}, {u'long_name': u'US', u'short_name': u'US', u'types': [u'country', u'political']}, {u'long_name': u'10023-2103', u'short_name': u'10023-2103', u'types': [u'postal_code']}], u'address_postcode': u'10023', u'address_country': u'US', u'publicTransit': u'1, 2 & 3 trains to 72nd Street, & M5, M5L, M7, M57, M11, M72 & M104 buses.', u'address_source': u'factual'}, u'restaurant': {u'cuisine': u'Italian, American, Deli, Tapas', u'priceScale': u'$30 and under', u'cuisine_timestamp': datetime.datetime(2012, 2, 27, 17, 51, 46, 793000), u'cuisine_source': u'factual', u'price_range_timestamp': datetime.datetime(2012, 2, 27, 17, 51, 46, 793000), u'dressCode': u'Casual Dress', u'offers': u'Bar Dining, Counter Seating, Full Bar, Patio/Outdoor Dining, Takeout, Wine', u'menu_source': u'singleplatform', u'menu_timestamp': datetime.datetime(2012, 2, 27, 17, 51, 46, 793000), u'price_range_source': u'factual', u'diningStyle': u'Casual Elegant', u'price_range': 1, u'payment': u'AMEX, MasterCard, Visa', u'acceptsWalkins': u'Yes'}}, u'_id': ObjectId('4e4c68353f4b4b2d59000142'), u'desc': u'The Rosi family, renowned in Italy for their family-owned and operated specialty meat company Parmacotto, and Tuscan-born, acclaimed chef Cesare Casella, collaborate to bring a unique Italian experience to New York\u2019s Upper West Side at Salumeria Rosi Parmacotto.The 25-seat space was designed by Italian Oscar-winning set designer Dante Ferretti and draws inspiration from a traditional salumeria juxtaposed in modern scenery.  Replicating the experience found in traditional salumeria throughout Italy, guests can  purchase a pound of the highest-quality cured or cooked meats to take home, or gossip with friends over a glass of wine and a selection of small plates.'}

# Uchiko
# old = {u'category': u'food', u'subtitle': u'food', u'subcategory': u'restaurant', u'title': u'Uchiko', u'titlel': u'uchiko', u'coordinates': {u'lat': 30.310690000000001, u'lng': -97.740043999999997}, u'sources': {u'googlePlaces': {u'gid': u'8e53946a2105f3076d4084df49521dce28d3e215', u'reference': u'CmRdAAAAX9PZKTBGhxvfLxA2nUJOBKwL65sRCtSd8NcTaNKq3H2GA1TvIdcdc5jiIdUILuu_EDJHSzwIycpQdYvt-KjMeA1cqxPadsnbIqd8_x_sfO8YCrr5r-kX4-iknWPH6LqzEhAMEEm3AtcIJbVPpeEyat5HGhSLkO1_j24UZIZAYB0pfD__K_Q8ng'}, u'openTable': {u'reserveURL': u'C063E288', u'rid': u'46240', u'neighborhoodName': u'Central Austin', u'countryID': u'US', u'metroName': u'Austin'}}, u'details': {u'contact': {u'phone': u'(512) 916-4808'}, u'place': {u'address_components': [{u'long_name': u'4200', u'short_name': u'4200', u'types': [u'street_number']}, {u'long_name': u'N. Lamar', u'short_name': u'N. Lamar', u'types': [u'route']}, {u'long_name': u'Austin', u'short_name': u'Austin', u'types': [u'locality', u'political']}, {u'long_name': u'TX', u'short_name': u'TX', u'types': [u'administrative_area_level_1', u'political']}, {u'long_name': u'US', u'short_name': u'US', u'types': [u'country', u'political']}, {u'long_name': u'78756', u'short_name': u'78756', u'types': [u'postal_code']}], u'neighborhood': u'N. Lamar, Austin', u'address': u'4200 N Lamar Blvd. Suite 140, Austin, TX 78756'}}, u'_id': ObjectId('4e4c6837f15dd72d2a0002a5')}

# Al Bustan
old = {u'category': u'food', u'subtitle': u'food', u'subcategory': u'restaurant', u'title': u'Al Bustan', u'image': u'http://images.zagat.com/sites/default/files/imagecache/restaurant_overview/restaurant-photo/50/50645_6.jpg', u'titlel': u'al bustan', u'coordinates': {u'lat': 40.756573000000003, u'lng': -73.966117999999994}, u'sources': {u'googlePlaces': {u'gid': u'6da82f12348011864019647b02e455f83afbc017', u'reference': u'CmRgAAAA_nJH9EC4fLFuh4DduUY-6wrRy7hlcueTJBIX_LRprz8KZR9QZE0V6CQblqAETZU_27mm38hHVEOC3kVzZj0x9EOX9dSPLS7FQgM6SCdORGyjeVJbGHf942ManxD9Un2qEhBJ7Al4UqKPXIsTpxruPgQRGhSYxITlQIeYMZLJhaBqPhdz5Eq3pA'}, u'zagat': {u'zurl': u'http://www.zagat.comhttp://www.zagat.com/r/al-bustan-manhattan'}, u'openTable': {u'reserveURL': u'1950CE62', u'rid': u'38155', u'neighborhoodName': u'Midtown East', u'countryID': u'US', u'metroName': u'New York / Tri-State Area'}}, u'details': {u'contact': {u'phone': u'(212) 759-5933', u'site': u'http://www.albustanny.com'}, u'place': {u'address_components': [{u'long_name': u'319', u'short_name': u'319', u'types': [u'street_number']}, {u'long_name': u'East 53rd Street', u'short_name': u'East 53rd Street', u'types': [u'route']}, {u'long_name': u'New York', u'short_name': u'New York', u'types': [u'locality', u'political']}, {u'long_name': u'NY', u'short_name': u'NY', u'types': [u'administrative_area_level_1', u'political']}, {u'long_name': u'US', u'short_name': u'US', u'types': [u'country', u'political']}, {u'long_name': u'10022', u'short_name': u'10022', u'types': [u'postal_code']}], u'neighborhood': u'East 53rd Street, New York', u'address': u'319 East 53rd Street, New York, NY 10022'}, u'restaurant': {u'cuisine': u'Lebanese'}}, u'_id': ObjectId('4e4c6853f15dd72f530002a1')}

# TV SHOW: Cats
old = {u'subcategory': u'tv', u'title': u'Cats', u'image': u'http://thetvdb.com/banners/_cache/fanart/original/94341-1.jpg', u'titlel': u'cats', u'sources': {u'thetvdb': {u'num_seasons': 1, u'air_time': u'40 minutes', u'thetvdb_id': u'94341'}}, u'details': {u'media': {u'genre': u'Documentary', u'original_release_date': u'January 1, 1991'}, u'video': {u'network_name': u'BBC One'}}, u'_id': ObjectId('4eb1be4241ad8531d20007d1'), u'desc': u"'Cats' is a BBC TV series for which biologist Roger Tabor is best known around the world. It has been shown in many countries, including the UK, USA, Japan, Australia etc. Roger is recognised as one of the world's authorities on cats, and his studies of them in different countries gave the basis for this series which he wrote and presented."}

# TV SHOW
old = {u'category': u'film', u'subtitle': u'2012', u'subcategory': u'tv', u'title': u'TV', u'timestamp': {u'created': datetime.datetime(2012, 2, 27, 22, 58, 51, 728000)}, u'titlel': u'tv', u'sources': {u'userGenerated': {u'generated_by': u'4f4bfe9c64c794440c000055'}}, u'details': {u'media': {u'original_release_date': None, u'artist_display_name': None}, u'book': {u'author': None}, u'video': {u'director': None, u'cast': None}, u'place': {u'address': u', US'}, u'song': {u'album_name': None}}, u'_id': ObjectId('4f4c0aab64c79447fe00002f'), u'desc': None}

# ARTIST
old = {u'subcategory': u'artist', u'title': u'A$AP Rocky', u'titlel': u'a$ap rocky', u'sources': {u'apple': {u'view_url': u'http://itunes.apple.com/us/artist/a$ap-rocky/id481488005?uo=4', u'aid': u'481488005'}}, u'details': {u'media': {u'genre': u'Hip Hop/Rap'}, u'artist': {u'songs': [{u'song_id': 481488008, u'song_name': u'Peso'}, {u'song_id': 481661506, u'song_name': u'Peso'}]}}, u'_id': ObjectId('4ecb19e6e4146a13ca0009f8')}

# ARTIST
old = {u'subcategory': u'artist', u'title': u'Die Antwoord', u'titlel': u'die antwoord', u'sources': {u'apple': {u'aid': u'380615226', u'view_url': u'http://itunes.apple.com/us/artist/die-antwoord/id380615226?uo=4'}, u'netflix': {u'images': {u'small': u'http://a2.mzstatic.com/us/r1000/051/Music/3f/91/82/mzi.nrcceatp.60x60-50.jpg', u'large': u'http://a3.mzstatic.com/us/r1000/051/Music/3f/91/82/mzi.nrcceatp.100x100-75.jpg'}}}, u'details': {u'media': {u'genre': u'Electronic'}, u'artist': {u'albums': [{u'album_name': u'$O$', u'album_id': 396129711}, {u'album_name': u'Ekstra - EP', u'album_id': 396130683}], u'songs': [{u'song_id': 396129717, u'song_name': u'Enter the Ninja'}, {u'song_id': 396129719, u'song_name': u'Evil Boy'}, {u'song_id': 396129720, u'song_name': u'Rich B***h'}, {u'song_id': 396129726, u'song_name': u'Beat Boy'}, {u'song_id': 396129715, u'song_name': u'In Your Face'}, {u'song_id': 396129721, u'song_name': u'Fish Paste'}, {u'song_id': 396129722, u'song_name': u'$Copie'}, {u'song_id': 396129730, u'song_name': u'$O$'}, {u'song_id': 396129718, u'song_name': u'Wat Kyk Jy?'}, {u'song_id': 396129728, u'song_name': u'Doos Dronk'}, {u'song_id': 396130700, u'song_name': u"I Don't Need You"}, {u'song_id': 396129727, u'song_name': u'She Makes Me a Killer'}, {u'song_id': 396130691, u'song_name': u'Very Fancy'}, {u'song_id': 396130692, u'song_name': u'Super Evil'}, {u'song_id': 396130701, u'song_name': u'Liewe Maatjies'}, {u'song_id': 396130689, u'song_name': u'Whatever Man'}]}}, u'_id': ObjectId('4eb3023a41ad855d53000e14')}

# ARTIST: Justin Bieber
# old = {u'category': u'music', u'mangled_title_timestamp': datetime.datetime(2012, 3, 21, 1, 6, 8, 909000), u'subtitle': u'Artist', u'subcategory': u'artist', u'title': u'Justin Bieber', u'subtitle_source': u'seed', u'titlel': u'justin bieber', u'sources': {u'rdio_source': u'rdio', u'spotify_id': u'spotify:artist:1uNFoZAHBGtllmzznpCI3s', u'apple': {u'view_url': u'http://itunes.apple.com/us/artist/justin-bieber/id320569549?uo=4', u'a_popular': True, u'aid': u'320569549'}, u'netflix': {u'images': {u'small': u'http://a3.mzstatic.com/us/r1000/064/Music/65/95/cd/mzi.uiaksxyo.60x60-50.jpg', u'large': u'http://a5.mzstatic.com/us/r1000/064/Music/65/95/cd/mzi.uiaksxyo.100x100-75.jpg'}}, u'spotify_source': u'spotify', u'itunes_timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'rdio_url': u'/artist/Justin_Bieber/', u'stamped_timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'stamped_source': u'stamped', u'rdio_id': u'r184130', u'spotify_timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'itunes_id': u'320569549', u'itunes_url': u'http://itunes.apple.com/us/artist/justin-bieber/id320569549?uo=4', u'itunes_source': u'itunes', u'rdio_timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000)}, u'details': {u'media': {u'genre': u'Pop', u'genre_timestamp': datetime.datetime(2012, 3, 21, 1, 6, 8, 909000), u'genre_source': u'seed', u'artist_display_name': u'Justin Bieber'}, u'artist': {u'albums_timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'songs_source': u'itunes', u'songs_timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'albums_source': u'itunes', u'albums': [{u'source': u'itunes', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'album_name': u'Boyfriend - Single', u'id': u'513122978', u'album_mangled': u'boyfriend'}, {u'source': u'itunes', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'album_name': u'My World 2.0 (Bonus Track Version)', u'id': u'361487155', u'album_mangled': u'my world 2.0'}, {u'source': u'itunes', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'album_name': u'My World', u'id': u'340234845', u'album_mangled': u'my world'}, {u'source': u'itunes', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'album_name': u'Never Say Never (The Remixes)', u'id': u'417853154', u'album_mangled': u'never say never'}, {u'source': u'itunes', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'album_name': u'Under the Mistletoe (Deluxe Edition)', u'id': u'474930087', u'album_mangled': u'under the mistletoe'}, {u'source': u'itunes', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'album_name': u'My Worlds Acoustic', u'id': u'417322123', u'album_mangled': u'my worlds acoustic'}, {u'source': u'itunes', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'album_name': u'Under the Mistletoe', u'id': u'474598519', u'album_mangled': u'under the mistletoe'}], u'songs': [{u'song_mangled': u'boyfriend', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Boyfriend', u'id': u'513123103', u'source': u'itunes'}, {u'song_mangled': u'baby', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Baby', u'id': u'361487208', u'source': u'itunes'}, {u'song_mangled': u'eenie meenie', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Eenie Meenie', u'id': u'359966562', u'source': u'itunes'}, {u'song_mangled': u'one time', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'One Time', u'id': u'340234868', u'source': u'itunes'}, {u'song_mangled': u'somebody to love', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Somebody to Love', u'id': u'361487223', u'source': u'itunes'}, {u'song_mangled': u'one less lonely girl', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'One Less Lonely Girl', u'id': u'340234896', u'source': u'itunes'}, {u'song_mangled': u'love me', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Love Me', u'id': u'340234901', u'source': u'itunes'}, {u'song_mangled': u'never say never', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Never Say Never (feat. Jaden Smith)', u'id': u'417853164', u'source': u'itunes'}, {u'song_mangled': u'u smile', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'U Smile', u'id': u'361487253', u'source': u'itunes'}, {u'song_mangled': u'mistletoe', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Mistletoe', u'id': u'474930419', u'source': u'itunes'}, {u'song_mangled': u'that should be me', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'That Should Be Me', u'id': u'361487446', u'source': u'itunes'}, {u'song_mangled': u'favorite girl', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Favorite Girl', u'id': u'340234870', u'source': u'itunes'}, {u'song_mangled': u'pray', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Pray', u'id': u'417322136', u'source': u'itunes'}, {u'song_mangled': u'down to earth', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Down to Earth', u'id': u'340234875', u'source': u'itunes'}, {u'song_mangled': u'stuck in the moment', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Stuck In the Moment', u'id': u'361487237', u'source': u'itunes'}, {u'song_mangled': u'never let you go', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Never Let You Go', u'id': u'361487350', u'source': u'itunes'}, {u'song_mangled': u'one time', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'One Time (My Heart Edition)', u'id': u'345760543', u'source': u'itunes'}, {u'song_mangled': u'bigger', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Bigger', u'id': u'340234892', u'source': u'itunes'}, {u'song_mangled': u'first dance', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'First Dance (feat. Usher)', u'id': u'340234900', u'source': u'itunes'}, {u'song_mangled': u'born to be somebody', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Born to Be Somebody', u'id': u'417853182', u'source': u'itunes'}, {u'song_mangled': u'overboard', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Overboard', u'id': u'361487418', u'source': u'itunes'}, {u'song_mangled': u'drummer boy', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Drummer Boy (feat. Busta Rhymes)', u'id': u'474930561', u'source': u'itunes'}, {u'song_mangled': u'up', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Up', u'id': u'361487428', u'source': u'itunes'}, {u'song_mangled': u'runaway love', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Runaway Love', u'id': u'361487312', u'source': u'itunes'}, {u'song_mangled': u'that should be me', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'That Should Be Me (Remix) [feat. Rascal Flatts]', u'id': u'417853165', u'source': u'itunes'}, {u'song_mangled': u'all i want for christmas is you', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'All I Want for Christmas Is You (SuperFestive!) [Duet With Mariah Carey]', u'id': u'474930560', u'source': u'itunes'}, {u'song_mangled': u'never say never', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Never Say Never', u'id': u'417322134', u'source': u'itunes'}, {u'song_mangled': u'pray', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Pray', u'id': u'474930568', u'source': u'itunes'}, {u'song_mangled': u'common denominator', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Common Denominator (Bonus Track)', u'id': u'340234902', u'source': u'itunes'}, {u'song_mangled': u'somebody to love', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Somebody to Love (Remix) [feat. Usher]', u'id': u'417853172', u'source': u'itunes'}, {u'song_mangled': u'mistletoe', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Mistletoe', u'id': u'474598521', u'source': u'itunes'}, {u'song_mangled': u'fa la la', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Fa La La (feat. Boyz II Men)', u'id': u'474930557', u'source': u'itunes'}, {u'song_mangled': u'santa claus is coming to town', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Santa Claus Is Coming to Town', u'id': u'474930421', u'source': u'itunes'}, {u'song_mangled': u'up', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Up (Remix) [feat. Chris Brown]', u'id': u'417853173', u'source': u'itunes'}, {u'song_mangled': u'christmas love', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Christmas Love', u'id': u'474930566', u'source': u'itunes'}, {u'song_mangled': u'baby', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Baby', u'id': u'417322125', u'source': u'itunes'}, {u'song_mangled': u'runaway love', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Runaway Love (Kanye West Remix)', u'id': u'417853178', u'source': u'itunes'}, {u'song_mangled': u'down to earth', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Down to Earth', u'id': u'417322127', u'source': u'itunes'}, {u'song_mangled': u'that should be me', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'That Should Be Me', u'id': u'417322131', u'source': u'itunes'}, {u'song_mangled': u'u smile', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'U Smile', u'id': u'417322128', u'source': u'itunes'}, {u'song_mangled': u'christmas song', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'The Christmas Song (Chestnuts Roasting On an Open Fire) [feat. Usher]', u'id': u'474930420', u'source': u'itunes'}, {u'song_mangled': u'favorite girl', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'Favorite Girl (Acoustic Version) [Live]', u'id': u'417322130', u'source': u'itunes'}, {u'song_mangled': u'all i want is you', u'timestamp': datetime.datetime(2012, 3, 27, 17, 29, 55, 633000), u'song_name': u'All I Want Is You', u'id': u'474930563', u'source': u'itunes'}]}}, u'subtitle_timestamp': datetime.datetime(2012, 3, 21, 1, 6, 8, 909000), u'_id': ObjectId('4ee0233c54533e75460010e1'), u'mangled_title': u'justin bieber', u'mangled_title_source': u'format'}

# ALBUM
old = {u'category': u'music', u'subcategory': u'album', u'title': u'Get Born', u'mangled_title_timestamp': datetime.datetime(2012, 3, 12, 15, 3, 11, 619000), u'titlel': u'get born', u'sources': {u'rdio_source': u'rdio', u'spotify_id': u'spotify:album:6NrLpQCPYrNS3kVWxDgIlg', u'apple': {u'view_url': u'http://itunes.apple.com/us/album/get-born/id2859605?uo=4', u'aid': u'2859605'}, u'netflix': {u'images': {u'small': u'http://a3.mzstatic.com/us/r1000/043/Features/09/06/38/dj.helusplu.60x60-50.jpg', u'large': u'http://a1.mzstatic.com/us/r1000/043/Features/09/06/38/dj.helusplu.100x100-75.jpg'}}, u'spotify_source': u'spotify', u'itunes_timestamp': datetime.datetime(2012, 3, 26, 18, 24, 19, 756000), u'rdio_url': u'/artist/Jet/album/Get_Born/', u'amazon_id': u'B0011Z0YJA', u'rdio_timestamp': datetime.datetime(2012, 3, 26, 18, 24, 19, 756000), u'amazon_source': u'amazon', u'stamped_timestamp': datetime.datetime(2012, 3, 26, 18, 24, 19, 756000), u'stamped_source': u'stamped', u'rdio_id': u'a98626', u'spotify_timestamp': datetime.datetime(2012, 3, 26, 18, 24, 19, 756000), u'itunes_id': u'2859605', u'itunes_source': u'itunes', u'amazon_timestamp': datetime.datetime(2012, 3, 26, 18, 24, 19, 756000)}, u'details': {u'album': {u'tracks_source': u'seed', u'tracks': [u'Last Chance', u'Are You Gonna Be My Girl', u'Rollover D.J.', u"Look What You've Done", u'Get What You Need', u'Move On', u'Radio Song', u'Get Me Outta Here', u'Cold Hard Bitch', u'Come Around Again', u'Lazy Gun', u'Timothy'], u'tracks_timestamp': datetime.datetime(2012, 3, 12, 15, 3, 11, 619000), u'track_count': 13}, u'media': {u'artist_display_name_timestamp': datetime.datetime(2012, 3, 12, 15, 3, 11, 619000), u'genre_source': u'seed', u'copyright': u'2003 Elektra Entertainment Group Inc. for the United States and WEA International Inc. for the world outside of the United States excluding Australia and New Zealand.', u'genre_timestamp': datetime.datetime(2012, 3, 12, 15, 3, 11, 619000), u'release_date': datetime.datetime(2003, 10, 7, 0, 0), u'release_date_timestamp': datetime.datetime(2012, 3, 12, 15, 3, 11, 619000), u'original_release_date': u'2003-10-07T07:00:00Z', u'release_date_source': u'format', u'artist_display_name_source': u'seed', u'artist_display_name': u'Jet', u'genre': u'Rock', u'artist_id': u'2502435'}}, u'_id': ObjectId('4f5e102f64c7947434000000'), u'mangled_title': u'get born', u'mangled_title_source': u'format'}
old = {u'category': u'music', u'subcategory': u'album', u'title': u'Mr. M (Bonus Track Version)', u'titlel': u'mr. m (bonus track version)', u'sources': {u'apple': {u'view_url': u'http://itunes.apple.com/us/album/mr.-m-bonus-track-version/id492763093?uo=4', u'aid': u'492763093'}, u'netflix': {u'images': {u'small': u'http://a5.mzstatic.com/us/r30/Music/97/d8/24/mzi.kusnijjf.60x60-50.jpg', u'large': u'http://a5.mzstatic.com/us/r30/Music/97/d8/24/mzi.kusnijjf.100x100-75.jpg'}}}, u'details': {u'album': {u'tracks': [u"If Not I'll Just Die", u'2B2', u'Gone Tomorrow', u'Mr. Met', u'Gar', u'Nice Without Mercy', u'Buttons', u'The Good Life (Is Wasted)', u'Kind Of', u"Betty's Overture", u'Never My Love', u'Gone Tomorrow (Nevers Remix) [Bonus Track]', u'Kind Of (Roger Moutenot Remix) [Bonus Track]'], u'track_count': 13}, u'media': {u'copyright': u'2012 Merge Records', u'release_date': datetime.datetime(2012, 2, 21, 0, 0), u'release_date_timestamp': datetime.datetime(2012, 2, 23, 0, 13, 49, 269000), u'original_release_date': u'2012-02-21T08:00:00Z', u'release_date_source': u'format', u'artist_display_name': u'Lambchop', u'genre': u'Alternative', u'artist_id': u'5046590'}}, u'_id': ObjectId('4f4584bd64c7946e46000034')}

# SONG
# old = {u'category': u'music', u'subcategory': u'song', u'title': u'Boyfriend', u'titlel': u'boyfriend', u'image': u'http://a2.mzstatic.com/us/r1000/111/Music/v4/38/77/35/3877356d-b8c2-2bbe-fab7-b157f7c36146/UMG_cvrart_00602537006038_01_RGB72_1200x1200_12UMGIM12122.100x100-75.jpg', u'mangled_title_timestamp': datetime.datetime(2012, 3, 27, 15, 40, 9, 207000), u'subcategory_source': u'format', u'sources': {u'rdio_source': u'rdio', u'spotify_id': u'spotify:track:712wTFutQLCdvg3gy94cyj', u'itunes_timestamp': datetime.datetime(2012, 3, 27, 15, 40, 9, 207000), u'spotify_source': u'spotify', u'rdio_url': u'/artist/Justin_Bieber_Tribute_Team/album/Boyfriend/track/Boyfriend/', u'rdio_timestamp': datetime.datetime(2012, 3, 27, 15, 40, 9, 207000), u'amazon_source': u'amazon', u'stamped_timestamp': datetime.datetime(2012, 3, 27, 15, 40, 9, 207000), u'stamped_source': u'stamped', u'rdio_id': u't16655937', u'spotify_timestamp': datetime.datetime(2012, 3, 27, 15, 40, 9, 207000), u'itunes_id': u'513123103', u'itunes_source': u'itunes', u'amazon_timestamp': datetime.datetime(2012, 3, 27, 15, 40, 9, 207000)}, u'details': {u'media': {u'artist_display_name_timestamp': datetime.datetime(2012, 3, 27, 15, 40, 9, 207000), u'track_length_timestamp': datetime.datetime(2012, 3, 27, 15, 40, 9, 207000), u'genre_timestamp': datetime.datetime(2012, 3, 27, 15, 40, 9, 207000), u'track_length_source': u'seed', u'track_length': u'172', u'genre_source': u'seed', u'artist_display_name_source': u'seed', u'artist_display_name': u'Justin Bieber', u'genre': u'Pop'}, u'song': {u'album_name': u'Boyfriend - Single'}}, u'subcategory_timestamp': datetime.datetime(2012, 3, 27, 15, 40, 9, 207000), u'_id': ObjectId('4f71df6864c79438aa000001'), u'mangled_title': u'boyfriend', u'mangled_title_source': u'format'}
# old = {u'category': u'music', u'subcategory': u'song', u'title': u'Fly', u'image': u'http://a3.mzstatic.com/us/r1000/058/Music/06/ea/9b/mzi.shvuiost.200x200-75.jpg', u'titlel': u'fly', u'sources': {u'apple': {u'view_url': u'http://itunes.apple.com/us/album/fly/id419894179?i=419894301&uo=2', u'a_popular': True, u'aid': u'419894179'}}, u'details': {u'album': {u'label_studio': u'2011 Cash Money Records Inc.'}, u'media': {u'genre': u'Hip Hop/Rap', u'artist_id': u'278464538', u'original_release_date': u'February 22, 2011', u'artist_display_name': u'Nicki Minaj'}, u'song': {u'song_album_id': u'419894179', u'album_name': u'Pink Friday', u'preview_url': u'http://a1.mzstatic.com/us/r1000/020/Music/92/d9/96/mzi.fnzxrplh.aac.p.m4a', u'preview_length': u'30000'}}, u'_id': ObjectId('4eb8737441ad850b9a0001f8')}
# old = {u'category': u'music', u'subcategory': u'song', u'title': u'Fat', u'type': u'track', u'image': u'http://a2.mzstatic.com/us/r1000/052/Features/4b/45/d6/dj.obkgqrgq.100x100-75.jpg', u'mangled_title_timestamp': datetime.datetime(2012, 3, 28, 18, 42, 42, 953000), u'titlel': u'fat', u'sources': {u'rdio_source': u'rdio', u'spotify_id': u'spotify:track:4bnqosidHvNAGENKTFm5Vm', u'itunes_timestamp': datetime.datetime(2012, 3, 28, 18, 42, 42, 953000), u'spotify_source': u'spotify', u'rdio_url': u'/artist/%22Weird_Al%22_Yankovic/album/The_Essential_Weird_Al_Yankovic/track/Fat/', u'rdio_timestamp': datetime.datetime(2012, 3, 28, 18, 42, 42, 953000), u'amazon_source': u'amazon', u'stamped_timestamp': datetime.datetime(2012, 3, 28, 18, 42, 42, 953000), u'stamped_source': u'stamped', u'rdio_id': u't2892473', u'spotify_timestamp': datetime.datetime(2012, 3, 28, 18, 42, 42, 953000), u'itunes_id': u'250500433', u'itunes_url': u'http://itunes.apple.com/us/album/fat/id250500424?i=250500433&uo=4', u'itunes_source': u'itunes', u'amazon_timestamp': datetime.datetime(2012, 3, 28, 18, 42, 42, 953000)}, u'details': {u'media': {u'genre': u'Comedy', u'track_length': u'215', u'album_name': u'Even Worse', u'artist_display_name': u'"Weird Al" Yankovic'}}, u'_id': ObjectId('4f735ba264c7945f50000000'), u'mangled_title': u'fat', u'mangled_title_source': u'format'}
# old = {u'category': u'music', u'subcategory': u'song', u'title': u'All Of Me', u'type': u'track', u'image': None, u'mangled_title_timestamp': datetime.datetime(2012, 3, 28, 18, 52, 55, 85000), u'titlel': u'all of me', u'sources': {u'rdio_source': u'rdio', u'spotify_id': u'spotify:track:0AWZRlmdLQ0OBU6WTTYSZE', u'itunes_timestamp': datetime.datetime(2012, 3, 28, 18, 52, 55, 85000), u'spotify_source': u'spotify', u'rdio_url': u'/artist/Tanlines/album/Mixed_Emotions/track/All_Of_Me/', u'amazon_id': u'B007CEVJ0W', u'rdio_timestamp': datetime.datetime(2012, 3, 28, 18, 52, 55, 85000), u'amazon_source': u'amazon', u'stamped_timestamp': datetime.datetime(2012, 3, 28, 18, 52, 55, 85000), u'stamped_source': u'stamped', u'rdio_id': u't15962164', u'spotify_timestamp': datetime.datetime(2012, 3, 28, 18, 52, 55, 85000), u'itunes_id': u'505531741', u'itunes_url': u'http://itunes.apple.com/us/album/all-of-me/id505531740?i=505531741&uo=4', u'itunes_source': u'itunes', u'amazon_timestamp': datetime.datetime(2012, 3, 28, 18, 52, 55, 85000)}, u'details': {u'media': {u'track_length_timestamp': datetime.datetime(2012, 3, 28, 18, 52, 55, 85000), u'genre_timestamp': datetime.datetime(2012, 3, 28, 18, 52, 55, 85000), u'release_date': datetime.datetime(2012, 3, 20, 0, 0), u'track_length_source': u'amazon', u'track_length': u'230.0', u'genre_source': u'itunes', u'artist_display_name': u'Tanlines', u'genre': u'Alternative', u'album_name': u'Mixed Emotions (Amazon Exclusive Version)'}}, u'_id': ObjectId('4f735e0664c79461b9000000'), u'mangled_title': u'all of me', u'mangled_title_source': u'format'}
# old = {u'category': u'music', u'subcategory': u'song', u'title': u'Call Me Maybe', u'mangled_title_timestamp': datetime.datetime(2012, 3, 5, 22, 55, 18, 535000), u'titlel': u'call me maybe', u'sources': {u'rdio_source': u'rdio', u'spotify_id': u'spotify:track:6ol4ZSifr7r3Lb2a9L5ZAB', u'apple': {u'view_url': u'http://itunes.apple.com/us/album/call-me-maybe/id465744617?i=465744628&uo=4', u'aid': u'465744628'}, u'netflix': {u'images': {u'small': u'http://a1.mzstatic.com/us/r1000/091/Music/26/2d/82/mzi.vlgypmkd.60x60-50.jpg', u'large': u'http://a2.mzstatic.com/us/r1000/091/Music/26/2d/82/mzi.vlgypmkd.100x100-75.jpg', u'tiny': u'http://a4.mzstatic.com/us/r1000/091/Music/26/2d/82/mzi.vlgypmkd.30x30-50.jpg'}}, u'spotify_source': u'spotify', u'itunes_timestamp': datetime.datetime(2012, 3, 9, 17, 20, 18, 192000), u'amazon_id': u'B007BZM3HK', u'rdio_timestamp': datetime.datetime(2012, 3, 9, 17, 20, 18, 192000), u'amazon_source': u'amazon', u'rdio_id': u't15832423', u'spotify_timestamp': datetime.datetime(2012, 3, 9, 17, 20, 18, 192000), u'itunes_id': u'504709664', u'itunes_source': u'itunes', u'amazon_timestamp': datetime.datetime(2012, 3, 9, 17, 20, 18, 192000)}, u'details': {u'album': {u'track_count': 1}, u'media': {u'artist_display_name_timestamp': datetime.datetime(2012, 3, 2, 20, 52, 18, 982000), u'original_release_date': u'2011-09-20T07:00:00Z', u'track_length_timestamp': datetime.datetime(2012, 3, 2, 20, 52, 18, 982000), u'track_length_source': u'seed', u'release_date': datetime.datetime(2012, 2, 22, 0, 0), u'genre_timestamp': datetime.datetime(2012, 3, 2, 20, 52, 18, 982000), u'track_length': u'193.4', u'release_date_timestamp': datetime.datetime(2012, 3, 9, 17, 20, 18, 192000), u'genre_source': u'seed', u'release_date_source': u'amazon', u'artist_display_name_source': u'seed', u'artist_display_name': u'Carly Rae Jepsen', u'genre': u'Pop', u'artist_id': u'284363062'}, u'product': {u'price': {u'amount': 129, u'formatted_price': u'$1.29', u'currency_code': u'USD'}}, u'song': {u'song_album_id': u'465744617', u'album_name_timestamp': datetime.datetime(2012, 3, 5, 22, 55, 18, 535000), u'album_name_source': u'amazon', u'album_name': u'Call Me Maybe', u'preview_url': u'http://a2.mzstatic.com/us/r1000/081/Music/b4/57/89/mzi.jnjushua.aac.p.m4a'}}, u'_id': ObjectId('4f44155664c7945d03000000'), u'mangled_title': u'call me maybe', u'mangled_title_source': u'format'}

# APP
# old = {u'subcategory': u'app', u'title': u'Stamped', u'image': u'http://a1.mzstatic.com/us/r1000/060/Purple/v4/0a/04/fb/0a04fb4d-8aa0-afd0-0336-80a664456d36/mzl.jdawexjx.png', u'titlel': u'stamped', u'sources': {u'itunes_id': u'467924760'}, u'details': {u'media': {u'release_date': datetime.datetime(2011, 11, 21, 0, 0), u'screenshots': [u'http://a5.mzstatic.com/us/r1000/106/Purple/v4/b0/89/f5/b089f587-6c55-3eed-9e3b-81621083a1f7/t6s9bfxdoHYpLjsBYAiR4g-temp-upload.akiwagwq.png', u'http://a4.mzstatic.com/us/r1000/071/Purple/v4/57/4c/3c/574c3c18-0522-9691-b185-a81ffcb7d66a/mzl.nicmitan.png', u'http://a5.mzstatic.com/us/r1000/091/Purple/v4/14/a8/4e/14a84e9a-599a-046f-a3fe-b146bb735ffe/mzl.tuscjxob.png', u'http://a1.mzstatic.com/us/r1000/108/Purple/v4/f3/d1/ec/f3d1ec71-fee9-4e8a-a3af-93538ba019f0/mzl.qmlfzqts.png'], u'artist_display_name': u'Stamped, Inc.'}}, u'_id': ObjectId('4f72112a64c79441f5000002'), u'desc': u'\u2605 Featured in the App Store under "What\'s Hot" and "Great Free Apps"\n\u2605 One of Mashable\'s "15 Best Mobile Apps of 2011"\n\nStamped is a new way to recommend only what you like best -- restaurants, books, movies, music and more. No noise, no strangers, just the things you and your friends love.\n\nHOW IT WORKS:\n1. Create a profile and customize your own unique stamp.\n2. Stamp the things you want your friends to know about, like an amazing burrito place or a great book.\n3. Follow your friends and trusted sources to discover great recommendations.\n\nFEATURES:\nPhotos - Add your own photo to any stamp \nTo-Do List - Organize all the stamps you want to try on a To-Do list\nMap View - View all of your friends\u2019 stamps on a map to check out what\u2019s nearby\nOpentable, Amazon, Fandango and iTunes integration - You can make reservations, buy books, get movie tickets, and download songs, all through the app\nTwitter/FB sharing - Post your stamps to Twitter and Facebook \nSearch - Easily search stamps by keyword, person or location'}


newType = deriveTypeFromSubcategory(old['subcategory'])

if newType in ['place']:
    new = PlaceEntity()
elif newType in ['artist']:
    new = PersonEntity()
elif newType in ['album', 'tv']:
    new = MediaCollectionEntity()
elif newType in ['track', 'movie', 'book']:
    new = MediaItemEntity()
elif newType in ['app']:
    new = SoftwareEntity()
else:
    new = BasicEntity()

def setBasicGroup(source, target, oldName, newName=None, oldSuffix=None, newSuffix=None, additionalSuffixes=None):
    if newName is None:
        newName = oldName
    if oldSuffix is None:
        item = source.pop(oldName, None)
    else:
        item = source.pop('%s_%s' % (oldName, oldSuffix), None)

    if item is not None:
        # Manual conversions...
        if oldName == 'track_length':
            try:
                item = int(str(item).split('.')[0])
            except:
                pass

        if newSuffix is None:
            target[newName] = item 
        else:
            target['%s_%s' % (newName, newSuffix)] = item

        if newName != 'tombstone':
            target['%s_source' % newName] = source.pop('%s_source' % oldName, 'seed')
        target['%s_timestamp' % newName]  = source.pop('%s_timestamp' % oldName, datetime.datetime.utcnow())

        if additionalSuffixes is not None:
            for s in additionalSuffixes:
                t = source.pop('%s_%s' % (oldName, s), None)
                if t is not None:
                    target['%s_%s' % (newName, s)] = t 

def setListGroup(source, target, oldName, newName=None, delimiter=',', wrapper=None):
    if newName is None:
        newName = oldName

    item = source.pop(oldName, None)

    if item is not None:
        items = []
        for i in item.split(delimiter):
            if wrapper is not None:
                entityMini = wrapper()
                entityMini.title = i.strip()
                items.append(entityMini)
            else:
                items.append(i.strip())
        target[newName] = items 

        target['%s_source' % newName]     = source.pop('%s_source' % oldName, 'seed')
        target['%s_timestamp' % newName]  = source.pop('%s_timestamp' % oldName, datetime.datetime.utcnow())




sources                 = old.pop('sources', {})
details                 = old.pop('details', {})
timestamp               = old.pop('timestamp', {})
place                   = details.pop('place', {})
contact                 = details.pop('contact', {})
restaurant              = details.pop('restaurant', {})
media                   = details.pop('media', {})
video                   = details.pop('video', {})
artist                  = details.pop('artist', {})
album                   = details.pop('album', {})
song                    = details.pop('song', {})


# General
new.schema_version      = 0
new.title               = old.pop('title', None)
new.title_lower         = old.pop('titlel', None)
new.image               = old.pop('image', None)
# TODO: Refactor image
# TODO: Include old.sources.netflix.images[large/small/etc.]
setBasicGroup(old, new, 'desc')
subcategory = old['subcategory']
if subcategory == 'song':
    subcategory = 'track'
new.types.append(subcategory)

# TODO: Add custom subtitle for user-generated


# Sources
setBasicGroup(sources, new['sources'], 'spotify', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
setBasicGroup(sources, new['sources'], 'rdio', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
setBasicGroup(sources, new['sources'], 'amazon', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
setBasicGroup(sources, new['sources'], 'fandango', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
setBasicGroup(sources, new['sources'], 'stamped', 'tombstone', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
setBasicGroup(sources.pop('tmdb', {}), new['sources'], 'tmdb', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
setBasicGroup(sources.pop('factual', {}), new['sources'], 'factual', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
# TODO: Add factual_crosswalk
setBasicGroup(sources.pop('singleplatform', {}), new['sources'], 'singleplatform', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])

# Apple / iTunes
setBasicGroup(sources, new['sources'], 'itunes', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
if new.sources.itunes_id is None:
    setBasicGroup(sources.pop('apple', {}), new['sources'], 'aid', 'itunes', newSuffix='id', additionalSuffixes=['url'])

# OpenTable
setBasicGroup(sources, new['sources'], 'opentable', oldSuffix='id', newSuffix='id', additionalSuffixes=['nickname', 'url'])
if new.sources.opentable_id is None:
    setBasicGroup(sources.pop('openTable', {}), new['sources'], 'rid', 'opentable', newSuffix='id', additionalSuffixes=['url'])

# Google Places
googleplaces = sources.pop('googlePlaces', {})
setBasicGroup(googleplaces, new['sources'], 'googleplaces', oldSuffix='id', newSuffix='id', additionalSuffixes=['url'])
if new.sources.googleplaces_id is None:
    setBasicGroup(googleplaces, new['sources'], 'reference', 'googleplaces', newSuffix='id', additionalSuffixes=['url'])

# User Generated
userGenerated = sources.pop('userGenerated', {}).pop('generated_by', None)
if userGenerated is not None:
    new.sources.user_generated_id = userGenerated
    if 'created' in timestamp:
        new.sources.user_generated_timestamp = timestamp['created']
    else:
        new.sources.user_generated_timestamp = datetime.datetime.utcnow()

# Contacts
setBasicGroup(contact, new.contact, 'phone')
setBasicGroup(contact, new.contact, 'site')
setBasicGroup(contact, new.contact, 'email')
setBasicGroup(contact, new.contact, 'fax')


# Places
if newType == 'place':
    coordinates = old.pop('coordinates', None)
    if coordinates is not None:
        new.coordinates = coordinates

    addressComponents = ['locality', 'postcode', 'region', 'street', 'street_ext']
    setBasicGroup(place, new, 'address', 'address', oldSuffix='country', newSuffix='country', additionalSuffixes=addressComponents)

    setBasicGroup(place, new, 'address', 'formatted_address')
    setBasicGroup(place, new, 'hours')
    setBasicGroup(restaurant, new, 'menu')
    setBasicGroup(restaurant, new, 'price_range')
    setBasicGroup(restaurant, new, 'alcohol_flag')
    
    setListGroup(restaurant, new, 'cuisine')


# Artist
if newType == 'artist':

    songs = artist.pop('songs', [])
    for song in songs:
        entityMini = MediaItemEntityMini()
        entityMini.title = song['song_name']
        if 'id' in song and 'source' in song and song['source'] == 'itunes':
            entityMini.sources.itunes_id = song['id']
            entityMini.sources.itunes_source = 'itunes'
            entityMini.sources.itunes_timestamp = song.pop('timestamp', datetime.datetime.utcnow())
        new.tracks.append(entityMini)
    if len(songs) > 0:
        new.tracks_source = artist.pop('songs_source', 'seed')
        new.tracks_timestamp = artist.pop('songs_timestamp', datetime.datetime.utcnow())

    albums = artist.pop('albums', [])
    for item in albums:
        entityMini = MediaCollectionEntityMini()
        entityMini.title = item['album_name']
        if 'id' in item and 'source' in item and item['source'] == 'itunes':
            entityMini.sources.itunes_id = item['id']
            entityMini.sources.itunes_source = 'itunes'
            entityMini.sources.itunes_timestamp = item.pop('timestamp', datetime.datetime.utcnow())
        new.albums.append(entityMini)
    if len(albums) > 0:
        new.albums_source = artist.pop('albums_source', 'seed')
        new.albums_timestamp = artist.pop('albums_timestamp', datetime.datetime.utcnow())

    setListGroup(media, new, 'genre', 'genres')


# General Media
if newType in ['album', 'tv', 'track', 'movie', 'book']:
    artwork_url = media.pop('artwork_url', None)
    if new.image is None and artwork_url is not None:
        new.image = artwork_url

    setBasicGroup(media, new, 'track_length', 'length')
    setBasicGroup(media, new, 'mpaa_rating')
    setBasicGroup(media, new, 'release_date')

    setListGroup(media, new, 'genre', 'genres')
    setListGroup(media, new, 'artist_display_name', 'artists', wrapper=PersonEntityMini)
    setListGroup(video, new, 'cast', 'cast', wrapper=PersonEntityMini)
    setListGroup(video, new, 'director', 'directors', wrapper=PersonEntityMini)

    originalReleaseDate = parseDateString(media.pop('original_release_date', None))
    if new.release_date is None and originalReleaseDate is not None:
        new.release_date = originalReleaseDate
        new.release_date_source = 'seed'
        new.release_date_timestamp = datetime.datetime.utcnow()


# Album
if newType == 'album':
    songs = album.pop('tracks', [])
    for song in songs:
        entityMini = MediaItemEntityMini()
        entityMini.title = song
        new.tracks.append(entityMini)
    if len(songs) > 0:
        new.tracks_source = album.pop('songs_source', 'seed')
        new.tracks_timestamp = album.pop('songs_timestamp', datetime.datetime.utcnow())


# Track
if newType == 'track':
    albumName = song.pop('album_name', media.pop('album_name', None))
    print albumName
    if albumName is not None:
        entityMini = MediaCollectionEntityMini()
        entityMini.title = albumName
        albumId = song.pop('song_album_id', None)
        if albumId is not None:
            entityMini.sources.itunes_id = albumId 
            entityMini.sources.itunes_source = 'seed'
            entityMini.sources.itunes_timestamp = datetime.datetime.utcnow()
        new.collections.append(entityMini)
        new.collections_source = song.pop('album_name_source', 'seed')
        new.collections_timestamp = song.pop('album_name_timestamp', datetime.datetime.utcnow())

# Apps
if newType == 'app':
    setBasicGroup(media, new, 'release_date')
    setListGroup(media, new, 'authors', 'artist_display_name', wrapper=PersonEntityMini)

    screenshots = media.pop('screenshots', [])
    for screenshot in screenshots:
        imageSchema = ImageSchema()
        imageSizeSchema = ImageSizeSchema()
        imageSizeSchema.url = screenshot
        imageSchema.sizes.append(imageSizeSchema)
        new.screenshots.append(imageSchema)
    if len(screenshots) > 0:
        new.screenshots_source = media.pop('screenshots_source', 'seed')
        new.screenshots_timestamp = media.pop('screenshots_timestamp', datetime.datetime.utcnow())


print '\n\nRESULT\n%s' % ('='*40)
print new
print
