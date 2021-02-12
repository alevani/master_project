import pygame
from pygame.locals import *
import math
from math import cos, sin
from shapely.geometry.point import Point
from utils import Position
import sys
from roboty import PointOfInterest
from time import sleep
import json
import os
import globals

WHITE = (255, 255, 255)
LIGHT_BLACK = (130, 130, 130)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 125, 0)

DECAY100 = (0, 0, 0)
DECAY75 = (50, 50, 50)
DECAY50 = (100, 100, 100)
DECAY25 = (150, 150, 150)
DECAY10 = (200, 200, 200)
LEFT_CLICK = 1
RIGHT_CLICK = 3


class Visualizator:
    def __init__(self, W, H, decay, FILE):
        pygame.display.set_caption(
            'Simulation of task allocation in ant colonies')
        pygame.font.init()
        self.font = pygame.font.Font(pygame.font.get_default_font(), 32)
        self.font_robot_number = pygame.font.Font(
            pygame.font.get_default_font(), 12)
        self.zoom = globals.ZOOM
        self.FILE = FILE
        self.arena_width, self.arena_height = int(
            W * 100 * self.zoom), int(H * 100 * self.zoom)

        self.MARGIN_W, self.MARGIN_H = 50, 50

        SCREEN_WIDTH, SCREEN_HEIGHT = self.arena_width + \
            2 * self.MARGIN_W, self.arena_height + 2 * self.MARGIN_H,

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.robot_size = globals.ROBOT_SIZE

        self.DECAY = decay

        self.DISPLAY_HANDLER = 0
        self.DRAW_BOX = False
        self.DRAW_RAYS = False
        self.DRAW_PATH = False
        self.DRAW_BOTTOM_SENSORS = False
        self.DRAW_DECAY = False

    def pygame_event_manager(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == LEFT_CLICK:
                    poi_type = 2
                else:
                    poi_type = 3

                pos = pygame.mouse.get_pos()
                x, y = self.unscale(pos[0], pos[1])

                index = len(globals.POIs)
                globals.POIs.append(PointOfInterest(
                    Position(x, y), 5000, poi_type, 10))

                x = int(x * 100) + int(globals.W * 100/2)
                y = int(y * 100) + int(globals.H * 100/2)

                globals.PHEROMONES_MAP[x][y] = PointOfInterest(
                    Position(x, y), 5000, poi_type, 10, index)

            elif event.type == QUIT:
                pygame.quit()
                os._exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    pause = True
                    while pause:
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_p:
                                    pause = False

                elif event.key == pygame.K_q:
                    if globals.DO_RECORD:
                        self.FILE.write(json.dumps([globals.CNT, globals.M]))
                        self.FILE.write("\n"+json.dumps(globals.DRAW_POIS))
                        for robot in globals.ROBOTS:
                            self.FILE.write(
                                "\n" + json.dumps(robot.path))
                        self.FILE.close()
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_d:
                    self.DRAW_DECAY = not self.DRAW_DECAY
                    print("[Display] Toggle pheromone decay visualization")
                elif event.key == pygame.K_x:
                    self.DRAW_PATH = not self.DRAW_PATH
                    print("[Display] Toggle Path visualization")
                elif event.key == pygame.K_y:
                    self.DISPLAY_HANDLER += 1

                    if self.DISPLAY_HANDLER == 3:
                        self.DRAW_RAYS = False
                        self.DRAW_BOX = False
                        self.DRAW_BOTTOM_SENSORS = False
                        self.DISPLAY_HANDLER = 0
                        print(
                            "[Display] Sensors and Box visualization desactivated")
                    elif self.DISPLAY_HANDLER == 1:
                        self.DRAW_RAYS = True
                        self.DRAW_BOTTOM_SENSORS = True
                        print("[Display] Sensors visualization activated")
                    elif self.DISPLAY_HANDLER == 2:
                        self.DRAW_BOX = True
                        print(
                            "[Display] Sensors and Box visualization activated")

    def draw_arena(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, WHITE, (self.MARGIN_W, self.MARGIN_H,
                                              self.arena_width, self.arena_height))
        pygame.draw.circle(self.screen, BLACK, (self.scale(0, 0)), 2)

    def draw_areas(self, areas):
        for area in areas:
            x, y = self.scale(area.position.x, area.position.y)

            pygame.draw.polygon(self.screen, area.color, (self.scale(area.right_bottom[0], area.right_bottom[1]), self.scale(
                area.left_bottom[0], area.left_bottom[1]), self.scale(area.left_top[0], area.left_top[1]), self.scale(area.right_top[0], area.right_top[1])))

    def draw_poi(self, pois):
        for poi in pois:
            if poi.is_visible:
                x, y = self.scale(poi.position.x, poi.position.y)
                if poi.type == 2:
                    color = GREEN
                else:
                    color = BLUE
                pygame.draw.circle(self.screen, color,
                                   (x, y), self.zoom//2 + 2)

    def draw_bottom_sensors(self, positions, states):

        for i, position in enumerate(positions):

            color = GRAY
            if states[i] == 1:
                color = RED
            pygame.draw.circle(self.screen, color, self.scale(
                position[0], position[1]), self.zoom)

    def rotate_center(self, image, rect, angle):
        rot_img = pygame.transform.rotate(image, angle)
        rot_rect = rot_img.get_rect(center=rect.center)
        return rot_img, rot_rect

    def draw_robot(self, pos, angle, color, n):

        robot_n = self.font_robot_number.render(str(n), True, GRAY)
        image = pygame.Surface(
            (self.robot_size, self.robot_size), pygame.SRCALPHA, 32)

        rect = image.get_rect()
        x, y = pos
        rect.topleft = (x-self.robot_size/2, y-self.robot_size/2)
        poly = ((0, 0), (0, self.robot_size), (self.robot_size//2, self.robot_size),
                (self.robot_size, self.robot_size//2), (self.robot_size//2, 0))
        pygame.draw.polygon(image, color, poly)

        a = math.degrees(angle)
        img, rect = self.rotate_center(image, rect, a)
        self.screen.blit(img, rect)
        self.screen.blit(robot_n, (pos[0], pos[1]))

    def scale(self, x, y):
        '''
        transpose from particule filter coordinate systemq
        to pygame coordinate system
        '''

        nx = self.arena_width/2 + x*100*self.zoom + self.MARGIN_W
        ny = self.arena_height/2 + y*100*self.zoom * -1 + self.MARGIN_H
        return nx, ny

    def unscale(self, nx, ny):

        x = (nx - self.MARGIN_W - self.arena_width/2)/100/self.zoom
        y = (ny - self.MARGIN_H - self.arena_height/2)/100/self.zoom * -1
        return x, y

    def draw_decay(self, paths):
        if not self.DRAW_DECAY:
            return
        for point in paths:

            color = BLACK
            if point.decay_time > self.DECAY * 0.75:
                color = DECAY100
            elif point.decay_time > self.DECAY * 0.5:
                color = DECAY75
            elif point.decay_time > self.DECAY * 0.25:
                color = DECAY50
            elif point.decay_time > self.DECAY * 0.10:
                color = DECAY25
            else:
                color = DECAY10

            pygame.draw.circle(self.screen, color,
                               self.scale(point.position.x, point.position.y), self.zoom//2+1)

    def draw(self, pos, color, i, path, box, sstate, spos, bottom_sensor_position, bottom_sensor_state, n):
        self.draw_robot(self.scale(pos.x, pos.y),
                        pos.theta, color, n)

        counter = self.font.render(str(i), True, RED, WHITE)
        self.screen.blit(counter, (self.MARGIN_W, self.MARGIN_H))

        if self.DRAW_BOTTOM_SENSORS:
            self.draw_bottom_sensors(
                bottom_sensor_position, bottom_sensor_state)

        if self.DRAW_BOX:
            self.draw_box(box)

        if self.DRAW_RAYS:
            self.draw_rays(spos, sstate, pos.theta)

        if self.DRAW_PATH:
            for p in path:
                self.draw_path(p, color)

    def draw_path(self, path, color):
        pygame.draw.circle(self.screen, color,
                           self.scale(path['x'], path['y']), self.zoom//2+1)

    def draw_box(self, box):
        for point in box:

            pygame.draw.circle(
                self.screen, BLUE, self.scale(point[0], point[1]), self.zoom)

    def draw_rays(self, rays, states, theta):
        for i, ray in enumerate(rays):
            x, y, theta = ray
            x_start, y_start = self.scale(x, y)
            nx_end = x+cos(theta)*0.05
            ny_end = y+sin(theta)*0.05
            x_end, y_end = self.scale(nx_end, ny_end)

            if states[i] == 0:
                color = GRAY
            elif states[i] == 1:
                color = RED

            pygame.draw.line(self.screen, color, (x_start, y_start),
                             (x_end, y_end))
