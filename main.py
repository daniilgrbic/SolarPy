import math
import numpy as np
import scipy as sp
import pygame
from solarsystem import SolarSystem
from geometry import *
from renderer import Renderer

import time


def mainloop():
    pygame.init()
    width, height = 800, 800
    window = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    pygame.display.set_caption("SolarPy")

    renderer = Renderer()

    for i in range(500):
        system.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.VIDEORESIZE:
                # renderer.window_resize()
                pass

        """
        start_time = time.time()
        for i in range(10000):
            system.update()
        print("--- %s seconds ---" % (time.time() - start_time))
        """
        system.update()

        renderer.handle_input()
        rendered_system = renderer.render(system)
        window.blit(rendered_system, (0, 0))

        pygame.display.flip()
        clock.tick(40)


if __name__ == '__main__':
    system = SolarSystem("2017-04-21")
    mainloop()
