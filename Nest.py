from RobotTaskStatus import RobotTaskStatus
import globals


class Nest:
    def __init__(self, resource_need):
        self.resource_need = resource_need
        self.resource_stock = 0
        self.resource_transformed = 0
        self.resource_waiste = 0
        self.total = 0
        self.robot_task_status = [RobotTaskStatus(
            i + 1, 0, False) for i in range(len(globals.ROBOTS) - 1)]

    # This will keep the state of the allocated task as a backup. so the information that an ant can acquire at time T are a snapshot of the past and not
    # a live event.
    def report(self, robot_number, robot_task, robot_has_to_work, robot_battery_level):
        self.robot_task_status[robot_number - 1].task = robot_task
        self.robot_task_status[robot_number -
                               1].has_to_work = robot_has_to_work
        self.robot_task_status[robot_number -
                               1].battery_level = robot_battery_level

    def energy(self, task):
        return [1 for robot in self.robot_task_status if robot.task == task and robot.has_to_work and robot.battery_level > 0]
