from random import uniform
from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, zeros
from PointOfInterest import PointOfInterest
from shapely.geometry.point import Point
from shapely.ops import nearest_points
from Visualizator import Visualizator
from shapely.affinity import rotate
from TaskHandler import TaskHandler
from TaskHandler import assigned
from Position import Position
from pygame.locals import *
from copy import deepcopy

from Robot import add_robot
from Robot import Robot

from time import sleep
from Area import Area
from Nest import Nest
from random import *

from const import RESOURCE_STATE_NEST_PROCESSING
from const import BOTTOM_LIGHT_SENSORS_POSITION
from const import PROXIMITY_SENSORS_POSITION
from const import RESOURCE_STATE_TRANSFORMED
from const import RESOURCE_STATE_FORAGING
from const import RESOURCE_STATE_WAISTE
from const import SIMULATION_TIMESTEP
from const import ROBOT_TIMESTEP
from const import BLACK
from const import dist
from const import W
from const import H
from const import R
from const import L

import numpy as np
import threading
import shapely
import globals
import pygame
import json
import math
import sys

# IDEAS
#!when on same x axis, the robot struggle to be correctly aligned so it turns and aligns .. forward.. turns and aligns .. and so on
# TODO how is it possible that the peak of each task is higher than the previous? they should be about the same as the payload value is substract and re-added to the next task.
########

### GLOBALS ###################################################################

# WORLD
WORLD = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

# PYGAME
if globals.DO_RECORD:
    FILE = open("record.json", "w")
else:
    FILE = None

globals.CSV_FILE = open("stats/stats.csv", "w")

ACT = True

DECAY = 750
if ACT:
    VISUALIZER = Visualizator(W, H, DECAY, FILE)
    pygame.init()
    fps = 60
    fpsClock = pygame.time.Clock()
###############################################################################

### Task allocation #########################################################
resting = 0
STATES_NAME = ['Resting', 'First reserve',
               'Second reserve', 'Temporary worker', 'Core worker']

# Array to keep track of the tasks
TASKS = []

# A task is a tuple of its energy and a task object
no_task = 0
foraging = 1
nest_maintenance = 2
brood_care = 3


TASKS_NAME = ['Foraging',
              'Nest maintenance', 'Brood care']

TASKS.append(foraging)
TASKS.append(nest_maintenance)
TASKS.append(brood_care)
# TASKS.append(patrolling)

globals.NEST = Nest(-50)
TaskHandler = TaskHandler(globals.NEST, TASKS)
#############################################################################

### Start's variables #########################################################
BASE_BATTERY_LEVEL = 100

