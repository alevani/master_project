import matplotlib
import matplotlib.pyplot as plt
import numpy as np

gta = open('../COVERED_GTA/EXP1/£GTA_r40/£GTA_r40.csv')
psi = open('../COVERED_PSI/EXP1/£PSI_r40/£PSI_r40.csv')
CAITA = open('../COVERED_CAITA/EXP1/£CAITA_r40/£CAITA_r40.csv')
DAITA = open('../COVERED_DAITA/EXP1/£DAITA_r40/£DAITA_r40.csv')
rnd = open('../COVERED_RND/EXP1/£RND_r40/£RND_r40.csv')

step = np.arange(10,  13000, 10)


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
distance_plot.plot(step, d_gta,linewidth=1, label="GTA")
distance_plot.plot(step, d_DAITA,linewidth=1, label="DAITA")
distance_plot.plot(step, d_CAITA,linewidth=1, label="CAITA")
distance_plot.plot(step, d_rnd,linewidth=1, label="RND")
distance_plot.plot(step, d_psi,linewidth=1, label="PSI")
distance_plot.set(xlabel='simulation step', ylabel='Covered distance (cm)')
distance_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

m = max(t_gta[len(t_gta) -1 ],t_CAITA[len(t_CAITA) -1 ],t_DAITA[len(t_DAITA) -1 ],t_rnd[len(t_rnd) -1 ],t_psi[len(t_psi) -1 ])
t_gta += [None for i in range(len(step) - len(t_gta))]
t_DAITA += [None for i in range(len(step) - len(t_DAITA))]
t_CAITA += [None for i in range(len(step) - len(t_CAITA))]
t_rnd += [None for i in range(len(step) - len(t_rnd))]
t_psi += [None for i in range(len(step) - len(t_psi))]



fig, total_plot = plt.subplots()
total_plot.plot(step, [t if not t == None else None for t in t_gta],
                label="GTA processed resources")
total_plot.plot(step, [t if not t == None else None for t in t_DAITA],
                label="DAITA total processed resources")
total_plot.plot(step, [t if not t == None else None for t in t_CAITA],
                label="CAITA total processed resources")
total_plot.plot(step, [t if not t == None else None for t in t_rnd],
                label="RND total processed resources")
total_plot.plot(step, [t if not t == None else None for t in t_psi],
                label="PSI processed resources")
total_plot.set(xlabel='simulation step', ylabel='Task completion')
total_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)

def mean(list):
  v = 0
  for i in list:
    v += i
  return v/len(list)

print("GTA: ", mean(sq_gta))
print("psi: ", mean(sq_psi))
print("DAITA: ", mean(sq_DAITA))
print("CAITA: ", mean(sq_CAITA))
print("RND: ", mean(sq_rnd))


# fig, sq_ = plt.subplots()
# sq_.plot(step, sq_gta,
#                 label="GTA")
# sq_.plot(step, sq_DAITA,
#                 label="DAITA")
# sq_.plot(step, sq_CAITA,
#                 label="CAITA")
# # sq_.plot(step, sq_rnd,
# #                 label="RND")
# sq_.plot(step, sq_psi,
#                 label="PSI")
# sq_.set(xlabel='simulation step', ylabel='squared error for the combined tasks')
# sq_.grid()

# plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
#            ncol=2, mode="expand", borderaxespad=0.)


fig, robot_n_task_plot = plt.subplots()
robot_n_task_plot.plot(range(1, 41), n_gta,linewidth=1,
                       label="GTA Number of task switch for a robot over the total period")
robot_n_task_plot.plot(range(1, 41), n_DAITA,linewidth=1,
                       label="DAITA Number of task switch for a robot over the total period")
robot_n_task_plot.plot(range(1, 41), n_CAITA,linewidth=1,
                       label="CAITA Number of task switch for a robot over the total period")
robot_n_task_plot.plot(range(1, 41), n_rnd,linewidth=1,
                       label="RND Number of task switch for a robot over the total period")
robot_n_task_plot.plot(range(1, 41), n_psi,linewidth=1,
                       label="PSI Number of task switch for a robot over the total period")
robot_n_task_plot.set(xlabel='Robot Number', ylabel='Number of task switch')

robot_n_task_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)


plt.show()
