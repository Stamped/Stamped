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
    import inspect, os
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
        self.__basepath = os.path.dirname(inspect.getfile(inspect.currentframe())) + '/instagram/'

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



    def createInstagramImage(self, entity_img_url, user_generated, coordinates, primary_color, secondary_color,
                             user_name, category, types, title, subtitle):
        def dropShadow(image, rounded, offset=(5,5), background=0xffffff, shadow=0x444444,
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
            back = Image.new('RGB', (totalWidth, totalHeight), background)
            if rounded:
                roundedsquare = Image.open(self.__basepath + 'roundedsquare.png')
                roundedsquare = roundedsquare.resize((totalWidth, totalHeight), Image.ANTIALIAS)
                roundedsquare.paste(back, (0, 0), roundedsquare)
                back = roundedsquare

            # Place the shadow, taking into account the offset from the image
            shadowLeft = border + max(offset[0], 0)
            shadowTop = border + max(offset[1], 0)
            back.paste(shadow, (shadowLeft, shadowTop, shadowLeft + image.size[0],
                                shadowTop + image.size[1]) )

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

        def fitImg(entityImg, width, height):
            aspect_ratio = width/float(height)
            w, h = entityImg.size
            print("aspect ratio: %s   w/h:%s" % (aspect_ratio, w/float(h)))

            print( w/float(h))

            if w/float(h) >= aspect_ratio:
                new_height = int( h / (w/float(width)))
                print ('width: %s  new_height: %s' % (width, new_height))
                return entityImg.resize((width, new_height), Image.ANTIALIAS)
            else:
                new_width = int( w / (h/float(height)))
                print ('new_width: %s  height: %s' % (new_width, height))
                return entityImg.resize((new_width, height), Image.ANTIALIAS)

        def transformEntityImage(entityImg, stampImg, rounded, pin, a,b,c,d,e,f,g,h, x, y):
            origAlbumSize = entityImg.size
            xResize = float(origAlbumSize[0])/600
            entityImg = entityImg.resize((600, int(origAlbumSize[1]/xResize)), Image.ANTIALIAS)
            entityImgSize = entityImg.size

#            draw = ImageDraw.Draw(entityImg)
#            draw.line((entityImg.size[0]/2, 0, entityImg.size[0]/2, entityImg.size[1]), fill='#000000')
#            draw.line((0, entityImg.size[1]/2, entityImg.size[0], entityImg.size[1]/2), fill='#000000')
            if rounded:
                buf = Image.new('RGBA', entityImgSize, (255,255,255,0))
                #buf2 = Image.new('RGBA', shadowSize, (255,255,255,0))
                roundedsquare = Image.open(self.__basepath + 'roundedsquare.png')
                entityImg = entityImg.resize((600,600), Image.ANTIALIAS)
                #shadow = shadow.resize((600,600), Image.ANTIALIAS)
                #roundedEntitySquare = roundedsquare.resize(entityImgSize, Image.ANTIALIAS)
                #roundedShadowSquare = roundedsquare.resize(shadowSize, Image.ANTIALIAS)
                buf.paste(entityImg, (0,0), roundedsquare)
                #buf2.paste(shadow, (0,0), roundedsquare)
                entityImg = buf
                #shadow = buf2
            shadow = dropShadow(entityImg, False, background=0xffffff, shadow=0xd0d0d0, offset=(0,0), border=20)#.show()
            shadowSize = shadow.size

            adjust = (((entityImgSize[1]/float(entityImgSize[0]))-1.0) * 0.2) + 1.0

            a = (a*adjust)/2
            b = (b*adjust)/2
            d = (d*adjust)/2
            e = (e*adjust)/2
            g = (g*adjust)/2
            h = (h*adjust)/2

            mode = "RGBA"
            size = 612, 612
            size2x = 612*2, 612*2
            shadowsize2x = 660*2, 660*2
            shadowOffset = x, y

            buf2 = Image.new(mode, size2x, (255,255,255,255))

            mask = Image.new('1', entityImgSize, 1)
            shadowmask = Image.new('1', shadowSize, 1)

            stampImg = stampImg.transform(size2x, Image.PERSPECTIVE, (a,-2.30/2,c,1.006/2,e,f,g,h), Image.BICUBIC)
            entityImg = entityImg.transform(size2x, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)
            shadow = shadow.transform(shadowsize2x, Image.PERSPECTIVE,(a,b,c,d,e,f,g,h), Image.BICUBIC)
            mask = mask.transform(size2x, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)
            shadowmask = shadowmask.transform(shadowsize2x, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)

            stampImg = stampImg.filter(ImageFilter.GaussianBlur)
            stampImg = stampImg.resize((1000,1000), Image.ANTIALIAS)
            if not rounded:
                buf2.paste(shadow, shadowOffset, shadowmask)
            buf2.paste(entityImg, (0, 0), mask)
            buf2.paste(stampImg, (412,-100), stampImg)
            entityImg = buf2.resize(size, Image.ANTIALIAS)

#            if pin:
#                pinImg = Image.open(self.__basepath + 'pin.png')
#                entityImg.paste(pinImg, (278,200), pinImg)

            return entityImg

        def getCategoryIcon(category):
            categoryIcons = Image.open(self.__basepath + 'categoryicons18px.png')
            #icon = Image.new('RGBA', (18,18), (255,255,255,0))

            categories = ('restaurant', 'bar', 'cafe', 'place', 'album', 'song', 'artist', 'film', 'tv_show',
                          'book', 'software', 'other')
            if category not in categories:
                categoryIndex = len(categories)-1
            else:
                categoryIndex = categories.index(category)
            print categoryIndex

            icon = ImageChops.offset(categoryIcons, -20*categoryIndex, 20)
            icon = icon.crop((0, 0, 18, 18))
            #icon.paste(categoryIcons, (20*categoryIndex, 20, (20*categoryIndex)+18, 38))
            return icon

        def getInstagramTextImg(user_name, category, types, title, subtitle):
            textImg = Image.new('RGBA', (612*2,195*2), (255,255,255,255))
            draw = ImageDraw.Draw(textImg)
            titling_gothic = ImageFont.truetype(self.__basepath +"TitlingGothicFB.ttf", 80*2)
            helvetica_neue_bold = ImageFont.truetype(self.__basepath +"HelveticaNeue-Bold.ttf", 24*2)
            helvetica_neue = ImageFont.truetype(self.__basepath + "HelveticaNeue.ttf", 24*2)
            header_nameW, header_nameH = draw.textsize(user_name, font=helvetica_neue_bold)

            prefix = 'a'
            if len(set(types).intersection(set(['establishment', 'app', 'album', 'artist', 'app']))) > 0:
                prefix = 'an'
            type = types[0].replace('_', ' ')
            if type == 'tv':
                type = 'TV show'


            header = ' stamped %s %s' % (prefix, type)
            headerW, headerH = draw.textsize(header, font=helvetica_neue)

            # truncate title text if necessary.  Allow ten pixels of padding on each side and append ellipsis
            final_title = title
            while True:
                titleW, titleH = draw.textsize(final_title, font=titling_gothic)
                if titleW > (612-20)*2:
                    final_title = final_title[:-2] + u"\u2026"
                    continue
                break
            subtitleW, subtitleH = draw.textsize(subtitle, font=helvetica_neue)

            draw.text((612-((headerW+header_nameW)/2),0), user_name, font=helvetica_neue_bold, fill='#939393')
            draw.text((612-((headerW+header_nameW)/2)+header_nameW,0), header, font=helvetica_neue, fill='#939393')
            draw.text((612-(titleW/2),40*2), final_title, font=titling_gothic, fill='#000000')
            draw.line((165*2, 134*2, (612-165)*2, 134*2), fill='#e0e0e0')
            draw.text(((612*2/2)-(subtitleW/2),(134+20)*2), subtitle, font=helvetica_neue, fill='#939393')
            del draw
            textImg = textImg.resize((612, 195), Image.ANTIALIAS)
            icon = getCategoryIcon(category)
            textImg.paste(icon, ((612/2)-(18/2), 124))
            return textImg

        masks = [
                    (270, 270, self.__basepath + 'stamp_mask.png'),
                    (612,  9,  self.__basepath + 'ribbon-top.png'),
                    (612,  9,  self.__basepath + 'ribbon-bottom.png'),
                ]

        gradientImgs = [self.__imageDB.generate_gradient_images(primary_color, secondary_color, x[0], x[1], x[2])
                        for x in masks]
        stamp = gradientImgs[0]
        ribbon_top = gradientImgs[1]
        ribbon_bot = gradientImgs[2]
        shadow_top = Image.open(self.__basepath + 'shadow-top.png')
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

        size = 612,612
        img = Image.new('RGBA', size, (255,255,255,255))

        if coordinates is not None and user_generated == False:
            entity_img_url = "https://maps.googleapis.com/maps/api/staticmap?center=%s&zoom=18&sensor=false&scale=1&format=png&maptype=roadmap&size=600x600&key=AIzaSyAEjlMEfxmlCBQeyw_82jjobQAFjYx-Las" % coordinates

        if entity_img_url is not None:
            #entityImg = Image.open(entity_img_url)
            entityImg = utils.getWebImage(entity_img_url)
            if user_generated:
                boxW = 612
                boxH = 612-195-40-30
                entityImg = fitImg(entityImg, boxW, boxH)
                w, h = entityImg.size
                offsetX = (boxW - w)/2
                offsetY = (boxH - h)/2 + 195+40
                img.paste(entityImg, (offsetX, offsetY))
            else:
                entityImg = transformEntityImage(entityImg, stamp, 'app' in types, coordinates is not None,
                    a,b,c,d,e,f,g,h,x,y)
                img.paste(entityImg, (7,166))
        else:
            pass
        textImg = getInstagramTextImg(user_name, category, types, title, subtitle)
        img.paste(textImg, (0, 40), textImg)
        img.paste(ribbon_top, (0, 0))
        img.paste(shadow_top, (0, ribbon_top.size[1]))
        img.paste(ribbon_bot, (0, 612-ribbon_bot.size[1]))
        img.paste(shadow_bot, (0, 612-ribbon_top.size[1]-shadow_bot.size[1]), shadow_bot)

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

