from Position import Position
from random import randint
from copy import deepcopy
import math

WHITE = (255, 255, 255)
LIGHT_BLACK = (130, 130, 130)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GREEN = (0, 125, 0)

# Speed of robot in simulation, keep FPS at 60 and only change the below variable to variate the speed
ROBOT_TIMESTEP = 1
SIMULATION_TIMESTEP = .01

R = 0.02  # radius of wheels in meters
L = 0.095  # distance between wheels in meters


# Assuming the robot is looking north
BOTTOM_LIGHT_SENSORS_POSITION = [
    Position(-0.01, 0.07), Position(0.01, 0.07)]

# Assuming the robot is looking north
PROXIMITY_SENSORS_POSITION = [
    Position(-0.05,   0.06, math.radians(130)),
    Position(0, 0.0778, math.radians(90)),
    Position(0.05,   0.06, math.radians(50))
]


# State in which a point of interest can end up in
RESOURCE_STATE_FORAGING = 0
RESOURCE_STATE_NEST_PROCESSING = 1
RESOURCE_STATE_TRANSFORMED = 2
RESOURCE_STATE_WAISTE = 3

# Height and Width of the arena
H = 7
W = 10


resting = 0
first_reserve = 1
second_reserve = 2
temp_worker = 3
core_worker = 4
