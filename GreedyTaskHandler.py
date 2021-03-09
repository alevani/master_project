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

        # The task that has the highest demand, not the highest needs (big diff)
        # TODO if all args are the same numpy will take the first task, but in that
        # case it could maybe be random?
        # denabd is diff from energy_status
        robot.task = numpy.argmax([globals.NEST.demand(task)
                                   for task in self.TASKS]) + 1
        robot.color = self.COLORS[robot.task]

    def print_stats(self):
        print("******* NEST *******")
        print("Resources: ", globals.NEST.resource_need)
        print("Nest processing: ", globals.NEST.resource_stock)
        print("Cleaning: ", globals.NEST.resource_transformed)
        print("Total: ", globals.NEST.total)
