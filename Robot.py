from shapely.geometry import LinearRing, LineString, Point, Polygon
from numpy import sin, cos, pi, sqrt, zeros
from shapely.geometry.point import Point
from CollisionBox import CollisionBox
from shapely.affinity import rotate
from Position import Position
from random import randint
from random import random
from copy import deepcopy

from const import BOTTOM_LIGHT_SENSORS_POSITION
from const import PROXIMITY_SENSORS_POSITION
from const import RESOURCE_STATE_WAISTE
from const import RESOURCE_STATE_NEST_PROCESSING
from const import RESOURCE_STATE_FORAGING
from const import RESOURCE_STATE_TRANSFORMED
from const import SIMULATION_TIMESTEP
from const import ROBOT_TIMESTEP
from const import core_worker
from const import temp_worker
from const import BLACK
from const import dist
from const import R
from const import W
from const import H
from const import L

import globals
import shapely
import math

OUT_RANGE = 10000

# X start and end borns for add_robot
x_a = int((-W/2 + 0.1) * 100)
x_b = int((-W/2 + 1.30) * 100)

# Y start and end borns for add_robot
y_a = int((H/2 - 3.1)*100)
y_b = int((H/2 - 0.1)*100)


def add_robot(do_avoid):
    posx = randint(x_a, x_b)
    posy = randint(y_a, y_b)
    globals.ROBOTS.append(Robot(len(globals.ROBOTS) + 1, deepcopy(PROXIMITY_SENSORS_POSITION), Position(posx/100, posy/100, math.radians(0)),
                                BLACK, deepcopy(BOTTOM_LIGHT_SENSORS_POSITION), 1, 1, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, 0, 0, 100, do_avoid))


