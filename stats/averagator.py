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

        robots_n_task_switch = [e[1] for e in arr]

    return distance, total, robots_n_task_switch


distance1, _, _ = read(open(filenames[0]))
distance2, _, _ = read(open(filenames[1]))
distance3, _, _ = read(open(filenames[2]))
distance4, _, _ = read(open(filenames[3]))
distance5, _, _ = read(open(filenames[4]))

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

print(distance1)
