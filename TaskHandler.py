from const import RESOURCE_STATE_FORAGING
from const import second_reserve
from const import first_reserve
from const import core_worker
from const import temp_worker
from const import resting
from const import BLACK

from random import randint
from random import random
import threading
import globals


class TaskHandler:
    def __init__(self, TASKS):
        self.TASKS = TASKS
        self.COLORS = [(0, 0, 0), (255, 0, 0), (0, 255, 0),
                       (0, 0, 255), (125, 125, 125)]

        self.resting = resting
        self.first_reserve = first_reserve
        self.second_reserve = second_reserve
        self.temp_worker = temp_worker
        self.core_worker = core_worker

    def assign_task(self, robot):
        if robot.state == self.resting:
            candidate = []
            for i, task in enumerate(self.TASKS):

                if self.feedback(task) < 0:  # Task is in energy surplus
                    robot.TASKS_Q[i] = 0
                else:  # Task is in energy deficit
                    #! the problem where all tasks are above three still occure
                    #! which leads the robot to be in a idle state even though the demand is high ..
                    robot.TASKS_Q[i] = robot.TASKS_Q[i] + 1
                    # robot.TASKS_Q[i] = max(robot.TASKS_Q[i] + 1, 3)
                # ! this is not in the model but it would makes sense...
                if robot.TASKS_Q[i] >= 3:
                    # if robot.TASKS_Q[i] == 3:
                    candidate.append(task)

            if candidate != []:
                if randint(0, 1):
                    for i in range(len(robot.TASKS_Q)):
                        robot.TASKS_Q[i] = 0

                    robot.task = candidate[randint(0, len(candidate)-1)]
                    robot.state = self.temp_worker

        elif robot.state == self.first_reserve:
            if self.feedback(robot.task) < 0:
                robot.state = self.resting
            elif randint(0, 1):
                robot.state = self.temp_worker
            else:
                robot.state = self.second_reserve
        elif robot.state == self.second_reserve:
            if self.feedback(robot.task) < 0:
                robot.state = self.resting
            else:
                robot.state = self.temp_worker

        elif robot.state == self.temp_worker:
            if self.feedback(robot.task) < 0:
                # As long as the robot holds a resource, do not change its task.
                if not robot.carry_resource:
                    robot.state = self.first_reserve
            else:
                robot.state = self.core_worker
        elif robot.state == self.core_worker:
            if self.feedback(robot.task) < 0:
                robot.state = self.temp_worker

        if robot.state == core_worker or robot.state == temp_worker:
            robot.color = self.COLORS[robot.task]
        else:
            robot.color = BLACK

        return robot

    def print_stats(self, assignments):
        print("******* NEST *******")
        print("Resources: " + str(globals.NEST.resource_need) +
              " | " + str(assignments[0][0]))
        print("Nest processing: " +
              str(globals.NEST.resource_stock) + " | " + str(assignments[1][0]))
        print("Cleaning: " + str(globals.NEST.resource_transformed) +
              " | " + str(assignments[2][0]))
        print("Total: ", globals.NEST.total)
        print("Amount of resources left in the arena: ",
              sum([1 for i in globals.POIs if i.state == RESOURCE_STATE_FORAGING]))

        #! not really its place.
        print("Total distance: " + str(int(globals.total_dist))+" cm")

    # Return the number of ant assigned to a task "task" at time "step" (0 for actively engaged and 1 for assigned but doing nothing)
    def assigned(self, task):
        # Tweak because it did not count the robot that were in task 0 and changing all statistical tool would be too long
        if task == 1:
            return sum([1 for robot in globals.ROBOTS if robot.task == task and robot.has_to_work()]), sum([1 for robot in globals.ROBOTS if robot.task == task and not robot.has_to_work()]) + sum([1 for robot in globals.ROBOTS if robot.task == 0])
        else:
            return sum([1 for robot in globals.ROBOTS if robot.task == task and robot.has_to_work()]), sum([1 for robot in globals.ROBOTS if robot.task == task and not robot.has_to_work()])

    def assigned_pov_nest(self, task):
        if task == 1:
            return sum([1 for robot in globals.NEST.robot_task_status if robot.task == task and robot.has_to_work]), sum([1 for robot in globals.NEST.robot_task_status if robot.task == task and not robot.has_to_work]) + sum([1 for robot in globals.NEST.robot_task_status if robot.task == 0])
        else:
            return sum([1 for robot in globals.NEST.robot_task_status if robot.task == task and robot.has_to_work]), sum([1 for robot in globals.NEST.robot_task_status if robot.task == task and not robot.has_to_work])

    # Local Feedback function
    def feedback(self, task):
        #! that actually also says that, if the demand is 0 (can be also because there are enough ant on a task) then you should still be given a task, as you might be helpful
        return 1 if globals.NEST.energy_status(task) >= 0 else -1
        #! I think this is better because then it means that if a task has no needs no robot will be assigned to it
        # return 1 if globals.NEST.energy_status(task) > 0 else -1
