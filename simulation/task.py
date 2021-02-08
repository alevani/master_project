import globals
import threading
import random


class TaskHandler:
    def __init__(self, nest):
        self.nest = nest
        self.resource_handler()
        super().__init__()

    def resource_handler(self):
        self.nest.resources -= 1

        # Decrease the resource of the nest randomly
        threading.Timer(random(), self.resource_handler).start()

    # such as ..
    def get_hunger_level(self):

        # Determined by external characteristics. Since we are working with robots, the demand will be when a robot has less than
        # FOOD_TRESHOLD energy

        # Now one can do two things: Either the demand increase depending on how many robots are below the treshold
        # or if the total "battery level" is below a treshold -> which would lead or more ants seeking for food the
        # closer energy in the the mass of robots gets closer to 0

        # as of now.. it is the first one. Which means, the more robots that are hungry, the higher the demand is (undependently of their hungerness)
        return sum([1 for robot in globals.ROBOTS if robot.hunger_level > globals.FOOD_TRESHOLD])

    def get_nest_maintenance_status(self):
        # TODO let's start with get_hunger .. one task at a time
        # Return the energy demand for task "task" at time "step
        pass

    # As of now, it seems obvious that the demand for the Idle task is 0
    # as we wish that no ant choose this state over an other?
    def get_idle_demand(self):
        return 0


def demand(task, step):
    if task == "Foraging":
        # print("["+str(task)+"]: Demand is " + str(TH.get_hunger_level()))
        return globals.NEST.resources
    elif task == "Idle":
        # print("["+str(task)+"]: Demand is " + str(TH.get_idle_demand()))
        return 0
    # ask the task handler for task information
    pass


# Return the energy an ant "robot" can supply to a task "task" at time "step"
def energy(task, robot, step):
    # Energy is based on ant characteristic to achieve a task.
    # Our simulation is a homogeneous system, meaning that no robots have better characteristics than others
    # The robot cannot sense their long-range environment, but maybe, for task such as food, we could sense the short
    # environment and say "if I sense food then the energy I can provide is higher"

    # The paper says it could also be impacted by previous experience .. maybe the robot can have a short memory
    # That would say "ho .. I was close to food 10 timestep ago.. it is likely that I still have food nearby"

    # As of now.. the energy is 1. Meaning that each robot can perform anytask as good as any other
    return 1


# # Return the number of ant assigned to a task "task" at time "step"
# def assigned(task, step):
#     return sum([1 for robot in globals.ROBOTS if robot.task == task])


# # Return the number of ant unassigned to a task at time "step"
# def unassigned(step):
#     sum([1 for robot in globals.ROBOTS if robot.task == "Idle"])


# Return the energy supplied to a task "task" at time "step"
def energy_supplied(task, step):
    return sum([energy(task, robot, step) for robot in globals.ROBOTS if robot.task == task])


# Return the energy status of a task "task" at time "step"
# R > 0 then task "task" has a deficit of energy
# R < 0 then task "task" has a surplus of energy
# R = 0 then task "task" is in equilibrium
def energy_status(task, step):
    return demand(task, step) - energy_supplied(task, step)


# Local Feedback function
def feedback(task, step):
    return 1 if energy_status(task, step) >= 0 else -1
