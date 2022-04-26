from solarsystem import SolarSystem
import pygame
import numpy as np
import numpy.typing as npt


class Renderer:
    def __init__(self, window: pygame.Surface, system: SolarSystem, mvp: npt.NDArray[float]):
        self.window = window
        self.trace = pygame.Surface(size=window.get_size())
        self.system = system
        self.mvp = mvp

    def update_perspective(self, mvp: npt.NDArray[float]):
        self.mvp = mvp

    def render(self):
        pass

    def render_planets(self):
        for planet in self.system.planets:
            pass