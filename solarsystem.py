from retriever import load_data
import math
import numpy as np
import numpy.typing as npt

GRAV_CONSTANT = 1.488e-34  # in units of AU^3 / (kg * day^2)
AU = 149597871


class Astrobject:
    def __init__(self, name: str, position: npt.NDArray[np.float], velocity: npt.NDArray[np.float]):
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
            dsq = dx[0] ** 2 + dx[1] ** 2 + dx[2] ** 2
            dr = math.sqrt(dsq)
            force = GRAV_CONSTANT * ao.mass / dsq
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


class OrbitalElements:
    def __init__(self, N, i, w, a, e, M):
        self.N = N
        self.i = i
        self.w = w
        self.a = a
        self.e = e
        self.M = M


def update_earth(d):
    d = d - 1.5
    T = d / 36525.0
    L0 = 280.46645 + 36000.76983 * T + 0.0003032 * (T ** 2)
    M0 = 357.52910 + 35999.05030 * T - 0.0001559 * (T ** 2) - 0.00000048 * (T ** 3)

    C = (
        (1.914600 - 0.004817 * T - 0.000014 * (T ** 2)) * Angle.sin_deg(M0)
        + (0.01993 - 0.000101 * T) * Angle.sin_deg(2 * M0)
        + 0.000290 * Angle.cos_deg(3 * M0)
    )

    LS = L0 + C
    e = 0.016708617 - T * (0.000042037 + 0.0000001236 * T)
    distance = (1.000001018 * (1 - e ** 2)) / (1 + e * Angle.cos_deg(M0 + C))
    x = -distance * Angle.cos_deg(LS)
    y = -distance * Angle.sin_deg(LS)
    return np.array([x, y, 0])


def update_pluto(d):
    S = 50.03 + 0.033459652 * d
    P = 238.95 + 0.003968789 * d

    lon_ecl = (
        238.9508 + 0.00400703 * d
        - 19.799 * Angle.sin_deg(P) + 19.848 * Angle.cos_deg(P)
        + 0.897 * Angle.sin_deg(2 * P) - 4.956 * Angle.cos_deg(2 * P)
        + 0.610 * Angle.sin_deg(3 * P) + 1.211 * Angle.cos_deg(3 * P)
        - 0.341 * Angle.sin_deg(4 * P) - 0.190 * Angle.cos_deg(4 * P)
        + 0.128 * Angle.sin_deg(5 * P) - 0.034 * Angle.cos_deg(5 * P)
        - 0.038 * Angle.sin_deg(6 * P) + 0.031 * Angle.cos_deg(6 * P)
        + 0.020 * Angle.sin_deg(S - P) - 0.010 * Angle.cos_deg(S - P)
    )

    lat_ecl = (
        -3.9082
        - 5.453 * Angle.sin_deg(P) - 14.975 * Angle.cos_deg(P)
        + 3.527 * Angle.sin_deg(2 * P) + 1.673 * Angle.cos_deg(2 * P)
        - 1.051 * Angle.sin_deg(3 * P) + 0.328 * Angle.cos_deg(3 * P)
        + 0.179 * Angle.sin_deg(4 * P) - 0.292 * Angle.cos_deg(4 * P)
        + 0.019 * Angle.sin_deg(5 * P) + 0.100 * Angle.cos_deg(5 * P)
        - 0.031 * Angle.sin_deg(6 * P) - 0.026 * Angle.cos_deg(6 * P)
        + 0.011 * Angle.cos_deg(S - P)
    )

    r = (
        40.72
        + 6.68 * Angle.sin_deg(P) + 6.90 * Angle.cos_deg(P)
        - 1.18 * Angle.sin_deg(2 * P) - 0.03 * Angle.cos_deg(2 * P)
        + 0.15 * Angle.sin_deg(3 * P) - 0.14 * Angle.cos_deg(3 * P)
    )

    cos_lon = Angle.cos_deg(lon_ecl)
    sin_lon = Angle.sin_deg(lon_ecl)
    cos_lat = Angle.cos_deg(lat_ecl)
    sin_lat = Angle.sin_deg(lat_ecl)

    x = r * cos_lon * cos_lat
    y = r * sin_lon * cos_lat
    z = r * sin_lat

    return np.array([x, y, z])


class Angle:
    DEG_FROM_RAD = 180.0 / math.pi
    RAD_FROM_DEG = math.pi / 180.0

    @classmethod
    def cos_deg(cls, degrees):
        return math.cos(cls.RAD_FROM_DEG * degrees)

    @classmethod
    def sin_deg(cls, degrees):
        return math.sin(cls.RAD_FROM_DEG * degrees)

    @classmethod
    def atan2_deg(cls, y, x):
        return cls.DEG_FROM_RAD * math.atan2(y, x)


