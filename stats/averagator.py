from os import walk

directory = './EXP/ALONE/EXP1/'
_, _, filenames = next(walk(directory))
filenames = [f for f in filenames if 'csv' in f]


all_file_distance = []
base = filenames.pop()

file = open(directory+base)

distance = []
for line in file:
    for line in file:
        arr = [int(value) for value in line.split(";")[:12]]
all_file_distance.append(distance)

for filename in filenames:

    # total = []
    # robots_n_task_switch = None
    file = open(directory+filename)
    for line in file:
        arr = [int(value) for value in line.split(";")[:12]]
        distance.append(arr[10])
        # total.append(arr[11])
    all_file_distance.append(distance)

print(all_file_distance)
