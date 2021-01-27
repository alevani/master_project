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
    def __init__(self, number, sensors, position):
        self.number = number

        self.sensors = sensors

        self.update_sensors_pos(position.x, position.y,
                                position.q-math.radians(90))
        self.rotate_all_pos(position.x, position.y,
                            position.q-math.radians(90))

        self.position = position
        self.draw_information = []
        self.has_collided = False
        self.path = []

        self.update_collision_box(position)

    def is_colliding(self, shape):
        return self.collision_box.box.intersects(shape)

    def is_sensing(self, ray):
        return self.collision_box.box.interesects(ray)

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

    def rotate_all_pos(self, x, y, q):
        for pos in self.sensors:
            point = rotate(Point(pos.x, pos.y), q,
                           (x, y), use_radians=True)
            pos.x = point.x
            pos.y = point.y

    def update_sensors_pos(self, x, y, q):
        for pos in self.sensors:
            pos.x = pos.x + x
            pos.y = pos.y + y
            pos.q = pos.q + q
