import pygame
from pygame.locals import *

WHITE = (255, 255, 255)
LIGHT_BLACK = (130, 130, 130)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
BLACK = (0, 0, 0)


class Visualizator:
    def __init__(self, screen, zoom_factor, W, H, margin_w, margin_h, robot_size):
        self.screen = screen
        self.zoom = zoom_factor
        self.arena_width, self.arena_height = int(
            W * 100 * self.zoom), int(H * 100 * self.zoom)
        self.MARGIN_W, self.MARGIN_H = 50, 50
        self.robot_size = robot_size

        DRAW_BOX = False
        DRAW_RAYS = False
        DRAW_PATH = False
        #! todo replace screen by self.screen

    def draw_arena(self, screen):
        screen.fill((0, 0, 0))
        pygame.draw.rect(screen, WHITE, (self.MARGIN_W, self.MARGIN_H,
                                         self.arena_width, self.arena_height))
        pygame.draw.circle(screen, BLACK, (scale(0, 0)), 2)

    def rotate_center(self, image, rect, angle):
        rot_img = pygame.transform.rotate(image, angle)
        rot_rect = rot_img.get_rect(center=rect.center)
        return rot_img, rot_rect

    def draw_robot(self, screen, pos, angle, virtual=True, size=ROBOT_SIZE, ROBOTCOLOR=LIGHT_BLACK):
        image = pygame.Surface((size, size), pygame.SRCALPHA, 32)

        rect = image.get_rect()
        x, y = pos
        rect.topleft = (x-size/2, y-size/2)
        poly = ((0, 0), (0, size), (size//2, size),
                (size, size//2), (size//2, 0))
        pygame.draw.polygon(image, ROBOTCOLOR, poly)

        a = math.degrees(angle)
        img, rect = rotate_center(image, rect, a)
        screen.blit(img, rect)

    def scale(self, x, y):
        '''
        transpose from particule filter coordinate system
        to pygame coordinate system
        '''
        tresh = 20
        nx = self.arena_width/2 + x*100*self.zoom + \
            self.MARGIN_W - self.robot_size/2 + tresh
        ny = self.arena_height/2 + y*100*self.zoom * -1 + \
            self.MARGIN_H - self.robot_size/2+tresh
        return nx, ny

    def draw(self, screen, point, cr, i, path):
        global DRAW_BOX, DRAW_RAYS

        x, y, a = point['rpos']['x'], point['rpos']['y'], point['rpos']['q']
        draw_robot(screen, scale(x, y), a, ROBOTCOLOR=cr)

        if DRAW_BOX:
            draw_box(screen, point['bpos'])

        if DRAW_RAYS:
            draw_rays(screen, point['spos'], point['sstate'])

        if DRAW_PATH:
            # for n in range(i - 50, i):  # ! Nice, it's like snake :D
            for n in range(i):
                draw_path(screen, path[n], cr)

    def draw_path(self, screen, path, color):
        pygame.draw.circle(screen, color, scale(path['x'], path['y']), 2)

    def draw_box(self, screen, box):
        for point in box:
            pygame.draw.circle(screen, RED, scale(point[0], point[1]), 5)

    def draw_rays(self, screen, rays, states):
        for i, ray in enumerate(rays):
            x_start, y_start = scale(ray[0][0], ray[0][1])
            x_end, y_end = scale(ray[1][0], ray[1][1])

            if states[i] == 0:
                color = GRAY
            elif states[i] == 1:
                color = RED

            pygame.draw.line(screen, color, (x_start, y_start),
                             (x_end, y_end))
