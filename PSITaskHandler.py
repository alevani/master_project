class PSITaskHandler:
    # ? do all the function have to lay in the class?
    def __init__(self):
        self.Xmin = 0
        self.Xmax = 1024
        self.delta = 1
        self.phi_base = 0.3
        self.lower_margin, self.upper_margin = 0
        self.x = 2
        self.d_lower = self.init_x - self.Xmin - 1
        self.d_upper = self.Xmax - self.init_x - 1

        #! maybe it should be something else than 0?
        self.w = 0  # ! she says in the paper has to be [0,1]

    def D(self):
        pass

    def eq1(self, robot):
        th = 0
        return abs(self.D() - self.x + ((robot.w / self.w) * (robot.x - th)))

    def eq3(self, robot):
        d_effective = self.eq1(robot)
        if robot.x < self.x and d_effective < self.d_lower:
            return d_effective
        else:
            self.d_lower

    def eq4(self, robot):
        d_effective = self.eq1(robot)
        d_effective = self.eq1(robot)
        if robot.x > self.x and d_effective < self.d_upper:
            return d_effective
        else:
            self.d_upper

    def eq5(self):
        self.d_lower += self.phi_base
        self.d_upper += self.phi_base

    def eq6(self):
        if self.d_lower < self.d_upper:
            x += self.delta
        elif self.d_lower > self.d_upper:
            x -= self.delta
        else:
            pass  # ???

    def eq7(self, robot):
        th = 0
        if self.x > th + self.d_upper
