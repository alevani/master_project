from const import second_reserve
from const import first_reserve
from const import core_worker
from const import temp_worker

from const import resting
from random import randint
from random import random
import threading
import globals


class TaskHandler:
    def __init__(self, nest, TASKS):
        self.nest = nest
        self.TASKS = TASKS
        self.COLORS = [(0, 0, 0), (255, 0, 0), (0, 255, 0),
                       (0, 0, 255), (125, 125, 125)]

        self.resting = resting
        self.first_reserve = first_reserve
        self.second_reserve = second_reserve
        self.temp_worker = temp_worker
        self.core_worker = core_worker

    def assign_task(self, robot):
        if robot.state == self.resting:
            candidate = []
            for i, task in enumerate(self.TASKS):
                if feedback(task) < 0:  # Task is in energy surplus
                    robot.TASKS_Q[i] = 0
                else:  # Task is in energy deficit
                    robot.TASKS_Q[i] = max(robot.TASKS_Q[i] + 1, 3)
                if robot.TASKS_Q[i] == 3:
                    candidate.append(task)
            if candidate != []:
                if randint(0, 1):
                    for i in range(len(robot.TASKS_Q)):
                        robot.TASKS_Q[i] = 0

                    robot.task = candidate[randint(0, len(candidate)-1)]
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
                # As long as the robot holds a resource, do not change its task.
                if not robot.carry_resource:
                    robot.state = self.first_reserve
            else:
                robot.state = self.core_worker
        elif robot.state == self.core_worker:
            if feedback(robot.task) < 0:
                robot.state = self.temp_worker

        robot.color = self.COLORS[robot.task]

    def print_stats(self):
        print("******* NEST *******")
        print("Resources: ", self.nest.resource_need)
        print("Nest Maintenance: ", self.nest.resource_stock)
        print("Brood Care: ", self.nest.resource_transformed)
        print("Total: ", self.nest.total)


def demand(task):
    if task == 1:
        return globals.NEST.resource_need * -1
    elif task == 2:
        return globals.NEST.resource_stock
    elif task == 3:
        return globals.NEST.resource_transformed


# Return the energy an ant "robot" can supply to a task "task" at time "step"
def energy(task, robot):
    if robot.has_to_work() and robot.battery_level > 0:
        return 1
    else:
        return 0


# # Return the number of ant assigned to a task "task" at time "step" (0 for actively engaged and 1 for assigned but doing nothing)
def assigned(task):
    return str(sum([1 for robot in globals.ROBOTS if robot.task == task and robot.has_to_work()]))+";"+str(sum([1 for robot in globals.ROBOTS if robot.task == task and not robot.has_to_work()]))

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
