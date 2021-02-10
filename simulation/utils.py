from numpy import sqrt
from math import atan, cos, sin, pi, radians


def distance(s, x, y):
    return sqrt((s.x-x)**2+(s.y-y)**2)


class Position:
    def __init__(self, x, y, q=None):
        self.x = x
        self.y = y
        self.q = q

    def __repr__(self):
        return "({}, {}, {})".format(self.x, self.y, self.q)