class SolarSystem:
    def __init__(self, start_date="2022-01-01"):
        self.sun = Astrobject(name="Sun", position=np.array([0, 0, 0, 1]), velocity=np.zeros(4))
        self.sun.mass = 1.989e30
        self.planets: list[Astrobject] = []
        for planet in load_data(start_date):
            self.planets.append(Astrobject(
                name=planet["name"],
                position=np.array(planet["position"] + [1]),
                velocity=np.array(planet["velocity"] + [0])
            ))
        planet_mass = [0.33, 4.87, 6.043, 0.642, 1898.0, 568.0, 86.8, 102.0, 0.013]
        planet_trace = [57, 108, 150, 228, 780, 1430, 2877, 4510, 5830]
        for i in range(9):
            self.planets[i].mass = planet_mass[i] * (10 ** 24)
            self.planets[i].max_trace_len = planet_trace[i]

    def update(self):
        dt = 1
        for planet in self.planets:
            planet.position += planet.velocity * dt
            acc = -2.959e-4 * planet.position / (np.sum(planet.position ** 2) - 1) ** 1.5  # in units of AU/day^2
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

    def update2(self, date):
        y, m, d = [int(i) for i in date.split("-")]
        d = 367 * y - 7 * (y + (m + 9) // 12) // 4 \
            - 3 * ((y + (m - 9) // 7) // 100 + 1) // 4 + 275 * m // 9 + d - 730515

        self.planets[2].position[0:3] = update_earth(d)
        self.planets[8].position[0:3] = update_pluto(d)

        planets = [
            OrbitalElements(
                48.3313 + 3.24587e-5 * d,
                7.0047 + 5.00e-8 * d,
                29.1241 + 1.01444e-5 * d,
                0.387098,
                0.205635 + 5.59e-10 * d,
                168.6562 + 4.0923344368 * d
            ),
            OrbitalElements(
                76.6799 + 2.46590e-5 * d,
                3.3946 + 2.75e-8 * d,
                54.8910 + 1.38374e-5 * d,
                0.723330,
                0.006773 - 1.302e-9 * d,
                48.0052 + 1.6021302244 * d
            ),
            OrbitalElements(
                0, 0, 0, 0, 0, 0
            ),
            OrbitalElements(
                49.5574 + 2.11081e-5 * d,
                1.8497 - 1.78e-8 * d,
                286.5016 + 2.92961e-5 * d,
                1.523688,
                0.093405 + 2.516e-9 * d,
                18.6021 + 0.5240207766 * d
            ),
            OrbitalElements(
                100.4542 + 2.76854e-5 * d,
                1.3030 - 1.557e-7 * d,
                273.8777 + 1.64505e-5 * d,
                5.20256,
                0.048498 + 4.469e-9 * d,
                19.8950 + 0.0830853001 * d
            ),
            OrbitalElements(
                113.6634 + 2.38980e-5 * d,
                2.4886 - 1.081e-7 * d,
                339.3939 + 2.97661e-5 * d,
                9.55475,
                0.055546 - 9.499e-9 * d,
                316.9670 + 0.0334442282 * d
            ),
            OrbitalElements(
                74.0005 + 1.3978e-5 * d,
                0.7733 + 1.9e-8 * d,
                96.6612 + 3.0565e-5 * d,
                19.18171 - 1.55e-8 * d,
                0.047318 + 7.45e-9 * d,
                142.5905 + 0.011725806 * d
            ),
            OrbitalElements(
                131.7806 + 3.0173e-5 * d,
                1.7700 - 2.55e-7 * d,
                272.8461 - 6.027e-6 * d,
                30.05826 + 3.313e-8 * d,
                0.008606 + 2.15e-9 * d,
                260.2471 + 0.005995147 * d
            )
        ]

        for i in range(8):
            if i == 2:
                continue
            M = planets[i].M
            e = planets[i].e
            E0 = M + (e * Angle.sin_deg(M) * (1.0 + (e * Angle.cos_deg(M))))
            while True:
                E1 = E0 - (E0 - (Angle.DEG_FROM_RAD * e * Angle.sin_deg(E0)) - M) / (1 - e * Angle.cos_deg(E0))
                diff = math.fabs(E1 - E0)
                E0 = E1
                if diff < 1e-8:
                    break

            a = planets[i].a
            xv = a * (Angle.cos_deg(E0) - e)
            yv = a * (math.sqrt(1.0 - e ** 2) * Angle.sin_deg(E0))
            v = Angle.atan2_deg(yv, xv)
            r = math.sqrt(xv ** 2 + yv ** 2)

            cos_n = Angle.cos_deg(planets[i].N)
            sin_n = Angle.sin_deg(planets[i].N)
            cos_i = Angle.cos_deg(planets[i].i)
            sin_i = Angle.sin_deg(planets[i].i)
            cos_vw = Angle.cos_deg(planets[i].w + v)
            sin_vw = Angle.sin_deg(planets[i].w + v)
            x = r * (cos_n * cos_vw - sin_n * sin_vw * cos_i)
            y = r * (sin_n * cos_vw + cos_n * sin_vw * cos_i)
            z = r * (sin_vw * sin_i)

            self.planets[i].position[0:3] = [x, y, z]
