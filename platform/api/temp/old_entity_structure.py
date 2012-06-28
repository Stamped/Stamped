# SOURCE: https://github.com/Stamped/Stamped/blob/bdf277e7989b2b5f6f7e86298e51bdae943f514b/platform/api/Schemas.py


# ######## #
# Entities #
# ######## #

class Entity(Schema):
    def setSchema(self):
        self.entity_id                  = SchemaElement(basestring)
        self.search_id                  = SchemaElement(basestring)
        self.title                      = SchemaElement(basestring, required=True)
        self.titlel                     = SchemaElement(basestring)
        self.subtitle                   = SchemaElement(basestring)

        # DONE self.category                   = SchemaElement(basestring, derivedFrom='subcategory', derivedFn=self.set_category)
        # DONE self.subcategory                = SchemaElement(basestring, required=True)
        
        # 1:1  self.desc                       = SchemaElement(basestring)

        self.image                      = SchemaElement(basestring)             # Keep
        # DONE self.timestamp                  = TimestampSchema()              # Keep
        # DONE self.coordinates                = CoordinatesSchema()            # Keep
        self.details                    = EntityDetailsSchema()                 # Keep
        self.sources                    = EntitySourcesSchema()                 # Keep

class CoordinatesSchema(Schema):
    def setSchema(self):
        # DONE self.lat                = SchemaElement(float, required=True)
        # DONE self.lng                = SchemaElement(float, required=True)

class EntityDetailsSchema(Schema):
    def setSchema(self):
        self.place              = PlaceSchema()
        self.contact            = ContactSchema()
        self.restaurant         = RestaurantSchema()
        self.app                = AppSchema()
        self.book               = BookSchema()
        self.video              = VideoSchema()
        self.artist             = ArtistSchema()
        self.song               = SongSchema()
        self.album              = AlbumSchema()
        self.media              = MediaSchema()

class PlaceSchema(Schema):
    def setSchema(self):
        self.hours              = TimesSchema()                         # Keep
        # DONE self.address            = SchemaElement(basestring)             # Keep
        # DONE self.address_components = SchemaList(AddressComponentSchema())  # Keep

class AddressComponentSchema(Schema):
    def setSchema(self):
        # SKIP self.long_name          = SchemaElement(basestring)
        # DONE self.short_name         = SchemaElement(basestring)
        # DONE self.types              = SchemaList(SchemaElement(basestring))

class ContactSchema(Schema):
    def setSchema(self):
        # DONE self.phone              = SchemaElement(basestring)     # Keep
        # DONE self.site               = SchemaElement(basestring)     # Keep

class RestaurantSchema(Schema):
    def setSchema(self):
        # DONE self.cuisine            = SchemaElement(basestring)     # Keep

class BookSchema(Schema):
    def setSchema(self):
        self.isbn               = SchemaElement(basestring)     # Keep
        self.author             = SchemaElement(basestring)     # Keep
        self.publisher          = SchemaElement(basestring)     # Keep
        self.publish_date       = SchemaElement(basestring)     # Keep
        self.language           = SchemaElement(basestring)     # Keep
        self.book_format        = SchemaElement(basestring)     # Keep
        self.edition            = SchemaElement(basestring)     # Keep
        self.num_pages          = SchemaElement(int)            # Keep

class VideoSchema(Schema):
    def setSchema(self):
        self.network_name       = SchemaElement(basestring)     # Keep
        self.cast               = SchemaElement(basestring)     # Keep
        self.director           = SchemaElement(basestring)     # Keep

class ArtistSchema(Schema):
    def setSchema(self):
        self.albums             = SchemaList(ArtistAlbumsSchema())  # Keep
        self.songs              = SchemaList(ArtistSongsSchema())   # Keep

class ArtistAlbumsSchema(Schema):
    def setSchema(self):
        self.album_name         = SchemaElement(basestring)     # Keep

class ArtistSongsSchema(Schema): 
    def setSchema(self):
        self.song_name          = SchemaElement(basestring)     # Keep

class SongSchema(Schema):
    def setSchema(self):
        self.preview_url        = SchemaElement(basestring)     # Keep
        self.album_name         = SchemaElement(basestring)     # Keep

class AlbumSchema(Schema):
    def setSchema(self):
        self.label_studio       = SchemaElement(basestring)     # Keep

class MediaSchema(Schema):
    def setSchema(self):
        self.release_date               = SchemaElement(datetime)       # Keep
        self.track_length               = SchemaElement(basestring)     # Keep
        self.parental_advisory_id       = SchemaElement(basestring)     # Keep
        self.original_release_date      = SchemaElement(basestring)     # Keep
        self.artwork_url                = SchemaElement(basestring)     # Keep
        self.mpaa_rating                = SchemaElement(basestring)     # Keep
        self.artist_display_name        = SchemaElement(basestring)     # Keep
        self.genre                      = SchemaElement(basestring)     # Keep







