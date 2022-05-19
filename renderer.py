from solarsystem import SolarSystem
from geometry import *
import pygame
import numpy as np


class Renderer:
    def __init__(self):
        self.font = pygame.font.SysFont(
            name="Consolas",
            size=16,
            bold=True
        )

        self.camera_position = np.array([0, 10, 10])
        self.camera_center = np.zeros(3)
        self.angle_vertical = 0
        self.angle_horizontal = 0
        self.scale = 1
        self.mvp = None
        self.calc_matrices()

    def handle_events(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEWHEEL and not pygame.mouse.get_pressed()[2]:
            self.scale = max(min(2.0, self.scale + event.y / 30), 0.05)
            self.calc_matrices()
        if event.type == pygame.WINDOWRESIZED:
            self.calc_matrices()

    def handle_input(self):
        mouse_movement = pygame.mouse.get_rel()
        mouse_pressed = pygame.mouse.get_pressed(5)

        if mouse_pressed[0] and mouse_movement != (0, 0):
            self.angle_vertical += mouse_movement[1] / 100
            if self.angle_vertical >= np.pi / 4:
                self.angle_vertical = np.pi / 4 - .00001
            elif self.angle_vertical < - np.pi * 3 / 4:
                self.angle_vertical = - np.pi * 3 / 4 + .00001
            self.camera_position = np.matmul(
                np.array([0, 10, 10]),
                rotate(
                    angle=self.angle_vertical,
                    axis=np.array([1, 0, 0])
                )
            )
            self.angle_horizontal += mouse_movement[0] / 100
            self.camera_position = np.matmul(
                self.camera_position,
                rotate(
                    angle=self.angle_horizontal,
                    axis=np.array([0, 0, -1])
                )
            )
            self.calc_matrices()

    def calc_matrices(self):
        projection_matrix = get_perspective(
            fov_y=np.radians(20),
            aspect=pygame.display.get_surface().get_width() / pygame.display.get_surface().get_height(),
            z_near=0.1,
            z_far=100
        )
        view_matrix = look_at(
            eye=self.camera_position,
            center=self.camera_center,
            up=np.array([0, 0, 1])
        )
        scale_matrix = scale(self.scale)
        self.mvp = np.matmul(
            scale_matrix,
            np.matmul(
                view_matrix,
                projection_matrix
            )
        )

    def render(self, system: SolarSystem, size=None) -> pygame.Surface:
        width, height = size if size else pygame.display.get_surface().get_size()
        surface = pygame.Surface(size=(width, height))
        surface.fill(pygame.Color("black"))

        self.render_grid(surface)

        # Draw traces
        for i, planet in enumerate(system.planets):
            pygame.draw.lines(
                surface=surface,
                color=pygame.Color("darkgray"),
                closed=False,
                points=[
                    (perspective_divide(np.matmul(pt, self.mvp)) + 1) * np.array([width // 2, height // 2])
                    for pt in [planet.trace[0]] + planet.trace[i * i + 1::i * i + 1] + [planet.trace[-1]]
                ],
                width=2
            )

        # Draw the Sun
        pygame.draw.circle(
            surface=surface,
            color=pygame.Color("yellow"),
            center=(width // 2, height // 2),
            radius=7 * self.scale + 3
        )
        surface.blit(
            source=(rendered_text := self.font.render("Sun", True, pygame.Color("yellow"))),
            dest=(width // 2 - rendered_text.get_width() // 2, height // 2 + 7 * self.scale + 3)
        )

        # Draw planets
        for planet in system.planets:
            position = ((perspective_divide(np.matmul(planet.position, self.mvp)) + 1)
                        * np.array([width // 2, height // 2]))
            pygame.draw.circle(
                surface=surface,
                color=pygame.Color("white"),
                center=position,
                radius=4 * self.scale + 3
            )
            surface.blit(
                source=(rendered_text := self.font.render(planet.name, True, pygame.Color("yellow"))),
                dest=(position[0] - rendered_text.get_width() // 2, position[1] + 4 * self.scale + 3)
            )

        return surface

    def render_grid(self, surface: pygame.Surface):
        width, height = surface.get_size()
        grid_size = min(int(4 / self.scale) + 2, 50)
        for i in range(-grid_size, grid_size + 1, 1):
            start = ((perspective_divide(np.matmul(np.array([-grid_size, i, 0, 1]), self.mvp)) + 1)
                     * np.array([width // 2, height // 2]))
            end = ((perspective_divide(np.matmul(np.array([grid_size, i, 0, 1]), self.mvp)) + 1)
                   * np.array([width // 2, height // 2]))
            pygame.draw.line(
                surface=surface,
                color=pygame.Color(165, 42, 42) if self.angle_vertical > - np.pi / 4 else pygame.Color(64, 64, 64),
                start_pos=start,
                end_pos=end
            )
            start = ((perspective_divide(np.matmul(np.array([i, -grid_size, 0, 1]), self.mvp)) + 1)
                     * np.array([width // 2, height // 2]))
            end = ((perspective_divide(np.matmul(np.array([i, grid_size, 0, 1]), self.mvp)) + 1)
                   * np.array([width // 2, height // 2]))
            pygame.draw.line(
                surface=surface,
                color=pygame.Color(61, 145, 64) if self.angle_vertical > - np.pi / 4 else pygame.Color(64, 64, 64),
                start_pos=start,
                end_pos=end
            )
