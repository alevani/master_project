class Position:
    def __init__(self, x, y, theta=None):
        self.x = x
        self.y = y
        self.theta = theta

    def __repr__(self):
        return "({}, {}, {})".format(self.x, self.y, self.theta)
