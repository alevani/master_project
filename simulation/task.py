''' Mostly pseudo code'''
Tasks = []
Tasks.append(Task(0, 'Foraging'))

robot = ""
Tasks[0].assign(robot)


class Task:
    def __init__(self, t, name):
        self.type = t
        self.name = name
        self.assigned = []

    def assign(self, ant):
        self.assigned.append(ant)


# Return the energy demand for task "task" at time "step"
def demand(task, step):
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
