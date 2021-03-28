# -*- coding: utf-8 -*-
import errno
import os
from random import uniform
from shapely.geometry import LinearRing, LineString, Point, Polygon
from PSISensedInformationPacket import PSISensedInformationPacket
from numpy import sin, cos, pi, sqrt, zeros
from PSITaskHandler import PSITaskHandler
from PointOfInterest import PointOfInterest
from shapely.geometry.point import Point
from shapely.ops import nearest_points
from Visualizator import delete_class
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
from const import RESOURCE_STATE_WASTE
from const import MARKER_CLEANING_AREA
from const import MARKER_WASTE_AREA
from const import X_lower_bound
from const import X_upper_bound
from const import Y_lower_bound
from const import Y_upper_bound
from const import MARKER_HOME
from const import TYPE_HOME
from const import scaleup
from const import COLORS
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
#! TODO have a file.close when sys.exit to makek sure no data is lost
# TODO do the median and not the mean
### GLOBALS ###################################################################
try:
    opts, args = getopt.getopt(sys.argv[1:], "hr:p:s:b:t:a:n:f:e:")
except getopt.GetoptError:
    print(
        'python simulation.py -r <nb_robot> -p <np_point> -s <is_simulation_visible> -b <do_robot_lose_battery> -t <do_record_trail> -a <avoidance_activation> -n <probability of communication failure [0,1]> -f <stats_file_name.csv> -e <exp_number>')
    sys.exit(2)

nb_point = 0
ACT = None
battery_effects = None
do_record_trail = None
exp_number = None
resource_decrease_number = 5
nest_start_value = 25
for opt, arg in opts:
    if opt == "-h":
        print('python simulation.py -r <nb_robot> -p <np_point> -s <is_simulation_visible> -b <do_robot_lose_battery> -t <do_record_trail> -a <avoidance_activation> -f <stats_file_name.csv> -e <exp_number (1 or 2)>')
        sys.exit(2)

    if opt == "-r":
        globals.NB_ROBOTS = int(arg)
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
    elif opt == "-n":
        globals.PROB_COMM_FAILURE = float(arg)
        if globals.PROB_COMM_FAILURE > 1 or globals.PROB_COMM_FAILURE < 0:
            print(
                "Warning, probability of communication failure was not within [0,1].")
            globals.PROB_COMM_FAILURE = 0 if globals.PROB_COMM_FAILURE < 0 else 1
    elif opt == "-f":

        filename = "stats/"+arg

        if "£" in arg:
            resource_decrease_number = 7
        elif "æ" in arg:
            nest_start_value = 50
    elif opt == "-e":
        exp_number = int(arg)


if not os.path.exists(os.path.dirname(filename)):
    try:
        os.makedirs(os.path.dirname(filename))
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise
globals.CSV_FILE = open(filename, "w")
# WORLD
WORLD = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])


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
nest_processing = 2
cleaning = 3


TASKS_NAME = ['Foraging',
              'Nest processing', 'Cleaning']

TASKS.append(foraging)
TASKS.append(nest_processing)
TASKS.append(cleaning)
#############################################################################
n_robot_to_add = 0
### Start's variables #########################################################
# Slow at creation, and heavy, but considerabely increase visualisation speed.
for x in range(int(W * 100)):
    inner = []
    for y in range(int(H * 100)):
        inner.append(0)
    globals.PHEROMONES_MAP.append(inner)


# Areas
AREAS = []

TYPE_CLEANING_AREA = 3
TYPE_WASTE_AREA = 4
TYPE_FORAGING_AREA = 5

home = Area(Position(0 - 2.1, -H/2+0.5), 1.4, 1.4, TYPE_HOME, (133, 147, 255))

# home = Area(Position(0 - 2.1 - .5, -H/2+0.5 - .5),
#             2.4, 2.4, TYPE_HOME, (133, 147, 255))

cleaning_area = Area(Position(0 - 0.7, -H/2+0.5), 1.4,
                     1.4, TYPE_CLEANING_AREA, (224, 153, 255))

waste_area = Area(Position(W/2-1.4, H/2-1.4), 1.4,
                  1.4, TYPE_WASTE_AREA, (240, 188, 91))

foraging_area = Area(Position(-W/2, -H/2), W,
                     H, TYPE_FORAGING_AREA, (255, 255, 255))

AREAS.append(foraging_area)
AREAS.append(home)
AREAS.append(cleaning_area)
AREAS.append(waste_area)


def is_point_on_area(x, y):
    box = Point(x, y).buffer(0.01)
    for area in AREAS[1:]:  # Disregards the foraging area as it is the entire map
        if area.box.intersects(box):
            return True
    return False


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


globals.NEST = Nest(nest_start_value)
for _ in range(globals.NB_ROBOTS):
    add_robot(nest_start_value, 1)

