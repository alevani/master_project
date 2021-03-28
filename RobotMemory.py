from RobotMemoryInformation import RobotMemoryInformation
from random import randint
import globals
import math

# TODO the robot also needs to save its own information
# otherwise demand is biased


class RobotMemory:
    def __init__(self, number, foraging_demand_start_value):
        # self.memory[0] == robot N1
        # self.memory[1] == robot N2
        # and so on ..
        self.memory = [RobotMemoryInformation()
                       for i in range(globals.NB_ROBOTS)]
        self.number = number

        # Foraging, Nest processing, Cleaning
        self.demand_memory = [foraging_demand_start_value, 0, 0]
        self.PSI_demand = [20, 1, 1]

    def step(self):

        for m in self.memory:
            m.time_since_last_registration += 1

    def can_register(self, robot_number):
        if self.memory[robot_number-1].time_since_last_registration >= self.memory[robot_number-1].time_before_registration:
            self.memory[robot_number-1].time_since_last_registration = 0
            self.memory[robot_number -
                        # This configuration offers the best distribution
                        1].time_before_registration = randint(40, len(globals.ROBOTS) + 40)
            return True
        else:
            False

    def register(self, robot_number, task, has_to_work, processed_resources):
        self.memory[robot_number - 1].task = task
        self.memory[robot_number - 1].has_to_work = has_to_work

        # If the processed_resources you receive is diff from the one saved, it means this robot has gone
        # Further in task completion, update the demand accordingly
        if self.memory[robot_number - 1].task_processed_resources != processed_resources:

            self.demand_memory[0] -= (processed_resources[0] -
                                      self.memory[robot_number - 1].task_processed_resources[0])
            self.demand_memory[1] += (processed_resources[0] -
                                      self.memory[robot_number - 1].task_processed_resources[0])

            self.demand_memory[1] -= (processed_resources[1] -
                                      self.memory[robot_number - 1].task_processed_resources[1])
            self.demand_memory[2] += (processed_resources[1] -
                                      self.memory[robot_number - 1].task_processed_resources[1])

            self.demand_memory[2] -= (processed_resources[2] -
                                      self.memory[robot_number - 1].task_processed_resources[2])
            self.memory[robot_number -
                        1].task_processed_resources = processed_resources

            m = max(self.demand_memory[0],
                    self.demand_memory[1], self.demand_memory[2])

            self.PSI_demand = [self.get_PSI_demand(
                m, d) for d in self.demand_memory]

    # used to map the demand to a 1 - 20 scale (as PSI seems to be designed like this.)
    def get_PSI_demand(self, m, demand):
        return math.ceil(demand/m * 20) if demand > 1 else 1

    def demand(self, task):
        return self.PSI_demand[task-1]
