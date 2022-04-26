import math
import numpy as np
import scipy as sp
import pygame
from solarsystem import SolarSystem
from geometry import *

import time


def mainloop():
    pygame.init()
    h = w = 800
    window = pygame.display.set_mode((w, h), pygame.RESIZABLE)
    pygame.display.set_caption("Solar Simulation")
    clock = pygame.time.Clock()
    scale = 150
    font = pygame.font.SysFont(name="Consolas", size=16)

    up = np.array([0, -1, 0])
    # eye = np.array([0, 0, -1])
    model_matrix = np.identity(4)
    projection_matrix = get_perspective(45, w / h, 0.1, 100)
    view_matrix = look_at(
        eye=np.array([0, 0, -1]),
        center=np.zeros(3),
        up=up
    )
    mvp = np.matmul(projection_matrix, view_matrix)

    vertical_rotation = 0
    horizontal_rotation = 0

    moved = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.VIDEORESIZE:
                w, h = pygame.display.get_surface().get_size()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    scale *= 1.1
                if event.button == 5 and scale > 1:
                    scale /= 1.1

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_UP]:
            vertical_rotation -= 0.03
            moved = True
        if pressed[pygame.K_DOWN]:
            vertical_rotation += 0.03
            moved = True
        if pressed[pygame.K_LEFT]:
            horizontal_rotation += 0.03
            moved = True
        if pressed[pygame.K_RIGHT]:
            horizontal_rotation -= 0.03
            moved = True

        if moved:
            moved = False
            vertical_rotation_matrix = get_rotation_matrix(
                np.array([1, 0, 0]),
                vertical_rotation
            )
            eye = np.matmul(np.array([0, 0, -1, 1]), vertical_rotation_matrix)
            horizontal_rotation_matrix = get_rotation_matrix(
                up,
                horizontal_rotation
            )
            eye = np.matmul(eye, horizontal_rotation_matrix)[:3]
            view_matrix = look_at(eye, np.zeros(3), up)
            # model_matrix = horizontal_rotation_matrix
            # model_matrix = np.matmul(vertical_rotation_matrix, model_matrix)
            mvp = np.matmul(projection_matrix, view_matrix)
            mvp = np.matmul(mvp, model_matrix)

        """
        start_time = time.time()
        for i in range(10000):
            system.update()
        print("--- %s seconds ---" % (time.time() - start_time))
        """
        system.update()

        window.fill(pygame.Color("black"))

        pygame.draw.circle(
            surface=window,
            color=pygame.Color("yellow"),
            center=(system.sun.position[0] * scale + w // 2, system.sun.position[1] * scale + h // 2),
            radius=15)
        window.blit(
            font.render("Sun", True, pygame.Color("yellow")),
            (system.sun.position[0] * scale + w // 2, system.sun.position[1] * scale + h // 2 + 16)
        )

        # print([np.matmul(mvp, pt * scale)[:2] for pt in system.planets[0].trace])

        for planet in system.planets:
            pygame.draw.lines(
                surface=window,
                color=pygame.Color("gray"),
                closed=False,
                points=[np.matmul(mvp, pt * scale)[:2] + np.array([w // 2, h // 2]) for pt in planet.trace],
                width=2
            )

        for planet in system.planets:
            position = np.matmul(mvp, planet.position)
            pygame.draw.circle(
                surface=window,
                color=pygame.Color("white"),
                center=(position[0] * scale + w // 2, position[1] * scale + h // 2),
                radius=8)
            window.blit(
                font.render(planet.name, True, pygame.Color("yellow")),
                (position[0] * scale + w // 2, position[1] * scale + h // 2 + 9)
            )

        pygame.display.flip()
        clock.tick(40)


if __name__ == '__main__':
    system = SolarSystem("2017-04-21")
    mainloop()
