from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, zeros
from shapely.geometry.point import Point
from shapely.affinity import rotate
from utils import distance
from random import randint
from utils import Position
from random import random
from copy import deepcopy
import globals
import shapely
import math

OUT_RANGE = 10000


class Nest:
    def __init__(self, resources, task2, position=None):
        self.resources = resources
        self.task2 = task2


class Area:
    def __init__(self, position, width, height, t, color):

        self.position = position

        x, y = position.x, position.y
        self.left_bottom = (x, y)
        self.right_bottom = (x + width, y)
        self.left_top = (x, y+height)
        self.right_top = (x+width, y+height)

        self.box = Polygon((self.left_bottom, self.right_bottom,
                            self.right_top, self.left_top))

        self.type = t
        self.color = color


class PointOfInterest:
    def __init__(self, position, decay_time, t, value=None, index=None, is_visible=True):
        self.is_visible = is_visible
        self.decay_time = decay_time
        self.position = position
        self.value = value
        self.index = index
        self.type = t

    def encode(self):
        return {
            'position': self.position.__dict__,
            'type': self.type
        }


class CollisionBox:
    def __init__(self, shape, position):
        self.position = position
        self.box = shape


class Robot:
    def __init__(self, number, proximity_sensors, position, color, bottom_sensors, LEFT_WHEEL_VELOCITY, RIGHT_WHEEL_VELOCITY, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, task, state, battery_level):
        self.number = number
        self.last_foraging_point = None
        self.color = color
        self.task = task
        self.destination = None
        self.state = state
        self.battery_level = battery_level
        self.proximity_sensors = proximity_sensors
        self.bottom_sensors = bottom_sensors
        self.LEFT_WHEEL_VELOCITY = LEFT_WHEEL_VELOCITY
        self.RIGHT_WHEEL_VELOCITY = RIGHT_WHEEL_VELOCITY
        self.ROBOT_TIMESTEP = ROBOT_TIMESTEP
        self.carry_resource = False
        self.SIMULATION_TIMESTEP = SIMULATION_TIMESTEP
        self.R = R
        self.L = L
        self.payload = None
        self.goto_objective_reached = True

        self.obstacle_detection_range = 0.05
        self.battery_low = False
        self.trail = True

        self.is_avoiding = False
        self.is_avoiding_cnt = 0
        self.NB_STEP_TO_AVOID = 15

        self.update_bottom_sensor_position(position.x, position.y)
        self.rotate_bottom_sensor(
            position.x, position.y, position.theta - math.radians(90))

        self.update_proximity_sensor_position(position.x, position.y,
                                              position.theta-math.radians(90))
        self.rotate_proximity_sensors(position.x, position.y,
                                      position.theta-math.radians(90))

        self.position = position
        self.start_position = position
        self.draw_information = []
        self.has_collided = False
        self.path = []

        self.update_collision_box(position)

    def is_colliding(self, shape):
        return self.collision_box.box.intersects(shape)

    def is_sensing(self, ray):
        return ray.crosses(self.collision_box.box)

    def update_position(self, position):
        self.position = position
        self.update_collision_box(position)

    def update_collision_box(self, position):
        theta = position.theta
        x = position.x
        y = position.y

        theta = theta - math.radians(90)
        box_x = 0.0525
        box_y_top = 0.0725
        box_y_bottom = 0.0725 - 0.03

        collision_box = Polygon(
            ((x - box_x, y - box_y_bottom), (x - box_x, y + box_y_top),
             (x + box_x, y + box_y_top), (x + box_x, y - box_y_bottom)))

        collision_box = rotate(collision_box, theta, (x, y), use_radians=True)
        self.collision_box = CollisionBox(collision_box, Position(theta, x, y))

    def get_collision_box_coordinate(self):
        x, y = self.collision_box.box.exterior.coords.xy
        return tuple(zip(x, y))

    def get_collision_box(self):
        return self.collision_box.box

    def rotate_proximity_sensors(self, x, y, theta):
        for pos in self.proximity_sensors:
            point = rotate(Point(pos.x, pos.y), theta,
                           (x, y), use_radians=True)
            pos.x = point.x
            pos.y = point.y

    def rotate_bottom_sensor(self, x, y, a):
        for pos in self.bottom_sensors:
            point = rotate(Point(pos.x, pos.y), a,
                           (x, y), use_radians=True)
            pos.x = point.x
            pos.y = point.y

    def update_proximity_sensor_position(self, x, y, theta):
        for pos in self.proximity_sensors:
            pos.x = pos.x + x
            pos.y = pos.y + y
            pos.theta = pos.theta + theta

    def update_bottom_sensor_position(self, x, y):
        for pos in self.bottom_sensors:
            pos.x = pos.x + x
            pos.y = pos.y + y

    def area_type(self, areas):
        box_left = Point(
            self.bottom_sensors[0].x, self.bottom_sensors[0].y).buffer(0.01)
        box_right = Point(
            self.bottom_sensors[1].x, self.bottom_sensors[1].y).buffer(0.01)

        for area in areas:
            if area.box.intersects(box_left) or area.box.intersects(box_right):
                return area.type
        return 0

    def get_proximity_sensor_state(self, sensors_values):
        top = sensors_values[1]
        left_most = sensors_values[0]
        right_most = sensors_values[2]

        top_value = 1 if top < self.obstacle_detection_range else 0
        left_most_value = 1 if left_most < self.obstacle_detection_range else 0
        right_most_value = 1 if right_most < self.obstacle_detection_range else 0
        return (left_most_value, top_value, right_most_value)

    def create_rays(self, W, H):
        rays = []
        spos = []
        for sensor in self.proximity_sensors:
            nx = sensor.x
            ny = sensor.y
            ntheta = sensor.theta
            nx_end = nx+cos(ntheta)*2*W
            ny_end = ny+sin(ntheta)*2*H
            ray = [(nx, ny), (nx_end, ny_end)]
            spos.append((nx, ny, ntheta))
            rays.append(LineString(ray))
        return rays, spos

    def simulationstep(self):
        # step model time/timestep times
        x = self.position.x
        y = self.position.y
        theta = self.position.theta
        for step in range(int(self.ROBOT_TIMESTEP/self.SIMULATION_TIMESTEP)):
            v_x = cos(theta)*(self.R*self.LEFT_WHEEL_VELOCITY /
                              2 + self.R*self.RIGHT_WHEEL_VELOCITY/2)
            v_y = sin(theta)*(self.R*self.LEFT_WHEEL_VELOCITY /
                              2 + self.R*self.RIGHT_WHEEL_VELOCITY/2)
            omega = (self.R*self.RIGHT_WHEEL_VELOCITY -
                     self.R*self.LEFT_WHEEL_VELOCITY)/(2*self.L)

            x += v_x * self.SIMULATION_TIMESTEP
            y += v_y * self.SIMULATION_TIMESTEP
            theta += omega * self.SIMULATION_TIMESTEP
            theta = theta % math.radians(360)

        self.update_proximity_sensor_position(
            x - self.position.x, y - self.position.y, theta-self.position.theta)
        self.rotate_proximity_sensors(x, y, theta-self.position.theta)

        self.update_bottom_sensor_position(
            x - self.position.x, y - self.position.y)
        self.rotate_bottom_sensor(x, y, theta-self.position.theta)

        self.update_position(Position(x, y, theta))

    def avoid(self):
        self.is_avoiding_cnt += 1
        self.turn_left()
        if self.is_avoiding_cnt >= self.NB_STEP_TO_AVOID:
            self.is_avoiding_cnt = 0
            self.is_avoiding = False

    def get_bottom_sensor_states(self, pheromones_map):
        left_x = int(self.bottom_sensors[0].x * 100) + int(globals.W * 100/2)
        left_y = int(self.bottom_sensors[0].y * 100) + int(globals.H * 100/2)

        # TODO go in the direction where the concentration of pheromones is the highest.
        # TODO that could work if I have a "pheromone level" along with the object, then I just take the highest
        # TODO, here get the highest interest level and return it.
        #! the way the code is written just assumes than return such as (?,2) can never occur.
        # TODO there's sometimes an index out of range here I must be one off, try and except to see tf is the issuefor x in range(left_x - 2, left_x + 2):
        #!!!!!!!!! that was working nice with the pheromone .. but isn't it overkill with only the pois?
        for x in range(left_x - 2, left_x + 2):
            for y in range(left_y - 2, left_y + 2):
                if pheromones_map[x][y] != 0:
                    return (pheromones_map[x][y].type, 0), pheromones_map[x][y]

        right_x = int(self.bottom_sensors[1].x *
                      100) + int(globals.W * 100/2)
        right_y = int(self.bottom_sensors[1].y *
                      100) + int(globals.H * 100/2)

        for x in range(right_x - 2, right_x + 2):
            for y in range(right_y - 2, right_y + 2):
                if pheromones_map[x][y] != 0:
                    return (0, pheromones_map[x][y].type), pheromones_map[x][y]

        return(0, 0), 0

    def turn_left(self):
        self.RIGHT_WHEEL_VELOCITY = -1
        self.LEFT_WHEEL_VELOCITY = 1

    def soft_turn_left(self):
        self.RIGHT_WHEEL_VELOCITY = 1
        self.LEFT_WHEEL_VELOCITY = 0

    def soft_turn_right(self):
        self.RIGHT_WHEEL_VELOCITY = 0
        self.LEFT_WHEEL_VELOCITY = 1

    def turn_right(self):
        self.RIGHT_WHEEL_VELOCITY = 1
        self.LEFT_WHEEL_VELOCITY = -1

    def wander(self):
        self.LEFT_WHEEL_VELOCITY = random()
        self.RIGHT_WHEEL_VELOCITY = random()

    def stop(self):
        self.LEFT_WHEEL_VELOCITY = 0
        self.RIGHT_WHEEL_VELOCITY = 0

    def forward(self, left, right):
        self.LEFT_WHEEL_VELOCITY = left
        self.RIGHT_WHEEL_VELOCITY = right

    def rotate(self, left, right):
        self.LEFT_WHEEL_VELOCITY = left
        self.RIGHT_WHEEL_VELOCITY = right

    #! from https://stackoverflow.com/questions/7586063/how-to-calculate-the-angle-between-a-line-and-the-horizontal-axis
    def angle_trunc(self, a):
        while a < 0.0:
            a += pi * 2
        return a

    def find_relative_angle(self, start, dest):
        return self.angle_trunc(math.atan2((dest.y-start.y), (dest.x-start.x)))

    # Make the robot move to a given position
    #
    # This function works with the simulation step as well
    # this means that the robot does not go blindly forward
    def goto(self, dest, proximity_sensor_values):

        # the simple algorithm would be to
        # the closer the obstacle is ..
        # the more the robot will be impacted
        # I am going to try to use only left most and right most for the moment

        # Obstacle range is 0.04 .. but I feel like that's already to close to act on
        # so I will use 0.1 as an arbitraty try value
        # That says .. above .1 .. disregard the obstacle

        top = proximity_sensor_values[1]
        left_most = proximity_sensor_values[0] if proximity_sensor_values[0] < 0.1 else OUT_RANGE
        right_most = proximity_sensor_values[2] if proximity_sensor_values[2] < 0.1 else OUT_RANGE

        left_most = left_most if left_most != 0 else 0.01
        right_most = right_most if right_most != 0 else 0.01

        #! 0.1 / math.sqrt(x) variates between 0.3 and 1
        # print("print (left,right) sensor value (cm)")
        # print(left_most, right_most)
        left_wheel_velocity_diff = 0.1 / math.sqrt(left_most)
        right_wheel_velocity_diff = 0.1 / math.sqrt(right_most)

        # First orientate the robot
        dest_angle = self.find_relative_angle(self.position, dest)
        diff = abs(dest_angle - self.position.theta)

        if diff > math.radians(5):
            # print("RRRRR ROTATING RRRRR")

            # Determine if the robot should rather turn left or right
            s = 1
            if (self.position.theta - dest_angle) % 360 >= math.radians(180):
                s = -1

            #! maybe the velo diff has to be proportional to 0.2 and 0.5
            #! maybe I should make sure speed < 1 here,,,
            # Let's assume our robot will move alway clockwise
            if diff < math.radians(10):
                # Try at .. If I get close enough to destination, reduce speed so I don't miss it.
                left_speed = 0.2 * s
                right_speed = -0.2 * s
            else:
                # Othewise full throttle
                left_speed = 0.5 * s
                right_speed = -0.5 * s

            if top < 0.05:
                left_speed -= 3  # ! yikes

            # print("right - left")
            # print(min(right_speed + right_wheel_velocity_diff, 1),
            #       min(left_speed + left_wheel_velocity_diff, 1))
            self.rotate(min(left_speed + left_wheel_velocity_diff, 1),
                        min(right_speed + right_wheel_velocity_diff, 1))

        # Angle is good, let's move toward the point
        else:
            # print("FFFFFF FORWARD FFFFFF")
            d = distance(self.position, dest.x, dest.y)
            # As long as we are more than 1cm away
            if d > 0.02:

                if top < 0.05:
                    # and left_most == OUT_RANGE and right_most == OUT_RANGE:
                    # print("WITHIN TOP RANGE")
                    right_wheel_velocity_diff = 2

                left_speed = 1 - right_wheel_velocity_diff
                right_speed = 1 - left_wheel_velocity_diff
                # print("right - left")
                # print(right_speed, left_speed)
                self.forward(left_speed, right_speed)

            else:
                self.goto_objective_reached = True
                self.destination = None
