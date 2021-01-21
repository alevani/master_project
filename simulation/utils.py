from numpy import sqrt


def distance(s, x, y):
    return sqrt((s.x-x)**2+(s.y-y)**2)


class Position:
    def __init__(self, x, y, a=None):
        self.x = x
        self.y = y
        self.a = a

    def __repr__(self):
        return "({}, {}, {})".format(self.x, self.y, self.a)
