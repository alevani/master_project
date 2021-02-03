import sys
import pygame
from time import sleep
import math
from random import randint
from utils_simu import Visualizator
from utils import Position
import json
from pygame.locals import *
import globals

with open('points.json', 'r') as f:
    points = f.readlines()

CNT, M = json.loads(points.pop(0))
### GLOBALS ###################################################################

ZOOM = 4
ARENA_WIDTH, ARENA_HEIGHT = int(
    globals.W * 100 * ZOOM), int(globals.H * 100 * ZOOM)
MARGIN_W, MARGIN_H = 50, 50
SCREEN_WIDTH, SCREEN_HEIGHT = ARENA_WIDTH + \
    2 * MARGIN_W, ARENA_HEIGHT + 2 * MARGIN_H,

ROBOT_SIZE = 40

WHITE = (255, 255, 255)
LIGHT_BLACK = (130, 130, 130)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

VISUALIZER = Visualizator(ZOOM, globals.W, globals.H, ROBOT_SIZE, 0, None)
NBPOINTS = int(CNT) / int(M)

###############################################################################


def simulation(points):
    DISPLAY_HANDLER = 0
    pygame.init()
    fps = 24
    fpsClock = pygame.time.Clock()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    robots_color = [(randint(0, 255), randint(0, 255), randint(0, 255))
                    for _ in range(len(points))]

    # Loads path
    paths = [json.loads(p)[1] for p in points]

    for i in range(int(NBPOINTS)):
        VISUALIZER.draw_arena()
        for p, point in enumerate(points):

            point = json.loads(point)[0][i]
            VISUALIZER.draw(
                Position(point['x'], point['y'], point['q']), robots_color[p], i, paths[p], [],  [], [], [], [], [])

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
                    if event.key == pygame.K_x:
                        VISUALIZER.DRAW_PATH = not VISUALIZER.DRAW_PATH
                        print("[Display] Toggle path visualization")

        pygame.display.flip()  # render drawing
        fpsClock.tick(fps)


simulation(points)
