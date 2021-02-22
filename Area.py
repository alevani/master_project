from shapely.geometry import Polygon


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
