import globals
import threading
from random import random


class TaskHandler:
    def __init__(self, nest):
        self.nest = nest
        self.resource_handler()
        self.task2()

    def print_stats(self):
        print("******* NEST *******")
        print("Resources: ", self.nest.resources)
        print("Task2: ", self.nest.task2)

    def resource_handler(self):
        self.nest.resources -= 10  # ? this affect the way task is allocated

        # Decrease the resource of the nest randomly
        thread = threading.Timer(random() + 3, self.resource_handler)
        thread.setDaemon(True)
        thread.start()

    def task2(self):
        self.nest.task2 -= 5  # ? this affect the way task is allocated

        # Decrease the resource of the nest randomly
        thread = threading.Timer(random() + 3, self.task2)
        thread.setDaemon(True)
        thread.start()

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
        return globals.NEST.task2 * -1
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
    return 1


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
