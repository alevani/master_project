# TODO move some of the globals here, as long as they are const.
from utils import Position
import math
# Speed of robot in simulation, keep FPS at 60 and only change the below variable to variate the speed
ROBOT_TIMESTEP = 1
SIMULATION_TIMESTEP = .01

R = 0.02  # radius of wheels in meters
L = 0.095  # distance between wheels in meters


BOTTOM_LIGHT_SENSORS_POSITION = [
    Position(-0.012, 0.05), Position(0.012, 0.05)]  # ! false measurments

# Assuming the robot is looking north
PROXIMITY_SENSORS_POSITION = [
    Position(-0.05,   0.06, math.radians(130)),
    Position(0, 0.0778, math.radians(90)),
    Position(0.05,   0.06, math.radians(50))
]
