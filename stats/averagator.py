# big boilderplate file
from os import walk

directory = './EXP/ALONE/EXP1/'
_, _, filenames = next(walk(directory))
filenames = [directory+f for f in filenames if 'csv' in f]

# All the array should be of the same lenght


def read(file):
    distance = []
    total = []
    robots_n_task_switch = None

    foraging_need = []
    foraging_assigned = []

    nest_processing_need = []
    nest_processing_assigned = []

    foraging_not_working = []
    nest_processing_not_working = []
    cleaning_not_working = []

    cleaning_need = []
    cleaning_assigned = []

    for line in file:
        arr = [float(value) for value in line.split(";")[:12]]

        foraging_need.append(arr[3])
        foraging_assigned.append(arr[1])
        foraging_not_working.append(arr[2])

        nest_processing_need.append(arr[6])
        nest_processing_assigned.append(arr[4])
        nest_processing_not_working.append(arr[5])

        cleaning_need.append(arr[9])
        cleaning_assigned.append(arr[7])
        cleaning_not_working.append(arr[8])

        distance.append(arr[10])
        total.append(arr[11])

        # ! this has to be complient with if i remove robots .. maybe use a dictionnary with robot's number a key

        robots_n_task_switch = sorted([list(eval(e))
                                       for e in line.split(";")[12:-1]])

    return [distance, total, robots_n_task_switch, foraging_need, foraging_assigned, nest_processing_need, nest_processing_assigned, cleaning_need, cleaning_assigned, foraging_not_working, nest_processing_not_working, cleaning_not_working]


all = []
for filename in filenames:
    all.append(read(open(filename)))


def process(a):

    size = max([len(e) for e in a])

    for e in a:
        e += [e[len(e) - 1]
              for i in range(size - len(e))]

    temp = a.pop(0)

    for i, _ in enumerate(temp):
        temp[i] += sum([e[i] for e in a])
        temp[i] /= len(a) + 1

    return temp


avg_distance = process([a[0] for a in all])
avg_total = process([a[1] for a in all])

avg_switch = [a[2] for a in all]

base = avg_switch.pop(0)

for i, _ in enumerate(base):
    base[i][1] += sum([e[i][1] for e in avg_switch])
    base[i][1] /= len(avg_switch) + 1

avg_switch = base


foraging_need = process([a[3] for a in all])
avg_foraging_assigned = process([a[4] for a in all])
avg_nest_processing_need = process([a[5] for a in all])
avg_nest_processing_assigned = process([a[6] for a in all])
avg_cleaning_need = process([a[7] for a in all])
avg_cleaning_assigned = process([a[8] for a in all])
avg_foraging_not_working = process([a[9] for a in all])
avg_nest_processing_not_working = process([a[10] for a in all])
avg_cleaning_not_working = process([a[11] for a in all])


txt = ""
for r in avg_switch:
    txt += ";" + str(r)

file = open('avged_file.csv', 'w+')
for i in range(len(avg_distance)):
    file.write(str((i + 1) * 10) + ";" +
               str(avg_foraging_assigned[i]) + ";" +
               str(avg_foraging_not_working[i]) + ";" +
               str(foraging_need[i]) + ";" +
               str(avg_nest_processing_assigned[i]) + ";" +
               str(avg_nest_processing_not_working[i]) + ";" +
               str(avg_nest_processing_need[i]) + ";" +
               str(avg_cleaning_assigned[i]) + ";" +
               str(avg_cleaning_not_working[i]) + ";" +
               str(avg_cleaning_need[i]) + ";" +
               str(avg_distance[i]) + ";" +
               str(avg_total[i]) + txt + "\n")


file.close()
