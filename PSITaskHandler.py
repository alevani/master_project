from random import random

"""
Code heavily inspired from the received code of the author of the paper
"""


class PSITaskHandler:
    # ? do all the function have to lay in the class?
    def __init__(self):
        self.Xmin = 0
        self.Xmax = 1024
        self.th_values = [int(0.3 * self.Xmax), int(0.6 * self.Xmax)]
        self.delta = 1
        self.phi_base = 0.3

        # ? do these numbers have to be coherent with how high my task demand can go?
        self.lower_margin = 3
        self.upper_margin = 3

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

        return abs(self.D(r1, r2) - r1.x + ((self.demand(r1.task) / self.demand(r2.task)) * (r2.x - th)))

    def eq3_4(self, r1, r2):
        d_effective = self.eq1(r1, r2)

        #! should the assigned values be bounded?
        if r2.x < r1.x and d_effective < r1.d_lower:
            r1.d_lower = d_effective

        if r2.x > r1.x and d_effective < r1.d_upper:
            r1.d_upper = d_effective

    # OK
    def eq5(self, r):
        r.d_lower -= max(self.phi_base, 0)
        r.d_upper += min(self.phi_base, 1024)

    # OK
    def change_x(self, r, a):
        if (r.x + a) >= 0 and(r.x + a) <= 1024:
            r.x += a

    # OK
    def eq6(self, r):
        ldist = r.x - r.d_lower
        hdist = r.d_upper - r.x

        if r.d_upper == 1024:
            hdist *= 2

        if r.d_lower == 0:
            ldist *= 2

        if hdist > ldist:
            self.change_x(r, self.delta)
        elif (hdist < ldist):
            self.change_x(r, -self.delta)
        else:
            self.change_x(r, -self.delta + 2 * self.delta * random())

        if (r.x <= 0):
            r.x = 0 + 1
            r.d_lower = 0

        if (r.x >= 1024):
            r.x = 1024 - 1
            r.d_upper = 1024

        if (r.x < r.d_lower):
            r.d_lower = r.x - self.delta
        if (r.x > r.d_upper):
            r.d_upper = r.x + self.delta
        if (r.d_lower < 0):
            r.d_lower = 0
        if (r.d_upper > 1024):
            r.d_upper = 1024

    # OK
    def eq7(self, r):
        # < 3 because the experiment has 3 tasks
        if r.task + 1 < 4 and r.x > self.th_values[r.task] + self.upper_margin:
            r.task += 1

        # >0 because we need the task to be at least 1
        elif r.task - 1 > 0 and r.x < self.th_values[r.task - 2] - self.lower_margin:
            r.task -= 1

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
