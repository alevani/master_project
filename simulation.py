# -*- coding: utf-8 -*-
from random import uniform
from shapely.geometry import LinearRing, LineString, Point, Polygon
from PSISensedInformationPacket import PSISensedInformationPacket
from GreedyTaskHandler import GreedyTaskHandler
from numpy import sin, cos, pi, sqrt, zeros
from PointOfInterest import PointOfInterest
from PSITaskHandler import PSITaskHandler
from shapely.geometry.point import Point
from shapely.ops import nearest_points
from Visualizator import Visualizator
from shapely.affinity import rotate
from TaskHandler import TaskHandler
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
from const import RESOURCE_STATE_TRANSFORMED
from const import RESOURCE_STATE_FORAGING
from const import RESOURCE_STATE_WAISTE
from const import MARKER_BROOD_CHAMBER
from const import MARKER_WAISTE_AREA
from const import X_lower_bound
from const import X_upper_bound
from const import Y_lower_bound
from const import Y_upper_bound
from const import MARKER_HOME
from const import TYPE_HOME
from const import scaleup
from const import dist
from const import W
from const import H


import numpy as np
import threading
import shapely
import globals
import pygame
import getopt
import json
import math
import sys

# IDEAS
########
# ? MVC Refactor
### GLOBALS ###################################################################
try:
    opts, args = getopt.getopt(sys.argv[1:], "hr:p:s:b:t:a:")
except getopt.GetoptError:
    print('python simulation.py -r <nb_robot> -p <np_point> -s <is_simulation_visible> -b <do_robot_lose_battery> -t <do_record_trail> -a <avoidance_activation')
    sys.exit(2)

nb_robot = 0
nb_point = 0
ACT = None
battery_effects = None
do_record_trail = None

for opt, arg in opts:
    if opt == "-h":
        print('python simulation.py -r <nb_robot> -p <np_point> -s <is_simulation_visible> -b <do_robot_lose_battery> -t <do_record_trail> -a <avoidance_activation')
        sys.exit(2)

    if opt == "-r":
        nb_robot = int(arg)
    elif opt == "-p":
        nb_point = int(arg)
    elif opt == "-s":
        ACT = True if arg == "True" else False
    elif opt == "-b":
        battery_effects = True if arg == "True" else False
    elif opt == "-t":
        do_record_trail = True if arg == "True" else False
    elif opt == "-a":
        globals.do_avoid = True if arg == "True" else False

# WORLD
WORLD = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

globals.CSV_FILE = open("stats/stats.csv", "w")

if ACT:
    VISUALIZER = Visualizator()
    pygame.init()
    fps = 60
    fpsClock = pygame.time.Clock()
###############################################################################

### Task allocation #########################################################
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
#############################################################################

### Start's variables #########################################################
# Slow at creation, and heavy, but considerabely increase visualisation speed.
for x in range(int(W * 100)):
    inner = []
    for y in range(int(H * 100)):
        inner.append(0)
    globals.PHEROMONES_MAP.append(inner)


# Areas
AREAS = []
TYPE_NEUTRAL = 0
TYPE_BROOD_CHAMBER = 3
TYPE_WAISTE_DEPOSIT = 4
TYPE_FORAGING_AREA = 5

home = Area(Position(0 - 2.1, -H/2+0.5), 1.4, 1.4, TYPE_HOME, (133, 147, 255))

brood_chamber = Area(Position(0 - 0.7, -H/2+0.5), 1.4,
                     1.4, TYPE_BROOD_CHAMBER, (224, 153, 255))

waiste_deposit = Area(Position(W/2-1.4, H/2-1.4), 1.4,
                      1.4, TYPE_WAISTE_DEPOSIT, (240, 188, 91))

foraging_area = Area(Position(-W/2, -H/2), W,
                     H, TYPE_FORAGING_AREA, (255, 255, 255))

AREAS.append(foraging_area)
AREAS.append(home)
AREAS.append(brood_chamber)
AREAS.append(waiste_deposit)


def is_point_on_area(x, y):
    box = Point(x, y).buffer(0.01)
    for area in AREAS[1:]:  # Disregards the foraging area as it is the entire map
        if area.box.intersects(box):
            return True
    return False


