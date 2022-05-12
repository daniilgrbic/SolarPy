import math

from solarsystem import SolarSystem
import pygame
import numpy as np
import numpy.typing as npt
from geometry import *


class Renderer:
    def __init__(self):
        self.font = pygame.font.SysFont(name="Consolas", size=16, bold=True)
        self.eye = np.array([0, 0, -10])
        self.vertical_axis = np.array([0, 0, -1, 0])
        self.mvp = None
        self.alpha = math.pi * 1.5
        self.raised = np.pi / 2 - 0.02
        self.calc_eye_position()
        self.calc_matrices()

    def handle_input(self):
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_DOWN] and self.raised > 0.02:
            self.raised -= 0.02
        if pressed[pygame.K_UP] and self.raised < math.pi * 0.5 - 0.02:
            self.raised += 0.02

        if any([pressed[pygame.K_DOWN], pressed[pygame.K_UP]]):
            self.calc_eye_position()
            self.calc_matrices()

    def calc_eye_position(self):
        x, y = math.cos(self.alpha), math.sin(self.alpha)
        z = math.sin(self.raised)
        x *= math.cos(self.raised)
        y *= math.cos(self.raised)
        self.eye = np.array([x, y, -z]) * 10

    def calc_matrices(self):
        projection_matrix = get_perspective(
            fov_y=np.radians(30),
            aspect=pygame.display.get_surface().get_width() / pygame.display.get_surface().get_height(),
            z_near=0.1,
            z_far=100
        )
        view_matrix = look_at(
            eye=self.eye,
            center=np.zeros(3),
            up=np.array([0, 1, 0])
        )
        self.mvp = np.matmul(view_matrix, projection_matrix)

    def render(self, system: SolarSystem) -> pygame.Surface:
        width, height = pygame.display.get_surface().get_size()
        surface = pygame.Surface(size=(width, height))
        surface.fill(pygame.Color("black"))

        self.render_grid(surface)

        # Draw the Sun
        pygame.draw.circle(
            surface=surface,
            color=pygame.Color("yellow"),
            center=(width // 2, height // 2),
            radius=15)
        surface.blit(
            source=(rendered_text := self.font.render("Sun", True, pygame.Color("yellow"))),
            dest=(width // 2 - rendered_text.get_width() // 2, height // 2 + 16)
        )

        # Draw traces
        for planet in system.planets:
            pygame.draw.lines(
                surface=surface,
                color=pygame.Color("darkgray"),
                closed=False,
                points=[
                    (perspective_divide(np.matmul(pt, self.mvp)) + 1) * np.array([width // 2, height // 2])
                    for pt in planet.trace
                ],
                width=2
            )

        # Draw planets
        for planet in system.planets:
            position = (perspective_divide(np.matmul(planet.position, self.mvp)) + 1) \
                       * np.array([width // 2, height // 2])
            pygame.draw.circle(
                surface=surface,
                color=pygame.Color("white"),
                center=position,
                radius=8)
            surface.blit(
                source=(rendered_text := self.font.render(planet.name, True, pygame.Color("yellow"))),
                dest=(
                    position[0] - rendered_text.get_width() // 2, position[1] + 9)
            )

        return surface

    def render_grid(self, surface: pygame.Surface):
        width, height = surface.get_size()
        for i in range(-10, 11, 1):
            start = (perspective_divide(np.matmul(np.array([-10, i, 0, 1]), self.mvp)) + 1) \
                    * np.array([width // 2, height // 2])
            end = (perspective_divide(np.matmul(np.array([10, i, 0, 1]), self.mvp)) + 1) \
                  * np.array([width // 2, height // 2])
            pygame.draw.line(
                surface=surface,
                color=pygame.Color(165, 42, 42),
                start_pos=start,
                end_pos=end
            )
            start = (perspective_divide(np.matmul(np.array([i, -10, 0, 1]), self.mvp)) + 1) \
                    * np.array([width // 2, height // 2])
            end = (perspective_divide(np.matmul(np.array([i, 10, 0, 1]), self.mvp)) + 1) \
                  * np.array([width // 2, height // 2])
            pygame.draw.line(
                surface=surface,
                color=pygame.Color(61, 145, 64),
                start_pos=start,
                end_pos=end
            )
