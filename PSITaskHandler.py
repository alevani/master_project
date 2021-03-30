from random import random
from math import ceil
import globals

# Code heavily inspired from the received code of the author of the paper


class PSITaskHandler:
    # ? do all the function have to lay in the class?
    def __init__(self):
        self.Xmin = 0
        self.Xmax = 512
        self.th_values = [ceil(0.333333 * self.Xmax),
                          ceil(0.6666666 * self.Xmax)]
        self.delta = 25  # was 1
        self.phi_base = 7.5  # was 0.3

        # ? do these numbers have to be coherent with how high my task demand can go?
        self.lower_margin = 3
        self.upper_margin = 3

    def _det_class(self, x):
        if x <= self.th_values[0]:
            return 1
        elif (x > self.th_values[0] and x <= self.th_values[1]):
            return 2
        elif x > self.th_values[1]:
            return 3

    def eq1(self, r1, r2):

        partner_actual_x = r2

        r2_task = self._det_class(partner_actual_x)
        # d1 = r1.memory.demand(
        #     r1.task if not r1.has_to_change_task_but_carry_resource else r1.new_task)
        r1_task = self._det_class(r1.x)
        d1 = r1.memory.demand(r1_task)
        d2 = r1.memory.demand(r2_task)

        if r2_task == r1.task:
            ratio = 1
        elif d1 < 1 or d2 < 1:
            ratio = 0.1
        else:
            ratio = d2/d1

        try:
            if ratio != 1:
                if partner_actual_x > r1.x:
                    partner_actual_x = self.th_values[r1_task-1] + (
                        partner_actual_x-self.th_values[r1_task-1])*ratio
                else:
                    partner_actual_x = self.th_values[r2_task-1]-(
                        self.th_values[r2_task-1]-partner_actual_x)*ratio
        except Exception as e:
            print(ratio)
            print(r1.task)
            print(r1.x)
            print(r2)
            print(r2_task)
            import sys
            print(e)
            sys.exit()

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
            r.x_high = self.Xmax

    # OK

    def change_x(self, r, a):
        if (r.x + a) >= 0 and(r.x + a) <= self.Xmax:
            r.x += a

    # OK
    def eq6(self, r):
        ldist = r.x - r.x_low
        hdist = r.x_high - r.x

        if r.x_high == self.Xmax:
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

        if (r.x >= self.Xmax):
            r.x = self.Xmax - 1
            r.x_high = self.Xmax

        if (r.x < r.x_low):
            r.x_low = r.x - self.delta
        if (r.x > r.x_high):
            r.x_high = r.x + self.delta
        if (r.x_low < 0):
            r.x_low = 0
        if (r.x_high > self.Xmax):
            r.x_high = self.Xmax

    # OK
    def eq7(self, r):
        robot_old_task = r.task

        """
        robot's task = 2
        robot's x = 361.
        but 2 : 153 < x 309
        """

        # print(r.task)
        # print(r.x)

        # < 4 because the experiment has 3 tasks
        # + self.upper_margin:
        #! problem is that the robot can jump of two segment
        #! SO I will add more test because it's true delta can actually be high.
        #! I think they did not really fall upon that problem because they never tried with such a big delta
        # if r.task < 3 and r.x > self.th_values[r.task-1]:
        #     r.task += 1

        # # >0 because we need the task to be at least 1
        # # t.task = 2 150 < 153
        # # - self.lower_margin:
        # elif r.task > 1 and r.x < self.th_values[r.task - 2]:
        #     r.task -= 1

        if r.x <= self.th_values[0]:
            r.task = 1
        elif (r.x > self.th_values[0] and r.x <= self.th_values[1]):
            r.task = 2
        elif r.x > self.th_values[1]:
            r.task = 3

        fail = False
        if r.task == 1:
            if not r.x <= self.th_values[0]:
                fail = True
        elif r.task == 2:
            if not (r.x > self.th_values[0] and r.x <= self.th_values[1]):
                fail = True
        elif r.task == 3:
            if not (r.x > self.th_values[1]):
                fail = True
        if fail:
            print("----")
            print(r.task)
            print(r.x)
            print(self.th_values[0])
            print(self.th_values[1])

            import sys
            sys.exit()

        if robot_old_task != r.task:
            r.n_task_switch += 1