# Adds random point on the map (up to nb_point)
for _ in range(nb_point):
    x = uniform(X_lower_bound, X_upper_bound)
    y = uniform(Y_lower_bound, Y_upper_bound)

    if not is_point_on_area(x, y):
        index = len(globals.POIs)
        globals.POIs.append(PointOfInterest(
            Position(x, y), 15000, 2, "s"))

        x_scaled, y_scaled = scaleup(x, y)

        # resource_value = randint(1, 2)
        resource_value = 1  # if random, then it biases the need for a task
        globals.PHEROMONES_MAP[x_scaled][y_scaled] = PointOfInterest(
            Position(x_scaled, y_scaled), 15000, 2, resource_value, index)


globals.NEST = Nest(-10)
for _ in range(nb_robot):
    add_robot()

PSITaskHandler = PSITaskHandler()
###############################################################################


def get_proximity_sensors_values(robot_rays, robot):
    values = []

    # Wall detection
    for index, ray in enumerate(robot_rays):
        point = WORLD.intersection(ray)
        values.append(dist((point.x, point.y),
                           (robot.proximity_sensors[index].x, robot.proximity_sensors[index].y)))

    # Robot detection
    if globals.do_avoid:
        for r in globals.ROBOTS:

            # Don't check ourselves
            if r.number != robot.number:

                # in range is used to reduce the amount of robot the robot as to compare.
                # TODO I could change to a polygone of the shape of the front row detection, I would have less to check :)

                if robot.in_range(r.position):

                    # "If one of my rays can sense you, get the distance"
                    for index, ray in enumerate(robot_rays):
                        if r.is_sensing(ray):

                            # # ? TEST: if I don't have any last_foraging_point, maybe the robot that I am sensing has one?
                            # # TODO delete if I choose to say "no communication within the robot what-so-ever"
                            # if r.last_foraging_point != None and robot.last_foraging_point == None:
                            #     robot.last_foraging_point = r.last_foraging_point

                            p1, p2 = nearest_points(r.get_collision_box(), Point(
                                robot.proximity_sensors[index].x, robot.proximity_sensors[index].y))
                            values[index] = dist(
                                (p1.x, p1.y), (p2.x, p2.y))

    return values


