# ? th
# ? +- X .. ? + or - ? sweat_smile
# ? is self.w updated in eq7?
# ? wasn't it a story about robot are distributed among the task in a uniform way?
# what is the init task of a robot
# what is the init w of a robot (the task's demand?)

#! Have I misunderstood something and when the paper says e.g. "dlower" it referes to a calcule of distance?
#! I think yes, so when for a calcule you have to return d_lower e.g. then you have to calculate the dist from x to it


"""
Code heavily inspired from the received code of the author of the paper
"""

"""
apparently everytime the task demand changes it recalculate calculateTh_fixed. why?

-> I think it is because they remove some tasks at some point which means they have
   to recalculate the tresh. (I do not need it)
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


"""
void change_x(int i, float a) {
	if ((robot[i].x + a) >= MIN_X && (robot[i].x + a) <= MAX_X )
		robot[i].x += a;
}

eq 6
	float hdist,ldist;

	// Have I misunderstood something and when the paper says e.g. "dlower" it referes to a calcule of distance?
	// I think yes, so when for a calcule you have to return d_lower e.g. then you have to calculate the dist from x to it
	ldist = robot[i].x - robot[i].x_low;
	hdist = robot[i].x_high - robot[i].x;
	if (robot[i].x_high == MAX_X)
		hdist *= 2;
	if (robot[i].x_low == MIN_X)
		ldist *= 2;

	if (hdist > ldist)
		change_x(i,robot[i].delta);
	else if (hdist < ldist)
		change_x(i,-robot[i].delta);
	else
	 	//change_x(i,-robot[i].delta+2*robot[i].delta*(float)rand()/(float)RAND_MAX);
		/*if(rand()%2<1)
			change_x(i,robot[i].delta);
		else 	change_x(i,-robot[i].delta);*/
	 	change_x(i,-robot[i].delta+2*robot[i].delta*(float)rand()/(float)RAND_MAX);

    // a bit of random change
    change_x(i,-RANODM_CHANGE+2*RANODM_CHANGE*(float)rand()/(float)RAND_MAX);


    if (robot[i].x <= MIN_X) {
        robot[i].x = MIN_X + 1;
        robot[i].x_low = MIN_X;
    }
    if (robot[i].x >= MAX_X) {
        robot[i].x = MAX_X - 1;
        robot[i].x_high = MAX_X;
    }
    if (robot[i].x < robot[i].x_low)
        robot[i].x_low = robot[i].x - robot[i].delta;
    if (robot[i].x > robot[i].x_high)
        robot[i].x_high = robot[i].x + robot[i].delta;
    if (robot[i].x_low < MIN_X)
        robot[i].x_low = MIN_X;
    if (robot[i].x_high > MAX_X)
        robot[i].x_high = MAX_X;
"""

   def eq7(self, r):
        # < 3 because the experiment has 3 tasks
        if r.task + 1 < 4 and r.x > self.th_values[r.task] + self.upper_margin:
            r.task += 1

        # >0 because we need the task to be at least 1
        elif r.task - 1 > 0 and r.x < self.th_values[r.task - 2] - self.lower_margin:
            r.task -= 1

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
