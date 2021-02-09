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
from roboty import PointOfInterest
from roboty import Area
from roboty import Nest
from task import feedback
from task import TaskHandler

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
#! It does not seem impossible to have a record button that would save the point. This record button would record idk like
#! 5000 begin and from there on, giving the user a chance to record something he just missed, also without to have to watch
#! it from the begining again

#! It is likely that adding pheromones at every step is wrong. like ant will activate their pheromones only under specific circumstances

#! Do ants have a specific go home or go to food pheromone? if so I can easily add this behaviour by adding a pheromone type in the pheromone object and filtering when matching

# TODO Right now it's funny that I can right and left click but
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

#! one need to fix: the way robot behave on pheromone, they should be able to take 90 degree angle
#! and also CIRCLE OF DEATH

#! Simulation time between live and point is not the same... important? I don't think so.

#! How do we induce operating cost of a task with the task allocation model? to be disscussed..

#! implement noise in the sensors? maybe not.. as I want to asses the value of the task allocation
#! try to have some noise in tasks such as in food hunger, so not every robot are hungry at the same time.

# ? since ant acts for their own survival .. what's the point? how could they understand any other task?

#! since above .. maybe we could imagine that it is the nest who assess the need of each task ..? and not the ant.
#! above is pas con DU TOUT

#! as assessed in the paper, an ant is capable to know that a task is in energy deficit or surplus, but not able to quantify it. so following the model, it is not because there's more deficit to a task that more ant should be allocated to it.
#! but I could trick that to have more ant working on the task that have the more deficit .. I need to assess if this is necessary or not.

#! next step is to create a new task in the same spirit of the foraging ..
#! so everything is the same, just a diff name

# ? maybe ..... would be nice to see the resources in the nest disapearing as the resources are being consumed? tiny bit useless :D


# !!!!!! not experiment before all the measurments and the brain completed.
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

globals.NEST = Nest(0, 0)
TaskHandler = TaskHandler(globals.NEST)

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
    #! I can't just remove stuff from the list as is.. is I do the whole new index thing will be fucky
    #! one need to remove the point of interest from the board as well (at least the visu, the board is ok)
    for i, point in enumerate(PHEROMONES_PATH):
        if point == 0:
            break

        point.decay_time -= 1
        if point.decay_time <= 0:
            globals.PHEROMONES_MAP[int(point.position.x * 100) + int(
                globals.W * 100/2)][int(point.position.y * 100) + int(globals.H * 100/2)] = 0

            PHEROMONES_PATH.pop(i)

    for i, poi in enumerate(globals.POIs):
        poi.decay_time -= 1
        if poi.decay_time <= 0:
            globals.PHEROMONES_MAP[int(poi.position.x * 100) + int(
                globals.W * 100/2)][int(poi.position.y * 100) + int(globals.H * 100/2)] = 0
            poi.is_visible = False


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


### Task allocation #########################################################
Resting = 0
FirstReserve = 1
SecondReserve = 2
TempWorker = 3
CoreWorker = 4

STATES_NAME = ['Resting', 'First reserve',
               'Second reserve', 'Temporary worker', 'Core worker']

# Energy of a task
TASKS_Q = []

# Array to keep track of the tasks
TASKS = []

# A task is a tuple of its energy and a task object
Idle = 0
Foraging = 1
NestMaintenance = 2
BroodCare = 3
Patrolling = 4

TASKS_NAME = ['Idle', 'Foraging',
              'Nest maintenance', 'Brood care', 'Patrolling']
COLORS = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (0, 0, 255), (125, 125, 125)]

TASKS_Q.append(0)  # Idle
TASKS_Q.append(0)  # Foraging
# TASKS_Q.append(0)  # Nest maintenance
# TASKS_Q.append([0, BroodCare])
# TASKS_Q.append([0, Patrolling])
TASKS.append(Idle)
TASKS.append(Foraging)
# TASKS.append(NestMaintenance)
# TASKS.append(BroodCare)
# TASKS.append(Patrolling)
#############################################################################
### Start's variables #########################################################
# Arbitrary food treshold
BASE_BATTERY_LEVEL = 100

BLACK = (0, 0, 0)