def update_comm_state(robot_rays, robot):
    for r in globals.ROBOTS:
        # Don't check ourselves
        if r.number != robot.number:
            #! my robot cannot really go up to 50cm, is it clever to keep going even if so ..?
            if robot.in_comm_range(r.position):
                for index, ray in enumerate(robot_rays):
                    if r.is_sensing(ray):

                        #! is deterministic, maybe introduce some noise to be closer to the reality
                        if robot.sensed_robot_information == None:
                            # ? Does it really need to be wrapped in an object? high overhead.
                            return PSISensedInformationPacket(r.x, r.task)
    return None


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

        robot.stop()
        robot.sense_area(AREAS)

        if not robot.battery_low:

            robot.sensed_robot_information = update_comm_state(
                robot_rays, robot)

            if robot.sensed_robot_information != None:
                PSITaskHandler.eq3_4(robot, robot.sensed_robot_information)

                # ? Does the information really has to be deleted when used?
                robot.sensed_robot_information = None  # Information consumed

            PSITaskHandler.eq6(robot)
            PSITaskHandler.eq5(robot)

            """ BROADCAST DATA -> induced by just updating the value and the robot being able to sense others at any given time. """
            PSITaskHandler.eq7(robot)

            # TODO has_to_work and anything related to an ant state is obsolete

            # if the robot does not have to work .. let it rest in its charging area.
            if not robot.has_to_work():
                if not robot.has_destination():
                    if robot.carry_resource:
                        robot.drop_resource()

                    robot.last_foraging_point = None
                    robot.go_and_stay_home()

            # the robot has to be active
            else:
                if robot.task == no_task:
                    robot.last_foraging_point = None
                    robot.go_and_stay_home()

                elif robot.task == foraging:

                    if robot.carry_resource and not robot.has_destination():
                        robot.destination = MARKER_HOME

                    if not robot.carry_resource:
                        if not robot.is_on_area(TYPE_FORAGING_AREA):
                            # Toggle for robot spread at start
                            # robot.destination = robot.last_foraging_point if not robot.last_foraging_point == None else Position(
                            #     0, 0)
                            robot.destination = robot.last_foraging_point if not robot.last_foraging_point == None else None
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
                        robot.destination = MARKER_HOME
                        robot.last_foraging_point = robot.position

                        # Arbitrary, makes sure the resource is in home (Hopefully)
                        robot.time_to_drop_out = randint(50, 150)

                elif robot.task == nest_maintenance:

                    if robot.is_on_area(TYPE_BROOD_CHAMBER) and robot.carry_resource and robot.payload_carry_time == 0:
                        robot.destination = None
                        if robot.time_in_zone >= robot.time_to_drop_out:
                            robot.transform_resource()
                        else:
                            robot.time_in_zone += 1

                    elif robot.is_on_area(TYPE_HOME):
                        robot.destination = None

                        if robot.carry_resource:
                            if globals.CNT - robot.payload_carry_time >= 200:
                                robot.destination = MARKER_BROOD_CHAMBER
                                robot.time_to_drop_out = randint(50, 100)
                                robot.time_in_zone = 0
                                robot.payload_carry_time = 0

                        elif (robot_bottom_sensor_states == (2, 0) or robot_bottom_sensor_states == (0, 2)) and robot.carry_resource == False and pointOfInterest.state == RESOURCE_STATE_NEST_PROCESSING:
                            robot.pickup_resource(pointOfInterest)
                            robot.payload_carry_time = globals.CNT
                    else:
                        if robot.destination != MARKER_BROOD_CHAMBER:
                            robot.destination = MARKER_HOME

                elif robot.task == brood_care:

                    if robot.carry_resource:
                        if robot.is_on_area(TYPE_WAISTE_DEPOSIT):
                            robot.destination = None
                            if robot.time_in_zone >= robot.time_to_drop_out:
                                robot.trash_resource()
                            else:
                                robot.time_in_zone += 1
                        else:
                            robot.destination = MARKER_WAISTE_AREA
                    else:
                        if robot.is_on_area(TYPE_BROOD_CHAMBER):
                            robot.destination = None
                            if (robot_bottom_sensor_states == (2, 0) or robot_bottom_sensor_states == (0, 2)) and robot.carry_resource == False and pointOfInterest.state == RESOURCE_STATE_TRANSFORMED:
                                robot.time_to_drop_out = 50
                                robot.time_in_zone = 0
                                robot.pickup_resource(pointOfInterest)
                                robot.destination = MARKER_WAISTE_AREA
                        else:
                            robot.destination = MARKER_BROOD_CHAMBER

        if robot.is_on_area(TYPE_HOME):
            if robot.destination == robot.start_position or robot.battery_low:

                if globals.CNT % 5 == 0 and robot.battery_level < 100:
                    robot.battery_level += 2

                if robot.battery_level >= 100:
                    robot.battery_low = False

                    if robot.carry_resource:
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

        # Decrease robot's battery .. Nothing much accurate to real world, but it is part of robotic problems
        if battery_effects:
            if globals.CNT % 100 == 0 and not robot.is_on_area(TYPE_HOME):
                robot.battery_level -= randint(0, 4)
                if robot.battery_level < 25:

                    # Robot's start position is its charging block
                    robot.battery_low = True
                    robot.saved_destination = robot.destination
                    robot.destination = robot.start_position

        # Robot wise
        if do_record_trail:
            if globals.CNT % globals.M == 0:
                robot.path.append(robot.position.__dict__)

        if collided:
            print("Robot {} collided, position reseted".format(robot.number))
            robot.reset()

    if ACT:
        VISUALIZER.pygame_event_manager(pygame.event.get())
        VISUALIZER.draw_poi(globals.POIs)

    if globals.CNT % 500 == 0:
        globals.NEST.resource_need -= 5

    # Task helper
    if globals.CNT % 10 == 0:
        print(chr(27) + "[2J")
        print(" ******* LIVE STATS [" + str(globals.CNT) + "] *******")
        print("N° | % | State | Task | Q | Timestep since last report | Has to report")
        for robot in globals.ROBOTS:
            print("["+str(robot.number)+"]: "+str(robot.battery_level) +
                  " | "+STATES_NAME[robot.state] +
                  " | "+TASKS_NAME[robot.task - 1] +
                  " | "+str(robot.time_to_task_report) +
                  " | " + ("True" if robot.has_to_report else "False") +
                  " | " + str(robot.TASKS_Q))

        task_assigned_unassigned = [TaskHandler.assigned(
            t) for t in range(1, len(TASKS) + 1)]

        TaskHandler.print_stats(task_assigned_unassigned)

        # print to csv file
        # TODO add a metric for total distance over POI density
        txt = str(globals.CNT)+";"
        for i in range(1, len(TASKS) + 1):
            txt += str(task_assigned_unassigned[i-1][0]) + \
                ";" + str(task_assigned_unassigned[i-1][1])+";"
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
