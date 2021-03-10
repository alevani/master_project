from RobotTaskStatus import RobotTaskStatus
import globals


class RobotMemory:

    def __init__(self, resource_need):
        self.resource_need = resource_need
        self.resource_stock = 0
        self.resource_transformed = 0
        self.resource_waste = 0
        self.total = 0
        self.robot_task_status = []

    def report(self, robot_number, robot_task, robot_has_to_work):
        self.robot_task_status[robot_number - 1].task = robot_task
        self.robot_task_status[robot_number -
                               1].has_to_work = robot_has_to_work
