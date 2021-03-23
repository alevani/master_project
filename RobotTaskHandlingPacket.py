class RobotTaskHandlingPacket:
    def __init__(self, TASKS_Q, task, state, color, n_task_switch, carry_resource):
        self.TASKS_Q = TASKS_Q
        self.task = task
        self.state = state
        self.color = color
        self.n_task_switch = n_task_switch
        self.carry_resource = carry_resource