#! some robot start on top of each others..
R1 = Robot(1, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+0.2, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R2 = Robot(2, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+0.4, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R3 = Robot(3, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+0.6, math.radians(
    0)), BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R4 = Robot(4, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+0.8, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R5 = Robot(5, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+1, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R6 = Robot(6, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+1.2, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R7 = Robot(7, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+1.4, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R8 = Robot(8, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+1.6, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R9 = Robot(9, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+1.8, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R10 = Robot(10, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+2, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R11 = Robot(11, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+2.2, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R12 = Robot(12, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+2.4, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R13 = Robot(13, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+2.6, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R14 = Robot(14, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+2.8, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R15 = Robot(15, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+3, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

globals.ROBOTS.append(R1)
# globals.ROBOTS.append(R2)
# globals.ROBOTS.append(R3)
# globals.ROBOTS.append(R4)
# globals.ROBOTS.append(R5)
# globals.ROBOTS.append(R6)
# globals.ROBOTS.append(R7)
# globals.ROBOTS.append(R8)
# globals.ROBOTS.append(R9)
# globals.ROBOTS.append(R10)
# globals.ROBOTS.append(R11)
# globals.ROBOTS.append(R12)
# globals.ROBOTS.append(R13)
# globals.ROBOTS.append(R14)
# globals.ROBOTS.append(R15)

# Slow at creation, and heavy, but considerabely increase visualisation speed.
#! nothing in (0,0) why?
for x in range(int(globals.W * 100)):
    inner = []
    for y in range(int(globals.H * 100)):
        inner.append(0)
    globals.PHEROMONES_MAP.append(inner)


PHEROMONES_PATH = []
AREAS = []


home = Area(Position(-W/2, -H/2), 1, 3.2, TYPE_HOME, (133, 147, 255))
AREAS.append(home)
###############################################################################

while True:
    globals.cnt += 1
    VISUALIZER.draw_arena()
    VISUALIZER.draw_areas(AREAS)
    VISUALIZER.draw_decay(PHEROMONES_PATH)
    for robot in globals.ROBOTS:

        if robot.has_collided:
            break

        rays, DRAW_proximity_sensor_position = robot.create_rays(W, H)

        proximity_sensor_values = get_proximity_sensor_values(
            rays, robot)

        bottom_sensor_states, POI = robot.get_bottom_sensor_states(
            globals.PHEROMONES_MAP)

        proximity_sensors_state = robot.get_proximity_sensor_state(
            proximity_sensor_values)

        # Robot's brain ############

        # Task allocation #
        #! I know I want to use robot simulated because I want to asses the efficenicy of the allocation system for robots
        #! I don't think I must simulate because what I need is to assess the efficiency
        if robot.state == Resting:
            candidate = []
            for i, task in enumerate(TASKS):
                if feedback(task) < 0:  # Task is in energy surplus
                    # print("Task ["+task+"] is in energy surplus")
                    #! that actually works, I am just a dumbass ..
                    #! if idle increasing, then somehow only foraging will enter this if
                    #! and it's value is yes.. reset to 0
                    TASKS_Q[i] = 0
                else:  # Task is in energy deficit
                    # print("Task ["+task+"] is in energy deficit")
                    # ? Does the model really takes into consideration wheter a task is over assigned or not ..?
                    # ? as of now, it seems that no ant takes advantages of switching if the task is in energy surplus
                    #! Maybe it's working .. I just need an actual food increase to put it to 0?
                    TASKS_Q[i] = min(TASKS_Q[i] + 1, 3)
                # print(TASKS_Q)
                # ? if TASKS_Q[i] >= 3:
                if TASKS_Q[i] == 3:
                    candidate.append(task)
                # print("Candidate tasks are:")
                # print(candidate)

            if candidate != []:
                if randint(0, 1):
                    # print("Robot enters candiate task selection")
                    for task in TASKS_Q:
                        task = 0
                    robot.task = candidate[randint(0, len(candidate)-1)]
                    # print("New robot's task is: " + robot.task)
                    robot.state = TempWorker
                    # print("New robot's state is: " + str(robot.state))
        # ? somehow, it waits for all the robot to be in foraging task to start to move????
        elif robot.state == FirstReserve:
            if feedback(robot.task) < 0:
                # print("First reserve .. resting")
                robot.state = Resting
            elif randint(0, 1):
                robot.state = TempWorker
            else:
                robot.state = SecondReserve
        elif robot.state == SecondReserve:
            if feedback(robot.task) < 0:
                # print("Second reserve .. resting")
                robot.state = Resting
            else:
                robot.state = TempWorker
        elif robot.state == TempWorker:
            if feedback(robot.task) < 0:
                robot.state = FirstReserve
            else:
                robot.state = CoreWorker
        elif robot.state == CoreWorker:
            if feedback(robot.task) < 0:
                robot.state = TempWorker

        robot.color = COLORS[robot.task]
        ###################

        robot.RIGHT_WHEEL_VELOCITY = 0
        robot.LEFT_WHEEL_VELOCITY = 0

        if robot.state == Resting:
            #! maybe an "if not home, ho home()"
            pass
        elif robot.state == CoreWorker and (robot.task == Foraging or robot.task == NestMaintenance):
            # Update the visu of the point of interest so it follows the robot moving around :D
            if robot.carry_resource:
                globals.POIs[robot.carried_resource.index].position.x = robot.position.x
                globals.POIs[robot.carried_resource.index].position.y = robot.position.y
                globals.POIs[robot.carried_resource.index].decay_time = 2

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

                area_type = robot.area_type(AREAS)
                if area_type == TYPE_HOME and robot.carry_resource:
                    robot.is_avoiding = True
                    robot.NB_STEP_TO_AVOID = 15
                    globals.NEST.resources += robot.carried_resource.value
                    globals.POIs[robot.carried_resource.index].is_visible = False
                    robot.carry_resource = False
                    robot.carried_resource = None

                # Here, depending on the pheromone trail type, we could easily avoid path to go home and such ..
                if (bottom_sensor_states == (2, 0) or bottom_sensor_states == (0, 2) or bottom_sensor_states == (1, 2) or bottom_sensor_states == (2, 1)) and robot.carry_resource == False:
                    robot.is_avoiding = True
                    robot.NB_STEP_TO_AVOID = 15
                    robot.trail = True
                    robot.carry_resource = True
                    robot.carried_resource = POI
                    globals.PHEROMONES_MAP[POI.position.x][POI.position.y] = 0
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
                        robot.path, collision_box, (proximity_sensors_state[0], 0, proximity_sensors_state[1], 0, proximity_sensors_state[2]), DRAW_proximity_sensor_position, DRAW_bottom_sensor_position, bottom_sensor_states, robot.number)

        if robot.trail:
            #! should I make sure here that I don't have already a point of interest? ^cause I don't want the ant to miss the food.
            #! maybe there is an interest in having a multi dimensional array for each pixel with multiple points? i dont think so....
            globals.PHEROMONES_MAP[int(robot.position.x * 100) + int(globals.W * 100/2)][int(
                robot.position.y * 100) + int(globals.H * 100/2)] = PointOfInterest(robot.position, DECAY, 1)
            PHEROMONES_PATH.append(
                PointOfInterest(robot.position, DECAY, None))

        # # Decrease robot's battery .. maybe not useful.
        # if globals.cnt % 50 == 0:
        #     robot.battery_level -= 1

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
    VISUALIZER.draw_poi(globals.POIs)
    # World wise
    if globals.DO_RECORD:
        if globals.cnt % globals.M == 0:
            globals.DRAW_POIS.append([o.encode()
                                      for o in deepcopy(globals.POIs)])
    # if globals.cnt % 10 == 0:
    #     print(chr(27) + "[2J")
    #     print(" ******* LIVE STATS *******")
    #     print("N° | % | State | Task")
    #     for robot in globals.ROBOTS:
    #         print("["+str(robot.number)+"]: "+str(robot.battery_level) +
    #               " | "+STATES_NAME[robot.state] + " | "+TASKS_NAME[robot.task])
    #     TaskHandler.print_stats()
    #     print("Q")
    #     print(TASKS_Q)

    pygame .display.flip()  # render drawing
    fpsClock.tick(fps)