class EntitySourcesSchema(Schema):
    def setSchema(self):
        self.singleplatform     = SinglePlatformSchema()
        self.factual            = FactualSchema()
        self.tmdb               = TMDBSchema()
        
        self.googlePlaces       = GooglePlacesSchema()
        self.openTable          = OpenTableSchema()
        self.apple              = AppleSchema()
        self.fandango           = FandangoSchema()
        self.netflix            = NetflixSchema()
        self.thetvdb            = TheTVDBSchema()
        self.amazon             = AmazonSchema()
        self.userGenerated      = UserGeneratedSchema()

class GooglePlacesSchema(Schema):
    def setSchema(self):
        self.gid                = SchemaElement(basestring)
        self.gurl               = SchemaElement(basestring)
        self.reference          = SchemaElement(basestring)
        self.googleplaces_id         = SchemaElement(basestring)
        self.googleplaces_timestamp  = SchemaElement(datetime)
        self.googleplaces_source     = SchemaElement(basestring)

class TMDBSchema(Schema):
    def setSchema(self):
        self.tmdb_id            = SchemaElement(basestring)
        self.tmdb_source        = SchemaElement(basestring)
        self.tmdb_timestamp     = SchemaElement(datetime)

class OpenTableSchema(Schema):
    def setSchema(self):
        self.rid                = SchemaElement(basestring)
        self.reserveURL         = SchemaElement(basestring)
        self.countryID          = SchemaElement(basestring)
        self.metroName          = SchemaElement(basestring)
        self.neighborhoodName   = SchemaElement(basestring)

class FactualSchema(Schema):
    def setSchema(self):
        self.faid               = SchemaElement(basestring)
        self.table              = SchemaElement(basestring)
        self.factual_id         = SchemaElement(basestring)
        self.factual_timestamp  = SchemaElement(datetime)
        self.factual_source     = SchemaElement(basestring)
        self.factual_crosswalk  = SchemaElement(datetime)

class SinglePlatformSchema(Schema):
    def setSchema(self):
        self.singleplatform_id  = SchemaElement(basestring)
        self.singleplatform_timestamp  = SchemaElement(datetime)
        self.singleplatform_source = SchemaElement(basestring)

class AppleSchema(Schema):
    def setSchema(self):
        self.aid                = SchemaElement(basestring)
        self.export_date        = SchemaElement(basestring)
        self.is_actual_artist   = SchemaElement(bool)
        self.view_url           = SchemaElement(basestring)
        self.a_popular          = SchemaElement(bool)
        self.match              = AppleMatchSchema()


class FandangoSchema(Schema):
    def setSchema(self):
        self.fid                = SchemaElement(basestring)
        self.f_url              = SchemaElement(basestring)

class AmazonSchema(Schema):
    def setSchema(self):
        self.asin               = SchemaElement(basestring)
        self.amazon_link        = SchemaElement(basestring)
        self.amazon_link_source = SchemaElement(basestring)
        self.amazon_link_timestamp = SchemaElement(datetime)
        self.amazon_underlying  = SchemaElement(basestring)
        self.amazon_underlying_source = SchemaElement(basestring)
        self.amazon_underlying_timestamp = SchemaElement(datetime)

class TheTVDBSchema(Schema):
    def setSchema(self):
        self.thetvdb_id         = SchemaElement(basestring)
        self.num_seasons        = SchemaElement(int)
        self.earliest_air_date  = SchemaElement(datetime)
        self.latest_air_date    = SchemaElement(datetime)
        self.air_time           = SchemaElement(basestring)

class NetflixSchema(Schema):
    def setSchema(self):
        self.nid                = SchemaElement(int)
        self.nrating            = SchemaElement(float)
        self.ngenres            = SchemaList(SchemaElement(basestring))
        self.nurl               = SchemaElement(basestring)
        self.images             = NetflixImageSchema()
        self.images_source      = SchemaElement(basestring)
        self.images_timestamp   = SchemaElement(datetime)


class UserGeneratedSchema(Schema):
    def setSchema(self):
        # TODO (tfischer) adding user_id in temporarily for koopa s.t. entities will 
        # validate for search, and removing required=True from generated_by for the 
        # same reason; this can be switched back after we migrate to boo.
        self.generated_by       = SchemaElement(basestring)
        self.user_id            = SchemaElement(basestring)





