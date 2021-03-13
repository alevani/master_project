from random import random
import globals

# Code heavily inspired from the received code of the author of the paper


class PSITaskHandler:
    # ? do all the function have to lay in the class?
    def __init__(self):
        self.Xmin = 0
        self.Xmax = 512
        self.th_values = [int(0.3 * self.Xmax), int(0.6 * self.Xmax)]
        self.delta = 12  # was 1
        self.phi_base = 0.3  # was 0.3

        # ? do these numbers have to be coherent with how high my task demand can go?
        self.lower_margin = 3
        self.upper_margin = 3

        self.COLORS = [(0, 0, 0), (255, 0, 0), (0, 255, 0),
                       (0, 0, 255), (125, 125, 125)]

    def eq1(self, r1, r2):

        partner_actual_x = r2.x

        d1 = globals.NEST.demand(r1.task)
        d2 = globals.NEST.demand(r2.task)

        """ That failed .. shouldn't have. since r2.x and r1.x are the same ratio should've been = to 1
        My guess: x are not a reflect of the actual task because I fucked up something with the report.
        Resources: 428 | 19
        Nest Maintenance: 231 | 13
        Brood Care: 203 | 18
        Total:  24
        Total distance: 4359 cm
        0.8787878787878788
        2
        309.9978488561499
        3
        309.9978488561499
        """
        if d1 == d2:
            ratio = 1
        elif d1 < 1 or d2 < 1:
            #! maybe that depends on who from d1 or d2 is as is
            """
            r1.task = 1
            demand(1) = -30y
            r1.x = 120
            r2.task = 2
            demand(2) = 27
            r2.x = 178
            """
            ratio = 0.1
        else:
            ratio = d2/d1

        try:
            if ratio != 1:
                if partner_actual_x > r1.x:
                    partner_actual_x = self.th_values[r1.task-1] + (
                        partner_actual_x-self.th_values[r1.task-1])*ratio
                else:
                    partner_actual_x = self.th_values[r2.task-1]-(
                        self.th_values[r2.task-1]-partner_actual_x)*ratio
        except Exception as e:
            print(ratio)
            print(r1.task)
            print(r1.x)
            print(r2.task)
            print(r2.x)
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
        # < 4 because the experiment has 3 tasks
        # + self.upper_margin:
        if r.task < 3 and r.x > self.th_values[r.task-1]:
            r.task += 1

        # >0 because we need the task to be at least 1
        # t.task = 2 150 < 153
        # - self.lower_margin:
        elif r.task > 1 and r.x < self.th_values[r.task - 2]:
            r.task -= 1
        if robot_old_task != r.task:
            r.n_task_switch += 1
        r.color = self.COLORS[r.task]
