import shapely
from shapely.affinity import rotate
from shapely.geometry import LinearRing, LineString, Point, Polygon
from shapely.geometry.point import Point
from env import Environment

import numpy as np
from numpy import sin, cos, pi, sqrt, zeros
import math

import sys
import json
from copy import deepcopy

from utils import Position
from utils import distance

from random import *

### GLOBALS ###################################################################
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

FILE = open("points.json", "w")
###############################################################################


def update_sensors_position(sensors, x, y, a):
    for pos in sensors:
        pos.x = pos.x + x
        pos.y = pos.y + y
        pos.a = pos.a + a
    return sensors


def create_rays(pos, robot_position):
    nx = pos.x + robot_position.x
    ny = pos.y + robot_position.y
    na = pos.a + robot_position.a
    return LineString([(nx, ny), (nx+cos(na)*2*W, (ny+sin(na)*2*H))])


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
        na = sensor.a
        nx_end = nx+cos(na)*2*W
        ny_end = ny+sin(na)*2*H
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

    top_value = 1 if top < 0.03 else 0
    left_value = 1 if left < 0.03 else 0
    right_value = 1 if right < 0.03 else 0
    leftest_value = 1 if leftest < 0.03 else 0
    rightest_value = 1 if rightest < 0.03 else 0

    return str(leftest_value) + str(left_value) + str(top_value) + str(right_value) + str(rightest_value)


def update_sensors_pos(sensors, x, y, a):
    for pos in sensors:
        pos.x = pos.x + x
        pos.y = pos.y + y
        pos.a = pos.a + a
    return sensors


def rotate_all_pos(sensors, x, y, a):
    for pos in sensors:
        point = rotate(Point(pos.x, pos.y), a,
                       (x, y), use_radians=True)
        pos.x = point.x
        pos.y = point.y

    return sensors


#! Keep in mind here that the box is larger at the top to prevent the Lidar module to fall in real life
def has_collided(x, y, a):
    a = a - math.radians(90)
    box_x = 0.0525
    box_y_top = 0.0725
    box_y_bottom = 0.0725 - 0.03
    # print((x - box_x, y - box_y_bottom), (x - box_x, y + box_y_top),
    #       (x + box_x, y + box_y_top), (x + box_x, y - box_y_bottom))
    collision_box = Polygon(
        ((x - box_x, y - box_y_bottom), (x - box_x, y + box_y_top),
         (x + box_x, y + box_y_top), (x + box_x, y - box_y_bottom)))

    collision_box = rotate(collision_box, a, (x, y), use_radians=True)
    x, y = collision_box.exterior.coords.xy

    return collision_box.intersects(WORLD), tuple(zip(x, y))


### Start's variables #########################################################

# Robot's starting position
x = 0
y = 0
q = math.radians(90)

sensors = PROXIMITY_SENSORS_POSITION

world = {
    "Name": "BaseArena",
    "W": W,
    "H": H,
    "X0": x,
    "Y0": y,
    "Q0": q
}

FILE.write(json.dumps(world))

###############################################################################

for cnt in range(10000):
    robot_draw = {
        'rpos': [],  # Robot position
        'spos': [],  # Sensors position
        'bpos': []   # Collision box position
    }

    robot_position = Position(x, y, q)
    robot_draw['rpos'] = robot_position.__dict__

    rays, spos = create_rays(sensors)
    robot_draw['spos'] = spos

    sensors_values = [
        distance(WORLD.intersection(ray), sensors[index].x, sensors[index].y) for index, ray in enumerate(rays)]

    state = get_sensors_state(sensors_values)

    LEFT_WHEEL_VELOCITY = 1
    RIGHT_WHEEL_VELOCITY = 1

    if state == '00000':
        LEFT_WHEEL_VELOCITY = random()
        RIGHT_WHEEL_VELOCITY = random()
    elif state == '00100':
        # Vague state, choose randomly wheter to turn left or right
        if randint(0, 1):
            LEFT_WHEEL_VELOCITY = 0
        else:
            RIGHT_WHEEL_VELOCITY = 0
    elif state == '01100' or state == '01000' or state == '10000' or state == '11000':
        RIGHT_WHEEL_VELOCITY = -1
    elif state == '00110' or state == '00010' or state == '00001' or state == '00011':
        LEFT_WHEEL_VELOCITY = -1
    else:
        LEFT_WHEEL_VELOCITY = 1
        RIGHT_WHEEL_VELOCITY = -1

    # elif state == '01100' or state == '01000':
    #     RIGHT_WHEEL_VELOCITY = 0
    # elif state == '00110' or state == '00010':
    #     LEFT_WHEEL_VELOCITY = 0
    # elif state == '10000' or state == '11000':
    #     LEFT_WHEEL_VELOCITY = 0.5
    # elif state == '00001' or state == '00011':
    #     RIGHT_WHEEL_VELOCITY = 0.5

    # # step simulation
    new_x, new_y, new_q = simulationstep(
        x, y, q, LEFT_WHEEL_VELOCITY, RIGHT_WHEEL_VELOCITY)

    sensors = update_sensors_pos(
        sensors, new_x - x, new_y - y, new_q-q)

    sensors = rotate_all_pos(sensors, new_x, new_y, new_q-q)

    x = new_x
    y = new_y
    q = new_q

    # # check collision with arena walls
    collided, collision_box = has_collided(x, y, q)
    robot_draw['bpos'] = collision_box

    if cnt % 20 == 0:
        FILE.write("\n" + json.dumps(robot_draw))

    if collided:
        print("collided")
        break

FILE.close()
