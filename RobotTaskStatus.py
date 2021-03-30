class RobotTaskStatus:
    def __init__(self, task, has_to_work, battery_level):
        self.task = task
        self.has_to_work = has_to_work
        self.battery_level = battery_level
        self.time_since_last_registration = 0
