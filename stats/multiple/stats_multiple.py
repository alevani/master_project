import matplotlib
import matplotlib.pyplot as plt
import numpy as np

gta = open('../GTA_50:7/EXP1/£GTA_r40/£GTA_r40.csv')
psi = open('../PSI_50:7/EXP1/£PSI_r40/£PSI_r40.csv')
CAITA = open('../CAITA_50:7/EXP1/£CAITA_r40/£CAITA_r40.csv')
DAITA = open('../DAITA_50:7/EXP1/£DAITA_r40/£DAITA_r40.csv')
rnd = open('../RND_50:7/EXP1/£RND_r40/£RND_r40.csv')

step = np.arange(10,  12600, 10)

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
    print(file)
    distance = []
    total = []
    robots_n_task_switch = None
    sq = []
    for line in file:
        arr = [float(value) for value in line.split(";")[:12 + shift]]
        
        if shift == 6:
          sq.append((arr[1] - arr[5])**2)
        else:
          sq.append((arr[1] - arr[3])**2)

        if shift == 3:
          sq[len(sq) -1] += (arr[5] - arr[7])**2 # 5 et 7 DAITA PSI GTA
          sq[len(sq) -1] += (arr[9] - arr[11])**2 # 9 et 11 DAITA PSI GTA
        elif shift == 6:
          sq[len(sq) -1] += (arr[6] - arr[10])**2 # CAITA
          sq[len(sq) -1] += (arr[11] - arr[15])**2 # CAITA
        else:
          sq[len(sq) -1] += (arr[4] - arr[6])**2 # RND
          sq[len(sq) -1] += (arr[9] - arr[7])**2 # RND
        
        distance.append(arr[10 + shift])
        total.append(arr[11 + shift])

        arr = sorted([eval(e) for e in line.split(";")[12 + shift:]])

        robots_n_task_switch = [e[1] for e in arr]

    return distance, total, robots_n_task_switch, sq


# Shifts are here because file may have different formats
d_gta, t_gta, n_gta, sq_gta = read(gta, 3)
d_DAITA, t_DAITA, n_DAITA, sq_DAITA = read(DAITA, 3)
d_CAITA, t_CAITA, n_CAITA, sq_CAITA = read(CAITA, 6)
d_rnd, t_rnd, n_rnd, sq_rnd = read(rnd)
d_psi, t_psi, n_psi, sq_psi = read(psi, 3)


d_gta += [d_gta[len(d_gta) - 1] for i in range(len(step) - len(d_gta))]
d_DAITA += [d_DAITA[len(d_DAITA) - 1] for i in range(len(step) - len(d_DAITA))]
d_CAITA += [d_CAITA[len(d_CAITA) - 1] for i in range(len(step) - len(d_CAITA))]
d_rnd += [d_rnd[len(d_rnd) - 1] for i in range(len(step) - len(d_rnd))]
d_psi += [d_psi[len(d_psi) - 1] for i in range(len(step) - len(d_psi))]

fig, distance_plot = plt.subplots()
print("---DIST---")
print("GTA: ", int(d_gta[len(d_gta) - 1]))
print("psi: ", int(d_psi[len(d_psi) - 1]))
print("DAITA: ", int(d_DAITA[len(d_DAITA) - 1]))
print("CAITA: ", int(d_CAITA[len(d_CAITA) - 1]))
print("RND: ", int(d_rnd[len(d_rnd) - 1]))
print("---N SWTICH MEAN---")
print("GTA: ", int(mean(n_gta)))
print("psi: ", int(mean(n_psi)))
print("DAITA: ", int(mean(n_DAITA)))
print("CAITA: ", int(mean(n_CAITA)))
print("RND: ", int(mean(n_rnd)))
print("---LEN---")
distance_plot.plot(step, d_gta, label="GTA")
distance_plot.plot(step, d_DAITA, label="DAITA")
distance_plot.plot(step, d_CAITA, label="CAITA")
distance_plot.plot(step, d_rnd, label="RND")
distance_plot.plot(step, d_psi, label="PSI")
distance_plot.set(xlabel='simulation step', ylabel='Covered distance (m)')
distance_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

print("GTA: ", int(len(t_gta)))
print("psi: ", int(len(t_psi)))
print("DAITA: ", int(len(t_DAITA)))
print("CAITA: ", int(len(t_CAITA)))
print("RND: ", int(len(t_rnd)))
print("---SQ---")
t_gta += [150 for i in range(len(step) - len(t_gta))]
t_DAITA += [150 for i in range(len(step) - len(t_DAITA))]
t_CAITA += [150 for i in range(len(step) - len(t_CAITA))]
t_rnd += [150 for i in range(len(step) - len(t_rnd))]
t_psi += [150 for i in range(len(step) - len(t_psi))]


fig, total_plot = plt.subplots()
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_gta],
                label="GTA")
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_DAITA],
                label="DAITA")
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_CAITA],
                label="CAITA")
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_rnd],
                label="RND")
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_psi],
                label="PSI")
total_plot.set(xlabel='simulation step', ylabel='Task completion rate (%)')
total_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)






fig, robot_n_task_plot = plt.subplots()
robot_n_task_plot.plot(range(1, 41), n_gta,
                       label="GTA Number of task switch for a robot over the total period")
robot_n_task_plot.plot(range(1, 41), n_DAITA,
                       label="DAITA Number of task switch for a robot over the total period")
robot_n_task_plot.plot(range(1, 41), n_CAITA,
                       label="CAITA Number of task switch for a robot over the total period")
robot_n_task_plot.plot(range(1, 41), n_rnd,
                       label="RND Number of task switch for a robot over the total period")

robot_n_task_plot.set(xlabel='Robot Number', ylabel='Number of task switch')

robot_n_task_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
ax0 = robot_n_task_plot.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:gray'
ax0.set_ylabel('PSI Number of task switch for a robot over the total period', color=color)  # we already handled the x-label with ax1
ax0.plot(range(1, 41), n_psi, color=color,alpha=0.3)
ax0.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)



sq_gta += [None for i in range(len(step) - len(sq_gta))]
sq_DAITA += [None for i in range(len(step) - len(sq_DAITA))]
sq_CAITA += [None for i in range(len(step) - len(sq_CAITA))]
sq_rnd += [None for i in range(len(step) - len(sq_rnd))]
sq_psi += [None for i in range(len(step) - len(sq_psi))]

print("GTA: ", int(mean(sq_gta)))
print("psi: ", int(mean(sq_psi)))
print("DAITA: ", int(mean(sq_DAITA)))
print("CAITA: ", int(mean(sq_CAITA)))
print("RND: ", int(mean(sq_rnd)))


fig, sq_ = plt.subplots()
sq_.plot(step, sq_gta,
                label="GTA")
sq_.plot(step, sq_DAITA,
                label="DAITA")
sq_.plot(step, sq_CAITA,
                label="CAITA")
# sq_.plot(step, sq_rnd,
#                 label="RND")
sq_.plot(step, sq_psi,
                label="PSI")
sq_.set(xlabel='simulation step', ylabel='squared error for the combined tasks')
sq_.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
ax2 = sq_.twinx()  # instantiate a second axes that shares the same x-axis

color = 'tab:gray'
ax2.set_ylabel('RND squared error for the combined tasks', color=color)  # we already handled the x-label with ax1
ax2.plot(step, sq_rnd, color=color,alpha=0.3)
ax2.tick_params(axis='y', labelcolor=color)

fig.tight_layout()  # otherwise the right y-label is slightly clipped




plt.show()
