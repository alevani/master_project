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
from roboty import Area

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
# It does not seem impossible to have a record button that would save the point. This record button would record idk like
# 5000 begin and from there on, giving the user a chance to record something he just missed, also without to have to watch
# it from the begining again

# It is likely that adding pheromones at every step is wrong. like ant will activate their pheromones only under specific circumstances

# Do ants have a specific go home or go to food pheromone? if so I can easily add this behaviour by adding a pheromone type in the pheromone object and filtering when matching

# TODO Right now it's funny that I can right and left click put
# TODO ultimately one will have to decide wheter POIs should all be in the same list or
# TODO if they should be in dedicated list (home_pois, task_pois, and so on)
# TODO IF in separated lists, then I can have multiple function for sensing (bottom)
# TODO as if, if robot sense a resource, then he shift to an other sensing function
# TODO that handles to only sense a "home" pois type (maybe there's going to be one home but anyway)
# TODO 'cause if so, then he would avoid resources on its way which is nice I imagine (even though technically new resources shouldn't pop in the middle of a path sinc the path already has been covered by the ant...)
# TODO because it's cheaper to have two list than one list and O(n + 1) each iteration
# TODO like .. if it searches for home no need to check in the resource list :)

#! next step is to think of a "setup" for an experiment. or maybe task allocation? more useful I guess (see personal notes).

# ? Thesis concern: If I were to work with real ants, I wouldn't need to dodge other robot as ant can go over each others.. but in real life not the same.

# ? Thesis: Maybe it's going to be important to retrace the step of the simulation development?
# ? i don't think so. But maybe about the speed and the improvement?

#! there are a lot of problem when converting to point, like lots of things shouldn't require that much convert..

#! do not spend to much time on the point visu, it's like the thing that I will the less use, and only what's in the handin counts.

#! it's not beautiful, but I think it's very convenient to keep path and maps. maybe there's some possible cleanup?

#! one need to fix: the way robot behave on pheromone, they should be able to take 90 degree angle
#! and also CIRCLE OF DEATH

#! Simulation time between live and point is not the same... important? I don't think so.

#! not sure but, there seems to be a problem with the randering size.
# TODO try to make that the zoom influence everything else. ultimately it would be nice to be able to live zoom.
########

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
    Position(-0.012, 0.05), Position(0.012, 0.05)]  # ! false measurments

# Assuming the robot is looking north
PROXIMITY_SENSORS_POSITION = [Position(-0.05,   0.06, math.radians(130)),
                              Position(-0.025,  0.075, math.radians(108.5)),
                              Position(0, 0.0778, math.radians(90)),
                              Position(0.025,  0.075, math.radians(71.5)),
                              Position(0.05,   0.06, math.radians(50))]

TYPE_HOME = 1

# PYGAME
globals.DO_RECORD = True
if globals.DO_RECORD:
    FILE = open("points.json", "w")
else:
    FILE = None

DECAY = 500
VISUALIZER = Visualizator(W, H, DECAY, FILE)
pygame.init()
fps = 60
fpsClock = pygame.time.Clock()
###############################################################################


def decay_check():
    for i, point in enumerate(PHEROMONES_PATH):
        point.decay_time -= 1
        if point.decay_time <= 0:
            globals.PHEROMONES_MAP[int(point.position.x * 100) + int(
                globals.W * 100/2)][int(point.position.y * 100) + int(globals.H * 100/2)] = 0
            PHEROMONES_PATH.pop(i)

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

R1 = Robot(1, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2 + 0.2, -H/2 + 0.2, math.radians(0)),
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

R9 = Robot(9, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-0.47, 0.47, math.radians(0)),
           (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)
