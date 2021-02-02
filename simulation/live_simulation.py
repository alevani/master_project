import shapely
from shapely.affinity import rotate
from shapely.geometry import LinearRing, LineString, Point, Polygon
from shapely.geometry.point import Point
from shapely.ops import nearest_points

import threading

import numpy as np
from numpy import sin, cos, pi, sqrt, zeros
import math

from roboty import Robot
from utils_simu import Visualizator
from utils_simu import PheromonePoint

from pygame.locals import *
import pygame

import sys
import json
from copy import deepcopy

from utils import Position
from utils import distance

from time import sleep
import math

from random import *

# IDEAS
# One can play with the buffers of the pheromone sensing to simulate crappy hardware of ant
#   -> as in, right now the detection pretty wide, maybe induce some noise with a randmoness in the buffer?

# Checking every point for decay is super slow, if I wasn't working with kinetic movement I could have a map
# of pixel and a absolute position for pheromones, and they finding if the sensor is on a point would only take O(1)
# but storage would be affected.
########

### GLOBALS ###################################################################

# WORLD
# TODO Redo measurements of the robot's sensors' position

#! Speed of robot in simulation, keep FPS at 60 and only change the below variable to variate the speed
ROBOT_TIMESTEP = 1  # 1/ROBOT_TIMESTEP equals update frequency of robot

# timestep in kinematics< sim (probably don't touch..)
SIMULATION_TIMESTEP = .01

R = 0.02  # radius of wheels in meters
L = 0.095  # distance between wheels in meters

LEFT_WHEEL_VELOCITY = 1
RIGHT_WHEEL_VELOCITY = 1

# W = 1.94  # width of arena
# H = 1.18  # height of arena
W = 4
H = 3

TOP_BORDER = H/2  # 0.59
BOTTOM_BORDER = -H/2
RIGHT_BORDER = W/2  # 0.97
LEFT_BORDER = -W/2

WORLD = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

BOTTOM_LIGHT_SENSORS_POSITION = [
    Position(-0.0097, 0.07), Position(0.0097, 0.07)]  # ! false measurments

# Assuming the robot is looking north
PROXIMITY_SENSORS_POSITION = [Position(-0.05,   0.06, math.radians(130)),
                              Position(-0.025,  0.075, math.radians(108.5)),
                              Position(0, 0.0778, math.radians(90)),
                              Position(0.025,  0.075, math.radians(71.5)),
                              Position(0.05,   0.06, math.radians(50))]


# PYGAME
ZOOM = 4
ROBOT_SIZE = 40
DECAY = 2500
VISUALIZER = Visualizator(ZOOM, W, H, ROBOT_SIZE, DECAY)
DISPLAY_HANDLER = 0
###############################################################################


def decay_check():
    for i, point in enumerate(PHEROMON_PATH):
        point.decay_time -= 1
        if point.decay_time <= 0:
            PHEROMON_PATH.pop(i)

    # threading.Timer(.1, decay_check).start()


def get_proximity_sensor_values(rays, robot, robots):
    dists = []

    # Wall detection
    for index, ray in enumerate(rays):
        dists.append(distance(WORLD.intersection(ray),
                              robot.proximity_sensors[index].x, robot.proximity_sensors[index].y))

    # Robot detection
    for r in robots:
        # Don't check ourselves
        if r.number != robot.number:
            for index, ray in enumerate(rays):
                if r.is_sensing(ray):
                    p1, p2 = nearest_points(r.get_collision_box(), Point(
                        robot.proximity_sensors[index].x, robot.proximity_sensors[index].y))
                    dists[index] = distance(p1, p2.x, p2.y)

    return dists
    # return [distance(WORLD.intersection(ray), sensors[index].x, sensors[index].y) for index, ray in enumerate(rays)]

### Start's variables #########################################################


# Robot's starting position
x = 0
y = 0
q = math.radians(90)

CNT = 15000
M = 20

ROBOTS = []
R1 = Robot(1, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-0.2, 0, math.radians(0)),
           (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)
R5 = Robot(5, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-0.2, 0.2, math.radians(0)),
           (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)
R4 = Robot(4, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-0.2, -.20, math.radians(0)),
           (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)