class Robot:
    def __init__(self, number, proximity_sensors, position, color, bottom_sensors, LEFT_WHEEL_VELOCITY, RIGHT_WHEEL_VELOCITY, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, task, state, battery_level, do_avoid):
        self.number = number
        self.do_avoid = do_avoid
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

        # Foraging  # Nest maintenance  # Brood care
        self.TASKS_Q = [0, 0, 0]

        self.payload = None
        self.area_left = -1
        self.area_right = -1
        self.time_in_zone = 0

        self.position = position
        self.update_bottom_sensor_position(position.x, position.y)
        self.rotate_bottom_sensors(
            position.x, position.y, position.theta - math.radians(90))

        self.update_proximity_sensor_position(position.x, position.y,
                                              position.theta-math.radians(90))
        self.rotate_proximity_sensors(position.x, position.y,
                                      position.theta-math.radians(90))
        self.update_collision_box(position)

        self.obstacle_detection_range = 0.05
        self.battery_low = False
        self.trail = True
        self.is_avoiding = False
        self.is_avoiding_cnt = 0
        self.NB_STEP_TO_AVOID = 15

        self.saved_destination = None

        self.position = position
        self.start_position = position
        self.draw_information = []
        self.path = []

        self.proximity_sensors_backup = deepcopy(proximity_sensors)
        self.bottom_sensors_backup = deepcopy(bottom_sensors)

    def in_range(self, position):
        return True if dist((position.x, position.y), (self.position.x, self.position.y)) <= 0.12 else False

    def rest(self):
        self.destination = None
        if self.carry_resource:
            self.drop_resource()

    def reset(self):
        position = self.start_position
        self.position = position
        self.proximity_sensors = deepcopy(self.proximity_sensors_backup)
        self.bottom_sensors = deepcopy(self.bottom_sensors_backup)
        self.update_collision_box(position)

    def stay_home(self):
        if not self.area_left and not self.area_right:
            if randint(0, 1):
                self.turn_left()
            else:
                self.turn_right()
        elif not self.area_right:
            self.soft_turn_left()
        elif not self.area_left:
            self.soft_turn_right()

    def pickup_resource(self, POI):
        self.carry_resource = True
        self.payload = POI
        globals.PHEROMONES_MAP[POI.position.x][POI.position.y] = 0

    def drop_resource(self):
        self.carry_resource = False
        x = int(self.position.x * 100) + \
            int(W * 100/2)
        y = int(self.position.y * 100) + \
            int(H * 100/2)
        globals.PHEROMONES_MAP[x][y] = self.payload
        self.payload = None
        self.time_to_drop_out = 0
        self.time_in_zone = 0

    def trash_resource(self):
        globals.NEST.resource_transformed -= self.payload.value
        globals.NEST.total += self.payload.value
        globals.POIs[self.payload.index].state = RESOURCE_STATE_WAISTE
        self.payload.state = RESOURCE_STATE_WAISTE
        self.drop_resource()

    def transform_resource(self):
        globals.NEST.resource_stock -= self.payload.value
        globals.NEST.resource_transformed += self.payload.value
        globals.POIs[self.payload.index].state = RESOURCE_STATE_TRANSFORMED
        self.payload.state = RESOURCE_STATE_TRANSFORMED
        self.drop_resource()

    def compute_resource(self):
        globals.NEST.resource_need += self.payload.value
        globals.NEST.resource_stock += self.payload.value
        globals.POIs[self.payload.index].state = RESOURCE_STATE_NEST_PROCESSING

        self.destination = self.last_foraging_point
        self.payload.state = RESOURCE_STATE_NEST_PROCESSING
        self.time_in_zone = 0
        self.drop_resource()

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

    def go_home(self):
        # set the robot's destination to its charging area
        self.last_foraging_point = None
        self.destination = self.start_position

    def rotate_bottom_sensors(self, x, y, a):
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

    def has_to_work(self):
        return self.state == core_worker or self.state == temp_worker

    def has_destination(self):
        return True if self.destination != None else False

    def sense_area(self, areas):
        box_left = Point(
            self.bottom_sensors[0].x, self.bottom_sensors[0].y).buffer(0.01)
        box_right = Point(
            self.bottom_sensors[1].x, self.bottom_sensors[1].y).buffer(0.01)

        self.area_left = 0
        self.area_right = 0

        for area in areas:
            if area.box.intersects(box_left):
                self.area_left = area.type

            if area.box.intersects(box_right):
                self.area_right = area.type

    def calculate_proximity_sensors_state(self, sensors_values):
        top = sensors_values[1]
        left_most = sensors_values[0]
        right_most = sensors_values[2]

        top_value = 1 if top < self.obstacle_detection_range else 0
        left_most_value = 1 if left_most < self.obstacle_detection_range else 0
        right_most_value = 1 if right_most < self.obstacle_detection_range else 0
        self.prox_sensors_state = (
            left_most_value, top_value, right_most_value)

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
        self.rotate_bottom_sensors(x, y, theta-self.position.theta)

        self.update_position(Position(x, y, theta))

    def avoid(self):
        self.is_avoiding_cnt += 1
        self.turn_left()
        if self.is_avoiding_cnt >= self.NB_STEP_TO_AVOID:
            self.is_avoiding_cnt = 0
            self.is_avoiding = False

    def get_bottom_sensors_state(self, pheromones_map):
        left_x = int(self.bottom_sensors[0].x * 100) + int(W * 100/2)
        left_y = int(self.bottom_sensors[0].y * 100) + int(H * 100/2)

        for x in range(left_x - 2, left_x + 2):
            for y in range(left_y - 2, left_y + 2):
                if pheromones_map[x][y] != 0:
                    return (pheromones_map[x][y].type, 0), pheromones_map[x][y]

        right_x = int(self.bottom_sensors[1].x *
                      100) + int(W * 100/2)
        right_y = int(self.bottom_sensors[1].y *
                      100) + int(H * 100/2)

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

    def is_on_area(self, area):
        return True if self.area_left == area or self.area_right == area else False

    # from https://stackoverflow.com/questions/7586063/how-to-calculate-the-angle-between-a-line-and-the-horizontal-axis
    def _angle_trunc(self, a):
        while a < 0.0:
            a += pi * 2
        return a

    def find_relative_angle(self, start, dest):
        return self._angle_trunc(math.atan2((dest.y-start.y), (dest.x-start.x)))

    # Make the robot move to a given position
    #
    # This function works with the simulation step as well
    # this means that the robot does not go blindly forward
    def goto(self, dest, proximity_sensor_values):

        if self.do_avoid:
            top = proximity_sensor_values[1]
            left_most = proximity_sensor_values[0] if proximity_sensor_values[0] < 0.1 else OUT_RANGE
            right_most = proximity_sensor_values[2] if proximity_sensor_values[2] < 0.1 else OUT_RANGE

            left_most = left_most if left_most != 0 else 0.01
            right_most = right_most if right_most != 0 else 0.01

            # 0.1 / math.sqrt(x) variates between 0.3 and 1
            left_wheel_velocity_diff = 0.1 / math.sqrt(left_most)
            right_wheel_velocity_diff = 0.1 / math.sqrt(right_most)

        # First orientate the robot
        dest_angle = self.find_relative_angle(self.position, dest)
        diff = abs(dest_angle - self.position.theta)

        if diff > math.radians(5):

            s = 1
            # Determine if the robot should rather turn left or right
            if (self.position.theta - dest_angle) % 360 >= math.radians(180):
                s = -1

            #! maybe the velo diff has to be proportional to 0.2 and 0.5
            #! maybe I should make sure speed < 1 here,,,

            # Speed down when approaching goal angle
            if diff < math.radians(10):
                left_speed = 0.2 * s
                right_speed = -0.2 * s
            else:
                left_speed = 0.5 * s
                right_speed = -0.5 * s

            if self.do_avoid:
                # ? should left or right be random?
                if top < 0.05:
                    left_speed -= 3  # ! yikes

                self.rotate(min(left_speed + left_wheel_velocity_diff, 1),
                            min(right_speed + right_wheel_velocity_diff, 1))
            else:
                self.rotate(left_speed, right_speed)

        # If angle dest reached, move forward
        else:
            d = dist((self.position.x, self.position.y), (dest.x, dest.y))

            # Speeds down the robot when approaching goal position
            if d > 0.02:
                if self.do_avoid:
                    if top < 0.05:
                        # ? should that be random
                        right_wheel_velocity_diff = 2

                    left_speed = 1 - right_wheel_velocity_diff
                    right_speed = 1 - left_wheel_velocity_diff
                else:
                    left_speed = 1
                    right_speed = 1
                self.forward(left_speed, right_speed)

            else:
                self.destination = None
                self.last_foraging_point = None

    # Navigation controller
    def step(self, robot_prox_sensors_values):
        self.calculate_proximity_sensors_state(robot_prox_sensors_values)

        if self.has_destination():
            self.goto(self.destination, robot_prox_sensors_values)
        else:
            if self.is_avoiding:
                self.avoid()
            else:
                # Wall / Robot avoidance under no goal
                if self.prox_sensors_state == (0, 1, 0):
                    if randint(0, 1):
                        self.turn_left()
                    else:
                        self.turn_right()
                elif self.prox_sensors_state == (1, 0, 0) or self.prox_sensors_state == (1, 1, 0):
                    self.turn_left()
                elif self.prox_sensors_state == (0, 0, 1) or self.prox_sensors_state == (0, 1, 1):
                    self.turn_right()
                elif self.prox_sensors_state == (1, 0, 1) or self.prox_sensors_state == (1, 1, 1):
                    self.is_avoiding = True
                    self.NB_STEP_TO_AVOID = 7
                else:
                    if not self.battery_low:
                        self.wander()

        self.simulationstep()

        # if the robot carries a resource, update the resource's position according to the robot's movement
        if self.carry_resource:
            globals.POIs[self.payload.index].position.x = self.position.x
            globals.POIs[self.payload.index].position.y = self.position.y
