# -*- coding: utf-8 -*-
import errno
import os
from random import uniform
from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, zeros
from PointOfInterest import PointOfInterest
from shapely.geometry.point import Point
from shapely.ops import nearest_points
from Visualizator import delete_class
from Visualizator import Visualizator
from shapely.affinity import rotate
from Position import Position
from pygame.locals import *
from copy import deepcopy

from Robot import add_robot
from Robot import Robot

from time import sleep
from Area import Area
from Nest import Nest
from random import *

from const import no_task, foraging, nest_processing, cleaning, TASKS_NAME, TASKS, STATES_NAME
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

nb_robot = 0
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
for _ in range(nb_robot):
    add_robot()

###############################################################################


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

        robot.time_to_task_report += 1
        if robot.time_to_task_report % 600 == 0:
            robot.time_to_task_report = 599
            robot.has_to_report = True
        if not robot.battery_low:

            if robot.is_on_area(TYPE_HOME) and not robot.carry_resource:
                # if robot.is_on_area(TYPE_HOME) and not robot.carry_resource and (robot.task == 0 or not robot.has_to_work()):
                robot.has_to_report = True

            if robot.has_to_report:
                if robot.is_on_area(TYPE_HOME):
                    robot.destination = None

                    """ Now let's say .. a bi-directional communication is engaged when a robot is asking for a report"""
                    nest_did_receive, robot_did_receive, packet = globals.NEST.try_report_and_get_task(robot.TASKS_Q, robot.task, robot.state, robot.color, robot.n_task_switch,
                                                                                                       robot.number, robot.battery_level, robot.trashed_resources, robot.resource_transformed, robot.resource_stock, robot.carry_resource)

                    # Here I could or maybe should have some communication overhead .. ?
                    # Maybe I should just say in the thesis that I disergard the communication over head.
                    # 'Cause when you initiate a connection with the nest in real life nothing says he will reply INSTANTLY

                    # in real life we would probabily have a while not re1ceive wait, timeout after n second and proceed with the stored information ..
                    # Quite hard to model
                    # Yeah it is going to be part of one of my asusmption I guess..
                    if robot_did_receive:
                        # Basically saying that if you haven't received data you are going to base you new
                        # Task on the memory you have of where everyone is at, which is basically the same as
                        # not being allocated a new task.
                        # So allocate task only if you receive information from the nest

                        robot.task = packet.task
                        robot.state = packet.state
                        robot.TASKS_Q = packet.TASKS_Q
                        robot.color = packet.color
                        robot.n_task_switch = packet.n_task_switch

                    # if the robot receive its new task, it means the nest had receive its report status
                    # Hard to tell if the nest receive if you don't receive answer back, but this is here as it is
                    # Related to the FAITA memory symbol comment a bit below
                    if nest_did_receive:

                        """ if try report returns True, then the nest has receive the information of the robot"""
                        """ if the nest receives a robot's information, it will reply by giving it the current status of each task"""
                        """ here in the code, this is symbolized by assigning the robot to a new task (since we could say "if I receive something from the nest, it's because I have previously sent my report, thus I will see if I need a new task now given what I just received from the nest)"""

                        # Including the below line (and "if nest_did_receive") sort of act as how the brain works in FAITA.
                        # In FAITA every time a robot receive an information it compares it to the memory brain it has of the robot's received information
                        # if the data differs it means the robot has done more since the last time it has contact "me", so update the internal demand.
                        # here I did not think this would be a problem until I added noise.
                        # Since the noise is added, if I did not include the below line (which regarding the current implementation would be the right thing to do)
                        # then some information would be lost as it resets the robot's knowledge on what it has done (and since a report can fail then he would lost this snapshot's information).
                        # Adding the line act the same as how the memory of a robot works in FAITA, but it's just not a correct implementation -> gain of time.
                        robot.trashed_resources, robot.resource_transformed, robot.resource_stock = 0, 0, 0

                    robot.has_to_report = False
                    robot.time_to_task_report = 0

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

        if robot.has_to_finish_task_before_stop:
            # If not, the robot has terminated its task, it can be killed
            if not robot.carry_resource:
                globals.NEST.report(
                    robot.number, 0, False, 100, robot.trashed_resources, robot.resource_transformed, robot.resource_stock)
                robot.reset()
                robot.trashed_resources, robot.resource_transformed, robot.resource_stock = 0, 0, 0
                globals.ADD_AVAILABLE_ROBOTS.append(robot)
                globals.ROBOTS.pop(i)

    globals.NEST.pkg = False
    if ACT:
        VISUALIZER.pygame_event_manager(pygame.event.get())
        VISUALIZER.draw_poi(globals.POIs)

    if globals.CNT % 500 == 0:
        globals.NEST.resource_need += resource_decrease_number

    # Task helper
    if globals.CNT % 10 == 0:
        task_assigned_unassigned = [globals.NEST.TaskHandler.assigned(
            t) for t in TASKS]

        task_assigned_unassigned_pov_nest = [globals.NEST.TaskHandler.assigned_pov_nest(
            t) for t in TASKS]

        print(chr(27) + "[2J")
        print(" ******* LIVE STATS [" + str(globals.CNT) + "] *******")
        print("N° | % | State | Task | Q | Timestep since last report | Has to report | N switch")
        for robot in globals.ROBOTS:
            print("["+str(robot.number)+"]: "+str(robot.battery_level) +
                  " | "+STATES_NAME[robot.state] +
                  " | "+TASKS_NAME[robot.task - 1] +
                  " | "+str(robot.time_to_task_report) +
                  " | " + ("True" if robot.has_to_report else "False") +
                  " | " + str(robot.TASKS_Q) +
                  " | " + str(robot.n_task_switch))

        globals.NEST.TaskHandler.print_stats(task_assigned_unassigned)

        # print to csv file
        # TODO add a metric for total distance over POI density
        txt = str(globals.CNT)+";"
        for i in TASKS:
            txt += str(task_assigned_unassigned[i-1][0]) + \
                ";" + str(task_assigned_unassigned[i-1][1])+";"

            txt += str(task_assigned_unassigned_pov_nest[i-1][0]) + \
                ";" + str(task_assigned_unassigned_pov_nest[i-1][1])+";"

            txt += str(globals.NEST.demand(i)) + ";"

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
            class_to_delete = 2

            keep_alive_robot = []
            for robot in globals.ROBOTS:

                if not robot.task == class_to_delete or (robot.task == class_to_delete and not robot.has_to_work()):
                    keep_alive_robot.append(robot)

                elif robot.carry_resource and robot.task == class_to_delete:
                    robot.has_to_finish_task_before_stop = True
                    keep_alive_robot.append(robot)

                elif robot.task == class_to_delete and robot.has_to_work():
                    globals.NEST.report(
                        robot.number, 0, False, 100, robot.trashed_resources, robot.resource_transformed, robot.resource_stock)
                    robot.reset()
                    robot.trashed_resources, robot.resource_transformed, robot.resource_stock = 0, 0, 0
                    globals.ADD_AVAILABLE_ROBOTS.append(robot)

            globals.ROBOTS = keep_alive_robot

        if globals.CNT == 15000:
            globals.ROBOTS += globals.ADD_AVAILABLE_ROBOTS

    if ACT:
        pygame .display.flip()  # render drawing
        fpsClock.tick(fps)

    #! here I could shuffle robot list so that the execution order is never the same. Less deterministic, more realistic.
    # shuffle(globals.ROBOTS)
