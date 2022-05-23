import constants
import numpy as np
import numpy.typing as npt
import datetime


class Astrobject:
    def __init__(self, name: str, position: npt.NDArray[float], velocity: npt.NDArray[float]):
        self.name = name
        self.position = position
        self.velocity = velocity
        self.mass = 0
        self.trace = [np.array(position), np.array(position)]
        self.max_trace_len = 0

    def accelerate(self, astro_objects):
        a = np.zeros(3)
        for ao in astro_objects:
            if ao.name == self.name or ao.name == 'sun':
                continue
            dx = ao.position[0:3] - self.position[0:3]
            dsq = np.sum(np.square(dx[0:3]))
            dr = np.sqrt(dsq)
            force = constants.GRAV_CONSTANT * ao.mass / dsq
            a = a + dx[0:3] * (force / dr)
        return a

    def initial_derivative(self, astro_objects):
        a = self.accelerate(astro_objects)
        return Derivative(self.velocity[0:3], a)

    def next_derivative(self, astro_objects, temp, derivative, dt):
        temp.position = self.position[0:3] + derivative.dx * dt
        temp.velocity = self.velocity[0:3] + derivative.dvx * dt
        a = temp.accelerate(astro_objects)
        return Derivative(temp.velocity[0:3], a)

    def update_planet(self, planets, sun, dt):
        temp = Astrobject(self.name, np.zeros(3), np.zeros(3))
        astro_objects = planets.copy()
        astro_objects.append(sun)
        k1 = self.initial_derivative(astro_objects)
        k2 = self.next_derivative(astro_objects, temp, k1, dt * 0.5)
        k3 = self.next_derivative(astro_objects, temp, k2, dt * 0.5)
        k4 = self.next_derivative(astro_objects, temp, k3, dt)
        kx = np.column_stack((k1.dx, k2.dx, k3.dx, k4.dx))
        kvx = np.column_stack((k1.dvx, k2.dvx, k3.dvx, k4.dvx))
        q = np.array([1 / 6, 1 / 3, 1 / 3, 1 / 6])
        dx_dt = np.array([np.sum(kx[0] * q), np.sum(kx[1] * q), np.sum(kx[2] * q)])
        dvx_dt = np.array([np.sum(kvx[0] * q), np.sum(kvx[1] * q), np.sum(kvx[2] * q)])
        self.position[0:3] += dx_dt * dt
        self.velocity[0:3] += dvx_dt * dt

    def update_trace(self):
        self.trace.append(np.array(self.position))
        if len(self.trace) > self.max_trace_len:
            self.trace.pop(0)


class Derivative:
    def __init__(self, dx, dvx):
        self.dx = dx
        self.dvx = dvx


class SolarSystem:
    def __init__(self, start_date, use_horizons=False):
        self.sun = Astrobject(name="Sun", position=np.array([0, 0, 0, 1]), velocity=np.zeros(4))
        self.sun.mass = constants.sun_mass
        self.planets: list[Astrobject] = []
        if use_horizons:
            import initial_state_astroquery
            planets = initial_state_astroquery.load_data(start_date)
        else:
            import initial_state
            planets = initial_state.load_data(start_date)
        for planet in planets:
            self.planets.append(Astrobject(
                name=planet["name"],
                position=np.array(planet["position"] + [1]),
                velocity=np.array(planet["velocity"] + [0])
            ))
        planet_trace = [88, 225, 366, 688, 11.9*366, 29.5*366, 84*366, 164.8*366, 247.7*366]
        for i in range(9):
            self.planets[i].mass = constants.planets_mass[i] * (10 ** 24)
            self.planets[i].max_trace_len = planet_trace[i] // max(1, i - 2)

        year, month, day = [int(i) for i in start_date.split("-")]
        self.start_date = datetime.datetime(year, month, day)
        self.date = datetime.datetime(year, month, day)

    def update_rk(self, dt=24):
        """ Update planet positions using Runge Kutta method """
        for i, planet in enumerate(self.planets):
            planet.update_planet(self.planets, self.sun, dt/24)
            if (self.date - self.start_date).days % max(1, i - 2) == 0 and (self.date - self.start_date).seconds == 0:
                planet.update_trace()
        self.date += datetime.timedelta(hours=dt)

    def get_date(self):
        return self.date.strftime("%Y-%m-%d (%Hh)")

    def dump_state(self):
        current_date = self.get_date()
        data = {
            "date": current_date,
            "planets": [{
                "name": planet.name,
                "position": list(planet.position[:3]),
                "velocity": list(planet.velocity[:3])
            } for planet in self.planets]
        }
        import os
        os.makedirs(os.path.dirname(f"output/{current_date}.json"), exist_ok=True)
        with open(f"output/{current_date}.json", "w") as f:
            import json
            json.dump(data, f, indent=4)
