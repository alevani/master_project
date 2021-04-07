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


step = np.arange(10,  12000, 10)


def read(file, shift=0):
    distance = []
    total = []
    robots_n_task_switch = None
    for line in file:
        arr = [float(value) for value in line.split(";")[:12 + shift]]

        distance.append(arr[10 + shift])
        total.append(arr[11 + shift])

        arr = sorted([eval(e) for e in line.split(";")[12 + shift:-1]])

        robots_n_task_switch = [e[1] for e in arr]

    return distance, total, robots_n_task_switch


# Shifts are here because file may have different formats
d_30, t_30, n_30 = read(f30, 3)
d_20, t_20, n_20 = read(f20, 3)
d_10, t_10, n_10 = read(f10, 3)
d_40, t_40, n_40 = read(f40, 3)
d_50, t_50, n_50 = read(f50, 3)
d_70, t_70, n_70 = read(f70, 3)
d_0, t_0, n_0 = read(f0, 3)
d_8000, t_8000, n_8000 = read(f8000, 3)



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
# total_plot.plot(step, [t if not t == None else None for t in t_0],
#                 label="0.1m")
total_plot.plot(step, [t if not t == None else None for t in t_10],
                label="0.5m")
total_plot.plot(step, [t if not t == None else None for t in t_20],
                label="1m")
total_plot.plot(step, [t if not t == None else None for t in t_30],
                label="5m")
total_plot.plot(step, [t if not t == None else None for t in t_40],
                label="7m ")

total_plot.plot(step, [t if not t == None else None for t in t_50],
                label="13m")
total_plot.plot(step, [t if not t == None else None for t in t_70],
                label="15m")
total_plot.plot(step, [t if not t == None else None for t in t_8000],
                label="Infinite range")



total_plot.set(xlabel='simulation step', ylabel='Task completion')
total_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
plt.show()
