import matplotlib
import matplotlib.pyplot as plt
import numpy as np

file = open('./stats.csv')


foraging_need = []
foraging_assigned = []
foraging_unassigned = []

nest_processing_need = []
nest_processing_assigned = []
nest_processing_unassigned = []

not_working_robot = []

cleaning_need = []
cleaning_assigned = []
cleaning_unassigned = []

distance = []
total = []

robots_n_task_switch = None

step = []
for line in file:
    arr = [int(value) for value in line.split(";")[:12]]
    step.append(arr[0])

    foraging_need.append(arr[3])
    foraging_assigned.append(arr[1])

    not_working_robot.append(arr[2])

    nest_processing_need.append(arr[6])
    nest_processing_assigned.append(arr[4])
    not_working_robot[len(not_working_robot) - 1] += arr[5]

    cleaning_need.append(arr[9])
    cleaning_assigned.append(arr[7])
    not_working_robot[len(not_working_robot) - 1] += arr[8]

    distance.append(arr[10])
    total.append(arr[11])

    arr = sorted([eval(e) for e in line.split(";")[12:-1]])

    if robots_n_task_switch == None:
        robots_n_task_switch = [e[1] for e in arr]
    else:
        for i, e in enumerate(arr):
            robots_n_task_switch[i] += e[1]


fig, ax = plt.subplots()
ax.plot(step, foraging_need, label="Resource need")
ax.plot(step, nest_processing_need, label="Nest processing need")
ax.plot(step, cleaning_need, label="Cleaning need")
ax.set(xlabel='simulation step', ylabel='Needs')
ax.grid()
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


fig, foraging_plot = plt.subplots()
foraging_plot.plot(step, foraging_assigned, label="Robot assigned to the task")
foraging_plot.plot(step, foraging_need, label="Resource need")
foraging_plot.set(xlabel='simulation step', ylabel='value')
foraging_plot.grid()
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


fig, nest_processing = plt.subplots()
nest_processing.plot(step, nest_processing_assigned,
                     label="Robot assigned to the task")
nest_processing.plot(step, nest_processing_need,
                     label="Resource need")
nest_processing.set(xlabel='simulation step', ylabel='value')
nest_processing.grid()


plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
fig, cleaning = plt.subplots()
cleaning.plot(step, cleaning_assigned, label="Robot assigned to the task")
cleaning.plot(step, cleaning_need, label="Resource need")
cleaning.set(xlabel='simulation step', ylabel='value')
cleaning.grid()


plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

fig, task_rep = plt.subplots()
task_rep.stackplot(step, foraging_assigned,
                   nest_processing_assigned, cleaning_assigned, not_working_robot)

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

fig, distance_plot = plt.subplots()
distance_plot.plot(step, distance, label="Distance")
distance_plot.set(xlabel='simulation step', ylabel='value')
distance_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

# TODO left legen should be in % saying the task is to grasp 50
fig, total_plot = plt.subplots()
total_plot.plot(step, total, label="Total processed resources")
total_plot.set(xlabel='simulation step', ylabel='value')
total_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


fig, robot_n_task_plot = plt.subplots()
robot_n_task_plot.plot(range(len(robots_n_task_switch)), robots_n_task_switch,
                       label="Total processed resources")
robot_n_task_plot.set(xlabel='simulation step', ylabel='value')
robot_n_task_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


plt.show()