TaskHandler = TaskHandler(TASKS)
PSITaskHandler = PSITaskHandler()
###############################################################################
# something a bit problematic here is that the ray does not stop when it touches
# a robot which will lead into information shared throughout bodies (physically impossible)


def comm(robot_rays, robot):
    '''
    Broadcast your information to everyone. 
    '''
    # Comm that covers the entire Arena. (sends the information to itself so it can register it in its memory)
    for r in globals.ROBOTS:
        if r.number == robot.number:
            r.memory.register(robot.number, robot.task, robot.has_to_work(), [
                robot.resource_stock, robot.resource_transformed, robot.trashed_resources])
        else:
            r.try_register((robot.number, robot.task, robot.has_to_work(), [
                robot.resource_stock, robot.resource_transformed, robot.trashed_resources]), robot.x)


def get_proximity_sensors_values(robot_rays, robot):
    values = []

    # Wall detection
    for index, ray in enumerate(robot_rays):
        point = WORLD.intersection(ray)
        values.append(dist((point.x, point.y),
                           (robot.proximity_sensors[index].x, robot.proximity_sensors[index].y)))

    if globals.do_avoid:
        for index, ray in enumerate(robot_rays):
            for r in globals.ROBOTS:

                # Don't check ourselves
                if r.number != robot.number:
                    # TODO I could change to a polygone of the shape of the front row detection, I would have less to check :)
                    if robot.in_range(r.position):
                        if r.is_sensing(ray):
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

    for i, robot in enumerate(globals.ROBOTS):

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

        # This is because sometimes the robot would not change it task because it was carrying a resource
        # but its x would change anyway and then the X wouldn't match the segment of the task the robot is in
        if robot.has_to_change_task_but_carry_resource and not robot.carry_resource:
            robot.task = robot.new_task
            PSITaskHandler.eq7(robot)
            robot.has_to_change_task_but_carry_resource = False

        if not robot.battery_low:

            if robot.network_packet != None:

                robot.consume_network_packet()
                PSITaskHandler.eq3_4(
                    robot, robot.task_packet)

                robot.task_packet = None  # Information consumed

            PSITaskHandler.eq6(robot)
            PSITaskHandler.eq5(robot)

            comm(robot_rays, robot)
            robot.memory.step()
            robot.color = COLORS[robot.task]

            # Don't switch off task if you are carrying a resouce.
            if not robot.carry_resource:
                PSITaskHandler.eq7(robot)
            elif not robot.has_to_change_task_but_carry_resource:
                old_task = robot.task
                PSITaskHandler.eq7(robot)
                robot.new_task = robot.task
                robot.task = old_task
                robot.has_to_change_task_but_carry_resource = True

            # if the robot does not have to work .. let it rest in its charging area.
            if not robot.has_to_work():
                if not robot.has_destination():
                    if robot.carry_resource:
                        robot.drop_resource()

                    robot.last_foraging_point = None

                    if globals.do_avoid:
                        robot.go_and_stay_home()
                    else:
                        robot.destination = MARKER_HOME

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

                elif robot.task == nest_processing:

                    if robot.is_on_area(TYPE_CLEANING_AREA) and robot.carry_resource and robot.payload_carry_time == 0:
                        robot.destination = None
                        if robot.time_in_zone >= robot.time_to_drop_out:
                            robot.transform_resource()
                        else:
                            robot.time_in_zone += 1

                    elif robot.is_on_area(TYPE_HOME):
                        robot.destination = None

                        if robot.carry_resource:
                            if globals.CNT - robot.payload_carry_time >= 200:
                                robot.destination = MARKER_CLEANING_AREA
                                robot.time_to_drop_out = randint(50, 100)
                                robot.time_in_zone = 0
                                robot.payload_carry_time = 0

                        elif (robot_bottom_sensor_states == (2, 0) or robot_bottom_sensor_states == (0, 2)) and robot.carry_resource == False and pointOfInterest.state == RESOURCE_STATE_NEST_PROCESSING:
                            robot.pickup_resource(pointOfInterest)
                            robot.payload_carry_time = globals.CNT
                    else:
                        if robot.destination != MARKER_CLEANING_AREA:
                            robot.destination = MARKER_HOME

                elif robot.task == cleaning:

                    if robot.carry_resource:
                        if robot.is_on_area(TYPE_WASTE_AREA):
                            robot.destination = None
                            if robot.time_in_zone >= robot.time_to_drop_out:
                                robot.trash_resource()
                            else:
                                robot.time_in_zone += 1
                        else:
                            robot.destination = MARKER_WASTE_AREA
                    else:
                        if robot.is_on_area(TYPE_CLEANING_AREA):
                            robot.destination = None
                            if (robot_bottom_sensor_states == (2, 0) or robot_bottom_sensor_states == (0, 2)) and robot.carry_resource == False and pointOfInterest.state == RESOURCE_STATE_TRANSFORMED:
                                robot.time_to_drop_out = 50
                                robot.time_in_zone = 0
                                robot.pickup_resource(pointOfInterest)
                                robot.destination = MARKER_WASTE_AREA
                        else:
                            robot.destination = MARKER_CLEANING_AREA

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
        ###################################

        collided = robot.is_colliding(WORLD)

        if ACT:
            DRAW_bottom_sensor_position = [(robot.bottom_sensors[0].x, robot.bottom_sensors[0].y), (
                robot.bottom_sensors[1].x, robot.bottom_sensors[1].y)]

            VISUALIZER.draw(robot.position, robot.color, globals.CNT,
                            robot.path, robot.get_collision_box_coordinate(), [], DRAW_proximity_sensor_position, DRAW_bottom_sensor_position, robot_bottom_sensor_states, robot.number)

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

        if robot.has_to_finish_task_before_stop:
            # If not, the robot has terminated its task, it can be killed
            if not robot.carry_resource:
                robot.has_to_finish_task_before_stop = False
                robot.reset()
                globals.ADD_AVAILABLE_ROBOTS.append(robot)
                globals.ROBOTS.pop(i)

    if ACT:
        VISUALIZER.pygame_event_manager(pygame.event.get())
        VISUALIZER.draw_poi(globals.POIs)

    if globals.CNT % 500 == 0:
        for robot in globals.ROBOTS:
            robot.memory.demand_memory[0] += resource_decrease_number
        for robot in globals.ADD_AVAILABLE_ROBOTS:
            robot.memory.demand_memory[0] += resource_decrease_number
        globals.NEST.resource_need += resource_decrease_number

    # Task helper
    if globals.CNT % 10 == 0:
        print(chr(27) + "[2J")
        print(" ******* LIVE STATS [" + str(globals.CNT) + "] *******")
        print("N° | % | Task | Demand | PSI demand | x | x_high | x_low")
        for robot in globals.ROBOTS:
            print("["+str(robot.number)+"]: "+str(robot.battery_level) +
                  " | "+TASKS_NAME[robot.task - 1] +
                  " | " + str(robot.memory.demand_memory) +
                  " | " + str(robot.memory.PSI_demand) +
                  " | "+str(robot.x) +
                  " | "+str(robot.x_high) +
                  " | "+str(robot.x_low))

        task_assigned_unassigned = [TaskHandler.assigned(
            t) for t in TASKS]
        TaskHandler.print_stats(task_assigned_unassigned)

        average_robot_demand = [0, 0, 0]

        for robot in globals.ROBOTS:
            for i, d in enumerate(robot.memory.demand_memory):
                average_robot_demand[i] += d

        average_robot_demand = [
            e/len(globals.NB_ROBOTS) for e in average_robot_demand]
        print(average_robot_demand)
        # print to csv file
        # TODO add a metric for total distance over POI density
        txt = str(globals.CNT)+";"
        for i in TASKS:
            txt += str(task_assigned_unassigned[i-1][0]) + \
                ";" + str(task_assigned_unassigned[i-1][1])+";"

            txt += str(globals.NEST.demand(i)) + ";" + \
                str(average_robot_demand[i - 1]) + ";"

        txt += str(float(globals.total_dist))
        txt += ";" + str(globals.NEST.total) + ";"
        for robot in globals.ROBOTS:
            txt += "(" + str(robot.number) + "," + \
                str(robot.n_task_switch)+");"

        globals.CSV_FILE.write(txt+"\n")

        if exp_number == 2:
            if globals.CNT >= 30000:
                import sys
                sys.exit()
        elif exp_number == 1:
            if globals.NEST.total >= 50:
                import sys
                sys.exit()

        elif exp_number == 3:
            if globals.CNT >= 25000:
                import sys
                sys.exit()

            if globals.CNT == 10000:
                classes_to_delete = [3]

                keep_alive_robot = []
                for robot in globals.ROBOTS:
                    if not robot.task in classes_to_delete:
                        keep_alive_robot.append(robot)

                    elif robot.carry_resource and robot.task in classes_to_delete:
                        robot.has_to_finish_task_before_stop = True
                        keep_alive_robot.append(robot)

                    elif robot.task in classes_to_delete:
                        robot.reset()
                        globals.ADD_AVAILABLE_ROBOTS.append(robot)

                globals.ROBOTS = keep_alive_robot

            if globals.CNT == 20000:
                globals.ROBOTS += globals.ADD_AVAILABLE_ROBOTS

    if ACT:
        pygame .display.flip()  # render drawing
        fpsClock.tick(fps)
