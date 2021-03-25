from const import second_reserve
from const import first_reserve
from const import core_worker
from const import temp_worker

from const import resting
from random import randint
from random import random
import globals
import numpy


class RandomTaskHandler:
    def __init__(self):
        self.COLORS = [(0, 0, 0), (255, 0, 0), (0, 255, 0),
                       (0, 0, 255), (125, 125, 125)]

    def assign_task(self, robot):

        robot.state = 3
        robot.task = randint(1, 3)
        robot.color = self.COLORS[robot.task]

    def print_stats(self):
        print("******* NEST *******")
        print("Resources: ", globals.NEST.resource_need)
        print("Nest processing: ", globals.NEST.resource_stock)
        print("Cleaning: ", globals.NEST.resource_transformed)
        print("Total: ", globals.NEST.total)
