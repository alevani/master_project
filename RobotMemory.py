from RobotMemoryInformation import RobotMemoryInformation
from random import randint
import globals

# TODO the robot also needs to save its own information
# otherwise demand is biased


class RobotMemory:
    def __init__(self, number):
        # self.memory[0] == robot N1
        # self.memory[1] == robot N2
        # and so on ..
        self.memory = [RobotMemoryInformation()
                       for i in range(globals.NB_ROBOTS)]
        self.number = number

        # Foraging, Nest processing, Cleaning
        self.demand_memory = [-25, 0, 0]

    def step(self):

        for i, m in enumerate(self.memory):
            m.time_since_last_registration += 1

            # If the robot cannot be contacted after a long period of time,
            # consider it gone.
            if not i + 1 == self.number and m.time_since_last_registration >= 100:
                m.has_to_work = False

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

            self.demand_memory[0] += (processed_resources[0] -
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

    def energy(self, task):
        return sum([1 for robot in self.memory if robot.task == task and robot.has_to_work])

    def demand(self, task):
        return self.demand_memory[task-1] if task != 1 else self.demand_memory[task-1] * -1

    # Return the energy status of a task "task" at time "step"
    # R > 0 then task "task" has a deficit of energy
    # R < 0 then task "task" has a surplus of energy
    # R = 0 then task "task" is in equilibrium
    def energy_status(self, task):
        return self.demand(task) - self.energy(task)
