from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, zeros
from shapely.geometry.point import Point
from shapely.ops import nearest_points
from shapely.affinity import rotate
from utils_simu import Visualizator
from roboty import PointOfInterest
from world import decay_check
from task import TaskHandler
from pygame.locals import *
from utils import Position
from utils import distance
from task import feedback
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
# ? Thesis concern: If I were to work with real ants, I wouldn't need to dodge other robot as ant can go over each others.. but in real life not the same.
# ? Thesis: Maybe it's going to be important to retrace the step of the simulation development?
# ? i don't think so. But maybe about the speed and the improvement?
#! I know I want to use robot simulated because I want to asses the efficenicy of the allocation system for robots
#! I don't think I must simulate because what I need is to assess the efficiency

#! there are a lot of problem when converting to point, like lots of things shouldn't require that much convert..

#! How do we induce operating cost of a task with the task allocation model? to be disscussed..

#! implement noise in the sensors? maybe not.. as I want to asses the value of the task allocation

#! as assessed in the paper, an ant is capable to know that a task is in energy deficit or surplus, but not able to quantify it. so following the model, it is not because there's more deficit to a task that more ant should be allocated to it.
#! but I could trick that to have more ant working on the task that have the more deficit .. I need to assess if this is necessary or not.

# !!!!!! not experiment before all the measurments and the brain completed.

#! maybe re-implement the whole interest level thingy....
#! https://github.com/alevani/master_project/commit/d7812d9175dfd5a8090e68be942d5bbc83cb0e68


# ? Does the model really takes into consideration wheter a task is over assigned or not ..?
# ? as of now, it seems that no ant takes advantages of switching if the task is in energy surplus
#! Maybe it's working .. I just need an actual food increase to put it to 0?
#! as said before, no, cause ants cannot quantify how much a task needs man power or not
########

### GLOBALS ###################################################################

# WORLD
# TODO Redo measurements of the robot's sensors' position

# Speed of robot in simulation, keep FPS at 60 and only change the below variable to variate the speed
ROBOT_TIMESTEP = 1
SIMULATION_TIMESTEP = .01

R = 0.02  # radius of wheels in meters
L = 0.095  # distance between wheels in meters

W = globals.W
H = globals.H

WORLD = LinearRing([(W/2, H/2), (-W/2, H/2), (-W/2, -H/2), (W/2, -H/2)])

BOTTOM_LIGHT_SENSORS_POSITION = [
    Position(-0.012, 0.05), Position(0.012, 0.05)]  # ! false measurments

# Assuming the robot is looking north
# TODO deactivate left and right ray
PROXIMITY_SENSORS_POSITION = [Position(-0.05,   0.06, math.radians(130)),
                              Position(-0.025,  0.075, math.radians(108.5)),
                              Position(0, 0.0778, math.radians(90)),
                              Position(0.025,  0.075, math.radians(71.5)),
                              Position(0.05,   0.06, math.radians(50))]

# PYGAME
globals.DO_RECORD = True
if globals.DO_RECORD:
    FILE = open("points.json", "w")
else:
    FILE = None

DECAY = 750
VISUALIZER = Visualizator(W, H, DECAY, FILE)
pygame.init()
fps = 60
fpsClock = pygame.time.Clock()
###############################################################################

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
TASKS_Q.append(0)  # Nest maintenance
# TASKS_Q.append([0, BroodCare])
# TASKS_Q.append([0, Patrolling])
TASKS.append(Idle)
TASKS.append(Foraging)
TASKS.append(NestMaintenance)
# TASKS.append(BroodCare)
# TASKS.append(Patrolling)
#############################################################################

### Start's variables #########################################################
TYPE_HOME = 1
TYPE_CHARGING_AREA = 2
# globals.NEST = Nest(-30, 0)
globals.NEST = Nest(-300, 0)
TaskHandler = TaskHandler(globals.NEST)

BASE_BATTERY_LEVEL = 100

BLACK = (0, 0, 0)

# R1 = Robot(1, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-0, 0, math.radians(270)),
#            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

