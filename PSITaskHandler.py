from random import random
import globals

# Code heavily inspired from the received code of the author of the paper


class PSITaskHandler:
    # ? do all the function have to lay in the class?
    def __init__(self):
        self.Xmin = 0
        self.Xmax = 512
        self.th_values = [int(0.3 * self.Xmax), int(0.6 * self.Xmax)]
        self.delta = 12
        self.phi_base = 0.3

        # ? do these numbers have to be coherent with how high my task demand can go?
        self.lower_margin = 3
        self.upper_margin = 3

        self.COLORS = [(0, 0, 0), (255, 0, 0), (0, 255, 0),
                       (0, 0, 255), (125, 125, 125)]

    def eq1(self, r1, r2):

        partner_actual_x = r2.x
        # ratio = self.demand(r2.task) / max(1, self.demand(r1.task))

        #! maybe say that if < 0 then ratio = 0?
        d1 = self.demand(r1.task) if self.demand(r1.task) > 0 else 1
        d2 = self.demand(r2.task) if self.demand(r2.task) > 0 else 1
        ratio = d2/d1
        # if r1.number == 1:
        #     print("demand for task: ", r1.task)
        #     print(self.demand(r1.task))
        #     print("ratio: ", ratio)

        if ratio != 1:
            if partner_actual_x > r1.x:
                partner_actual_x = self.th_values[r1.task-1] + (
                    partner_actual_x-self.th_values[r1.task-1])*ratio
            else:
                partner_actual_x = self.th_values[r2.task-1]-(
                    self.th_values[r2.task-1]-partner_actual_x)*ratio

        return partner_actual_x

    def eq3_4(self, r1, r2):
        partner_actual_x = self.eq1(r1, r2)

        if r1.x <= partner_actual_x and partner_actual_x < r1.x_high:
            r1.x_high = partner_actual_x
        if r1.x_low < partner_actual_x and partner_actual_x <= r1.x:
            r1.x_low = partner_actual_x

    # OK
    def eq5(self, r):

        r.x_low -= self.phi_base
        if r.x_low < self.Xmin:
            r.x_low = 0

        r.x_high += self.phi_base
        if r.x_high > self.Xmax:
            r.x_high = 1024

    # OK

    def change_x(self, r, a):
        if (r.x + a) >= 0 and(r.x + a) <= 1024:
            r.x += a

    # OK
    def eq6(self, r):
        ldist = r.x - r.x_low
        hdist = r.x_high - r.x

        if r.x_high == 1024:
            hdist *= 2

        if r.x_low == 0:
            ldist *= 2

        if hdist > ldist:
            self.change_x(r, self.delta)
        elif (hdist < ldist):
            self.change_x(r, -self.delta)
        else:
            self.change_x(r, -self.delta + 2 * self.delta * random())

        if (r.x <= 0):
            r.x = 0 + 1
            r.x_low = 0

        if (r.x >= 1024):
            r.x = 1024 - 1
            r.x_high = 1024

        if (r.x < r.x_low):
            r.x_low = r.x - self.delta
        if (r.x > r.x_high):
            r.x_high = r.x + self.delta
        if (r.x_low < 0):
            r.x_low = 0
        if (r.x_high > 1024):
            r.x_high = 1024

    # OK
    def eq7(self, r):
        # < 4 because the experiment has 3 tasks
        if r.task < 3 and r.x > self.th_values[r.task-1] + self.upper_margin:
            r.task += 1

        # >0 because we need the task to be at least 1
        elif r.task > 1 and r.x < self.th_values[r.task - 2] - self.lower_margin:
            r.task -= 1

        r.color = self.COLORS[r.task]

    def demand(self, task):
        # as long as the demand is coherent the ratio (r2.w / r1.w) is going to be calculated in the correct way
        # if task == 1:
        #     return 1
        # elif task == 2:
        #     return 5
        # elif task == 3:
        #     return 1
        if task == 1:
            return globals.NEST.resource_need * -1
        elif task == 2:
            return globals.NEST.resource_stock
        elif task == 3:
            return globals.NEST.resource_transformed
