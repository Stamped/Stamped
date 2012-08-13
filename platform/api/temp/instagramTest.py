import Globals
import utils
from StringIO           import StringIO
import os, time, zlib, struct, array, random, urllib2
import PIL, Image, ImageFile, ImageFilter, ImageFont, ImageDraw
from ImageColor import getrgb



def generate_gradient_images(primary_color, secondary_color):
    def output_chunk(out, chunk_type, data):
        out.write(struct.pack("!I", len(data)))
        out.write(chunk_type)
        out.write(data)
        checksum = zlib.crc32(data, zlib.crc32(chunk_type))
        out.write(struct.pack("!i", checksum))

    def get_data(width, height, rgb_func):
        fw = float(width)
        fh = float(height)
        compressor = zlib.compressobj()
        data = array.array("B")
        for y in range(height):
            data.append(0)
            fy = float(y)
            for x in range(width):
                fx = float(x)
                data.extend([min(255, max(0, int(v * 255)))\
                             for v in rgb_func(fx / fw, fy / fh)])
        compressed = compressor.compress(data.tostring())
        flushed = compressor.flush()
        return compressed + flushed

    def linear_gradient(start_value, stop_value, start_offset=0.0, stop_offset=1.0):
        return lambda offset: (start_value + ((offset - start_offset) /\
                                              (stop_offset - start_offset) *\
                                              (stop_value - start_value))) / 255.0

    def gradient(DATA):
        def gradient_function(x, y):
            initial_offset = 0.0
            v = x + y
            for offset, start, end in DATA:
                if v < offset:
                    r = linear_gradient(start[0], end[0], initial_offset, offset)(v)
                    g = linear_gradient(start[1], end[1], initial_offset, offset)(v)
                    b = linear_gradient(start[2], end[2], initial_offset, offset)(v)
                    return r, g, b
                initial_offset = offset
            return end[0] / 255.0, end[1] / 255.0, end[2] / 255.0
        return gradient_function

    def rgb(c):
        split = (c[0:2], c[2:4], c[4:6])
        return [int(x, 16) for x in split]

    def generateImage(mask, width, height, rgb_func):
        out = StringIO()
        out.write(struct.pack("8B", 137, 80, 78, 71, 13, 10, 26, 10))
        output_chunk(out, "IHDR", struct.pack("!2I5B", width, height, 8, 2, 0, 0, 0))
        output_chunk(out, "IDAT", get_data(width, height, rgb_func))
        output_chunk(out, "IEND", "")
        out.seek(0)

        image = Image.open(out)
        __dir__  = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(__dir__, mask)
        mask = Image.open(filepath).convert('RGBA').split()[3]
        image.putalpha(mask)

        return image
        #self._addPNG('logos/%s' % filename, image)

    output = [
        (195, 195, 'stamped_logo_mask.png'),
        (612,  16,  'ribbon-top.png'),
        (612,  16,  'ribbon-bottom.png'),
    ]

    imgs = []
    for width, height, mask in output:
        imgs.append(generateImage(mask, width, height, gradient([
            (2.0, rgb(primary_color), rgb(secondary_color)),
        ])))
    return imgs




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


def makeTransparent(img):
    img = img.convert("RGBA")
    pixdata = img.load()

    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y] == (0, 0, 0, 255):
                pixdata[x, y] = (255, 255, 255, 0)
                #img.save("img2.png", "PNG")


