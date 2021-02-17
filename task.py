import globals
import threading
from random import random
from random import randint


class TaskHandler:
    def __init__(self, nest, TASKS_Q, TASKS):
        self.nest = nest
        self.TASKS = TASKS
        self.TASKS_Q = TASKS_Q
        self.COLORS = [(0, 0, 0), (255, 0, 0), (0, 255, 0),
                       (0, 0, 255), (125, 125, 125)]

        self.resting = 0
        self.first_reserve = 1
        self.second_reserve = 2
        self.temp_worker = 3
        self.core_worker = 4

    def assign_task(self, robot):
        if robot.state == self.resting:
            candidate = []
            for i, task in enumerate(self.TASKS):
                if feedback(task) < 0:  # Task is in energy surplus
                    self.TASKS_Q[i] = 0
                else:  # Task is in energy deficit
                    self.TASKS_Q[i] = min(self.TASKS_Q[i] + 1, 3)
                    # self.TASKS_Q[i] = max(self.TASKS_Q[i] + 1, 3)
                if self.TASKS_Q[i] == 3:
                    candidate.append(task)

            if candidate != []:
                if randint(0, 1):
                    for task in self.TASKS_Q:
                        task = 0

                    robot.task = candidate[randint(0, len(candidate)-1)]
                    # when the robot get attributed a new task, let's make sure there's no mixup with the current state
                    robot.rest()
                    robot.state = self.temp_worker
        elif robot.state == self.first_reserve:
            if feedback(robot.task) < 0:
                robot.state = self.resting
                robot.rest()
            elif randint(0, 1):
                robot.state = self.temp_worker
            else:
                robot.state = self.second_reserve
        elif robot.state == self.second_reserve:
            if feedback(robot.task) < 0:
                robot.state = self.resting
                robot.rest()
            else:
                robot.state = self.temp_worker
        elif robot.state == self.temp_worker:
            if feedback(robot.task) < 0:
                robot.state = self.first_reserve
            else:
                robot.state = self.core_worker
        elif robot.state == self.core_worker:
            if feedback(robot.task) < 0:
                robot.state = self.temp_worker

        robot.color = self.COLORS[robot.task]

    def simulationstep(self):
        # if globals.CNT % 100 == 0:
        #     self.nest.resources -= randint(0, 3)

        # if globals.CNT % 50 == 0:
        #     self.nest.maintenance -= randint(0, 10)

        # if globals.CNT % 50 == 0:
        #     self.nest.brood_care -= randint(0, 10)
        pass

    def print_stats(self):
        print("******* NEST *******")
        print("Resources: ", self.nest.resources)
        print("Nest Maintenance: ", self.nest.maintenance)
        print("Brood Care: ", self.nest.brood_care)

    # such as ..
    def get_hunger_level(self):

        # Determined by external characteristics. Since we are working with robots, the demand will be when a robot has less than
        # FOOD_TRESHOLD energy

        # Now one can do two things: Either the demand increase depending on how many robots are below the treshold
        # or if the total "battery level" is below a treshold -> which would lead or more ants seeking for food the
        # closer energy in the the mass of robots gets closer to 0

        # as of now.. it is the first one. Which means, the more robots that are hungry, the higher the demand is (undependently of their hungerness)
        # return sum([1 for robot in globals.ROBOTS if robot.hunger_level > globals.FOOD_TRESHOLD])
        pass

    def get_nest_maintenance_status(self):
        # TODO let's start with get_hunger .. one task at a time
        # Return the energy demand for task "task" at time "step
        pass

    # As of now, it seems obvious that the demand for the Idle task is 0
    # as we wish that no ant choose this state over an other?
    def get_idle_demand(self):
        return 0


def demand(task):
    if task == 1:
        # print("["+str(task)+"]: Demand is " + str(TH.get_hunger_level()))
        return globals.NEST.resources * -1
    elif task == 0:
        # print("["+str(task)+"]: Demand is " + str(TH.get_idle_demand()))
        return 0
    elif task == 2:
        return globals.NEST.maintenance * -1
    elif task == 3:
        return globals.NEST.brood_care * -1
    # ask the task handler for task information
    pass


# Return the energy an ant "robot" can supply to a task "task" at time "step"
def energy(task, robot):
    # Energy is based on ant characteristic to achieve a task.
    # Our simulation is a homogeneous system, meaning that no robots have better characteristics than others
    # The robot cannot sense their long-range environment, but maybe, for task such as food, we could sense the short
    # environment and say "if I sense food then the energy I can provide is higher"

    # The paper says it could also be impacted by previous experience .. maybe the robot can have a short memory
    # That would say "ho .. I was close to food 10 timestep ago.. it is likely that I still have food nearby"

    # As of now.. the energy is 1. Meaning that each robot can perform anytask as good as any other

    #! but the energy will depend of the task
    if not robot.state == 0:  # 0 is resting
        return 1
    else:
        return 0


# # Return the number of ant assigned to a task "task" at time "step"
# def assigned(task):
#     return sum([1 for robot in globals.ROBOTS if robot.task == task])


# # Return the number of ant unassigned to a task at time "step"
# def unassigned(step):
#     sum([1 for robot in globals.ROBOTS if robot.task == "Idle"])


# Return the energy supplied to a task "task" at time "step"
def energy_supplied(task):
    return sum([energy(task, robot) for robot in globals.ROBOTS if robot.task == task])


# Return the energy status of a task "task" at time "step"
# R > 0 then task "task" has a deficit of energy
# R < 0 then task "task" has a surplus of energy
# R = 0 then task "task" is in equilibrium
def energy_status(task):
    return demand(task) - energy_supplied(task)


# Local Feedback function
def feedback(task):
    return 1 if energy_status(task) >= 0 else -1
