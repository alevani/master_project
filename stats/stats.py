import matplotlib
import matplotlib.pyplot as plt
import numpy as np

file = open('CAITA_50:7/EXP1/£CAITA_r10/£CAITA_r10.csv')


foraging_need = []
foraging_assigned = []
foraging_assigned_pov_nest = []

nest_processing_need = []
nest_processing_assigned = []
nest_processing_assigned_pov_nest = []


not_working_robot = []
not_working_robot_pov_nest = []

cleaning_need = []
cleaning_assigned = []
cleaning_assigned_pov_nest = []


distance = []
total = []

robots_n_task_switch = None

step = []

for line in file:
    arr = [float(value) for value in line.split(";")[:18]]
    step.append(arr[0])

    foraging_assigned.append(arr[1])
    not_working_robot.append(arr[2])
    foraging_assigned_pov_nest.append(arr[3])
    not_working_robot_pov_nest.append(arr[4])
    foraging_need.append(arr[5])

    if arr[0] % 500 == 0:
      print(foraging_need[len(foraging_need)-1] - foraging_need[len(foraging_need) -2])

    nest_processing_assigned.append(arr[6])
    not_working_robot[len(not_working_robot) - 1] += arr[7]
    nest_processing_assigned_pov_nest.append(arr[8])
    not_working_robot_pov_nest[len(not_working_robot_pov_nest) - 1] += arr[9]
    nest_processing_need.append(arr[10])

    cleaning_assigned.append(arr[11])
    not_working_robot[len(not_working_robot) - 1] += arr[12]
    cleaning_assigned_pov_nest.append(arr[13])
    not_working_robot_pov_nest[len(not_working_robot_pov_nest) - 1] += arr[14]
    cleaning_need.append(arr[15])

    distance.append(arr[16])
    total.append(arr[17])

    arr = sorted([eval(e) for e in line.split(";")[18:]])
    robots_n_task_switch = [e[1] for e in arr]

fig, ax = plt.subplots()
ax.plot(step, foraging_need, label="Resource need")
ax.plot(step, nest_processing_need, label="Nest processing need")
ax.plot(step, cleaning_need, label="Cleaning need")
ax.set(xlabel='simulation step', ylabel='Needs')
ax.grid()
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
# fig.suptitle('This is a somewhat long figure title', fontsize=16)


fig, foraging_plot = plt.subplots()
foraging_plot.plot(step, foraging_assigned,
                   label="Robot assigned to the foraging task")
foraging_plot.plot(step, foraging_assigned_pov_nest,
                   label="Robot assigned to the foraging task (NEST POV)")
foraging_plot.plot(step, foraging_need, label="Resource need")
foraging_plot.set(xlabel='simulation step', ylabel='value')
foraging_plot.grid()
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


fig, nest_processing = plt.subplots()
nest_processing.plot(step, nest_processing_assigned,
                     label="Robot assigned to the nest processing task")
nest_processing.plot(step, nest_processing_assigned_pov_nest,
                     label="Robot assigned to the nest processing task (NEST POV)")
nest_processing.plot(step, nest_processing_need,
                     label="Resource need")
nest_processing.set(xlabel='simulation step', ylabel='value')
nest_processing.grid()


plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
fig, cleaning = plt.subplots()
cleaning.plot(step, cleaning_assigned,
              label="Robot assigned to the cleaning task")
cleaning.plot(step, cleaning_assigned_pov_nest,
              label="Robot assigned to the cleaning task (NEST POV)")
cleaning.plot(step, cleaning_need, label="Resource need")
cleaning.set(xlabel='simulation step', ylabel='value')
cleaning.grid()


plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

fig, task_rep = plt.subplots()
task_rep.stackplot(step, foraging_assigned,
                   nest_processing_assigned, cleaning_assigned, not_working_robot, labels=["Foragers", "Nest processors", "Cleaners", "Unassigned"])
task_rep.set(xlabel='simulation step', ylabel='Number of robot')
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

fig, task_rep_pov_nest = plt.subplots()
task_rep_pov_nest.stackplot(step, foraging_assigned_pov_nest,
                            nest_processing_assigned_pov_nest, cleaning_assigned_pov_nest, not_working_robot_pov_nest, labels=["Foragers", "Nest processors", "Cleaners", "Unassigned"])
task_rep_pov_nest.set(xlabel='simulation step (NEST POV)',
                      ylabel='Number of robot')
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

fig, distance_plot = plt.subplots()
distance_plot.plot(
    step, distance, label="Overall distance for all robot over the full period")
distance_plot.set(xlabel='simulation step', ylabel='Covered distance (cm)')
distance_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

fig, total_plot = plt.subplots()
last = total[len(total) - 1]
total_plot.plot(step, [t/max(1, last)
                       for t in total], label="Total processed resources")
total_plot.set(xlabel='simulation step', ylabel='Task completion')
total_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


fig, robot_n_task_plot = plt.subplots()
robot_n_task_plot.plot(range(1, len(robots_n_task_switch) + 1), robots_n_task_switch,
                       label="Number of task switch for a robot over the total period")
robot_n_task_plot.set(xlabel='Robot Number', ylabel='Number of task switch')
robot_n_task_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


plt.show()
