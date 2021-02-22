import shapely
from shapely.affinity import rotate
from shapely.geometry import LinearRing, LineString, Point, Polygon
from shapely.geometry.point import Point
from shapely.ops import nearest_points

import numpy as np
from numpy import sin, cos, pi, sqrt, zeros
import math

from roboty import Robot
from utils_simu import Visualizator

from pygame.locals import *
import pygame

import sys
import json
from copy import deepcopy

from utils_simu import Position
from utils_simu import distance

from time import time_ns
from time import sleep
import math

from random import *

### GLOBALS ###################################################################

# WORLD
# TODO Redo measurements of the robot's sensors' position

ROBOT_TIMESTEP = 0.1  # 1/ROBOT_TIMESTEP equals update frequency of robot

# timestep in kinematics< sim (probably don't touch..)
SIMULATION_TIMESTEP = .01

R = 0.02  # radius of wheels in meters
L = 0.095  # distance between wheels in meters

LEFT_WHEEL_VELOCITY = 1
RIGHT_WHEEL_VELOCITY = 1

W = 1.94  # width of arena
H = 1.18  # height of arena

TOP_BORDER = H/2  # 0.59
BOTTOM_BORDER = -H/2
RIGHT_BORDER = W/2  # 0.97
LEFT_BORDER = -W/2

WORLD = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

BOTTOM_LIGHT_SENSORS_POSITION = [
    Position(-0.0097, 0.074), Position(0.0097, 0.074)]

# Assuming the robot is looking north
PROXIMITY_SENSORS_POSITION = [Position(-0.05,   0.06, math.radians(130)),
                              Position(-0.025,  0.075, math.radians(108.5)),
                              Position(0, 0.0778, math.radians(90)),
                              Position(0.025,  0.075, math.radians(71.5)),
                              Position(0.05,   0.06, math.radians(50))]


# PYGAME
ZOOM = 4
ROBOT_SIZE = 40
VISUALIZER = Visualizator(ZOOM, W, H, ROBOT_SIZE)
DISPLAY_HANDLER = 0

###############################################################################


def update_sensors_position(sensors, x, y, q):
    for pos in sensors:
        pos.x = pos.x + x
        pos.y = pos.y + y
        pos.q = pos.q + q
    return sensors


def simulationstep(x, y, q, left_wheel_velocity, right_wheel_velocity):
    # step model time/timestep times
    for step in range(int(ROBOT_TIMESTEP/SIMULATION_TIMESTEP)):
        v_x = cos(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2)
        v_y = sin(q)*(R*left_wheel_velocity/2 + R*right_wheel_velocity/2)
        omega = (R*right_wheel_velocity - R*left_wheel_velocity)/(2*L)

        x += v_x * SIMULATION_TIMESTEP
        y += v_y * SIMULATION_TIMESTEP
        q += omega * SIMULATION_TIMESTEP
    return x, y, q


def create_rays(sensors):
    rays = []
    spos = []
    for sensor in sensors:
        nx = sensor.x
        ny = sensor.y
        nq = sensor.q
        nx_end = nx+cos(nq)*2*W
        ny_end = ny+sin(nq)*2*H
        ray = [(nx, ny), (nx_end, ny_end)]
        spos.append(ray)
        rays.append(LineString(ray))
    return rays, spos


def get_sensors_state(sensors):
    top = sensors_values[2]
    left = sensors_values[1]
    right = sensors_values[3]
    leftest = sensors_values[0]
    rightest = sensors_values[4]

    top_value = 1 if top < 0.1 else 0
    left_value = 1 if left < 0.1 else 0
    right_value = 1 if right < 0.1 else 0
    leftest_value = 1 if leftest < 0.1 else 0
    rightest_value = 1 if rightest < 0.1 else 0

    # return (leftest_value, left_value, top_value, right_value, rightest_value)
    return (leftest_value, top_value, rightest_value)


def get_sensor_values(rays, robot, robots):
    dists = []

    # Wall detection
    for index, ray in enumerate(rays):
        dists.append(distance(WORLD.intersection(ray),
                              robot.sensors[index].x, robot.sensors[index].y))

    # # Robot detection
    # for r in robots:
    #     # Don't check ourselves
    #     if r.number != robot.number:
    #         for index, ray in enumerate(rays):
    #             if r.is_sensing(ray):
    #                 p1, p2 = nearest_points(r.get_collision_box(), Point(
    #                     robot.sensors[index].x, robot.sensors[index].y))
    #                 dists[index] = distance(p1, p2.x, p2.y)

    return dists
    # return [distance(WORLD.intersection(ray), sensors[index].x, sensors[index].y) for index, ray in enumerate(rays)]

### Start's variables #########################################################


# Robot's starting position
x = 0
y = 0
q = math.radians(90)