R1 = Robot(1, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+0.2+3.8, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R2 = Robot(2, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+0.4 + 3.8, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R3 = Robot(3, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+0.6 + 3.8, math.radians(
    0)), BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R4 = Robot(4, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+0.8 + 3.8, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R5 = Robot(5, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+1 + 3.8, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R6 = Robot(6, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+1.2 + 3.8, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R7 = Robot(7, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+1.4 + 3.8, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R8 = Robot(8, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+1.6 + 3.8, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R9 = Robot(9, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+1.8 + 3.8, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R10 = Robot(10, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+2 + 3.8, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R11 = Robot(11, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+2.2 + 3.8, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R12 = Robot(12, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+2.4 + 3.8, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R13 = Robot(13, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+2.6 + 3.8, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R14 = Robot(14, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+2.8 + 3.8, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

R15 = Robot(15, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+3 + 3.8, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, no_task, resting, BASE_BATTERY_LEVEL)

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
for x in range(int(W * 100)):
    inner = []
    for y in range(int(H * 100)):
        inner.append(0)
    globals.PHEROMONES_MAP.append(inner)


# Markers
globals.MARKER_HOME = Position(-W/2 + 1.15, -H/2 + 1.15)
globals.MARKER_BROOD_CHAMBER = Position(-W/2 + 3.3, -H/2 + 1.15)
globals.MARKER_WAISTE_AREA = Position(W/2-0.7, H/2 - 0.7)

# Areas
AREAS = []
TYPE_NEUTRAL = 0
TYPE_HOME = 1
TYPE_CHARGING_AREA = 2
TYPE_BROOD_CHAMBER = 3
TYPE_WAISTE_DEPOSIT = 4
TYPE_FORAGING_AREA = 5

home = Area(Position(-W/2, -H/2), 2.3, 2.3, TYPE_HOME, (133, 147, 255))

brood_chamber = Area(Position(-W/2 + 2.3, -H/2), 2,
                     2.3, TYPE_BROOD_CHAMBER, (224, 153, 255))

charging_area = Area(Position(-W/2, -H/2+3.8),
                     1.4, 3.2, TYPE_CHARGING_AREA, (168, 255, 153))

waiste_deposit = Area(Position(W/2-1.4, H/2-1.4), 1.4,
                      1.4, TYPE_WAISTE_DEPOSIT, (240, 188, 91))

foraging_area = Area(Position(-W/2, -H/2), W,
                     H, TYPE_FORAGING_AREA, (255, 255, 255))

AREAS.append(foraging_area)
AREAS.append(home)
AREAS.append(brood_chamber)
AREAS.append(charging_area)
AREAS.append(waiste_deposit)


def is_point_on_area(x, y):
    box = Point(x, y).buffer(0.01)
    for area in AREAS[1:]:  # Disregard the foraging area as it is the entire map
        if area.box.intersects(box):
            return True
    return False


for _ in range(2000):
    x = uniform(-W/2+0.01, W/2-0.01)
    y = uniform(-H/2+0.01, H/2-0.01)

    if not is_point_on_area(x, y):
        index = len(globals.POIs)
        globals.POIs.append(PointOfInterest(
            Position(x, y), 15000, 2, 10))

        x_scaled = int(x * 100) + int(W/2 * 100)
        y_scaled = int(y * 100) + int(H/2 * 100)

        resource_value = randint(1, 2)
        # globals.NEST.resource_need -= resource_value
        globals.PHEROMONES_MAP[x_scaled][y_scaled] = PointOfInterest(
            Position(x_scaled, y_scaled), 15000, 2, resource_value, index)

# for _ in range(35):
#     add_robot()
###############################################################################


def get_proximity_sensors_values(robot_rays, robot):
    values = []

    # Wall detection
    for index, ray in enumerate(robot_rays):
        point = WORLD.intersection(ray)
        values.append(dist((point.x, point.y),
                           (robot.proximity_sensors[index].x, robot.proximity_sensors[index].y)))

    # Robot detection
    for r in globals.ROBOTS:

        # Don't check ourselves
        if r.number != robot.number:

            # in range is used to reduce the amount of robot the robot as to compare.
            # TODO I could change to a polygone of the shape of the front row detection, I would have less to check :)
            if robot.in_range(r.position):

                # "If one of my rays can sense you, get the distance"
                for index, ray in enumerate(robot_rays):
                    if r.is_sensing(ray):

                        # ? TEST: if I don't have any last_foraging_point, maybe the robot that I am sensing has one?
                        if r.last_foraging_point != None and robot.last_foraging_point == None:
                            robot.last_foraging_point = r.last_foraging_point

                        p1, p2 = nearest_points(r.get_collision_box(), Point(
                            robot.proximity_sensors[index].x, robot.proximity_sensors[index].y))
                        values[index] = dist(
                            (p1.x, p1.y), (p2.x, p2.y))

    return values


while True:
    globals.CNT += 1

    if ACT:
        VISUALIZER.draw_arena()
        VISUALIZER.draw_areas(AREAS)

    for robot in globals.ROBOTS:

        # If the robot is out of power, don't process it
        if robot.battery_level <= 0:
            break

        robot_rays, DRAW_proximity_sensor_position = robot.create_rays(W, H)

        robot_prox_sensors_values = get_proximity_sensors_values(
            robot_rays, robot)

        robot_bottom_sensor_states, pointOfInterest = robot.get_bottom_sensors_state(
            globals.PHEROMONES_MAP)

        TaskHandler.assign_task(robot)

        robot.stop()
        robot.sense_area(AREAS)

        if not robot.battery_low:
            # if the robot does not have to work .. let it rest in its charging area.
            if not robot.has_to_work():
                if not robot.has_destination():
                    if robot.carry_resource:
                        robot.drop_resource()
                    robot.go_home()

            # the robot has to be active
            else:
                if robot.task == no_task:
                    robot.go_home()

                elif robot.task == foraging:

                    if robot.carry_resource and not robot.has_destination():
                        robot.destination = globals.MARKER_HOME

                    if not robot.carry_resource:
                        if not robot.is_on_area(TYPE_FORAGING_AREA):
                            robot.destination = robot.last_foraging_point if not robot.last_foraging_point == None else Position(
                                0, 0)
                        else:
                            robot.destination = robot.last_foraging_point if not robot.last_foraging_point == None else None

                    # if I arrived home and I do carry a resource, unload it.
                    if robot.is_on_area(TYPE_HOME) and robot.carry_resource:
                        robot.destination = None
                        if robot.time_in_zone >= robot.time_to_drop_out:
                            robot.compute_resource()
                        else:
                            robot.time_in_zone += 1

                    # else if I find a resource on the ground, and I am not already carrying a resource
                    elif (robot_bottom_sensor_states == (2, 0) or robot_bottom_sensor_states == (0, 2)) and not robot.carry_resource and pointOfInterest.state == RESOURCE_STATE_FORAGING:
                        robot.pickup_resource(pointOfInterest)
                        robot.destination = globals.MARKER_HOME
                        robot.last_foraging_point = robot.position

                        # Arbitrary, makes sure the resource is in home (Hopefully)
                        robot.time_to_drop_out = randint(50, 150)

                elif robot.task == nest_maintenance:

                    if robot.is_on_area(TYPE_BROOD_CHAMBER) and robot.carry_resource and robot.payload_carry_time == 0:
                        #! sometimes the resource vanishes
                        robot.destination = None
                        if robot.time_in_zone >= robot.time_to_drop_out:
                            robot.transform_resource()
                        else:
                            robot.time_in_zone += 1

                    elif robot.is_on_area(TYPE_HOME):
                        robot.destination = None

                        if robot.carry_resource:
                            if globals.CNT - robot.payload_carry_time >= 200:
                                robot.destination = globals.MARKER_BROOD_CHAMBER
                                robot.time_to_drop_out = randint(50, 100)
                                robot.time_in_zone = 0
                                robot.payload_carry_time = 0

                        elif (robot_bottom_sensor_states == (2, 0) or robot_bottom_sensor_states == (0, 2)) and robot.carry_resource == False and pointOfInterest.state == RESOURCE_STATE_NEST_PROCESSING:
                            robot.pickup_resource(pointOfInterest)
                            robot.payload_carry_time = globals.CNT
                    else:
                        if robot.destination != globals.MARKER_BROOD_CHAMBER:
                            robot.destination = globals.MARKER_HOME

                elif robot.task == brood_care:

                    if robot.carry_resource:
                        if robot.is_on_area(TYPE_WAISTE_DEPOSIT):
                            robot.destination = None
                            if robot.time_in_zone >= robot.time_to_drop_out:
                                robot.trash_resource()
                            else:
                                robot.time_in_zone += 1
                        else:
                            robot.destination = globals.MARKER_WAISTE_AREA
                    else:
                        if robot.is_on_area(TYPE_BROOD_CHAMBER):
                            robot.destination = None
                            if (robot_bottom_sensor_states == (2, 0) or robot_bottom_sensor_states == (0, 2)) and robot.carry_resource == False and pointOfInterest.state == RESOURCE_STATE_TRANSFORMED:
                                robot.time_to_drop_out = 50
                                robot.time_in_zone = 0
                                robot.pickup_resource(pointOfInterest)
                                robot.destination = globals.MARKER_WAISTE_AREA
                        else:
                            robot.destination = globals.MARKER_BROOD_CHAMBER

        if robot.is_on_area(TYPE_CHARGING_AREA):
            if robot.destination == robot.start_position or robot.battery_low:

                if globals.CNT % 5 == 0 and robot.battery_level < 100:
                    robot.battery_level += 2

                if robot.battery_level >= 100:
                    robot.battery_low = False

                    if robot.carry_resource:
                        #! potential bug generator, if anything goes wrong look at it
                        robot.destination = robot.saved_destination
                    else:
                        robot.destination = None

        robot.step(robot_prox_sensors_values)
        # ###################################

        collided = robot.is_colliding(WORLD)

        if ACT:
            DRAW_bottom_sensor_position = [(robot.bottom_sensors[0].x, robot.bottom_sensors[0].y), (
                robot.bottom_sensors[1].x, robot.bottom_sensors[1].y)]

            VISUALIZER.draw(robot.position, robot.color, globals.CNT,
                            robot.path, robot.get_collision_box_coordinate(), robot.prox_sensors_state, DRAW_proximity_sensor_position, DRAW_bottom_sensor_position, robot_bottom_sensor_states, robot.number)

        # # Decrease robot's battery .. Nothing much accurate to real world, but it is part of robotic problems
        # if globals.CNT % 100 == 0 and not robot.is_on_area(TYPE_CHARGING_AREA):
        #     robot.battery_level -= randint(0, 4)
        #     if robot.battery_level < 25:

        #         # Robot's start position is its charging block
        #         robot.battery_low = True
        #         robot.saved_destination = robot.destination
        #         robot.destination = robot.start_position

        # Robot wise
        # if globals.DO_RECORD:
        # if globals.CNT % globals.M == 0:
        #     robot.path.append(robot.position.__dict__)

        if collided:
            print("Robot {} collided, position reseted".format(robot.number))
            robot.reset()

    if ACT:
        VISUALIZER.pygame_event_manager(pygame.event.get())
        VISUALIZER.draw_poi(globals.POIs)

    # World wise
    if globals.DO_RECORD:
        if globals.CNT % globals.M == 0:
            globals.DRAW_POIS.append([o.encode()
                                      for o in deepcopy(globals.POIs)])

    #! to delete
    if globals.CNT % 500 == 0:
        globals.NEST.resource_need -= 10

    # Task helper
    if globals.CNT % 10 == 0:
        print(chr(27) + "[2J")
        print(" ******* LIVE STATS [" + str(globals.CNT) + "] *******")
        print("N° | % | State | Task | Q")
        for robot in globals.ROBOTS:
            print("["+str(robot.number)+"]: "+str(robot.battery_level) +
                  " | "+STATES_NAME[robot.state] +
                  " | "+TASKS_NAME[robot.task - 1])
        TaskHandler.print_stats()

        # print to csv file
        # TODO could be nice to also print each robot task and state to see oscillation ?
        txt = str(globals.CNT)+";"
        for i in range(1, len(TASKS) + 1):
            txt += assigned(i) + ";"
            if i == foraging:
                txt += str(globals.NEST.resource_need * -1)+";"
            elif i == nest_maintenance:
                txt += str(globals.NEST.resource_stock)+";"
            elif i == brood_care:
                txt += str(globals.NEST.resource_transformed)
        globals.CSV_FILE.write(txt+"\n")

    if ACT:
        pygame .display.flip()  # render drawing
        fpsClock.tick(fps)
