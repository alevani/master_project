import sys
import pygame
from time import sleep
import math
import json
from pygame.locals import *

with open('points.json', 'r') as f:
    points = f.readlines()

header = json.loads(points.pop(0))

### GLOBALS ###################################################################

ZOOM = 4
ARENA_WIDTH, ARENA_HEIGHT = int(
    header['W'] * 100 * ZOOM), int(header['H'] * 100 * ZOOM)
MARGIN_W, MARGIN_H = 50, 50
SCREEN_WIDTH, SCREEN_HEIGHT = ARENA_WIDTH + \
    2 * MARGIN_W, ARENA_HEIGHT + 2 * MARGIN_H,

ROBOT_SIZE = 40

WHITE = (255, 255, 255)
LIGHT_BLACK = (130, 130, 130)
RED = (255, 0, 0)

DRAW_BOX = False
DRAW_RAYS = False

###############################################################################

# def draw_ray(screen, start, end):
#     pygame.draw.line(screen, red, start, end)


def draw_arena(screen):
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, WHITE, (MARGIN_W, MARGIN_H,
                                     ARENA_WIDTH, ARENA_HEIGHT))


def rotate_center(image, rect, angle):
    rot_img = pygame.transform.rotate(image, angle)
    rot_rect = rot_img.get_rect(center=rect.center)
    return rot_img, rot_rect


def draw_robot(screen, pos, angle, virtual=True, size=ROBOT_SIZE):
    image = pygame.Surface((size, size), pygame.SRCALPHA, 32)

    rect = image.get_rect()
    x, y = pos
    rect.topleft = (x-size/2, y-size/2)
    poly = ((0, 0), (0, size), (size//2, size), (size, size//2), (size//2, 0))
    pygame.draw.polygon(image, LIGHT_BLACK, poly)

    a = math.degrees(angle)
    img, rect = rotate_center(image, rect, a)
    screen.blit(img, rect)


def scale(x, y):
    '''
    transpose from particule filter coordinate system
    to pygame coordinate system
    '''
    tresh = 20
    nx = ARENA_WIDTH/2 + x*100*ZOOM + MARGIN_W - ROBOT_SIZE/2 + tresh
    ny = ARENA_HEIGHT/2 + y*100*ZOOM * -1 + MARGIN_H - ROBOT_SIZE/2+tresh
    return nx, ny


def draw(screen, point):
    global DRAW_BOX, DRAW_RAYS
    draw_arena(screen)

    point = json.loads(point)
    x, y, a = point['rpos']['x'], point['rpos']['y'], point['rpos']['a']
    draw_robot(screen, scale(x, y), a)

    if DRAW_BOX:
        draw_box(screen, point['bpos'])

    if DRAW_RAYS:
        draw_rays(screen, point['spos'])


def draw_box(screen, box):
    for point in box:
        pygame.draw.circle(screen, RED, scale(point[0], point[1]), 5)


def draw_rays(screen, rays):
    for ray in rays:
        x_start, y_start = scale(ray[0][0], ray[0][1])
        x_end, y_end = scale(ray[1][0], ray[1][1])
        pygame.draw.line(screen, RED, (x_start, y_start),
                         (x_end, y_end))


def simulation(points):
    global DRAW_BOX, DRAW_RAYS
    DISPLAY_HANDLER = 0
    pygame.init()
    fps = 24
    fpsClock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    for point in points:
        draw(screen, point)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    sleep(5)
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_y:
                    DISPLAY_HANDLER += 1

                    if DISPLAY_HANDLER == 3:
                        DRAW_RAYS = False
                        DRAW_BOX = False
                        DISPLAY_HANDLER = 0
                        print("[Display] Rays and Box visualization desactivated")
                    elif DISPLAY_HANDLER == 1:
                        DRAW_RAYS = True
                        print("[Display] Rays visualization activated")
                    elif DISPLAY_HANDLER == 2:
                        DRAW_BOX = True
                        print("[Display] Rays and Box visualization activated")

        pygame.display.flip()  # render drawing
        fpsClock.tick(fps)


simulation(points)
