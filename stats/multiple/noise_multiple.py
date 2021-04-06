import matplotlib
import matplotlib.pyplot as plt
import numpy as np

f10 = open(
    '/Users/freak/Desktop/master_project/stats/0FAITA_EXP_NOISE/EXP1/0.05_æFAITA_r40/0.05_æFAITA_r40.csv')
f20 = open(
    '/Users/freak/Desktop/master_project/stats/0FAITA_EXP_NOISE/EXP1/0.1_æFAITA_r40/0.1_æFAITA_r40.csv')
f30 = open(
    '/Users/freak/Desktop/master_project/stats/0FAITA_EXP_NOISE/EXP1/0.3_æFAITA_r40/0.3_æFAITA_r40.csv')
f40 = open(
    '/Users/freak/Desktop/master_project/stats/0FAITA_EXP_NOISE/EXP1/0.5_æFAITA_r40/0.5_æFAITA_r40.csv')
f50 = open(
    '/Users/freak/Desktop/master_project/stats/0FAITA_EXP_NOISE/EXP1/0.7_æFAITA_r40/0.7_æFAITA_r40.csv')
f70 = open(
    '/Users/freak/Desktop/master_project/stats/0FAITA_EXP_NOISE/EXP1/0_æFAITA_r40/0_æFAITA_r40.csv')


step = np.arange(10,  4200, 10)


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


m = max(t_30[len(t_30) - 1], t_10[len(t_10) - 1],
    t_20[len(t_20) - 1], t_40[len(t_40) - 1], t_50[len(t_50) - 1])
t_30 += [50 for i in range(len(step) - len(t_30))]
t_20 += [50 for i in range(len(step) - len(t_20))]
t_10 += [50 for i in range(len(step) - len(t_10))]
t_40 += [50 for i in range(len(step) - len(t_40))]
t_50 += [50 for i in range(len(step) - len(t_50))]
t_70 += [50 for i in range(len(step) - len(t_70))]


fig, total_plot = plt.subplots()
total_plot.plot(step, [t if not t == None else None for t in t_30],
                label="P = 0.3")
total_plot.plot(step, [t if not t == None else None for t in t_20],
                label="P = 0.1")
total_plot.plot(step, [t if not t == None else None for t in t_10],
                label="P = 0.05")
total_plot.plot(step, [t if not t == None else None for t in t_40],
                label="P = 0.5")
total_plot.plot(step, [t if not t == None else None for t in t_50],
                label="P = 0.7")
total_plot.plot(step, [t if not t == None else None for t in t_70],
                label="P = 0")

total_plot.set(xlabel='simulation step', ylabel='Task completion')
total_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
plt.show()