R10 = Robot(10, deepcopy(PROXIMITY_SENSORS_POSITION), Position(0.47, -0.47, math.radians(0)),
            (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)
R11 = Robot(11, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-0.60, 0.60, math.radians(0)),
            (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)
R12 = Robot(12, deepcopy(PROXIMITY_SENSORS_POSITION), Position(0.60, -0.60, math.radians(0)),
            (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)
R13 = Robot(13, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-0.70, -0.70, math.radians(0)),
            (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)
R14 = Robot(14, deepcopy(PROXIMITY_SENSORS_POSITION), Position(0.70, 0.70, math.radians(0)),
            (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)
R15 = Robot(15, deepcopy(PROXIMITY_SENSORS_POSITION), Position(0.70, -0.70, math.radians(0)),
            (randint(0, 255), randint(0, 255), randint(0, 255)), deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L)

globals.ROBOTS.append(R1)
globals.ROBOTS.append(R2)
globals.ROBOTS.append(R3)
globals.ROBOTS.append(R4)
globals.ROBOTS.append(R5)
globals.ROBOTS.append(R6)
globals.ROBOTS.append(R7)
globals.ROBOTS.append(R8)
globals.ROBOTS.append(R9)
globals.ROBOTS.append(R10)
globals.ROBOTS.append(R11)
globals.ROBOTS.append(R12)
globals.ROBOTS.append(R13)
globals.ROBOTS.append(R14)
globals.ROBOTS.append(R15)

# Slow at creation, and heavy, but considerabely increase visualisation speed.
#! nothing in (0,0) why?
for x in range(int(globals.W * 100)):
    inner = []
    for y in range(int(globals.H * 100)):
        inner.append(0)
    globals.PHEROMONES_MAP.append(inner)


PHEROMONES_PATH = []
AREAS = []

# Nest = Area(Position(-W/2, -H/2), 0.5, 1, TYPE_HOME, (133, 147, 255))

# AREAS.append(Nest)
###############################################################################

while True:
    globals.cnt += 1
    VISUALIZER.draw_arena()
    VISUALIZER.draw_poi(globals.POIs)
    VISUALIZER.draw_areas(AREAS)
    VISUALIZER.draw_decay(PHEROMONES_PATH)
    for robot in globals.ROBOTS:

        if robot.has_collided:
            break

        rays, DRAW_proximity_sensor_position = robot.create_rays(W, H)

        proximity_sensor_values = get_proximity_sensor_values(
            rays, robot)

        bottom_sensor_states = robot.get_bottom_sensor_states(
            globals.PHEROMONES_MAP)

        proximity_sensors_state = robot.get_proximity_sensor_state(
            proximity_sensor_values)

        # Robot's brain
        robot.RIGHT_WHEEL_VELOCITY = 0
        robot.LEFT_WHEEL_VELOCITY = 0

        if robot.is_avoiding:
            robot.avoid()
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
            robot.is_avoiding = True
            robot.NB_STEP_TO_AVOID = 7
        else:
            # area_type = robot.area_type(AREAS)
            # if area_type != 0:
            #     if area_type == TYPE_HOME:
            #         robot.RIGHT_WHEEL_VELOCITY = 0
            #         robot.LEFT_WHEEL_VELOCITY = 0
            # else:

            # Here, depending on the pheromone trail type, we could easily avoid path to go home and such ..
            if bottom_sensor_states == (2, 0) or bottom_sensor_states == (0, 2) or bottom_sensor_states == (1, 2) or bottom_sensor_states == (2, 1):
                robot.is_avoiding = True
                robot.NB_STEP_TO_AVOID = 15
                robot.trail = True
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

        VISUALIZER.draw(robot.position, robot.color, globals.cnt,
                        robot.path, collision_box, (proximity_sensors_state[0], 0, proximity_sensors_state[1], 0, proximity_sensors_state[2]), DRAW_proximity_sensor_position, DRAW_bottom_sensor_position, bottom_sensor_states)

        if robot.trail:
            globals.PHEROMONES_MAP[int(robot.position.x * 100) + int(globals.W * 100/2)][int(
                robot.position.y * 100) + int(globals.H * 100/2)] = PheromonePoint(robot.position, DECAY, 1)
            PHEROMONES_PATH.append(PheromonePoint(robot.position, DECAY, None))

        # Robot wise
        if globals.DO_RECORD:
            if globals.cnt % globals.M == 0:
                robot.path.append(robot.position.__dict__)

        if collided:
            #! sometimes a lot of robot that are not even in the same area collide in the same time
            #! I need to figure out why.
            print("collided")
            robot.has_collided = True

        VISUALIZER.pygame_event_manager(pygame.event.get())

    decay_check()
    # World wise
    if globals.DO_RECORD:
        if globals.cnt % globals.M == 0:
            globals.DRAW_POIS.append([o.encode()
                                      for o in deepcopy(globals.POIs)])

    pygame.display.flip()  # render drawing
    fpsClock.tick(fps)
