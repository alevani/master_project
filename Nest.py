from GreedyTaskHandler import GreedyTaskHandler
from TaskHandler import TaskHandler
from random import uniform, randint
from copy import deepcopy
import globals

from const import core_worker, temp_worker
from const import TASKS

from RobotTaskHandlingPacket import RobotTaskHandlingPacket


class Nest:
    def __init__(self, resource_need):
        self.TaskHandler = TaskHandler(TASKS)
        self.GreedyTaskHandler = GreedyTaskHandler(TASKS)
        self.resource_need = resource_need
        self.resource_stock = 0
        self.resource_transformed = 0
        self.resource_waste = 0
        self.total = 0
        self.robot_task_status = []
        self.pkg = False

    def robot_has_to_work(self, state):
        return state == core_worker or state == temp_worker

    def try_report_and_get_task(self, TASKS_Q, task, state, color, n_task_switch, number, battery_level, trashed_resources, resource_transformed, resource_stock, carry_resource):
        if not uniform(0, 1) < globals.PROB_COMM_FAILURE:

            robot_old_task = task
            ProcessedTaskHandlerPacket = self.TaskHandler.assign_task(RobotTaskHandlingPacket(
                TASKS_Q, task, state, color, n_task_switch, carry_resource))
            # self.GreedyTaskHandler.assign_task(robot)
            if robot_old_task != ProcessedTaskHandlerPacket.task:
                ProcessedTaskHandlerPacket.n_task_switch += 1

            self.report(number, ProcessedTaskHandlerPacket.task, self.robot_has_to_work(ProcessedTaskHandlerPacket.state), battery_level,
                        trashed_resources, resource_transformed, resource_stock)

            # Small probability of the robot not receiving back information from the nest (done here for ease)
            if not uniform(0, 1) < globals.PROB_COMM_FAILURE:

                # if one end communication is successful
                return True, True, ProcessedTaskHandlerPacket
            else:
                return True, False, None
        else:
            return False, False, None

    def step(self):
        for m in self.robot_task_status:
            m.time_since_last_registration += 1

            # If the robot cannot be contacted after a long period of time,
            # consider it gone.
            if m.time_since_last_registration >= 2000:
                m.has_to_work = False

    def report(self, robot_number, robot_task, robot_has_to_work, robot_battery_level, trashed_resources, resource_transformed, resource_stock):
        self.robot_task_status[robot_number - 1].task = robot_task
        self.robot_task_status[robot_number -
                               1].has_to_work = robot_has_to_work
        self.robot_task_status[robot_number -
                               1].battery_level = robot_battery_level
        self.robot_task_status[robot_number -
                               1].time_since_last_registration = 0

        self.resource_transformed -= trashed_resources
        self.total += trashed_resources

        self.resource_stock -= resource_transformed
        self.resource_transformed += resource_transformed

        self.resource_need -= resource_stock
        self.resource_stock += resource_stock

    def energy(self, task):
        return sum([1 for robot in self.robot_task_status if robot.task == task and robot.has_to_work and robot.battery_level > 0])

    def demand(self, task):
        if task == 1:
            return self.resource_need
        elif task == 2:
            return self.resource_stock
        elif task == 3:
            return self.resource_transformed

    # Return the energy status of a task "task" at time "step"
    # R > 0 then task "task" has a deficit of energy
    # R < 0 then task "task" has a surplus of energy
    # R = 0 then task "task" is in equilibrium
    def energy_status(self, task):
        return self.demand(task) - self.energy(task)
