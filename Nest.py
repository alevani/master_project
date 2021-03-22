import globals
from random import uniform, randint


class Nest:
    def __init__(self, resource_need):
        self.resource_need = resource_need
        self.resource_stock = 0
        self.resource_transformed = 0
        self.resource_waste = 0
        self.total = 0
        self.robot_task_status = []

    def step(self):

        for i, m in enumerate(self.robot_task_status):
            m.time_since_last_registration += 1

            # If the robot cannot be contacted after a long period of time,
            # consider it gone.
            # TODO remove report in simulation.py as robot have to figure by themselves what is the need.
            if not i + 1 == self.number and m.time_since_last_registration >= 1200:  # 1200 is arbitrary
                m.has_to_work = False
                m.task = 0

    def can_register(self, robot_number):
        if self.robot_task_status[robot_number-1].time_since_last_registration >= self.robot_task_status[robot_number-1].time_before_registration:
            self.robot_task_status[robot_number -
                                   1].time_since_last_registration = 0
            self.robot_task_status[robot_number -
                                   # This configuration offers the best distribution
                                   1].time_before_registration = randint(len(globals.ROBOTS), len(globals.ROBOTS) + len(globals.ROBOTS))
            return True
        else:
            False

    def try_report(self, pkg):
        # Small probability of not correctly receiving a robot's information
        #! todo it should only receive one packet at once, here it received everything
        #! add internal var and clean it in simulation after all robot are gone
        if not uniform(0, 1) < globals.PROB_COMM_FAILURE and self.can_register(pkg[0]):
            self.report(*pkg)
            # Small probability of the robot not receiving back information from the nest (done here for ease)
            if not uniform(0, 1) < globals.PROB_COMM_FAILURE:
                return True, True  # if one end communication is successful
            else:
                return True, False
        else:
            return False, False

    # This will keep the state of the allocated task as a backup. so the information that an ant can acquire at time T are a snapshot of the past and not
    # a live event.
    def report(self, robot_number, robot_task, robot_has_to_work, robot_battery_level, trashed_resources, resource_transformed, resource_stock):
        self.robot_task_status[robot_number - 1].task = robot_task
        self.robot_task_status[robot_number -
                               1].has_to_work = robot_has_to_work
        self.robot_task_status[robot_number -
                               1].battery_level = robot_battery_level

        self.resource_transformed -= trashed_resources
        self.total += trashed_resources

        self.resource_stock -= resource_transformed
        self.resource_transformed += resource_transformed

        self.resource_need += resource_stock
        self.resource_stock += resource_stock

    def energy(self, task):
        return sum([1 for robot in self.robot_task_status if robot.task == task and robot.has_to_work and robot.battery_level > 0])

    def demand(self, task):
        if task == 1:
            return self.resource_need * -1
        elif task == 2:
            return self.resource_stock
        elif task == 3:
            return self.resource_transformed

    # Return the energy status of a task "task" at time "step"
    # R > 0 then task "task" has a deficit of energy
    # R < 0 then task "task" has a surplus of energy
    # R = 0 then task "task" is in equilibrium
    def energy_status(self, task):
        return self.demand(task) - self.energy(task)
