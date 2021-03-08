# big boilderplate file
from os import walk

directory = './EXP/ALONE/EXP1/'
_, _, filenames = next(walk(directory))
filenames = [directory+f for f in filenames if 'csv' in f]


def read(file):
    distance = []
    total = []
    robots_n_task_switch = None
    for line in file:
        arr = [int(value) for value in line.split(";")[:12]]

        distance.append(arr[10])
        total.append(arr[11])

        arr = sorted([eval(e) for e in line.split(";")[12:-1]])

        # this has to be adaptive for EXP3
        robots_n_task_switch = [e[1] for e in arr]

    return distance, total, robots_n_task_switch


distance1, total1, switch1 = read(open(filenames[0]))
distance2, total2, switch2 = read(open(filenames[1]))
distance3, total3, switch3 = read(open(filenames[2]))
distance4, total4, switch4 = read(open(filenames[3]))
distance5, total5, switch5 = read(open(filenames[4]))

size = max(len(distance1), len(distance2), len(
    distance3), len(distance4), len(distance5))

distance1 += [distance1[len(distance1) - 1]
              for i in range(size - len(distance1))]
distance2 += [distance2[len(distance2) - 1]
              for i in range(size - len(distance2))]
distance3 += [distance3[len(distance3) - 1]
              for i in range(size - len(distance3))]
distance4 += [distance4[len(distance4) - 1]
              for i in range(size - len(distance4))]
distance5 += [distance5[len(distance5) - 1]
              for i in range(size - len(distance5))]

for i, _ in enumerate(distance1):
    distance1[i] += distance2[i] + distance3[i] + distance4[i] + distance5[i]
    distance1[i] /= 5

size = max(len(total1), len(total2), len(
    total3), len(total4), len(total5))

total1 += [total1[len(total1) - 1]
           for i in range(size - len(total1))]
total2 += [total2[len(total2) - 1]
           for i in range(size - len(total2))]
total3 += [total3[len(total3) - 1]
           for i in range(size - len(total3))]
total4 += [total4[len(total4) - 1]
           for i in range(size - len(total4))]
total5 += [total5[len(total5) - 1]
           for i in range(size - len(total5))]

for i, _ in enumerate(total1):
    total1[i] += total2[i] + total3[i] + total4[i] + total5[i]
    total1[i] /= 5


size = max(len(switch1), len(switch2), len(
    switch3), len(switch4), len(switch5))

switch1 += [switch1[len(switch1) - 1]
            for i in range(size - len(switch1))]
switch2 += [switch2[len(switch2) - 1]
            for i in range(size - len(switch2))]
switch3 += [switch3[len(switch3) - 1]
            for i in range(size - len(switch3))]
switch4 += [switch4[len(switch4) - 1]
            for i in range(size - len(switch4))]
switch5 += [switch5[len(switch5) - 1]
            for i in range(size - len(switch5))]

for i, _ in enumerate(switch1):
    switch1[i] += switch2[i] + switch3[i] + switch4[i] + switch5[i]
    switch1[i] /= 5

print(switch1)
