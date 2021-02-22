from robot_start_vars import second_reserve
from robot_start_vars import first_reserve
from robot_start_vars import core_worker
from robot_start_vars import temp_worker
from robot_start_vars import resting
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
        elif not robot.carry_resource:  # ! if the robot carries a resource, it shouldn't change task until the resource is processed
            if robot.state == self.temp_worker:
                if feedback(robot.task) < 0:
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


def demand(task):
    if task == 1:
        return globals.NEST.resource_need * -1
    elif task == 2:
        return globals.NEST.resource_stock
    elif task == 3:
        return globals.NEST.resource_transformed


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
    #! what does "engaged means .. because if the robot is in second worker or so it will not work .."
    # ? maybe .. if the robots know about any last foraging point .. then maybe the energy it can supply is greater?
    #! or .. if you already are on the area for the task .. maybe increase?
    #! based on gordon as well

    #! 1 because you need to assess how much ants currently assigned to the task in any state can supply .. cause if it is grearter than 0 then you might as well don't switch to this task. I guess
    # TODO should I have for some instance something that calculate the closest point to an area instead than just having a marker inside the area?
    # TODO it is highly okay if we don't variate here as if we do it he proven to be np complet
    #! should not count robot that are dead
    if robot.has_to_work():
        return 1
    else:
        return 0


# # Return the number of ant assigned to a task "task" at time "step" (0 for actively engaged and 1 for assigned but doing nothing)
def assigned(task):
    #! does engaged really means an ant has to be temp or core work?
    return str(sum([1 for robot in globals.ROBOTS if robot.task == task and robot.has_to_work()]))+";"+str(sum([1 for robot in globals.ROBOTS if robot.task == task and not robot.has_to_work()]))

# Return the energy supplied to a task "task" at time "step"


def energy_supplied(task):
    #! write in the thesis that "local feedback" from the paper just means that any robot can ask every robots their current task
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
