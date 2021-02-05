class Task:
    def __init__(self, name):
        self.name = name
        self.assigned = []

    def assign(self, robot):
        self.assigned.append(robot)


class TaskHandler:
    def __init__(self):
        super().__init__()

    # maybe call every 10 step or so, or threader
    # Depending on the task I decide to implement, this will asses the demand for each task
    # maybe by local sensing (like how many ants are performing the same task ,what pheromone do I find)
    # the ant can then return an estimate of the demands

    # such as ..
    #! How do we induce operating cost of a task with the task allocation model? to be disscussed..
    def get_food_level(self):
        food_level = 0
        for robot in globals.ROBOTS:
            food_level += robot.food_level
            if food_level > globals.FOOD_TRESHOLD:
                # ? maybe return the number of ants that are below the food level treshold instead?
                return 1

        return 0

    def get_nest_maintenance_status(self):
        # TODO let's start with get_hunger .. one task at a time
        # Return the energy demand for task "task" at time "step
        pass


def demand(task, step):
    #! roughly ..
    if task == "Foraging":
        return TaskHandler.get_food_level()
    else:
        pass
    # ask the task handler for task information
    pass


# Return the energy an ant "robot" can supply to a task "task" at time "step"
def energy(task, robot, step):
    #! maybe an ant as one unit of energy? how it that calculated? maybe it is link to the level of hunger
    #! but I have to relate it to a robotic setup where the energy of the robot will always be its battery life
    # ? ¯\_(ツ)_/¯
    pass

# Return the number of ant assigned to a task "task" at time "step"


def assigned(task, step):
    return sum([1 for robot in globals.ROBOTS if robot.task == task])


# Return the number of ant unassigned to a task at time "step"
def unassigned(step):
    sum([1 for robot in globals.ROBOTS if robot.task == Idle])


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
