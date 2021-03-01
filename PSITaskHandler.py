# ? th
# ? +- X .. ? + or - ? sweat_smile
# ? is self.w updated in eq7?
# ? wasn't it a story about robot are distributed among the task in a uniform way?
# ? what if eq7 yields to go task -= 1 but task is already 1
# what is the init task of a robot
# what is the init w of a robot (the task's demand?)


class PSITaskHandler:
    # ? do all the function have to lay in the class?
    def __init__(self):
        self.Xmin = 0
        self.Xmax = 1024
        self.th_values = [int(0.3 * self.Xmax), int(0.6 * self.Xmax)]
        self.delta = 1
        self.phi_base = 0.3
        self.lower_margin = 0
        self.upper_margin = 0
        self.COLORS = [(0, 0, 0), (255, 0, 0), (0, 255, 0),
                       (0, 0, 255), (125, 125, 125)]

    def D(self, r1, r2):
        if r2.x < r1.x:
            # -2 since arrays start at 0
            # but tasks at  1
            return self.th_values[r1.task - 2]
        else:
            return self.th_values[r1.task]

    def eq1(self, r1, r2):
        th = 1
        print(r2.w, r1.w)
        return abs(self.D(r1, r2) - r1.x + ((r2.w / r1.w) * (r2.x - th)))

    def eq3_4(self, r1, r2):
        d_effective = self.eq1(r1, r2)

        #! should the assigned values be bounded?
        if r2.x < r1.x and d_effective < r1.d_lower:
            r1.d_lower = d_effective

        if r2.x > r1.x and d_effective < r1.d_upper:
            r1.d_upper = d_effective

    def eq5(self, r):
        r.d_lower += self.phi_base
        r.d_upper += self.phi_base

    def eq6(self, r):
        #! should the assigned values be bounded?
        if r.d_lower < r.d_upper:
            r.x = min(r.x + self.delta, self.Xmax)
        elif r.d_lower > r.d_upper:
            r.x = max(r.x - self.delta, self.Xmin)
        else:
            r.x += 0

    def eq7(self, r):
        if r.x > self.th_values[r.task] + self.upper_margin:
            r.task += 1
        elif r.x < self.th_values[r.task - 2] - self.lower_margin:
            r.task -= 1

        print(r.task)
        r.w = self.demand(r.task)
        r.color = self.COLORS[r.task]

    def demand(self, task):
        # # nest demand / nb robots and bound to 1? (as done below)
        # nb_robots = len(globals.ROBOTS)
        # if task == 1:
        #     return min(globals.NEST.resource_need * -1 / nb_robots, 1)
        # elif task == 2:
        #     return min(globals.NEST.resource_stock / nb_robots, 1)
        # elif task == 3:
        #     return min(globals.NEST.resource_transformed / nb_robots, 1)

        # as long as the demand is coherent the ratio (r2.w / r1.w) is going to be calculated in the correct way
        if task == 1:
            return globals.NEST.resource_need * -1
        elif task == 2:
            return globals.NEST.resource_stock
        elif task == 3:
            return globals.NEST.resource_transformed
