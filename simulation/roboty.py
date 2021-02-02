import shapely
from shapely.affinity import rotate
from shapely.geometry import LinearRing, LineString, Point, Polygon
from shapely.geometry.point import Point
from numpy import sin, cos, pi, sqrt, zeros
import math
from utils import Position
from copy import deepcopy


class CollisionBox:
    def __init__(self, shape, position):
        self.box = shape
        self.position = position


class Robot:
    def __init__(self, number, proximity_sensors, position, color, bottom_sensors, LEFT_WHEEL_VELOCITY, RIGHT_WHEEL_VELOCITY, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L):
        self.number = number
        self.color = color
        self.proximity_sensors = proximity_sensors
        self.bottom_sensors = bottom_sensors
        self.LEFT_WHEEL_VELOCITY = LEFT_WHEEL_VELOCITY
        self.RIGHT_WHEEL_VELOCITY = RIGHT_WHEEL_VELOCITY
        self.ROBOT_TIMESTEP = ROBOT_TIMESTEP
        self.SIMULATION_TIMESTEP = SIMULATION_TIMESTEP
        self.R = R
        self.L = L

        self.update_bottom_sensor_position(position.x, position.y)
        self.rotate_bottom_sensor(
            position.x, position.y, position.q - math.radians(90))

        self.update_proximity_sensor_position(position.x, position.y,
                                              position.q-math.radians(90))
        self.rotate_proximity_sensors(position.x, position.y,
                                      position.q-math.radians(90))

        self.position = position
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
        q = position.q
        x = position.x
        y = position.y

        q = q - math.radians(90)
        box_x = 0.0525
        box_y_top = 0.0725
        box_y_bottom = 0.0725 - 0.03

        collision_box = Polygon(
            ((x - box_x, y - box_y_bottom), (x - box_x, y + box_y_top),
             (x + box_x, y + box_y_top), (x + box_x, y - box_y_bottom)))

        collision_box = rotate(collision_box, q, (x, y), use_radians=True)
        self.collision_box = CollisionBox(collision_box, Position(q, x, y))

    def get_collision_box_coordinate(self):
        x, y = self.collision_box.box.exterior.coords.xy
        return tuple(zip(x, y))

    def get_collision_box(self):
        return self.collision_box.box

    def rotate_proximity_sensors(self, x, y, q):
        for pos in self.proximity_sensors:
            point = rotate(Point(pos.x, pos.y), q,
                           (x, y), use_radians=True)
            pos.x = point.x
            pos.y = point.y

    def rotate_bottom_sensor(self, x, y, a):
        for pos in self.bottom_sensors:
            point = rotate(Point(pos.x, pos.y), a,
                           (x, y), use_radians=True)
            pos.x = point.x
            pos.y = point.y

    def update_proximity_sensor_position(self, x, y, q):
        for pos in self.proximity_sensors:
            pos.x = pos.x + x
            pos.y = pos.y + y
            pos.q = pos.q + q

    def update_bottom_sensor_position(self, x, y):
        for pos in self.bottom_sensors:
            pos.x = pos.x + x
            pos.y = pos.y + y

    def get_proximity_sensor_state(self, sensors_values):
        top = sensors_values[2]
        left = sensors_values[1]
        right = sensors_values[3]
        leftest = sensors_values[0]
        rightest = sensors_values[4]

        top_value = 1 if top < 0.04 else 0
        left_value = 1 if left < 0.04 else 0
        right_value = 1 if right < 0.04 else 0
        leftest_value = 1 if leftest < 0.04 else 0
        rightest_value = 1 if rightest < 0.04 else 0

        # return (leftest_value, left_value, top_value, right_value, rightest_value)
        return (leftest_value, top_value, rightest_value)

    def create_rays(self, W, H):
        rays = []
        spos = []
        for sensor in self.proximity_sensors:
            nx = sensor.x
            ny = sensor.y
            nq = sensor.q
            nx_end = nx+cos(nq)*2*W
            ny_end = ny+sin(nq)*2*H
            ray = [(nx, ny), (nx_end, ny_end)]
            spos.append((nx, ny, nq))
            rays.append(LineString(ray))
        return rays, spos

    def simulationstep(self):
        # step model time/timestep times
        x = self.position.x
        y = self.position.y
        q = self.position.q
        for step in range(int(self.ROBOT_TIMESTEP/self.SIMULATION_TIMESTEP)):
            v_x = cos(q)*(self.R*self.LEFT_WHEEL_VELOCITY /
                          2 + self.R*self.RIGHT_WHEEL_VELOCITY/2)
            v_y = sin(q)*(self.R*self.LEFT_WHEEL_VELOCITY /
                          2 + self.R*self.RIGHT_WHEEL_VELOCITY/2)
            omega = (self.R*self.RIGHT_WHEEL_VELOCITY -
                     self.R*self.LEFT_WHEEL_VELOCITY)/(2*self.L)

            x += v_x * self.SIMULATION_TIMESTEP
            y += v_y * self.SIMULATION_TIMESTEP
            q += omega * self.SIMULATION_TIMESTEP

        self.update_proximity_sensor_position(
            x - self.position.x, y - self.position.y, q-self.position.q)
        self.rotate_proximity_sensors(x, y, q-self.position.q)

        self.update_bottom_sensor_position(
            x - self.position.x, y - self.position.y)
        self.rotate_bottom_sensor(x, y, q-self.position.q)

        self.update_position(Position(x, y, q))

    def get_bottom_sensor_states(self, POINTS):
        #! what can be nice here is to say "is there anything between the line formed by this two points" (let's make it a rectangle maybe?)
        box_left = Point(
            self.bottom_sensors[0].x, self.bottom_sensors[0].y).buffer(0.02)
        box_right = Point(
            self.bottom_sensors[1].x, self.bottom_sensors[1].y).buffer(0.02)

        left_state = 0
        right_state = 0

        # For the sake of optimisation, let's assume that the two sensors cannot be active at the same time
        # #! but then, what if multiple path ..?
        for p in POINTS:
            if p.box.intersects(box_left):
                left_state = 1
                break
            elif p.box.intersects(box_right):
                right_state = 1
                break

        return (left_state, right_state)

        # right_state = 0
        # for p in POINTS:
        #     if p.contains(box_left):
        #         right_state = 1
        # break

        # TODO here, it will have to compare a list of all floor object present in the map
        # TODO, then each object is a python object with a position and a gray color value
        # TODO that way, in real life I can "easily" reproduce it
        # TODO even though it is likely that I will have to implement camera anyway
        # ? each object, even the path left by the robot, could be in the list (then supress path from robot.path). the object path in
        # ? specific could have a decay (evaporation) counter and leave the list at some point.
        #! or here we just check if we are on a path left by one of the n robot
        # return (0 if Polygon(BLACK_TAPE).contains(box_left) else 1, 0 if Polygon(BLACK_TAPE).contains(box_right) else 1)
