import sys
import pygame
from time import sleep
import math
from random import randint
from utils_simu import Visualizator
from utils import Position
import json
from roboty import PointOfInterest
from pygame.locals import *
import globals

with open('points.json', 'r') as f:
    points = f.readlines()

CNT, M = json.loads(points.pop(0))
POIS = json.loads(points.pop(0))
### GLOBALS ###################################################################
WHITE = (255, 255, 255)
LIGHT_BLACK = (130, 130, 130)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

VISUALIZER = Visualizator(globals.W, globals.H, 0, None)
NBPOINTS = int(CNT) / int(M)

###############################################################################


def simulation(points):
    DISPLAY_HANDLER = 0
    pygame.init()
    fps = 24
    fpsClock = pygame.time.Clock()
    robots_color = [(randint(0, 255), randint(0, 255), randint(0, 255))
                    for _ in range(len(points))]

    # Loads path
    paths = [json.loads(p) for p in points]

    pois = []

    for poi in POIS:
        if poi == []:
            pois.append([])
        else:
            sub = []
            for p in poi:
                sub.append(PointOfInterest(
                    Position(p['position']['x'], p['position']['y']), 0, p['type']))
            pois.append(sub)

    for i in range(int(NBPOINTS) - 1):
        VISUALIZER.draw_arena()
        VISUALIZER.draw_poi(pois[i])
        for p, point in enumerate(points):

            point = json.loads(point)[i]
            VISUALIZER.draw(
                Position(point['x'], point['y'], point['theta']), robots_color[p], i, paths[p][:i], [],  [], [], [], [], 0)

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
