class Task:
    def __init__(self, name):
        self.name = name
        self.assigned = []

    def assign(self, robot):
        self.assigned.append(robot)


# Return the energy demand for task "task" at time "step"
def demand(task, step):
    # maybe by local sensing (like how many ants are performing the same task ,what pheromone do I find)
    # the ant can then return an estimate of the demands
    pass


# Return the energy an ant "robot" can supply to a task "task" at time "step"
def energy(task, robot, step):
    pass


# Assign a task "task" to a ant "robot"
def assign(task, robot):
    # ? robot.assign(task)
    # ? or
    # ? Task.assign(robot)?
    pass


# Return the number of ant assigned to a task "task" at time "step"
def assigned(task, step):
    pass


# Return the number of ant unassigned to a task at time "step"
def unassigned(step):
    pass


# Return the energy supplied to a task "task" at time "step"
def energy_supplied(task, step):
    '''
    For every ant in the set of ant that are assigned the task "task" , at time "step"
        sum energy(task, ant, robot)
    '''


# Return the energy status of a task "task" at time "step"
# R > 0 then task "task" has a deficit of energy
# R < 0 then task "task" has a surplus of energy
# R = 0 then task "task" is in equilibrium
def energy_status(task, step):
    return demand(task, step) - energy_supplied(task, step)


# Local Feedback function
def feedback(task, step):
    return 1 if energy_status(task, step) >= 0 else -1