R2 = Robot(2, deepcopy(PROXIMITY_SENSORS_POSITION), Position(0.20, 0, math.radians(180)),
           (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)
R3 = Robot(3, deepcopy(PROXIMITY_SENSORS_POSITION), Position(0.20, 0.20, math.radians(
    180)), (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)
R6 = Robot(6, deepcopy(PROXIMITY_SENSORS_POSITION), Position(0.20, -0.20, math.radians(180)),
           (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)

R7 = Robot(7, deepcopy(PROXIMITY_SENSORS_POSITION), Position(0.40, -0.40, math.radians(180)),
           (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)

R8 = Robot(8, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-0.40, 0.40, math.radians(0)),
           (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)

ROBOTS.append(R1)
ROBOTS.append(R2)
ROBOTS.append(R3)
ROBOTS.append(R4)
ROBOTS.append(R5)
ROBOTS.append(R6)
ROBOTS.append(R7)
ROBOTS.append(R8)

PHEROMON_PATH = []

###############################################################################

#! Il y a beaucoup de points qui sont enregistré, peut-être que je devrais faire en sorte d'avoir une option
#! pour choisir quels set de points vont être activement enregistré ou non.
pygame.init()
fps = 60
fpsClock = pygame.time.Clock()
cnt = 0
while True:
    cnt += 1
    VISUALIZER.draw_arena()
    for robot in ROBOTS:

        if robot.has_collided:
            break

        rays, DRAW_proximity_sensor_position = robot.create_rays(W, H)

        proximity_sensor_values = get_proximity_sensor_values(
            rays, robot, ROBOTS)

        # Robot's brain
        bottom_sensor_states = robot.get_bottom_sensor_states(PHEROMON_PATH)

        proximity_sensors_state = robot.get_proximity_sensor_state(
            proximity_sensor_values)

        if proximity_sensors_state == (0, 1, 0):
            if randint(0, 1):
                robot.RIGHT_WHEEL_VELOCITY = -1
                robot.LEFT_WHEEL_VELOCITY = 1
            else:
                robot.RIGHT_WHEEL_VELOCITY = 1
                robot.LEFT_WHEEL_VELOCITY = -1
        elif proximity_sensors_state == (1, 0, 0) or proximity_sensors_state == (1, 1, 0):
            robot.RIGHT_WHEEL_VELOCITY = -1
            robot.LEFT_WHEEL_VELOCITY = 1
        elif proximity_sensors_state == (0, 0, 1) or proximity_sensors_state == (0, 1, 1):
            robot.RIGHT_WHEEL_VELOCITY = 1
            robot.LEFT_WHEEL_VELOCITY = -1
        #  I am stuck state
        elif proximity_sensors_state == (1, 0, 1) or proximity_sensors_state == (1, 1, 1):
            # TODO robot somwhow still get stuck in the corner
            robot.RIGHT_WHEEL_VELOCITY = -1
            robot.LEFT_WHEEL_VELOCITY = -1
        else:
            #! right now it cannot take 90 degree angle
            #! could be because: wheel speed, or how many points are added (maybe it misses the path as it goes through it)
            if bottom_sensor_states == (1, 0):
                robot.RIGHT_WHEEL_VELOCITY = 1
                robot.LEFT_WHEEL_VELOCITY = 0
            elif bottom_sensor_states == (1, 1):
                pass
            elif bottom_sensor_states == (0, 1):
                robot.RIGHT_WHEEL_VELOCITY = 0
                robot.LEFT_WHEEL_VELOCITY = 1
            else:
                robot.LEFT_WHEEL_VELOCITY = random()
                robot.RIGHT_WHEEL_VELOCITY = random()
        ###################################

        robot.simulationstep()

        # check collision with arena walls
        collided = robot.is_colliding(WORLD)
        collision_box = robot.get_collision_box_coordinate()

        DRAW_bottom_sensor_position = [(robot.bottom_sensors[0].x, robot.bottom_sensors[0].y), (
            robot.bottom_sensors[1].x, robot.bottom_sensors[1].y)]

        # if there's too much point, one can put spos to [] (and collision box and state, but it's nonsense)
        VISUALIZER.draw(robot.position, robot.color, cnt,
                        robot.path, collision_box, (proximity_sensors_state[0], 0, proximity_sensors_state[1], 0, proximity_sensors_state[2]), DRAW_proximity_sensor_position, DRAW_bottom_sensor_position, bottom_sensor_states, PHEROMON_PATH)
        decay_check()
        if cnt % 2 == 0:
            PHEROMON_PATH.append(PheromonePoint(robot.position, DECAY))
            #! I imagine appening the point will only be activated under certain circumst.
            # robot.path.append(robot.position.__dict__)

        if collided:
            #! Right now, if robot collides, it will disapear form the simulation (since no more point)
            print("collided")
            robot.has_collided = True

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    sleep(0.2)
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_d:
                    VISUALIZER.DRAW_DECAY = not VISUALIZER.DRAW_DECAY
                    print("[Display] Toggle pheromone decay visualization")
                if event.key == pygame.K_x:
                    VISUALIZER.DRAW_PATH = not VISUALIZER.DRAW_PATH
                    print("[Display] Toggle path visualization")
                if event.key == pygame.K_y:
                    DISPLAY_HANDLER += 1

                    if DISPLAY_HANDLER == 3:
                        VISUALIZER.DRAW_RAYS = False
                        VISUALIZER.DRAW_BOX = False
                        VISUALIZER.DRAW_BOTTOM_SENSORS = False
                        DISPLAY_HANDLER = 0
                        print(
                            "[Display] Sensors and Box visualization desactivated")
                    elif DISPLAY_HANDLER == 1:
                        VISUALIZER.DRAW_RAYS = True
                        VISUALIZER.DRAW_BOTTOM_SENSORS = True
                        print("[Display] Sensors visualization activated")
                    elif DISPLAY_HANDLER == 2:
                        VISUALIZER.DRAW_BOX = True
                        print(
                            "[Display] Sensors and Box visualization activated")

    pygame.display.flip()  # render drawing
    fpsClock.tick(fps)