# R2 = Robot(2, deepcopy(PROXIMITY_SENSORS_POSITION), Position(0, -0.5, math.radians(270)),
#            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R1 = Robot(1, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+0.2+3.1, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R2 = Robot(2, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+0.4 + 3.1, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R3 = Robot(3, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+0.6 + 3.1, math.radians(
    0)), BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R4 = Robot(4, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+0.8 + 3.1, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R5 = Robot(5, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+1 + 3.1, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R6 = Robot(6, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+1.2 + 3.1, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R7 = Robot(7, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+1.4 + 3.1, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R8 = Robot(8, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+1.6 + 3.1, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R9 = Robot(9, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+1.8 + 3.1, math.radians(0)),
           BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R10 = Robot(10, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+2 + 3.1, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R11 = Robot(11, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+2.2 + 3.1, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R12 = Robot(12, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+2.4 + 3.1, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R13 = Robot(13, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+2.6 + 3.1, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R14 = Robot(14, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.4, -H/2+2.8 + 3.1, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

R15 = Robot(15, deepcopy(PROXIMITY_SENSORS_POSITION), Position(-W/2+0.2, -H/2+3 + 3.1, math.radians(0)),
            BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, Idle, Resting, BASE_BATTERY_LEVEL)

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


PHEROMONES_PATH = []
AREAS = []


# Markers
Marker_ResourceDelivery = Position(-W/2 + 1.6, -H/2 + 1.6)

home = Area(Position(-W/2, -H/2), 3.2, 3.2, TYPE_HOME, (133, 147, 255))
egg_chamber = Area(Position(-W/2 + 3.2, -H/2), 1.6,
                   3.2, 10, (224, 153, 255))

charging_area = Area(Position(-W/2, -H/2+3.2),
                     0.7, 3.2, TYPE_CHARGING_AREA, (168, 255, 153))
AREAS.append(home)
AREAS.append(egg_chamber)
AREAS.append(charging_area)
###############################################################################

# This is not in the robot's object because it seemed to be slower if so


def get_proximity_sensor_values(rays, robot):
    dists = []

    # Wall detection
    for index, ray in enumerate(rays):
        dists.append(distance(WORLD.intersection(ray),
                              robot.proximity_sensors[index].x, robot.proximity_sensors[index].y))

    # Robot detection
    #! if I don't use the left and right ..
    #! why do I bother calculating it ..
    for r in globals.ROBOTS:
        #! maybe r is trying to reach a point, take 1/2 chance that I stop or go backward for a few st
        #! maybe this is the best decision .. with a flag .. let's try
        # Don't check ourselves
        if r.number != robot.number:
            for index, ray in enumerate(rays):
                if r.is_sensing(ray):
                    p1, p2 = nearest_points(r.get_collision_box(), Point(
                        robot.proximity_sensors[index].x, robot.proximity_sensors[index].y))
                    dists[index] = distance(p1, p2.x, p2.y)

    return dists


while True:
    globals.CNT += 1
    VISUALIZER.draw_arena()
    VISUALIZER.draw_areas(AREAS)
    # VISUALIZER.draw_decay(PHEROMONES_PATH)
    globals.POIs.append(PointOfInterest(Position(0, -3), 100000, 1))
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

        # Robot's brain
        # Task allocation #
        if robot.state == Resting:
            candidate = []
            for i, task in enumerate(TASKS):
                if feedback(task) < 0:  # Task is in energy surplus
                    # print("Task ["+task+"] is in energy surplus")
                    TASKS_Q[i] = 0
                else:  # Task is in energy deficit
                    # print("Task ["+task+"] is in energy deficit")
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

        robot.stop()
        area_type = robot.area_type(AREAS)

        # TODO Problem, if to close to a wall, tries to turn left because shortest angle, but then bumps into the wall and go right .. then go left .. and so on
        #! I think the problem as been fixed when changing the rotation direction to the correct one
        #! robot can still block each others

        if robot.state == Resting or robot.state == SecondReserve or robot.state == FirstReserve:
            #       if robot carries resoure
            #       -> Leave the resource on the ground
            if robot.carry_resource:
                robot.carry_resource = False

                x = int(robot.position.x * 100) + int(globals.W * 100/2)
                y = int(robot.position.y * 100) + int(globals.H * 100/2)
                globals.PHEROMONES_MAP[x][y] = robot.payload
                robot.payload = None

            robot.last_foraging_point = None
            robot.destination = robot.start_position
            robot.goto_objective_reached = False

        if robot.carry_resource:
            globals.POIs[robot.payload.index].position.x = robot.position.x
            globals.POIs[robot.payload.index].position.y = robot.position.y

        if robot.is_avoiding:
            robot.avoid()
        #! Here I say .. if the robot is trying to reach a goal .. then you disregard non-dynamic obstacle avoidance
        #! because I assume that no walls exist in the arena (but the arena itself) .. only dynamic object
        elif robot.goto_objective_reached:
            if proximity_sensors_state == (0, 1, 0):
                if randint(0, 1):
                    robot.turn_left()
                else:
                    robot.turn_right()
            elif proximity_sensors_state == (1, 0, 0) or proximity_sensors_state == (1, 1, 0):
                robot.turn_left()
            elif proximity_sensors_state == (0, 0, 1) or proximity_sensors_state == (0, 1, 1):
                robot.turn_right()
            elif proximity_sensors_state == (1, 0, 1) or proximity_sensors_state == (1, 1, 1):
                robot.is_avoiding = True
                robot.NB_STEP_TO_AVOID = 7
            # Mathematic model seems to say that also TempWorker can work ..
            #! assuming only foragers will be interested into picking up food.
            elif (bottom_sensor_states == (2, 0) or bottom_sensor_states == (0, 2) or bottom_sensor_states == (1, 2) or bottom_sensor_states == (2, 1)) and robot.carry_resource == False and robot.task == Foraging and (robot.state == CoreWorker or robot.state == TempWorker):
                robot.goto_objective_reached = False
                robot.destination = Marker_ResourceDelivery
                robot.last_foraging_point = robot.position
                robot.carry_resource = True
                robot.payload = POI
                globals.PHEROMONES_MAP[POI.position.x][POI.position.y] = 0
            else:
                robot.wander()
        # Specifying robot.destination == robot.start_position means that the robot intends to be charged
        elif area_type == TYPE_CHARGING_AREA and robot.destination == robot.start_position:
            # For now, let's say everytime a robot enters the area he as to charge up to 90 to leave
            if globals.CNT % 5 == 0 and robot.battery_level < 100:
                robot.battery_level += 2

            if robot.battery_level >= 100:
                # As the robot can be interrupted in its task while charging .. we need to make sure he gets back to it
                if robot.carry_resource:
                    robot.destination = Marker_ResourceDelivery
                else:
                    robot.destination = None
                    robot.goto_objective_reached = True
        else:
            if area_type == TYPE_HOME and robot.carry_resource:
                globals.NEST.resources += robot.payload.value
                globals.POIs[robot.payload.index].is_visible = False
                robot.carry_resource = False
                robot.payload = None
                robot.destination = robot.last_foraging_point

            robot.goto(robot.destination, proximity_sensor_values)

        # robot.destination = Position(0, -3)
        # robot.goto(robot.destination, proximity_sensor_values)
        # if robot.number == 1:
        robot.simulationstep()
        # ###################################

        # check collision with arena walls
        collided = robot.is_colliding(WORLD)
        collision_box = robot.get_collision_box_coordinate()

        DRAW_bottom_sensor_position = [(robot.bottom_sensors[0].x, robot.bottom_sensors[0].y), (
            robot.bottom_sensors[1].x, robot.bottom_sensors[1].y)]

        VISUALIZER.draw(robot.position, robot.color, globals.CNT,
                        robot.path, collision_box, (proximity_sensors_state[0], 0, proximity_sensors_state[1], 0, proximity_sensors_state[2]), DRAW_proximity_sensor_position, DRAW_bottom_sensor_position, bottom_sensor_states, robot.number)

        # if robot.trail:
        PHEROMONES_PATH.append(
            PointOfInterest(robot.position, DECAY, None))

        # Decrease robot's battery .. Nothing much accurate to real world, but it is part of robotic problems
        if globals.CNT % 100 == 0 and not area_type == TYPE_CHARGING_AREA:
            robot.battery_level -= randint(0, 4)
            if robot.battery_level < 50:
                # Robot's start position is its charging block
                # TODO if that happens, I should probably change the task of the robot so an other one can take over
                robot.destination = robot.start_position
                robot.goto_objective_reached = False

        # Robot wise
        if globals.DO_RECORD:
            if globals.CNT % globals.M == 0:
                robot.path.append(robot.position.__dict__)

        if collided:
            #! sometimes a lot of robot that are not even in the same area collide in the same time
            #! I need to figure out why.
            print("collided")
            robot.has_collided = True
    # sleep(0.2)
    VISUALIZER.pygame_event_manager(pygame.event.get())
    VISUALIZER.draw_poi(globals.POIs)

    decay_check()
    # World wise
    if globals.DO_RECORD:
        if globals.CNT % globals.M == 0:
            globals.DRAW_POIS.append([o.encode()
                                      for o in deepcopy(globals.POIs)])
    # Task helper
    TaskHandler.simulationstep()
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

    pygame .display.flip()  # render drawing
    fpsClock.tick(fps)
