import matplotlib
import matplotlib.pyplot as plt
import numpy as np

file = open('./stats.csv')


foraging_need = []
foraging_assigned = []
foraging_unassigned = []

nest_maintenance_need = []
nest_maintenance_assigned = []
nest_maintenance_unassigned = []

not_working_robot = []

brood_care_need = []
brood_care_assigned = []
brood_care_unassigned = []

step = []
for line in file:
    arr = [int(value) for value in line.split(";")]
    step.append(arr[0])

    foraging_need.append(arr[3])
    foraging_assigned.append(arr[1])

    not_working_robot.append(arr[2])

    nest_maintenance_need.append(arr[6])
    nest_maintenance_assigned.append(arr[4])
    not_working_robot[len(not_working_robot) - 1] += arr[5]

    brood_care_need.append(arr[9])
    brood_care_assigned.append(arr[7])
    not_working_robot[len(not_working_robot) - 1] += arr[8]


fig, ax = plt.subplots()
ax.plot(step, foraging_need, label="Resource need")
ax.plot(step, nest_maintenance_need, label="Nest maintenance need")
ax.plot(step, brood_care_need, label="Brood caring need")
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


fig, nest_maintenance = plt.subplots()
nest_maintenance.plot(step, nest_maintenance_assigned,
                      label="Robot assigned to the task")
nest_maintenance.plot(step, nest_maintenance_need,
                      label="Resource need")
nest_maintenance.set(xlabel='simulation step', ylabel='value')
nest_maintenance.grid()


plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
fig, brood_care = plt.subplots()
brood_care.plot(step, brood_care_assigned, label="Robot assigned to the task")
brood_care.plot(step, brood_care_need, label="Resource need")
brood_care.set(xlabel='simulation step', ylabel='value')
brood_care.grid()


plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

fig, task_rep = plt.subplots()
task_rep.stackplot(step, foraging_assigned,
                   nest_maintenance_assigned, brood_care_assigned, not_working_robot)

plt.show()
