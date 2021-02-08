import globals


class TaskHandler:
    def __init__(self):
        super().__init__()

    # maybe call every 10 step or so, or threader
    # Depending on the task I decide to implement, this will asses the demand for each task
    # maybe by local sensing (like how many ants are performing the same task ,what pheromone do I find)
    # the ant can then return an estimate of the demands

    # such as ..
    def get_food_level(self):
        return sum([1 for robot in globals.ROBOTS if robot.food_level < globals.FOOD_TRESHOLD])

    def get_nest_maintenance_status(self):
        # TODO let's start with get_hunger .. one task at a time
        # Return the energy demand for task "task" at time "step
        pass

    # As of now, it seems obvious that the demand for the Idle task is 0
    # as we wish that no ant choose this state over an other?
    def get_idle_demand(self):
        return 0


TH = TaskHandler()


def demand(task, step):
    #! roughly ..
    if task == "Foraging":
        return TH.get_food_level()
    elif task == "Idle":
        return TH.get_idle_demand()
    # ask the task handler for task information
    pass


# Return the energy an ant "robot" can supply to a task "task" at time "step"
def energy(task, robot, step):
    #! maybe an ant as one unit of energy? how it that calculated? maybe it is link to the level of hunger
    #! but I have to relate it to a robotic setup where the energy of the robot will always be its battery life
    # ? ¯\_(ツ)_/¯
    # idk yet
    return 2


# Return the number of ant assigned to a task "task" at time "step"
def assigned(task, step):
    return sum([1 for robot in globals.ROBOTS if robot.task == task])


# Return the number of ant unassigned to a task at time "step"
def unassigned(step):
    sum([1 for robot in globals.ROBOTS if robot.task == "Idle"])


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
