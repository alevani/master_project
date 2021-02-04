class Task:
    def __init__(self):
        super().__init__()


# Return the energy demand for task "task" at time "step"
def demand(task, step):
    pass


# Return the energy an ant "robot" can supply to a task "task" at time "step"
def energy(task, robot, step):
    pass


# Assign a task "task" to a ant "robot"
def assign(task, robot):
    pass


# Return the number of ant assigned to a task "task" at time "step"
def assigned(task, step):
    pass


# Return the number of ant unassigned to a task at time "step"
def unassigned(step):
    pass
