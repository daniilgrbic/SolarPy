import constants
import math


class OrbitalElements:
    def __init__(self, N, i, w1, a, e, L):
        self.N = N  # longitude of the ascending node
        self.i = i  # inclination to the ecliptic
        self.w1 = w1  # longitude of perihelion
        self.a = a  # semi-major axis, or mean distance from Sun
        self.e = e  # eccentricity
        self.L = L  # mean longitude


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


def load_data(start_date: str) -> list[dict]:
    y, m, d = [int(i) for i in start_date.split("-")]
    day = (367 * y - 7 * (y + (m + 9) // 12) // 4
           - 3 * ((y + (m - 9) // 7) // 100 + 1) // 4 + 275 * m // 9 + d + 1721029)  # Julian Ephemeris Date

    T = (day - 2451545.0) / 36525

    if 2378497 <= day <= 2469808:
        elements = constants.keplerian_elements_1800_2050
        print("Using Keplerian elements for time-interval 1800 AD - 2050 AD")
    else:
        elements = constants.keplerian_elements_3000_3000
        print("Using Keplerian elements for time-interval 3000 BC – 3000 AD")

    planets_elements = []
    for i in range(9):
        planets_elements.append(OrbitalElements(
            N=elements[i]['N'][0] + T * elements[i]['N'][1],
            i=elements[i]['i'][0] + T * elements[i]['i'][1],
            w1=elements[i]['w1'][0] + T * elements[i]['w1'][1],
            a=elements[i]['a'][0] + T * elements[i]['a'][1],
            e=elements[i]['e'][0] + T * elements[i]['e'][1],
            L=elements[i]['L'][0] + T * elements[i]['L'][1]
        ))

    planets = [{"name": constants.planets_names[i]} for i in range(9)]

    for i in range(9):
        w = planets_elements[i].w1 - planets_elements[i].N
        M = planets_elements[i].L - planets_elements[i].w1
        if i in range(4, 9):
            M += (constants.b[i - 4] * (T ** 2) + constants.c[i - 4] * math.cos(constants.f[i - 4] * T)
                  + constants.s[i - 4] * math.sin(constants.f[i - 4] * T))
        M %= 360

        e = planets_elements[i].e
        e1 = e * Angle.DEG_FROM_RAD

        E = M + e1 * Angle.sin_deg(M)
        while True:
            M1 = M - (E - e1 * Angle.sin_deg(E))
            E1 = M1 / (1 - e * Angle.cos_deg(E))
            E += E1
            if E1 < 1e-9:
                break

        a = planets_elements[i].a
        c1 = a * (Angle.cos_deg(E) - e)
        c2 = a * (math.sqrt(1.0 - e ** 2) * Angle.sin_deg(E))
        r = math.sqrt(c1 ** 2 + c2 ** 2)

        cos_w = Angle.cos_deg(w)
        sin_w = Angle.sin_deg(w)
        cos_N = Angle.cos_deg(planets_elements[i].N)
        sin_N = Angle.sin_deg(planets_elements[i].N)
        cos_i = Angle.cos_deg(planets_elements[i].i)
        sin_i = Angle.sin_deg(planets_elements[i].i)

        x = c1 * (cos_w * cos_N - sin_w * sin_N * cos_i) + c2 * (-sin_w * cos_N - cos_w * sin_N * cos_i)
        y = c1 * (cos_w * sin_N + sin_w * cos_N * cos_i) + c2 * (-sin_w * sin_N + cos_w * cos_N * cos_i)
        z = c1 * sin_w * sin_i + c2 * cos_w * sin_i

        planets[i]["position"] = [x, y, z]

        ni = constants.GRAV_CONSTANT * (constants.sun_mass + constants.planets_mass[i])

        c1 = -Angle.sin_deg(E) * math.sqrt(ni * a) / r
        c2 = math.sqrt(1 - e ** 2) * Angle.cos_deg(E) * math.sqrt(ni * a) / r

        vx = c1 * (cos_w * cos_N - sin_w * sin_N * cos_i) - c2 * (sin_w * cos_N + cos_w * sin_N * cos_i)
        vy = c1 * (cos_w * sin_N + sin_w * cos_N * cos_i) + c2 * (cos_w * cos_N * cos_i - sin_w * sin_N)
        vz = c1 * sin_w * sin_i + c2 * cos_w * sin_i

        planets[i]["velocity"] = [vx, vy, vz]

    return planets
