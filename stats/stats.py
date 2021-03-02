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

step = []
for line in file:
    arr = [int(value) for value in line.split(";")]
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

plt.show()
