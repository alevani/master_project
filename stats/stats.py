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

brood_care_need = []
brood_care_assigned = []
brood_care_unassigned = []

step = []
for line in file:
    arr = [int(value) for value in line.split(";")]
    step.append(arr[0])

    foraging_need.append(arr[3])
    foraging_assigned.append(arr[2])
    foraging_unassigned.append(arr[1])

    nest_maintenance_need.append(arr[6])
    nest_maintenance_assigned.append(arr[5])
    nest_maintenance_unassigned.append(arr[4])

    brood_care_need.append(arr[9])
    brood_care_assigned.append(arr[8])
    brood_care_unassigned.append(arr[7])


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
foraging_plot.plot(step, foraging_unassigned,
                   label="Robot not assigned to the task")
foraging_plot.plot(step, foraging_need, label="Resource need")
foraging_plot.set(xlabel='simulation step', ylabel='value')
foraging_plot.grid()
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


fig, nest_maintenance = plt.subplots()
nest_maintenance.plot(step, nest_maintenance_assigned,
                      label="Robot assigned to the task")
nest_maintenance.plot(step, nest_maintenance_unassigned,
                      label="Robot not assigned to the task")
nest_maintenance.plot(step, nest_maintenance_need,
                      label="Resource need")
nest_maintenance.set(xlabel='simulation step', ylabel='value')
nest_maintenance.grid()


plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
fig, brood_care = plt.subplots()
brood_care.plot(step, brood_care_assigned, label="Robot assigned to the task")
brood_care.plot(step, brood_care_unassigned,
                label="Robot not assigned to the task")
brood_care.plot(step, brood_care_need, label="Resource need")
brood_care.set(xlabel='simulation step', ylabel='value')
brood_care.grid()


plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

plt.show()
