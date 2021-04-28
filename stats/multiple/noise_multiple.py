import matplotlib
import matplotlib.pyplot as plt
import numpy as np

f10 = open(
    '../0FAITA_EXP_HARD_NOISE/EXP1/0/0.csv')
f20 = open(
    '../0FAITA_EXP_HARD_NOISE/EXP1/0.1/0.1.csv')
f30 = open(
    '../0FAITA_EXP_HARD_NOISE/EXP1/0.3/0.3.csv')
f40 = open(
    '../0FAITA_EXP_HARD_NOISE/EXP1/0.5/0.5.csv')
f50 = open(
    '../0FAITA_EXP_HARD_NOISE/EXP1/0.7/0.7.csv')
f70 = open(
    '../0FAITA_EXP_HARD_NOISE/EXP1/0.99/0.99.csv')


step = np.arange(10,  12000, 10)

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
        error[len(error) -1 ] += abs(arr[7]- arr[8])
        error[len(error) -1 ] += abs(arr[11]- arr[12])

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

print(len(n_70))

m = max(t_30[len(t_30) - 1], t_10[len(t_10) - 1],
    t_20[len(t_20) - 1], t_40[len(t_40) - 1], t_50[len(t_50) - 1])

t_30 += [150 for i in range(len(step) - len(t_30))]
t_20 += [150 for i in range(len(step) - len(t_20))]
t_10 += [150 for i in range(len(step) - len(t_10))]
t_40 += [150 for i in range(len(step) - len(t_40))]
t_50 += [150 for i in range(len(step) - len(t_50))]
t_70 += [150 for i in range(len(step) - len(t_70))]


fig, total_plot = plt.subplots()
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_10],
                label="P = 0")
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_20],
                label="P = 0.1")
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_30],
                label="P = 0.3")
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_40],
                label="P = 0.5")
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_50],
                label="P = 0.7")
total_plot.plot(step, [t/1.5 if not t == None else None for t in t_70],
                label="P = 0.99")

total_plot.set(xlabel='simulation step', ylabel='Task completion rate (%)')
total_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
print("---DIST---")


e_30 += [None for i in range(len(step) - len(e_30))]
e_20 += [None for i in range(len(step) - len(e_20))]
e_10 += [None for i in range(len(step) - len(e_10))]
e_40 += [None for i in range(len(step) - len(e_40))]
e_50 += [None for i in range(len(step) - len(e_50))]
e_70 += [None for i in range(len(step) - len(e_70))]

print("---ERROR MEAN---")
print("10: ", mean(e_10))
print("20: ", mean(e_20))
print("30: ", mean(e_30))
print("40: ", mean(e_40))
print("50: ", mean(e_50))
print("70: ", mean(e_70))


fig, error_ = plt.subplots()
error_.plot(step,e_10,
                label="P = 0",linewidth=1)
# error_.plot(step,e_20,
#                 label="P = 0.1")
error_.plot(step,e_30,
                label="P = 0.3",linewidth=1)
# error_.plot(step,e_40,
#                 label="P = 1")
# error_.plot(step,e_50,
#                 label="P = 0.7")
#error_.plot(step,e_40,
 #               label="P = 0.5",linewidth=1)
error_.plot(step,e_50,
                label="P = 0.7",linewidth=1)
error_.plot(step,e_70,
                label="P = 0.99",linewidth=1)

error_.set(xlabel='simulation step', ylabel='Swarm perception error (in resources)')
error_.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)





fig, robot_n_task_plot = plt.subplots()
robot_n_task_plot.plot(range(1,41), n_10,
                       label="P = 0")
robot_n_task_plot.plot(range(1,41), n_30,
                       label="P = 0.3")
robot_n_task_plot.plot(range(1,41), n_50,
                       label="P = 0.7")
robot_n_task_plot.plot(range(1,41), n_70,
                       label="P = 0.99")

robot_n_task_plot.set(xlabel='Robot ID', ylabel='Number of task switch')

robot_n_task_plot.grid()

plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)




plt.show()
