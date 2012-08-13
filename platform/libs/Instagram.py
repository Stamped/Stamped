#!/usr/bin/env python
from __future__ import absolute_import

"""
"""

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"


__all__ = ['Instagram', 'globalInstagram']

import Globals
import httplib
from libs import oauth as oauth
from logs   import report
try:
    import sys
    import json
    import urllib2
    import logs

    from urllib2            import HTTPError
    from gevent             import sleep
    from pprint             import pprint
    from libs.RateLimiter   import RateLimiter, RateException
    from libs.LRUCache      import lru_cache
    from libs.Memcache      import memcached_function
    from libs.Request       import service_request
    from libs.APIKeys       import get_api_key
    from S3ImageDB          import S3ImageDB
    import utils
    import PIL, Image, ImageFile, ImageFilter, ImageFont, ImageDraw, ImageChops
except:
    report()
    raise

HOST            = 'https://api.instagram.com/v1'
PORT            = '80'
CLIENT_ID       = get_api_key('instagram', 'client_id')
CLIENT_SECRET   = get_api_key('instagram', 'client_secret')

class Instagram(object):
    def __init__(self, client_id=CLIENT_ID, client_secret=CLIENT_SECRET):
        self.__client_id=client_id
        self.__client_secret=client_secret
        self.__consumer = oauth.OAuthConsumer(self.__client_id, self.__client_secret)
        self.__signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
        self.__imageDB = S3ImageDB()

    #def place_search(self, **kwargs):
    #    return self.__instagram('locations/search', **kwargs)

    def place_search(self, foursquare_id, priority='low', timeout=None):
        return self.__instagram('locations/search', priority, timeout, foursquare_v2_id=foursquare_id)

    def place_lookup(self, instagram_id, priority='low', timeout=None):
        return self.__instagram('locations/' + instagram_id, priority, timeout)

    def place_recent_media(self, instagram_id, priority='low', timeout=None):
        return self.__instagram('locations/%s/media/recent' % instagram_id, priority, timeout)

#    def place_recent_media(self, **kwargs):
#        return self.

    # note: these decorators add tiered caching to this function, such that
    # results will be cached locally with a very small LRU cache of 64 items
    # and also cached remotely via memcached with a TTL of 7 days
