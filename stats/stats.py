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
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

ax.set(xlabel='simulation step', ylabel='Needs')

ax.grid()

plt.show()
