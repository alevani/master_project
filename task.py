import globals
import threading
from random import random
from random import randint


class TaskHandler:
    def __init__(self, nest, TASKS):
        self.nest = nest
        self.TASKS = TASKS
        #! is Q local to a robot?
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
                    robot.TASKS_Q[i] = 0
                else:  # Task is in energy deficit
                    # robot.TASKS_Q[i] = min(robot.TASKS_Q[i] + 1, 3)
                    robot.TASKS_Q[i] = max(robot.TASKS_Q[i] + 1, 3)
                if robot.TASKS_Q[i] == 3:
                    candidate.append(task)

            if candidate != []:
                if randint(0, 1):
                    for task in robot.TASKS_Q:
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

    def print_stats(self):
        print("******* NEST *******")
        print("Resources: ", self.nest.resource_need)
        print("Nest Maintenance: ", self.nest.resource_stock)
        print("Brood Care: ", self.nest.resource_transformed)

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
        return globals.NEST.resource_need * -1
    elif task == 0:
        return 0
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
    if robot.has_to_work and robot.task == task:  # 0 is resting
        return 1
    else:
        return 0


# # Return the number of ant assigned to a task "task" at time "step" (0 for actively engaged and 1 for assigned but doing nothing)
def assigned(task):
    return str(sum([1 for robot in globals.ROBOTS if robot.task == task and robot.has_to_work]))+";"+str(sum([1 for robot in globals.ROBOTS if robot.task == task and not robot.has_to_work]))


# # Return the number of ant unassigned to a task at time "step"
# def unassigned(step):
#     sum([1 for robot in globals.ROBOTS if robot.task == "Idle"])


# Return the energy supplied to a task "task" at time "step"
def energy_supplied(task):
    return sum([energy(task, robot) for robot in globals.ROBOTS])


# Return the energy status of a task "task" at time "step"
# R > 0 then task "task" has a deficit of energy
# R < 0 then task "task" has a surplus of energy
# R = 0 then task "task" is in equilibrium
def energy_status(task):
    return demand(task) - energy_supplied(task)


# Local Feedback function
def feedback(task):
    return 1 if energy_status(task) >= 0 else -1
