import globals


def decay_check():
    # for i, point in enumerate(PHEROMONES_PATH):
    #     if point == 0:
    #         print("REMOVE ME IF THIS EVER HAPPEN")  #  -> yes .
    #         break

    #     point.decay_time -= 1

    #     x = int(point.position.x * 100) + int(globals.W * 100/2)
    #     y = int(point.position.y * 100) + int(globals.H * 100/2)

    #     if point.decay_time <= 0:
    #         globals.PHEROMONES_MAP[x][y] = 0
    #         PHEROMONES_PATH.pop(i)

    for i, poi in enumerate(globals.POIs):
        poi.decay_time -= 1
        if poi.decay_time <= 0:
            globals.PHEROMONES_MAP[int(poi.position.x * 100) + int(
                globals.W * 100/2)][int(poi.position.y * 100) + int(globals.H * 100/2)] = 0
            poi.is_visible = False
