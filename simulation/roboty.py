import shapely
from shapely.affinity import rotate
from shapely.geometry import LinearRing, LineString, Point, Polygon
from shapely.geometry.point import Point
import math
from utils import Position
from copy import deepcopy


class CollisionBox:
    def __init__(self, shape, position):
        self.box = shape
        self.position = position


class Robot:
    def __init__(self, number, proximity_sensors, position, color, bottom_sensors):
        self.number = number
        self.color = color
        self.proximity_sensors = proximity_sensors
        self.bottom_sensors = bottom_sensors

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
