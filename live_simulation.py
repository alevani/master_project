from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, zeros
from shapely.geometry.point import Point
from shapely.ops import nearest_points
from shapely.affinity import rotate
from utils_simu import Visualizator
from roboty import PointOfInterest
from robot_start_vars import *
from world import decay_check
from task import TaskHandler
from pygame.locals import *
from utils import distance
from task import assigned
from copy import deepcopy
from roboty import Robot
from roboty import Area
from roboty import Nest
from time import sleep
from random import *
import numpy as np
import threading
import shapely
import globals
import pygame
import json
import math
import sys

# IDEAS
# !!!!!! not experiment before all the measurments and the brain completed.

#! maybe re-implement the whole interest level thingy....
#! https://github.com/alevani/master_project/commit/d7812d9175dfd5a8090e68be942d5bbc83cb0e68


#! it could be interesting to implement a comm system that would tell the other forager a robot encounter where is your foraging point
#! it could be interesting for a forager to live a trail on the ground and for another forager to follow it (increase the chances of food encountering) -> how good or how bad is it to do it?
#! could be nice to have something to save a state .. ? and then load back the state for study

#! ok to retrace what happended it will actually be interesting to be able to visu ..
########

### GLOBALS ###################################################################

# WORLD
# TODO Redo measurements of the robot's sensors' position

W = globals.W
H = globals.H

WORLD = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

# PYGAME
if globals.DO_RECORD:
    FILE = open("points.json", "w")
else:
    FILE = None

globals.CSV_FILE = open("stats.csv", "w")

DECAY = 750
VISUALIZER = Visualizator(W, H, DECAY, FILE)
pygame.init()
fps = 60
fpsClock = pygame.time.Clock()
###############################################################################

### Task allocation #########################################################
resting = 0
STATES_NAME = ['Resting', 'First reserve',
               'Second reserve', 'Temporary worker', 'Core worker']

# Energy of a task
TASKS_Q = []

# Array to keep track of the tasks
TASKS = []

# A task is a tuple of its energy and a task object
idle = 0
foraging = 1
nest_maintenance = 2
brood_care = 3
patrolling = 4

TASKS_NAME = ['Idle', 'Foraging',
              'Nest maintenance', 'Brood care', 'Patrolling']

TASKS_Q.append(0)  # Idle
TASKS_Q.append(0)  # Foraging
TASKS_Q.append(0)  # Nest maintenance
TASKS_Q.append(0)  # Brood care
# TASKS_Q.append(0) # Patrolling

TASKS.append(idle)
TASKS.append(foraging)
TASKS.append(nest_maintenance)
TASKS.append(brood_care)
# TASKS.append(patrolling)

globals.NEST = Nest(0)
TaskHandler = TaskHandler(globals.NEST, TASKS_Q, TASKS)
#############################################################################

### Start's variables #########################################################


#! robot gather resource (foraging).. then a few of these resource will be transform (brood_caring) and finally waste frmo the transformation will be clean (nest maintenance) ?
#! we could also imagine a waste task where the robot would take pills from the nest to the waste once transformed by the brood worker.
#! I think it is important to have task where needs depends on other task.
#! pas normal: the robot should not wait for a task need to be fulfilled before thinking of re-assignement .. should they?

BASE_BATTERY_LEVEL = 100
BLACK = (0, 0, 0)

