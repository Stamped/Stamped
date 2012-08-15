import Globals
import utils
from StringIO           import StringIO
import os, time, zlib, struct, array, random, urllib2
import PIL, Image, ImageFile, ImageFilter, ImageFont, ImageDraw, ImageChops
from ImageColor import getrgb

from libs.Instagram import Instagram

import sys, pygame
pygame.init()

instagram = Instagram()

size = width, height = 612, 612
speed = [2, 2]
black = 0, 0, 0
white = 255, 255, 255

screen = pygame.display.set_mode(size)


#a =  1.77
#b =  -1.61
#c =  298
#d =  1.074
#e =  4.11
#f =  -820
#g =  -0.0001
#h =  0.00215
#x = -44
#y = 1
a =  1.92
b =  -1.61
c =  298
d =  1.074
e =  4.42
f =  -820
g =  -0.0001
h =  0.00215
x = -44
y = 1

ball = pygame.image.load("instagramtest.png")
background = pygame.image.load("background3.png")
ballrect = ball.get_rect()

#imgs = generate_gradient_images('ff0000', '0000ff')
#stamp = imgs[0]
#ribbon_top = imgs[1]
#ribbon_bot = imgs[2]
#stamp.save('stamp.png')
#ribbon_top.save('ribbon_top.png')
#ribbon_bot.save('ribbon_bot.png')
##stamp = pygame.image.load("stamp.png")
#ribbon_bot = pygame.image.load("ribbon_bot.png")
#ribbon_top = pygame.image.load("ribbon_top.png")

font = pygame.font.Font(None, 24)
clock = pygame.time.Clock()


img = instagram.createInstagramImage('purplerain.jpg', False, None, 'FF0000', '0000FF', 'ml', 'film', ['movie_theater'], 'The Dark Knight Keeps on Rising and BLAAARGH', '2012')
img.save('instagramtest.png')

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
    if pressed[pygame.K_e]: e = 1 + (0.02 * (mousex-300))
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
    if pressed[pygame.K_p]:
        file = "batman.jpg"
    else:
        file = 'purplerain.jpg'

    ball = pygame.image.load("instagramtest.png")

    ballrect = ball.get_rect()

    text = font.render("a:%s b:%s c:%s d:%s e:%s f:%s g:%s h:%s  key:%s x:%s y:%s" % (a,b,c,d,e,f,g,h, key, mousex, mousey), 1, (5, 5, 5))
    #text = font.render("x:%s  y:%s" % (x, y), 1, (5, 5, 5))
    textpos = text.get_rect(centerx=ball.get_width()/2)

    screen.fill(white)
    #screen.blit(background, ballrect)
    if not pressed[pygame.K_z]:
        screen.blit(ball, ballrect)
    screen.blit(text, textpos)
    #screen.blit(ribbon_top, (0, 0))
    pygame.display.flip()
    clock.tick(60)