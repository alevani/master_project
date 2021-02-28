from const import second_reserve
from const import first_reserve
from const import core_worker
from const import temp_worker

from const import resting
from random import randint
from random import random
import globals
import numpy


class GreedyTaskHandler:
    def __init__(self, TASKS):
        self.TASKS = TASKS
        self.COLORS = [(0, 0, 0), (255, 0, 0), (0, 255, 0),
                       (0, 0, 255), (125, 125, 125)]

        self.temp_worker = temp_worker

    def assign_task(self, robot):

        robot.rest()
        robot.state = self.temp_worker
        robot.task = numpy.argmax([self.demand(task)
                                   for task in self.TASKS]) + 1
        robot.color = self.COLORS[robot.task]

    def print_stats(self):
        print("******* NEST *******")
        print("Resources: ", globals.NEST.resource_need)
        print("Nest Maintenance: ", globals.NEST.resource_stock)
        print("Brood Care: ", globals.NEST.resource_transformed)
        print("Total: ", globals.NEST.total)

    def demand(self, task):
        if task == 1:
            return globals.NEST.resource_need * -1
        elif task == 2:
            return globals.NEST.resource_stock
        elif task == 3:
            return globals.NEST.resource_transformed

    # Return the number of ant assigned to a task "task" at time "step" (0 for actively engaged and 1 for assigned but doing nothing)
    def assigned(self, task):
        return str(sum([1 for robot in globals.ROBOTS if robot.task == task and robot.has_to_work()]))+";"+str(sum([1 for robot in globals.ROBOTS if robot.task == task and not robot.has_to_work()]))