def createInstagramImage():
    def transformEntityImage(img, a,b,c,d,e,f,g,h, x, y):
        albumArtImg = img
        albumSize = albumArtImg.size
        xResize = float(albumSize[0])/600
        albumArtImg = albumArtImg.resize((500, int(albumSize[1]/xResize)), Image.ANTIALIAS)
        albumSize = albumArtImg.size

        shadow = dropShadow(albumArtImg, background=0xffffff, shadow=0xd0d0d0, offset=(0,0), border=20)#.show()
        shadowSize = shadow.size

        yTranslate = int((600-albumSize[1])/4)
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

        buf = Image.new(mode, size, transparent)#getrgb("#000000"))
        buf2 = Image.new(mode, size2x, transparent)

        mask = Image.new('1', albumSize, 1)
        shadowmask = Image.new('1', shadowSize, 1)

        albumArtImg = albumArtImg.transform(size2x, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)
        shadow = shadow.transform(size2x, Image.PERSPECTIVE,(a,b,c,d,e,f,g,h), Image.BICUBIC)
        mask = mask.transform(size2x, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)
        shadowmask = shadowmask.transform(size2x, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)

        buf2.paste(shadow, shadowOffset, shadowmask)
        buf2.paste(albumArtImg, (0, 0), mask)
        albumArtImg = buf2.resize(size, Image.ANTIALIAS)


        #buf.paste(albumArtImg, albumOffset)

        #buf.save('instagramtest.png', 'png')
        #return buf
        return albumArtImg, yTranslate

    def drawInstagramText(img):
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("fbEiMTd1F3B3c35Z4OrK.ttf", 80)
        textW, textH = draw.textsize("Purple Rain", font=font)
        draw.text(((612/2)-(textW/2),80), "Purple Rain", font=font, fill='#000000')
        draw.line((0, 0) + img.size, fill=128)
        del draw
        return img

    gradientImgs = generate_gradient_images('ff0000', '0000ff')
    stamp = gradientImgs[0]
    ribbon_top = gradientImgs[1]
    ribbon_bot = gradientImgs[2]

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
    entityImg = Image.open('batman.jpg')
    entityImg, yTranslate = transformEntityImage(entityImg, a,b,c,d,e,f,g,h,x,y)

    albumOffset = 7, 166+yTranslate

    size = 612,612
    img = Image.new('RGBA', size)
    img.paste(entityImg, albumOffset)
    img = drawInstagramText(img)
    img.paste(ribbon_top, (0, 0))
    img.paste(ribbon_bot, (0, 612-16))

    return img


import sys, pygame
pygame.init()

size = width, height = 612, 612
speed = [2, 2]
black = 0, 0, 0
white = 255, 255, 255

screen = pygame.display.set_mode(size)


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

ball = pygame.image.load("instagramtest.png")
background = pygame.image.load("background2.jpg")
ballrect = ball.get_rect()

imgs = generate_gradient_images('ff0000', '0000ff')
stamp = imgs[0]
ribbon_top = imgs[1]
ribbon_bot = imgs[2]
stamp.save('stamp.png')
ribbon_top.save('ribbon_top.png')
ribbon_bot.save('ribbon_bot.png')
#stamp = pygame.image.load("stamp.png")
ribbon_bot = pygame.image.load("ribbon_bot.png")
ribbon_top = pygame.image.load("ribbon_top.png")

font = pygame.font.Font(None, 24)
clock = pygame.time.Clock()



key = 0

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()
    #        if event.type == pygame.KEYUP:
    #            #up
    #            if event.key == 273:

    mod = None

    mousex, mousey = pygame.mouse.get_pos()

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_a]: a = 1 + (0.01 * (mousex-300))
    if pressed[pygame.K_b]: b = 0.01 * (mousex-300)
    if pressed[pygame.K_c]: c = 2 * (mousex-300)
    if pressed[pygame.K_d]: d = 0.003 * (mousex-100)
    if pressed[pygame.K_e]: e = 1 + (0.01 * (mousex-300))
    if pressed[pygame.K_f]: f = 4 * (mousex-300)
    if pressed[pygame.K_g]: g = 0.00001 * (mousex-300)
    if pressed[pygame.K_h]: h = 0.00001 * (mousex-300)
    if pressed[pygame.K_r]:
        a = 1.77
        b = -1.61
        c = 298
        d = 1.074
        e = 4.11
        f = -820
        g = -0.0001
        h = 0.00215
    if pressed[pygame.K_s]:
        x = mousex - 100
        y = mousey - 100
    if pressed[pygame.K_x]:
        factor = (mousex - 300) / 1000
        factor = 0.01
        a = a*(1.0+factor)
        b = b*(1.0+factor)
        c = c*(1.0+factor)
        d = d*(1.0+factor)
        e = e*(1.0+factor)
        f = f*(1.0+factor)
        g = g*(1.0+factor)
        h = h*(1.0+factor)

    img = createInstagramImage()
    img.save('instagramtest.png')
    ball = pygame.image.load("instagramtest.png")

    ballrect = ball.get_rect()


    #text = font.render("a:%s b:%s c:%s d:%s e:%s f:%s g:%s h:%s  key:%s x:%s y:%s" % (a,b,c,d,e,f,g,h, key, mousex, mousey), 1, (5, 5, 5))
    text = font.render("x:%s  y:%s" % (x, y), 1, (5, 5, 5))
    textpos = text.get_rect(centerx=ball.get_width()/2)



    screen.fill(white)
    #screen.blit(background, ballrect)
    if not pressed[pygame.K_z]:
        screen.blit(ball, ballrect)
    screen.blit(text, textpos)
    #screen.blit(ribbon_top, (0, 0))
    pygame.display.flip()
    clock.tick(60)