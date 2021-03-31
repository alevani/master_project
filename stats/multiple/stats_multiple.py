import matplotlib
import matplotlib.pyplot as plt
import numpy as np

aita = open('../£AITA3_stats.csv')
faita = open('../£FAITA3_stats.csv')
gta = open('../£GTA3_stats.csv')
rnd = open('../£RND3_stats.csv')
psi = open('../£PSI3_stats.csv')


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
d_gta, t_gta, n_gta = read(gta, 3)
d_faita, t_faita, n_faita = read(faita, 3)
d_aita, t_aita, n_aita = read(aita, 6)
d_rnd, t_rnd, n_rnd = read(rnd)
d_psi, t_psi, n_psi = read(psi, 3)


d_gta += [d_gta[len(d_gta) - 1] for i in range(len(step) - len(d_gta))]
d_faita += [d_faita[len(d_faita) - 1] for i in range(len(step) - len(d_faita))]
d_aita += [d_aita[len(d_aita) - 1] for i in range(len(step) - len(d_aita))]
d_rnd += [d_rnd[len(d_rnd) - 1] for i in range(len(step) - len(d_rnd))]
d_psi += [d_psi[len(d_psi) - 1] for i in range(len(step) - len(d_psi))]

fig, distance_plot = plt.subplots()
distance_plot.plot(step, d_gta, label="GTA distance")
distance_plot.plot(step, d_faita, label="FAITA distance")
distance_plot.plot(step, d_aita, label="AITA distance")
distance_plot.plot(step, d_rnd, label="RND distance")
distance_plot.plot(step, d_psi, label="PSI distance")
distance_plot.set(xlabel='simulation step', ylabel='Covered distance (cm)')
distance_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

m = max(t_gta[len(t_gta) -1 ],t_aita[len(t_aita) -1 ],t_faita[len(t_faita) -1 ],t_rnd[len(t_rnd) -1 ],t_psi[len(t_psi) -1 ])
t_gta += [None for i in range(len(step) - len(t_gta))]
t_faita += [None for i in range(len(step) - len(t_faita))]
t_aita += [None for i in range(len(step) - len(t_aita))]
t_rnd += [None for i in range(len(step) - len(t_rnd))]
t_psi += [None for i in range(len(step) - len(t_psi))]



fig, total_plot = plt.subplots()
total_plot.plot(step, [t if not t == None else None for t in t_gta],
                label="GTA processed resources")
total_plot.plot(step, [t if not t == None else None for t in t_faita],
                label="FAITA total processed resources")
total_plot.plot(step, [t if not t == None else None for t in t_aita],
                label="AITA total processed resources")
total_plot.plot(step, [t if not t == None else None for t in t_rnd],
                label="RND total processed resources")
total_plot.plot(step, [t if not t == None else None for t in t_psi],
                label="PSI processed resources")
total_plot.set(xlabel='simulation step', ylabel='Task completion')
total_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


fig, robot_n_task_plot = plt.subplots()
robot_n_task_plot.plot(range(1, len(n_gta) + 1), n_gta,
                       label="GTA Number of task switch for a robot over the total period")
robot_n_task_plot.plot(range(1, len(n_faita) + 1), n_faita,
                       label="FAITA Number of task switch for a robot over the total period")
robot_n_task_plot.plot(range(1, len(n_aita) + 1), n_aita,
                       label="AITA Number of task switch for a robot over the total period")
robot_n_task_plot.plot(range(1, len(n_rnd) + 1), n_rnd,
                       label="RND Number of task switch for a robot over the total period")
robot_n_task_plot.plot(range(1, len(n_psi) + 1), n_psi,
                       label="PSI Number of task switch for a robot over the total period")
robot_n_task_plot.set(xlabel='Robot Number', ylabel='Number of task switch')

robot_n_task_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


plt.show()
