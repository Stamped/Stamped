# Model classes taken from https://github.com/Instagram/python-instagram/blob/master/instagram/models.py

from utils              import lazyProperty
from libs.Instagram     import globalInstagram
from GenericSource      import GenericSource
from Resolver           import *
from ResolverObject     import ResolverPlace

#class InstagramObject(object):
#
#    def __init__(self, data=None, instagram=None):
#        if instagram is None:
#            instagram = globalInstagram()
#        self.__instagram          = instagram
#        self.__data               = data

class InstagramPlace(ResolverPlace):
    def __init__(self, data, instagram=None):
        ResolverPlace.__init__(self)
        if instagram is None:
            instagram = globalInstagram()
        self.__instagram = instagram
        self.__instagram_id = data['id']
        self.__data = data

    @lazyProperty
    def key(self):
        return self.__instagram_id

    @lazyProperty
    def name(self):
        return self.__data['name']

    @property
    def source(self):
        return 'instagram'

    @lazyProperty
    def coordinates(self):
        return (self.__data['latitude'], self.__data['longitude'])

    @lazyProperty
    def gallery(self):
        media = self.__instagram.place_recent_media(self.__instagram_id)
        gallery = []
        for item in [x for x in media['data'] if x['type'] == 'image']:
            gallery_item = dict()
            gallery_item['url']                 = item['images']['standard_resolution']['url']
            gallery_item['height']              = item['images']['standard_resolution']['height']
            gallery_item['width']               = item['images']['standard_resolution']['width']
#            gallery_item['thumb_url']           = item['images']['thumbnail']['url']
#            gallery_item['thumb_height']        = item['images']['thumbnail']['height']
#            gallery_item['thumb_width']         = item['images']['thumbnail']['width']
            gallery_item['caption']             = item['caption']['text']
            gallery_item['source']              = 'instagram'
            gallery.append(gallery_item)
        #construct a list of dicts containing 'url' and 'caption'
        return gallery

#    @classmethod
#    def object_from_dictionary(cls, entry):
#        point = None
#        if 'latitude' in entry:
#            point = Point(entry.get('latitude'),
#                entry.get('longitude'))
#        location = Location(entry.get('id', 0),
#            point=point,
#            name=entry.get('name', ''))
#        return location

#    def __unicode__(self):
#        return "Location: %s (%s)" % (self.id, self.point)



class InstagramSource(GenericSource):
    """
    Data-Source proxy for Instagram.
    """
    def __init__(self):
        GenericSource.__init__(self, 'instagram',
            groups=[
                'site',
                'coordinates',
                'gallery',
            ],
            kinds=[
                'place',
            ]
        )

    @lazyProperty
    def __instagram(self):
        return globalInstagram()

    def enrichEntityWithEntityProxy(self, proxy, entity, controller=None, decorations=None, timestamps=None):
        GenericSource.enrichEntityWithEntityProxy(self, proxy, entity, controller, decorations, timestamps)
        entity.sources.instagram_id = proxy.key
        return True

    def matchSource(self, query):
        #if query.type == 'place' and query.entity.sources.foursquare_id is not None:
        if query.kind == 'place':
            return self.placeSource(query)

        return self.emptySource

    def placeSource(self, query):
        def gen():
            try:
                if query.entity.sources.foursquare_id is None:
                    return
                places = self.__instagram.place_search(query.entity.sources.foursquare_id)
                if places is not None:
                    for place in places['data']:
                        yield InstagramPlace(place)
            except GeneratorExit:
                pass

        return self.generatorSource(gen())
#        items = self.__instagram.place_search(foursquare_id='4d1bb4017e10a35d5737f982')
#        return listSource(items, constructor=lambda x: Location(data=x))

if __name__ == '__main__':
    demo(InstagramSource(), 'barley swine')