#    @lru_cache(maxsize=64)
#    @memcached_function(time=7*24*60*60)
    def __instagram(self, service, priority='low', timeout=None, max_retries=3, verb='GET', **params):
        if 'client_id' not in params:
            params['client_id'] = self.__client_id

        if service.startswith('http'):
            url = service
        else:
            url = "%s/%s" % (HOST, service)

        response, content = service_request('instagram',
                                            'GET',
                                            url,
                                            query_params=params,
                                            header={ 'Accept' : 'application/json' },
                                            priority=priority,
                                            timeout=timeout)

        data = json.loads(content)
        return data



    def createInstagramImage(self, entity_img_url, primary_color, secondary_color, user_name, category, title, subtitle):
        def dropShadow( image, offset=(5,5), background=0xffffff, shadow=0x444444,
                        border=8, iterations=3):
            """
            Add a gaussian blur drop shadow to an image.

            image       - The image to overlay on top of the shadow.
            offset      - Offset of the shadow from the image as an (x,y) tuple.  Can be
                          positive or negative.
            background  - Background colour behind the image.
            shadow      - Shadow colour (darkness).
            border      - Width of the border around the image.  This must be wide
                          enough to account for the blurring of the shadow.
            iterations  - Number of times to apply the filter.  More iterations
                          produce a more blurred shadow, but increase processing time.
            """

            # Create the backdrop image -- a box in the background colour with a
            # shadow on it.
            totalWidth = image.size[0] + abs(offset[0]) + 2*border
            totalHeight = image.size[1] + abs(offset[1]) + 2*border
            back = Image.new(image.mode, (totalWidth, totalHeight), background)

            # Place the shadow, taking into account the offset from the image
            shadowLeft = border + max(offset[0], 0)
            shadowTop = border + max(offset[1], 0)
            back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0],
                                shadowTop + image.size[1]] )

            # Apply the filter to blur the edges of the shadow.  Since a small kernel
            # is used, the filter must be applied repeatedly to get a decent blur.
            n = 0
            while n < iterations:
                back = back.filter(ImageFilter.BLUR)
                n += 1

            # Paste the input image onto the shadow backdrop
            imageLeft = border - min(offset[0], 0)
            imageTop = border - min(offset[1], 0)
            #back.paste(image, (imageLeft, imageTop))

            return back


        def transformEntityImage(img, stampImg, a,b,c,d,e,f,g,h, x, y):
            albumArtImg = img
            origAlbumSize = albumArtImg.size
            xResize = float(origAlbumSize[0])/600
            albumArtImg = albumArtImg.resize((600, int(origAlbumSize[1]/xResize)), Image.ANTIALIAS)
            albumSize = albumArtImg.size

            shadow = dropShadow(albumArtImg, background=0xffffff, shadow=0xd0d0d0, offset=(0,0), border=20)#.show()
            shadowSize = shadow.size

            a = (a)/2
            b = (b)/2
            d = (d)/2
            e = (e)/2
            g = (g)/2
            h = (h)/2

            mode = "RGBA"
            size = 612, 612
            size2x = 612*2, 612*2
            shadowOffset = x, y

            transparent = (255,255,255,0)

            buf2 = Image.new(mode, size2x, transparent)

            mask = Image.new('1', albumSize, 1)
            shadowmask = Image.new('1', shadowSize, 1)


            stampImg = stampImg.transform(size2x, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)
            albumArtImg = albumArtImg.transform(size2x, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)
            shadow = shadow.transform(size2x, Image.PERSPECTIVE,(a,b,c,d,e,f,g,h), Image.BICUBIC)
            mask = mask.transform(size2x, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)
            shadowmask = shadowmask.transform(size2x, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)

            stampImg = stampImg.filter(ImageFilter.GaussianBlur)
            stampImg = stampImg.resize((1000,1000), Image.ANTIALIAS)
            buf2.paste(shadow, shadowOffset, shadowmask)
            buf2.paste(albumArtImg, (0, 0), mask)
            buf2.paste(stampImg, (520,-130), stampImg)
            albumArtImg = buf2.resize(size, Image.ANTIALIAS)
            return albumArtImg

        def getCategoryIcon(category):
            categoryIcons = Image.open('categoryicons18px.png')
            #icon = Image.new('RGBA', (18,18), (255,255,255,0))
            categories = ('restaurant', 'bar', 'cafe', 'establishment', 'album', 'song', 'artist', 'film', 'tv_show',
                          'book', 'app', 'other')
            if category not in categories:
                categoryIndex = categories[-1]
            else:
                categoryIndex = categories.index(category)
            print categoryIndex

            icon = ImageChops.offset(categoryIcons, -20*categoryIndex, 20)
            icon = icon.crop((0, 0, 18, 18))
            #icon.paste(categoryIcons, (20*categoryIndex, 20, (20*categoryIndex)+18, 38))
            return icon

        def getInstagramTextImg(user_name, category, title, subtitle):
            textImg = Image.new('RGBA', (612,195), (255,255,255,0))
            draw = ImageDraw.Draw(textImg)
            titling_gothic = ImageFont.truetype("TitlingGothicFB.ttf", 80)
            helvetica_neue_bold = ImageFont.truetype("HelveticaNeue-Bold.ttf", 24)
            helvetica_neue = ImageFont.truetype("HelveticaNeue.ttf", 24)
            header_nameW, header_nameH = draw.textsize(user_name, font=helvetica_neue_bold)
            header = ' stamped a %s' % category
            headerW, headerH = draw.textsize(header, font=helvetica_neue)
            titleW, titleH = draw.textsize(title, font=titling_gothic)
            subtitleW, subtitleH = draw.textsize(subtitle, font=helvetica_neue)
            draw.text(((612/2)-((headerW+header_nameW)/2),0), user_name, font=helvetica_neue_bold, fill='#939393')
            draw.text(((612/2)-((headerW+header_nameW)/2)+header_nameW,0), header, font=helvetica_neue, fill='#939393')
            draw.text(((612/2)-(titleW/2),40), title, font=titling_gothic, fill='#000000')
            draw.line((165, 134, 612-165, 134), fill='#e0e0e0')
            #draw.line((165, 134, 165+129, 134), fill='#dddddd')
            #draw.line((165+129+18, 134, 165+129+18+129, 134), fill='#dddddd')
            draw.text(((612/2)-(subtitleW/2),134+20), subtitle, font=helvetica_neue, fill='#939393')
            del draw
            icon = getCategoryIcon(category)
            textImg.paste(icon, ((612/2)-(18/2), 124))
            return textImg

        masks = [
                    (270, 270, 'temp/stamp_mask2.png'),
                    (612,  9,  'temp/ribbon-top.png'),
                    (612,  9,  'temp/ribbon-bottom.png'),
                ]

        gradientImgs = [self.__imageDB.generate_gradient_images(primary_color, secondary_color, x[0], x[1], x[2])
                        for x in masks]
        stamp = gradientImgs[0]
        ribbon_top = gradientImgs[1]
        ribbon_bot = gradientImgs[2]
        shadow_top = Image.open('temp/shadow-top3.png')
        shadow_bot = shadow_top.transpose(Image.FLIP_TOP_BOTTOM)

        a =  1.77
        b =  -1.61
        c =  298
        d =  1.074
        e =  4.11
        f =  -820
        g =  -0.0001
        h =  0.00215
        x = -44
        y = 1
#        entityImg = Image.open(entity_img_url)
        entityImg = utils.getWebImage(entity_img_url)
        entityImg = transformEntityImage(entityImg, stamp, a,b,c,d,e,f,g,h,x,y)

        albumOffset = 7, 166

        size = 612,612
        img = Image.new('RGBA', size)
        img.paste(entityImg, albumOffset)
        textImg = getInstagramTextImg(user_name, category, title, subtitle)
        img.paste(textImg, (0, 40))
        img.paste(ribbon_top, (0, 0))
        img.paste(shadow_top, (0, ribbon_top.size[1]))
        img.paste(ribbon_bot, (0, 612-ribbon_bot.size[1]))
        img.paste(shadow_bot, (0, 612-ribbon_top.size[1]-shadow_bot.size[1]))

        return img


__globalInstagram = None

def globalInstagram():
    global __globalInstagram

    if __globalInstagram is None:
        __globalInstagram = Instagram()

    return __globalInstagram

def demo(foursquare_id, **params):
    instagram = Instagram()
    place = instagram.place_search(foursquare_id)
    recent_media = instagram.place_recent_media(place['data'][0]['id'])
    pprint(recent_media)


if __name__ == '__main__':
    import sys
    params = {}
    foursquare_id = '4d1bb4017e10a35d5737f982'
    if len(sys.argv) > 1:
        foursquare_id = sys.argv[1]
    if len(sys.argv) > 2:
        params = {}
        for arg in sys.argv[2:]:
            pair = arg.split('=')
            params[pair[0]] = pair[1]
    demo(foursquare_id, **params)