sensors = PROXIMITY_SENSORS_POSITION

CNT = 15000
M = 20
DV = CNT / M

#! Since the simulation must last long, it is likely that I need to find ways
#! to make the program faster. Maybe by removing the box and rays from the point file?

world = {
    "NAME": "BaseArena",
    "W": W,
    "H": H,
    "X0": x,
    "Y0": y,
    "Q0": q,
    "NBPOINTS": DV,
}

ROBOTS = []
R1 = Robot(1, deepcopy(sensors), Position(-0.2, 0, math.radians(0)),
           (randint(0, 255), randint(0, 255), randint(0, 255)))
R5 = Robot(5, deepcopy(sensors), Position(-0.2, 0.2, math.radians(0)),
           (randint(0, 255), randint(0, 255), randint(0, 255)))
R4 = Robot(4, deepcopy(sensors), Position(-0.2, -.20, math.radians(0)),
           (randint(0, 255), randint(0, 255), randint(0, 255)))

R2 = Robot(2, deepcopy(sensors), Position(0.20, 0, math.radians(180)),
           (randint(0, 255), randint(0, 255), randint(0, 255)))
R3 = Robot(3, deepcopy(sensors), Position(0.20, 0.20, math.radians(
    180)), (randint(0, 255), randint(0, 255), randint(0, 255)))
R6 = Robot(6, deepcopy(sensors), Position(0.20, -0.20, math.radians(180)),
           (randint(0, 255), randint(0, 255), randint(0, 255)))

ROBOTS.append(R1)
ROBOTS.append(R2)
ROBOTS.append(R3)
ROBOTS.append(R4)
ROBOTS.append(R5)
ROBOTS.append(R6)
###############################################################################


def calculate_position_robot(robot):
    rays, spos = create_rays(robot.sensors)
    sensors_values = get_sensor_values(rays, robot, ROBOTS)
    state = get_sensors_state(sensors_values)

    LEFT_WHEEL_VELOCITY = 1
    RIGHT_WHEEL_VELOCITY = 1

    if state == (0, 1, 0):
        if randint(0, 1):
            RIGHT_WHEEL_VELOCITY = -1
        else:
            LEFT_WHEEL_VELOCITY = -1
        # LEFT_WHEEL_VELOCITY = -1  # ! Random seems to make them wiggle to much :D
    elif state == (1, 0, 0) or state == (1, 1, 0):
        RIGHT_WHEEL_VELOCITY = -1
    elif state == (0, 0, 1) or state == (0, 1, 1):
        LEFT_WHEEL_VELOCITY = -1
        # TODO robot somwhow still get stuck in the corner
    elif state == (1, 0, 1) or state == (1, 1, 1):  #  I am stuck state
        # ! in software, escaping the corner looks difficult. but hardware should be easy.
        LEFT_WHEEL_VELOCITY = -1
    else:
        LEFT_WHEEL_VELOCITY = random()
        RIGHT_WHEEL_VELOCITY = random()

    # # step simulation
    x = robot.position.x
    y = robot.position.y
    q = robot.position.q

    new_x, new_y, new_q = simulationstep(
        x, y, q, LEFT_WHEEL_VELOCITY, RIGHT_WHEEL_VELOCITY)

    robot.update_sensors_pos(new_x - x, new_y - y, new_q-q)
    robot.rotate_all_pos(new_x, new_y, new_q-q)

    robot.update_position(Position(new_x, new_y, new_q))


try:
    pygame.init()
    fps = 24
    fpsClock = pygame.time.Clock()
    while True:
        VISUALIZER.draw_arena()
        for robot in ROBOTS:

            if robot.has_collided:
                break

            VISUALIZER.draw(robot.position, robot.color, 0,
                            robot.path, robot.get_collision_box_coordinate(), (0,) + robot.proximity_sensors_state + (0,), robot.spos)

            if robot.is_colliding(WORLD):
                print("collided")
                robot.has_collided = True

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
                    if event.key == pygame.K_y:
                        DISPLAY_HANDLER += 1

                        if DISPLAY_HANDLER == 3:
                            VISUALIZER.DRAW_RAYS = False
                            VISUALIZER.DRAW_BOX = False
                            DISPLAY_HANDLER = 0
                            print(
                                "[Display] Rays and Box visualization desactivated")
                        elif DISPLAY_HANDLER == 1:
                            VISUALIZER.DRAW_RAYS = True
                            print("[Display] Rays visualization activated")
                        elif DISPLAY_HANDLER == 2:
                            VISUALIZER.DRAW_BOX = True
                            print(
                                "[Display] Rays and Box visualization activated")

        pygame.display.flip()  # render drawing
        fpsClock.tick(fps)
except Exception as e:
    print(e)
    print("The program has encountered an error. Points written, but incompleted.")
