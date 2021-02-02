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
from roboty import PheromonePoint

from pygame.locals import *
import pygame

import sys
import json
from copy import deepcopy

from utils import Position
from utils import distance
import globals

from time import sleep
import math

from random import *

# IDEAS
# One can play with the buffers of the pheromone sensing to simulate crappy hardware of ant
#   -> as in, right now the detection pretty wide, maybe induce some noise with a randmoness in the buffer?
#   -> which is also why sometimes it misses rough angles.

# Checking every point for decay is super slow, if I wasn't working with kinetic movement I could have a map
# of pixel and a absolute position for pheromones, and they finding if the sensor is on a point would only take O(1)
# but storage would be affected.

# It does not seem impossible to have a record button that would save the point. This record button would record idk like
# 5000 begin and from there on, giving the user a chance to record something he just missed, also without to have to watch
# it from the begining again

# It is likely that adding pheromones at every step is wrong. like ant will activate their pheromones only under specific circumstances

# Do ants have a specific go home or go to food pheromone? if so I can easily add this behaviour by adding a pheromone type in the pheromone object and filtering when matching

# Scaling could only occure once. We scale from at the moment we register the point
# 'cause then we don't have to re-scale every iteration of display..
########

# TODO one should be able to see POIs in the point_simulation

### GLOBALS ###################################################################

# WORLD
# TODO Redo measurements of the robot's sensors' position

# Speed of robot in simulation, keep FPS at 60 and only change the below variable to variate the speed
ROBOT_TIMESTEP = 1
SIMULATION_TIMESTEP = .01

R = 0.02  # radius of wheels in meters
L = 0.095  # distance between wheels in meters

# W = 1.94  # width of arena
# H = 1.18  # height of arena
W = globals.W
H = globals.H

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
FILE = open("points.json", "w")
ZOOM = 4
ROBOT_SIZE = 40
DECAY = 2500
VISUALIZER = Visualizator(ZOOM, W, H, ROBOT_SIZE, DECAY, FILE)
pygame.init()
fps = 60
fpsClock = pygame.time.Clock()
###############################################################################


def decay_check():
    for i, point in enumerate(PHEROMON_PATH):
        point.decay_time -= 1
        if point.decay_time <= 0:
            PHEROMON_PATH.pop(i)

    # threading.Timer(.1, decay_check).start()


# This is not in the robot's object because it seemed to be slower if so
def get_proximity_sensor_values(rays, robot):
    dists = []

    # Wall detection
    for index, ray in enumerate(rays):
        dists.append(distance(WORLD.intersection(ray),
                              robot.proximity_sensors[index].x, robot.proximity_sensors[index].y))

    # Robot detection
    for r in globals.ROBOTS:
        # Don't check ourselves
        if r.number != robot.number:
            for index, ray in enumerate(rays):
                if r.is_sensing(ray):
                    p1, p2 = nearest_points(r.get_collision_box(), Point(
                        robot.proximity_sensors[index].x, robot.proximity_sensors[index].y))
                    dists[index] = distance(p1, p2.x, p2.y)

    return dists


### Start's variables #########################################################
# Robot's starting position
x = 0
y = 0
q = math.radians(90)

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

globals.ROBOTS.append(R1)
globals.ROBOTS.append(R2)
globals.ROBOTS.append(R3)
globals.ROBOTS.append(R4)
# globals.ROBOTS.append(R5)
# globals.ROBOTS.append(R6)
# globals.ROBOTS.append(R7)
# globals.ROBOTS.append(R8)

PHEROMON_PATH = []
###############################################################################

while True:
    globals.cnt += 1
    VISUALIZER.draw_arena()
    VISUALIZER.draw_poi()
    for robot in globals.ROBOTS:

        if robot.has_collided:
            break

        draw_information = {
            'rpos': [],  # Robot position
        }

        rays, DRAW_proximity_sensor_position = robot.create_rays(W, H)

        proximity_sensor_values = get_proximity_sensor_values(
            rays, robot)

        # Robot's brain
        bottom_sensor_states = robot.get_bottom_sensor_states(PHEROMON_PATH)

        proximity_sensors_state = robot.get_proximity_sensor_state(
            proximity_sensor_values)

        if robot.is_turning_to_face_home:
            robot.face_home_behaviour()
        elif proximity_sensors_state == (0, 1, 0):
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
        elif proximity_sensors_state == (1, 0, 1) or proximity_sensors_state == (1, 1, 1):
            # Workaround for corner avoidance.
            for _ in range(200):  # ! could be change to like I did for face home but meh
                robot.RIGHT_WHEEL_VELOCITY = -1
                robot.LEFT_WHEEL_VELOCITY = 1
                robot.simulationstep()
        else:
            if bottom_sensor_states == (2, 0) or bottom_sensor_states == (0, 2) or bottom_sensor_states == (1, 2) or bottom_sensor_states == (2, 1):
                robot.is_turning_to_face_home = True
                robot.RIGHT_WHEEL_VELOCITY = 0
                robot.LEFT_WHEEL_VELOCITY = 0
            elif bottom_sensor_states == (1, 0):
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

        # VISUALIZER.draw(robot.position, robot.color, globals.cnt,
        #                 robot.path, collision_box, (proximity_sensors_state[0], 0, proximity_sensors_state[1], 0, proximity_sensors_state[2]), DRAW_proximity_sensor_position, DRAW_bottom_sensor_position, bottom_sensor_states, PHEROMON_PATH)
        VISUALIZER.draw(robot.position, robot.color, globals.cnt,
                        [], collision_box, (proximity_sensors_state[0], 0, proximity_sensors_state[1], 0, proximity_sensors_state[2]), DRAW_proximity_sensor_position, DRAW_bottom_sensor_position, bottom_sensor_states, PHEROMON_PATH)
        decay_check()

        draw_information['rpos'] = robot.position.__dict__

        if globals.cnt % globals.M == 0:
            PHEROMON_PATH.append(PheromonePoint(robot.position, DECAY))
            robot.path.append(robot.position.__dict__)
            robot.draw_information.append(draw_information)

        if collided:
            print("collided")
            robot.has_collided = True

        VISUALIZER.pygame_event_manager(pygame.event.get())

    pygame.display.flip()  # render drawing
    fpsClock.tick(fps)
