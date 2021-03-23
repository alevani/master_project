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

TYPE_HOME = 1

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
RESOURCE_STATE_WASTE = 3

# Height and Width of the arena
H = 7
W = 10

# Boundaries for random generation
X_lower_bound = -W/2+0.10
X_upper_bound = W/2-0.10
Y_lower_bound = -H/2+0.10
Y_upper_bound = H/2-0.10


def dist(p, q):
    return math.sqrt(sum((px - qx) ** 2.0 for px, qx in zip(p, q)))


scaleup_width = int(W/2 * 100)
scaleup_height = int(H/2 * 100)


def scaleup(x, y):
    return int(x * 100) + scaleup_width, int(y * 100) + scaleup_height


resting = 0
first_reserve = 1
second_reserve = 2
temp_worker = 3
core_worker = 4

### Task allocation #########################################################
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


# Markers
MARKER_CLEANING_AREA = Position(0, -H/2 + 0.7 + .5)
MARKER_HOME = Position(0 - 1.4, -H/2 + 0.7 + .5)
MARKER_WASTE_AREA = Position(W/2-0.7, H/2 - 0.7)
