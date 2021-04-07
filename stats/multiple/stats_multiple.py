import matplotlib
import matplotlib.pyplot as plt
import numpy as np

gta = open('./stats20_GTA.csv')
gata = open('./stats20_GATA.csv')
aita = open('./stats20_AITA.csv')


step = np.arange(10, 3010, 10)


def read(file):
    distance = []
    total = []
    robots_n_task_switch = None
    for line in file:
        arr = [int(value) for value in line.split(";")[:12]]

        distance.append(arr[10])
        total.append(arr[11])

        arr = sorted([eval(e) for e in line.split(";")[12:]])

        robots_n_task_switch = [e[1] for e in arr]
 
    return distance, total, robots_n_task_switch


d_gta, t_gta, n_gta = read(gta)
d_gata, t_gata, n_gata = read(gata)
d_aita, t_aita, n_aita = read(aita)

# max_x_len = max(max(len(d_gta), len(d_gata)), len(d_aita))


d_gta += [d_gta[len(d_gta) - 1] for i in range(len(step) - len(d_gta))]
d_gata += [d_gata[len(d_gata) - 1] for i in range(len(step) - len(d_gata))]
d_aita += [d_aita[len(d_aita) - 1] for i in range(len(step) - len(d_aita))]

fig, distance_plot = plt.subplots()
distance_plot.plot(step, d_gta, label="Greedy TA distance")
distance_plot.plot(step, d_gata, label="Ameliored Greedy TA distance")
distance_plot.plot(step, d_aita, label="Ant inspired TA distance")
distance_plot.set(xlabel='simulation step', ylabel='Covered distance (cm)')
distance_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


t_gta += [20 for i in range(len(step) - len(t_gta))]
t_gata += [20 for i in range(len(step) - len(t_gata))]
t_aita += [20 for i in range(len(step) - len(t_aita))]


fig, total_plot = plt.subplots()
total_plot.plot(step, [t/20 if not t == None else None for t in t_gta],
                label="Greedy TA total processed resources")
total_plot.plot(step, [t/20 if not t == None else None for t in t_gata],
                label="Ameliored Greedy total processed resources")
total_plot.plot(step, [t/20 if not t == None else None for t in t_aita],
                label="Ant inspired TA total processed resources")
total_plot.set(xlabel='simulation step', ylabel='Task completion')
total_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


fig, robot_n_task_plot = plt.subplots()
robot_n_task_plot.plot(range(1, len(n_gta) +2), n_gta,
                       label="GTA Number of task switch for a robot over the total period")
robot_n_task_plot.plot(range(1, len(n_gata) +2), n_gata,
                       label="GATA Number of task switch for a robot over the total period")
robot_n_task_plot.plot(range(1, len(n_aita) +2), n_aita,
                       label="AITA Number of task switch for a robot over the total period")
robot_n_task_plot.set(xlabel='Robot Number', ylabel='Number of task switch')

robot_n_task_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


plt.show()
