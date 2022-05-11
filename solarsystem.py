from retriever import load_data
import math
import numpy as np
import numpy.typing as npt

GRAVCONSTANT = 1.488e-34  # in units of AU^3 / (kg * day^2)
AU = 149597871

class Astrobject:
    def __init__(self, name: str, position: npt.NDArray[np.float], velocity: npt.NDArray[np.float]):
        self.name = name
        self.position = position
        self.velocity = velocity
        self.mass = 0
        self.trace = [np.array(position), np.array(position)]
        self.max_trace_len = 0

    def accelerate(self, planets, sun):
        a = np.array([0, 0, 0])
        objects = planets.copy()
        objects.append(sun)
        for object in objects:
            if object.name == self.name:
                continue
            dx = object.position[0:3] - self.position[0:3]
            dsq = dx[0]**2 + dx[1]**2 + dx[2]**2
            dr = math.sqrt(dsq)
            force = GRAVCONSTANT * object.mass / dsq
            a = a + dx[0:3] * (force / dr)
        return a

    def initial_derivative(self, planets, sun):
        a = self.accelerate(planets, sun)
        return Derivative(self.velocity[0:3], a)

    def next_derivative(self, planets, sun, derivative, dt):
        ao = Astrobject(self.name, self.position[0:3] + derivative.dx * dt, self.velocity[0:3] + derivative.dvx * dt)
        a = ao.accelerate(planets, sun)
        return Derivative(ao.velocity[0:3], a)

    def update_planet(self, planets, sun, dt):
        k1 = self.initial_derivative(planets, sun)
        k2 = self.next_derivative(planets, sun, k1, dt * 0.5)
        k3 = self.next_derivative(planets, sun, k2, dt * 0.5)
        k4 = self.next_derivative(planets, sun, k3, dt)
        kx = np.column_stack((k1.dx, k2.dx, k3.dx, k4.dx))
        kvx = np.column_stack((k1.dvx, k2.dvx, k3.dvx, k4.dvx))
        q = np.array([1/6, 1/3, 1/3, 1/6])
        dxdt = np.array([np.sum(kx[0] * q), np.sum(kx[1] * q), np.sum(kx[2] * q)])
        dvxdt = np.array([np.sum(kvx[0] * q), np.sum(kvx[1] * q), np.sum(kvx[2] * q)])
        self.position[0:3] += dxdt * dt
        self.velocity[0:3] += dvxdt * dt

    def update_trace(self):
        self.trace.append(np.array(self.position))
        if len(self.trace) > self.max_trace_len:
            self.trace.pop(0)

class Derivative:
    def __init__(self, dx, dvx):
        self.dx = dx
        self.dvx = dvx

class SolarSystem:
    def __init__(self, start_date="2022-01-01"):
        self.sun = Astrobject(name="Sun", position=np.array([0, 0, 0, 1]), velocity=np.zeros(0))
        self.sun.mass = 1.989e30
        self.planets: list[Astrobject] = []
        for planet in load_data(start_date):
            self.planets.append(Astrobject(
                name=planet["name"],
                position=np.array(planet["position"]+[1]),
                velocity=np.array(planet["velocity"]+[0])
            ))
        planet_mass = [0.33, 4.87, 6.043, 0.642, 1898.0, 568.0, 86.8, 102.0, 0.013]
        planet_trace = [57, 108, 150, 228, 780, 1430, 2877, 4510, 5830]
        for i in range (9):
            self.planets[i].mass = planet_mass[i] * (10**24)
            self.planets[i].max_trace_len = planet_trace[i]

    def update(self):
        dt = 1
        for planet in self.planets:
            planet.position += planet.velocity * dt
            acc = -2.959e-4 * planet.position / (np.sum(planet.position**2)-1)**1.5  # in units of AU/day^2
            #acc = -2.959e-4 * planet.position / np.sum(planet.position[:3] ** 2) ** (3. / 2)  # in units of AU/day^2
            acc[3] = 0
            planet.velocity += acc * dt
            planet.update_trace()

    def update1(self):
        """
        Runge Kutta method
        """
        dt = 1
        for planet in self.planets:
            planet.update_planet(self.planets, self.sun, dt)
            planet.update_trace()