R1 = Robot(1, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+0.2+3.3, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R2 = Robot(2, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+0.4 + 3.3, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R3 = Robot(3, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+0.6 + 3.3, math.radians(
    0)), BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R4 = Robot(4, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+0.8 + 3.3, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R5 = Robot(5, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+1 + 3.3, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R6 = Robot(6, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+1.2 + 3.3, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R7 = Robot(7, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+1.4 + 3.3, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R8 = Robot(8, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+1.6 + 3.3, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R9 = Robot(9, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+1.8 + 3.3, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R10 = Robot(10, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+2 + 3.3, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R11 = Robot(11, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+2.2 + 3.3, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R12 = Robot(12, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+2.4 + 3.3, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R13 = Robot(13, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+2.6 + 3.3, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R14 = Robot(14, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+2.8 + 3.3, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

R15 = Robot(15, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+3 + 3.3, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, idle, resting, BASE_BATTERY_LEVEL)

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
for x in range(int(globals.W * 100)):
    inner = []
    for y in range(int(globals.H * 100)):
        inner.append(0)
    globals.PHEROMONES_MAP.append(inner)


# Contains robot's pheromone (if used)
# PHEROMONES_PATH = []


# Markers
globals.MARKER_HOME = Position(-W/2 + 1.6, -H/2 + 1.6)
globals.MARKER_BROOD_CHAMBER = Position(-W/2 + 4, -H/2 + 1.6)

# Areas
AREAS = []
TYPE_NEUTRAL = 0
TYPE_HOME = 1
TYPE_CHARGING_AREA = 2
TYPE_BROOD_CHAMBER = 3
home = Area(Position(-W/2, -H/2), 3.2, 3.2, TYPE_HOME, (133, 147, 255))
brood_chamber = Area(Position(-W/2 + 3.2, -H/2), 1.6,
                     3.2, TYPE_BROOD_CHAMBER, (224, 153, 255))
charging_area = Area(Position(-W/2, -H/2+3.4),
                     1.4, 3.2, TYPE_CHARGING_AREA, (168, 255, 153))
AREAS.append(home)
AREAS.append(brood_chamber)
AREAS.append(charging_area)
###############################################################################


#! to move in the robot
def get_proximity_sensors_values(robot_rays, robot):
    values = []

    # Wall detection
    for index, ray in enumerate(robot_rays):
        values.append(distance(WORLD.intersection(ray),
                               robot.proximity_sensors[index].x, robot.proximity_sensors[index].y))

    # Robot detection
    for r in globals.ROBOTS:
        #! What I add here only serves the purpose to make the program faster
        #! should not be reproduce into a real life setup
        #! but does not affect how accurate to real life the setup currently is

        # Don't check ourselves
        if r.number != robot.number:
            if robot.in_range(r.position):
                for index, ray in enumerate(robot_rays):
                    if r.is_sensing(ray):
                        p1, p2 = nearest_points(r.get_collision_box(), Point(
                            robot.proximity_sensors[index].x, robot.proximity_sensors[index].y))
                        values[index] = distance(p1, p2.x, p2.y)

    return values


while True:
    globals.CNT += 1
    VISUALIZER.draw_arena()
    VISUALIZER.draw_areas(AREAS)
    # VISUALIZER.draw_decay(PHEROMONES_PATH)
    for robot in globals.ROBOTS:

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

        #! I have witnessed something unusual ... the robots were all in the chargin area and they could not get out of it .. like if I had implemented them to stay in but no :|
        # TODO this is due to calling goto charching area everytime when wandering, which is quite nice to keep them in an area
        # ? but I don't get why they would've been blocked in the CHARGING zone .. try to analyze the code pleaase -> no.

        #!OBSERVATION TASK: when one task when all robot go to resting even though like brood care is -9, then when I hit R, the robot who was resting but brood caring goes back to work .. why? he shouldn't have stopped in the first place

        # if the robot does not have to work .. let it rest in its charging area.
        if not robot.battery_low:
            if not robot.has_to_work():
                if not robot.has_destination:
                    if robot.carry_resource:
                        robot.drop_resource()
                    robot.go_home()
            # the robot has to be active
            else:
                if robot.task == idle:
                    robot.go_home()
                elif robot.task == foraging:
                    # if I arrived home and I do carry a resource, unload it.
                    if robot.is_on_area(TYPE_HOME) and robot.carry_resource:

                        robot.compute_resource()

                    # else if I find a resource on the ground, and I am not already carrying a resource
                    elif (robot_bottom_sensor_states == (2, 0) or robot_bottom_sensor_states == (0, 2)) and robot.carry_resource == False and pointOfInterest.state == RESOURCE_STATE_FORAGING:
                        robot.pickup_resource(pointOfInterest)

                        # Arbitrary, makes sure the resource is in home (Hopefully)
                        robot.time_before_drop_out = randint(50, 100)

                elif robot.task == nest_maintenance:

                    if robot.carry_resource:
                        if globals.CNT - robot.payload_carry_time == 200:
                            robot.transform_resource()

                    # robot is off
                    if robot.reaching_for_resource and not robot.has_destination:
                        robot.has_destination = True
                        robot.destination = robot.backup_resource_pos

                    if not robot.carry_resource and not robot.reaching_for_resource and len(globals.STOCK) > 0:
                        robot.has_destination = True
                        robot.reaching_for_resource = True
                        #! is a new internal state known by all ants

                        robot.reaching_for_resource_label, robot.destination = globals.STOCK.pop(
                            0)
                        robot.backup_resource_pos = robot.destination

                        #! is a new internal state known by all ants
                        #! that for the task allocation assessement it is okay... ? like no matter how I do the task as long as I can assess them ..
                        #! robot.payload_carry_time = globals.CNT -> wrong place, start the carry time when robot picks up the resource.

                    elif robot.reaching_for_resource:
                        if (robot_bottom_sensor_states == (2, 0) or robot_bottom_sensor_states == (0, 2)) and robot.carry_resource == False and pointOfInterest.state == RESOURCE_STATE_NEST_PROCESSING and pointOfInterest.index == robot.reaching_for_resource_label:
                            robot.pickup_resource(pointOfInterest)
                            robot.payload_carry_time = globals.CNT
                            robot.reaching_for_resource = False
                            robot.reaching_for_resource_label = None
                            robot.backup_resource_pos = None

                    elif not robot.is_on_area(TYPE_HOME):
                        robot.destination = globals.MARKER_HOME
                        robot.has_destination = True
                    elif robot.is_on_area(TYPE_HOME):
                        # TODO, basic area detection + motor impact
                        robot.destination = None
                        robot.has_destination = False
                        robot.stay_home()

                elif robot.task == brood_care:
                    if robot.is_on_area(TYPE_BROOD_CHAMBER):
                        robot.destination = None
                        robot.has_destination = False
                        # if globals.CNT % 50 == 0:
                        #     globals.NEST.brood_care += randint(0, 3)
                    else:
                        robot.destination = globals.MARKER_BROOD_CHAMBER
                        robot.has_destination = True

        # if the robot intends to go back to its station to charge. The robot can charge even though it is not battery_low
        if robot.is_on_area(TYPE_CHARGING_AREA):
            if robot.destination == robot.start_position or robot.battery_low:
                # charge its battery level up to 100
                if globals.CNT % 5 == 0 and robot.battery_level < 100:
                    robot.battery_level += 2

                if robot.battery_level >= 100:
                    # As the robot can be interrupted in its task while charging .. we need to make sure he gets back to it
                    robot.battery_low = False
                    if robot.carry_resource:
                        robot.destination = globals.MARKER_HOME
                    else:
                        robot.destination = None
                        robot.has_destination = False

        robot.step(robot_prox_sensors_values)
        # ###################################

        # check collision with arena walls
        collided = robot.is_colliding(WORLD)

        DRAW_bottom_sensor_position = [(robot.bottom_sensors[0].x, robot.bottom_sensors[0].y), (
            robot.bottom_sensors[1].x, robot.bottom_sensors[1].y)]

        VISUALIZER.draw(robot.position, robot.color, globals.CNT,
                        robot.path, robot.get_collision_box_coordinate(), robot.prox_sensors_state, DRAW_proximity_sensor_position, DRAW_bottom_sensor_position, robot_bottom_sensor_states, robot.number)

        # Decrease robot's battery .. Nothing much accurate to real world, but it is part of robotic problems
        if globals.CNT % 100 == 0 and not robot.is_on_area(TYPE_CHARGING_AREA):
            robot.battery_level -= randint(0, 4)
            if robot.battery_level < 25:
                # Robot's start position is its charging block
                #! below is making a good point
                # TODO if that happens, I should probably change the task of the robot so an other one can take over -> yes, but let's think about that later shall we.
                robot.battery_low = True
                robot.destination = robot.start_position
                robot.has_destination = True

        # Robot wise
        # if globals.DO_RECORD:
        # if globals.CNT % globals.M == 0:
        #     robot.path.append(robot.position.__dict__)

        if collided:
            #! sometimes a lot of robot that are not even in the same area collide in the same time
            #! I need to figure out why.
            print("Robot {} collided, position reseted".format(robot.number))
            robot.reset()

    # sleep(0.2)
    VISUALIZER.pygame_event_manager(pygame.event.get())
    VISUALIZER.draw_poi(globals.POIs)

    # ? I don't think that the decay is fully necessary. if it is not, then delete and re assess the need of making POIs invisible instead of deleting
    # decay_check()
    # World wise
    if globals.DO_RECORD:
        if globals.CNT % globals.M == 0:
            globals.DRAW_POIS.append([o.encode()
                                      for o in deepcopy(globals.POIs)])
    # Task helper
    # if globals.CNT % 10 == 0:
    #     print(chr(27) + "[2J")
    #     print(" ******* LIVE STATS *******")
    #     print("N° | % | State | Task")
    #     for robot in globals.ROBOTS:
    #         print("["+str(robot.number)+"]: "+str(robot.battery_level) +
    #               " | "+STATES_NAME[robot.state] + " | "+TASKS_NAME[robot.task])
    #     TaskHandler.print_stats()
    #     print("Q")
    #     print(TASKS_Q)

    #     # print to csv file
    #     # TODO could be nice to also print each robot task and state to see oscillation ?
    #     #! problem here .. the assigned right is always 0 but should fluctuate..
    #     txt = str(globals.CNT)+";"
    #     for i in range(len(TASKS)):
    #         txt += assigned(i) + ";"
    #         if i == foraging:
    #             txt += str(globals.NEST.resource_need)+";"
    #         elif i == idle:
    #             txt += "0;"
    #         elif i == nest_maintenance:
    #             txt += str(globals.NEST.resource_stock)+";"
    #         elif i == brood_care:
    #             txt += str(globals.NEST.resource_transformed)
    #     globals.CSV_FILE.write(txt+"\n")

    pygame .display.flip()  # render drawing
    fpsClock.tick(fps)
