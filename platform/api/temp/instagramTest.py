import Globals
import utils
import PIL, Image, ImageFile, ImageFilter
from ImageColor import getrgb




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

def createImage(a,b,c,d,e,f,g,h):


    #albumArtUrl = "http://a1.mzstatic.com/us/r1000/030/Music/88/b5/b2/mzi.shgvhklf.600x600-75.jpg"
    #albumArtImg = utils.getWebImage(albumArtUrl)
    albumArtImg = Image.open('refused.jpg')
    albumSize = albumArtImg.size


    shadow = dropShadow(albumArtImg, background=0xffffff, shadow=0xd0d0d0, offset=(0,0), border=20)#.show()
    shadowSize = shadow.size


    #albumArtImg.save('instagramtest.png', 'png')

    mode = "RGBA"
    size = 612, 612
    albumOffset = 40, 100
    shadowOffset = 20, 105

    transparent = (
        255,
        255,
        255,
        0
        )

    buf = Image.new(mode, size, transparent)#getrgb("#000000"))

    mask = Image.new('1', albumSize, 1)
    shadowmask = Image.new('1', shadowSize, 1)

    #albumArtImg = albumArtImg.resize(albumSize, Image.ANTIALIAS)
    albumArtImg = albumArtImg.transform(size, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)
    shadow = shadow.transform(size, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)
    mask = mask.transform(size, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)
    shadowmask = shadowmask.transform(size, Image.PERSPECTIVE, (a,b,c,d,e,f,g,h), Image.BICUBIC)


    #makeTransparent(albumArtImg)

    buf.paste(shadow, shadowOffset, shadowmask)
    buf.paste(albumArtImg, albumOffset, mask)

    #makeTransparent(buf)

    buf.save('instagramtest.png', 'png')


import sys, pygame
pygame.init()

size = width, height = 612, 612
speed = [2, 2]
black = 0, 0, 0
white = 255, 255, 255

screen = pygame.display.set_mode(size)


#a = 1.67
#b = -1.54
#c = 294
#d = 0.957
#e = 3.56
#f = -650#-753
#g = -0.00022
#h = 0.00174
a = 1.75
b = -1.54
c = 368
d = 1.02
e = 3.72
f = -756
g = -0.00017
h = 0.00187
createImage(a,b,c,d,e,f,g,h)

ball = pygame.image.load("instagramtest.png")
background = pygame.image.load("instagram.jpg")
ballrect = ball.get_rect()

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
    if pressed[pygame.K_f]: f = 3 * (mousex-300)
    if pressed[pygame.K_g]: g = 0.00001 * (mousex-300)
    if pressed[pygame.K_h]: h = 0.00001 * (mousex-300)
    if pressed[pygame.K_r]:
        b=c=d=f=g=h = 0
        a = e = 1

    #h += 0.00001



    createImage(a,b,c,d,e,f,g,h)
    ball = pygame.image.load("instagramtest.png")

    ballrect = ball.get_rect()


    text = font.render("a:%s b:%s c:%s d:%s e:%s f:%s g:%s h:%s  key:%s x:%s y:%s" % (a,b,c,d,e,f,g,h, key, mousex, mousey), 1, (5, 5, 5))
    textpos = text.get_rect(centerx=ball.get_width()/2)

    screen.fill(white)
    #screen.blit(background, ballrect)
    if not pressed[pygame.K_z]:
        screen.blit(ball, ballrect)
    screen.blit(text, textpos)
    pygame.display.flip()
    clock.tick(60)