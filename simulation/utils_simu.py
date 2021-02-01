import pygame
from pygame.locals import *
import math
from math import cos, sin
from shapely.geometry.point import Point

WHITE = (255, 255, 255)
LIGHT_BLACK = (130, 130, 130)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)


class PheromonePoint:
    def __init__(self, position, decay_time):
        self.position = position
        self.point = Point(position.x, position.y).buffer(0.05)
        self.decay_time = decay_time


class Visualizator:
    def __init__(self, zoom_factor, W, H, robot_size):
        self.zoom = zoom_factor
        self.arena_width, self.arena_height = int(
            W * 100 * self.zoom), int(H * 100 * self.zoom)

        self.MARGIN_W, self.MARGIN_H = 50, 50

        SCREEN_WIDTH, SCREEN_HEIGHT = self.arena_width + \
            2 * self.MARGIN_W, self.arena_height + 2 * self.MARGIN_H,

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.robot_size = robot_size

        self.DRAW_BOX = False
        self.DRAW_RAYS = False
        self.DRAW_PATH = False
        self.DRAW_BOTTOM_SENSORS = False

    def draw_arena(self):
        self.screen.fill((0, 0, 0))
        pygame.draw.rect(self.screen, WHITE, (self.MARGIN_W, self.MARGIN_H,
                                              self.arena_width, self.arena_height))
        pygame.draw.circle(self.screen, BLACK, (self.scale(0, 0)), 2)

    def draw_bottom_sensors(self, positions):
        for position in positions:
            pygame.draw.circle(self.screen, GRAY, self.scale(
                position[0], position[1]), 5)

    def rotate_center(self, image, rect, angle):
        rot_img = pygame.transform.rotate(image, angle)
        rot_rect = rot_img.get_rect(center=rect.center)
        return rot_img, rot_rect

    def draw_robot(self, pos, angle, color):
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

    def scale(self, x, y):
        '''
        transpose from particule filter coordinate system
        to pygame coordinate system
        '''
        tresh = 20
        nx = self.arena_width/2 + x*100*self.zoom + \
            self.MARGIN_W - self.robot_size/2 + tresh
        ny = self.arena_height/2 + y*100*self.zoom * -1 + \
            self.MARGIN_H - self.robot_size/2+tresh
        return nx, ny

    def draw(self, robot, color, i, path, box, sstate, spos, bottom_sensor_position):
        self.draw_robot(self.scale(robot.x, robot.y), robot.q, color)

        if self.DRAW_BOTTOM_SENSORS:
            self.draw_bottom_sensors(bottom_sensor_position)

        if self.DRAW_BOX:
            self.draw_box(box)

        if self.DRAW_RAYS:
            self.draw_rays(spos, sstate, robot.q)

        if self.DRAW_PATH:
            #! take the last 1000 points, simulate evaporation
            # path = path[-200:]
            for point in path:
                self.draw_path(point, color)

    def draw_path(self, path, color):
        pygame.draw.circle(self.screen, color,
                           self.scale(path['x'], path['y']), 1.5)

    def draw_box(self, box):
        for point in box:
            pygame.draw.circle(
                self.screen, RED, self.scale(point[0], point[1]), 5)

    def draw_rays(self, rays, states, q):
        for i, ray in enumerate(rays):
            x, y, q = ray
            x_start, y_start = self.scale(x, y)
            nx_end = x+cos(q)*0.05
            ny_end = y+sin(q)*0.05
            x_end, y_end = self.scale(nx_end, ny_end)

            if states[i] == 0:
                color = GRAY
            elif states[i] == 1:
                color = RED

            pygame.draw.line(self.screen, color, (x_start, y_start),
                             (x_end, y_end))
