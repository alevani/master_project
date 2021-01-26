import shapely
from shapely.affinity import rotate
from shapely.geometry import LinearRing, LineString, Point, Polygon
from shapely.geometry.point import Point
from env import Environment

import numpy as np
from numpy import sin, cos, pi, sqrt, zeros
import math

from roboty import Robot

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


def update_sensors_position(sensors, x, y, q):
    for pos in sensors:
        pos.x = pos.x + x
        pos.y = pos.y + y
        pos.q = pos.q + q
    return sensors


def create_rays(pos, robot_position):
    nx = pos.x + robot_position.x
    ny = pos.y + robot_position.y
    nq = pos.q + robot_position.q
    return LineString([(nx, ny), (nx+cos(nq)*2*W, (ny+sin(nq)*2*H))])


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


def update_sensors_pos(sensors, x, y, q):
    for pos in sensors:
        pos.x = pos.x + x
        pos.y = pos.y + y
        pos.q = pos.q + q
    return sensors


def rotate_all_pos(sensors, x, y, q):
    for pos in sensors:
        point = rotate(Point(pos.x, pos.y), q,
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
# sensors = update_sensors_pos(sensors, x, y, math.radians(90) - q)
# sensors = rotate_all_pos(sensors, x, y, math.radians(90) - q)

CNT = 15000
M = 100
DV = CNT / M
NBROBOT = 10

world = {
    "NAME": "BaseArena",
    "W": W,
    "H": H,
    "X0": x,
    "Y0": y,
    "Q0": q,
    "NBPOINTS": DV,
    "NBROBOTS": NBROBOT
}

FILE.write(json.dumps(world))


ROBOTS = [Robot(n, deepcopy(sensors), Position(x, y, q))
          for n in range(NBROBOT)]

###############################################################################
try:
    for cnt in range(CNT):
        for robot in ROBOTS:

            if robot.has_collided:
                break

            draw_information = {
                'cnt': cnt,
                'rpos': [],  # Robot position
                'spos': [],  # Sensors position
                'sstate': [],  # Sensors state
                'bpos': [],   # Collision box position
                'lpos': []   # Keep track of where the robot has been
            }

            sensors = robot.sensors

            draw_information['rpos'] = robot.position.__dict__

            rays, spos = create_rays(sensors)

            sensors_values = [
                distance(WORLD.intersection(ray), sensors[index].x, sensors[index].y) for index, ray in enumerate(rays)]

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

            sensors = update_sensors_pos(
                sensors, new_x - x, new_y - y, new_q-q)

            sensors = rotate_all_pos(sensors, new_x, new_y, new_q-q)

            # # check collision with arena walls
            collided, collision_box = has_collided(x, y, q)

            # Update robot's information
            robot.sensors = deepcopy(sensors)
            robot.position = Position(new_x, new_y, new_q)

            draw_information['spos'] = spos
            # ! (0,) is to fake ray for visu
            draw_information['sstate'] = (0,) + state + (0,)
            draw_information['bpos'] = collision_box
            draw_information[]

            if cnt % M == 0:
                robot.draw_information.append(draw_information)

            if collided:
                print("collided")
                robot.has_collided = True

except:
    print("ERROR")
    for robot in ROBOTS:
        FILE.write("\n" + json.dumps(robot.draw_information))


for robot in ROBOTS:
    FILE.write("\n" + json.dumps(robot.draw_information))

FILE.close()

# elif state == '01100' or state == '01000':
#     RIGHT_WHEEL_VELOCITY = 0
# elif state == '00110' or state == '00010':
#     LEFT_WHEEL_VELOCITY = 0
# elif state == '10000' or state == '11000':
#     LEFT_WHEEL_VELOCITY = 0.5
# elif state == '00001' or state == '00011':
#     RIGHT_WHEEL_VELOCITY = 0.5

# if state == '00000':
#     print("FORWARD")
#     # LEFT_WHEEL_VELOCITY = random()
#     # RIGHT_WHEEL_VELOCITY = random()
#     pass
# elif state == '00100' or state == '01110' or state == '11111' or state == '11011' or state == 'state = 10001':
#     # Vague state, choose randomly wheter to turn left or right
#     # if randint(0, 1):
#     LEFT_WHEEL_VELOCITY = -1
#     # else:
#     #     RIGHT_WHEEL_VELOCITY = -1

# elif state == '00010' or state == '00001':
#     print("LEFT")
#     LEFT_WHEEL_VELOCITY = -1
#     RIGHT_WHEEL_VELOCITY = 1
# elif state == '01000':
#     print("RIGHT")
#     RIGHT_WHEEL_VELOCITY = -1
#     LEFT_WHEEL_VELOCITY = 1
# else:
#     print("BACKWARD")

# elif state == '01100' or state == '01000' or state == '10000' or state == '11000':
#     RIGHT_WHEEL_VELOCITY = -1

# elif state == '00110' or state == '00010' or state == '00001' or state == '00011':
#     LEFT_WHEEL_VELOCITY = -1
# else:
#     LEFT_WHEEL_VELOCITY = 1
#     RIGHT_WHEEL_VELOCITY = -1

# if state == (0, 0, 1, 0, 0):
#     if randint(0, 1):
#         RIGHT_WHEEL_VELOCITY = -1
#     else:
#         LEFT_WHEEL_VELOCITY = -1
# elif state == (1, 0, 0, 0, 0) or state == (1, 1, 0, 0, 0)or state == (1, 1, 1, 0, 0):
#     RIGHT_WHEEL_VELOCITY = -1
# elif state == (0, 0, 0, 0, 1) or state == (0, 0, 0, 1, 1) or state == (0, 0, 1, 1, 1):
#     LEFT_WHEEL_VELOCITY = -1
# elif state == (0, 1, 0, 1, 0):
#     LEFT_WHEEL_VELOCITY = -1
# else:
#     pass
