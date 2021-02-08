import shapely
from shapely.affinity import rotate
from shapely.geometry import LinearRing, LineString, Point, Polygon
from shapely.geometry.point import Point
from numpy import sin, cos, pi, sqrt, zeros
import math
import globals
from utils import Position
from copy import deepcopy


class Nest:
    def __init__(self, resources, position=None):
        self.resources = resources


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


class PheromonePoint:
    def __init__(self, position, decay_time, t):
        self.position = position
        self.decay_time = decay_time
        self.type = t

    def encode(self):
        return {
            'position': self.position.__dict__,
            'type': self.type
        }


class CollisionBox:
    def __init__(self, shape, position):
        self.box = shape
        self.position = position


class Robot:
    def __init__(self, number, proximity_sensors, position, color, bottom_sensors, LEFT_WHEEL_VELOCITY, RIGHT_WHEEL_VELOCITY, ROBOT_TIMESTEP, SIMULATION_TIMESTEP, R, L, task, state, hunger_level):
        self.number = number
        self.color = color
        self.task = task
        self.state = state
        self.hunger_level = hunger_level
        self.proximity_sensors = proximity_sensors
        self.bottom_sensors = bottom_sensors
        self.LEFT_WHEEL_VELOCITY = LEFT_WHEEL_VELOCITY
        self.RIGHT_WHEEL_VELOCITY = RIGHT_WHEEL_VELOCITY
        self.ROBOT_TIMESTEP = ROBOT_TIMESTEP
        self.SIMULATION_TIMESTEP = SIMULATION_TIMESTEP
        self.R = R
        self.L = L

        self.trail = True

        self.is_avoiding = False
        self.is_avoiding_cnt = 0
        self.NB_STEP_TO_AVOID = 15

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

    def avoid(self):
        self.is_avoiding_cnt += 1
        self.RIGHT_WHEEL_VELOCITY = -1
        self.LEFT_WHEEL_VELOCITY = 1
        if self.is_avoiding_cnt >= self.NB_STEP_TO_AVOID:
            self.is_avoiding_cnt = 0
            self.is_avoiding = False

    def get_bottom_sensor_states(self, pheromones_map):
        # ? here, I can induce randmoness as to simulate that sometimes an ant might decide to take a different path
        left_x = int(self.bottom_sensors[0].x * 100) + int(globals.W * 100/2)
        left_y = int(self.bottom_sensors[0].y * 100) + int(globals.H * 100/2)

        #! maybe here, instead of picking the first one
        #! I could add the candidate to a list and average
        #! so that if there's more green that pheromone then it chooses to sense the pheromone

        #! or

        #! I could to a random exclusion, exclude cell as long as it is empty with a random distribution .. return the first non-empty cell
        for x in range(left_x - 2, left_x + 2):
            for y in range(left_y - 2, left_y + 2):
                if pheromones_map[x][y] != 0:
                    return (pheromones_map[x][y].type, 0)

        #! the way the code is written just assumes than return such as (?,2) can never occur.
        # TODO there's sometimes an index out of range here I must be one off, try and except to see tf is the issue
        right_x = int(self.bottom_sensors[1].x *
                      100) + int(globals.W * 100/2)
        right_y = int(self.bottom_sensors[1].y *
                      100) + int(globals.H * 100/2)

        for x in range(right_x - 2, right_x + 2):
            for y in range(right_y - 2, right_y + 2):
                if pheromones_map[x][y] != 0:
                    return (0, pheromones_map[x][y].type)

        return(0, 0)
