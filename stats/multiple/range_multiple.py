import matplotlib
import matplotlib.pyplot as plt
import numpy as np


f0 = open(
    '../0FAITA_EXP_HARD_RANGE/EXP1/range0.1/range0.1.csv')
f10 = open(
    '../0FAITA_EXP_HARD_RANGE/EXP1/range0.5/range0.5.csv')
f20 = open(
    '../0FAITA_EXP_HARD_RANGE/EXP1/range1/range1.csv')
f30 = open(
    '../0FAITA_EXP_HARD_RANGE/EXP1/range5/range5.csv')
f40 = open(
    '../0FAITA_EXP_HARD_RANGE/EXP1/range7/range7.csv')
f50 = open(
    '../0FAITA_EXP_HARD_RANGE/EXP1/range13/range13.csv')
f70 = open(
    '../0FAITA_EXP_HARD_RANGE/EXP1/range15/range15.csv')
f8000 = open(
    '../0FAITA_EXP_HARD_RANGE/EXP1/range80000/range80000.csv')


step = np.arange(10,  32000, 10)

def mean(list):
  v = 0
  cnt = 0
  for i in list:
    if i == None:
      cnt +=1
    else:
      v += i
  return v/(len(list)-cnt)
def read(file, shift=0):
    distance = []
    total = []
    error = []
    robots_n_task_switch = None
    for line in file:
        arr = [float(value) for value in line.split(";")[:12 + shift]]

        distance.append(arr[10 + shift])
        total.append(arr[11 + shift])

        error.append(abs(arr[4] - arr[3]))
        error[len(error) - 1] += abs(arr[7] - arr[8])
        error[len(error) - 1] += abs(arr[11] - arr[12])

        arr = sorted([eval(e) for e in line.split(";")[12 + shift:]])

        robots_n_task_switch = [e[1] for e in arr]

    return distance, total, robots_n_task_switch, error


# Shifts are here because file may have different formats
d_30, t_30, n_30, e_30 = read(f30, 3)
d_20, t_20, n_20, e_20 = read(f20, 3)
d_10, t_10, n_10, e_10 = read(f10, 3)
d_40, t_40, n_40, e_40 = read(f40, 3)
d_50, t_50, n_50, e_50 = read(f50, 3)
d_70, t_70, n_70, e_70 = read(f70, 3)
d_0, t_0, n_0, e_0 = read(f0, 3)
d_8000, t_8000, n_8000, e_8000 = read(f8000, 3)


# m = max(t_30[len(t_30) - 1], t_10[len(t_10) - 1],
#         t_20[len(t_20) - 1], t_40[len(t_40) - 1], t_50[len(t_50) - 1])
t_30 += [150 for i in range(len(step) - len(t_30))]
t_20 += [150 for i in range(len(step) - len(t_20))]
t_10 += [150 for i in range(len(step) - len(t_10))]
t_40 += [150 for i in range(len(step) - len(t_40))]
t_50 += [150 for i in range(len(step) - len(t_50))]
t_70 += [150 for i in range(len(step) - len(t_70))]
t_0 += [150 for i in range(len(step) - len(t_0))]
t_8000 += [150 for i in range(len(step) - len(t_8000))]


fig, total_plot = plt.subplots()
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_0],
                label="0.1m")
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_10],
                label="Range = 0.5m")
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_20],
                label="Range = 1m")
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_30],
                label="Range = 5m")
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_40],
                label="Range = 7m ")

total_plot.plot(step, [t/1.5 if not t == None else None for t in t_50],
                label="Range = 13m (entire arena)")


total_plot.set(xlabel='simulation step', ylabel='Task completion rate (%)')
total_plot.grid()


plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


step = np.arange(10,  32000, 10)

e_0 += [None for i in range(len(step) - len(e_0))]
e_30 += [None for i in range(len(step) - len(e_30))]
e_20 += [None for i in range(len(step) - len(e_20))]
e_10 += [None for i in range(len(step) - len(e_10))]
e_40 += [None for i in range(len(step) - len(e_40))]
e_50 += [None for i in range(len(step) - len(e_50))]
e_70 += [None for i in range(len(step) - len(e_70))]
e_8000 += [None for i in range(len(step) - len(e_8000))]
fig, error_ = plt.subplots()


print(mean(e_0))
print(mean(e_10))
print(mean(e_20))
print(mean(e_30))
print(mean(e_40))
print(mean(e_50))
print(mean(e_70))
print(mean(e_8000))


error_.plot(step, e_10,
            label="Range = 0.5m", linewidth=1.2)
error_.plot(step, e_20,
            label="Range = 1m", linewidth=1.2)
error_.plot(step, e_30,
            label="Range = 5m", linewidth=1.2)
error_.plot(step, e_40,
            label="Range = 7m", linewidth=1.2)
error_.plot(step, e_50,
            label="Range = 13m (entire arena)", linewidth=1.2)

error_.set(xlabel='simulation step',
           ylabel='Swarm perception error (in resources)')
error_.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


ax2 = error_.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:gray'
ax2.set_ylabel('Range = 0.1m, swarm perception error (in resources)', color=color)  # we already handled the x-label with ax1
ax2.plot(step, e_0, color=color,alpha=0.3)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped



fig, robot_n_task_plot = plt.subplots()
robot_n_task_plot.plot(range(1, 41), n_0,
                       label="Range = 0.1m")

robot_n_task_plot.plot(range(1, 41), n_10,
                       label="Range = 0.5m")

# robot_n_task_plot.plot(range(1, 41), n_20,
#                        label="Range = 1m")
robot_n_task_plot.plot(range(1, 41), n_30,
                       label="Range = 5m")
# robot_n_task_plot.plot(range(1, 41), n_40,
#                        label="Range = 7m")

robot_n_task_plot.plot(range(1, 41), n_8000,
                       label="Range = 13m (entire arena)")

robot_n_task_plot.set(xlabel='Robot ID',
                      ylabel='Number of task switch')

robot_n_task_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

plt.show()
