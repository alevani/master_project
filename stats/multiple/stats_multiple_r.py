import matplotlib
import matplotlib.pyplot as plt
import numpy as np

f10 = open(
    '/Users/freak/Desktop/master_project/stats/03FAITA/EXP3/£FAITA_r10/£FAITA_r10.csv')
f20 = open(
    '/Users/freak/Desktop/master_project/stats/03FAITA/EXP3/£FAITA_r20/£FAITA_r20.csv')
f30 = open(
    '/Users/freak/Desktop/master_project/stats/03FAITA/EXP3/£FAITA_r30/£FAITA_r30.csv')
f40 = open(
    '/Users/freak/Desktop/master_project/stats/03FAITA/EXP3/£FAITA_r40/£FAITA_r40.csv')
f50 = open(
    '/Users/freak/Desktop/master_project/stats/03FAITA/EXP3/£FAITA_r50/£FAITA_r50.csv')


step = np.arange(10,  61000, 10)


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


# Shifts are here because file may have different formats
d_30, t_30, n_30 = read(f30, 3)
d_20, t_20, n_20 = read(f20, 3)
d_10, t_10, n_10 = read(f10, 3)
d_40, t_40, n_40 = read(f40, 3)
d_50, t_50, n_50 = read(f50, 3)


d_30 += [d_30[len(d_30) - 1] for i in range(len(step) - len(d_30))]
d_20 += [d_20[len(d_20) - 1] for i in range(len(step) - len(d_20))]
d_10 += [d_10[len(d_10) - 1] for i in range(len(step) - len(d_10))]
d_40 += [d_40[len(d_40) - 1] for i in range(len(step) - len(d_40))]
d_50 += [d_50[len(d_50) - 1] for i in range(len(step) - len(d_50))]

fig, distance_plot = plt.subplots()
distance_plot.plot(step, d_30, label="30 robots")
distance_plot.plot(step, d_20, label="20 robots")
distance_plot.plot(step, d_10, label="10 robots")
distance_plot.plot(step, d_40, label="40 robots")
distance_plot.plot(step, d_50, label="50 robots")
distance_plot.set(xlabel='simulation step', ylabel='Covered distance (cm)')
distance_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

m = max(t_30[len(t_30) - 1], t_10[len(t_10) - 1],
        t_20[len(t_20) - 1], t_40[len(t_40) - 1], t_50[len(t_50) - 1])
t_30 += [None for i in range(len(step) - len(t_30))]
t_20 += [None for i in range(len(step) - len(t_20))]
t_10 += [None for i in range(len(step) - len(t_10))]
t_40 += [None for i in range(len(step) - len(t_40))]
t_50 += [None for i in range(len(step) - len(t_50))]


fig, total_plot = plt.subplots()
total_plot.plot(step, [t if not t == None else None for t in t_30],
                label="30 robots")
total_plot.plot(step, [t if not t == None else None for t in t_20],
                label="20 robots")
total_plot.plot(step, [t if not t == None else None for t in t_10],
                label="10 robots")
total_plot.plot(step, [t if not t == None else None for t in t_40],
                label="40 robots")
total_plot.plot(step, [t if not t == None else None for t in t_50],
                label="50 robots")
total_plot.set(xlabel='simulation step', ylabel='Task completion')
total_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
plt.show()
