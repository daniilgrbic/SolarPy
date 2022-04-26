from retriever import load_data
import numpy as np
import numpy.typing as npt


class Astrobject:
    def __init__(self, name: str, position: npt.NDArray[np.float], velocity: npt.NDArray[np.float]):
        self.name = name
        self.position = position
        self.velocity = velocity
        self.trace = [np.array(position), np.array(position)]


class SolarSystem:
    def __init__(self, start_date="2022-01-01"):
        self.sun = Astrobject(name="Sun", position=np.array([0, 0, 0, 1]), velocity=np.zeros(0))
        self.planets: list[Astrobject] = []
        for planet in load_data(start_date):
            self.planets.append(Astrobject(
                name=planet["name"],
                position=np.array(planet["position"]+[1]),
                velocity=np.array(planet["velocity"]+[0])
            ))

    # TODO Gogic
    def update(self):
        dt = 1
        for planet in self.planets:
            planet.position += planet.velocity * dt
            acc = -2.959e-4 * planet.position / (np.sum(planet.position**2)-1)**1.5  # in units of AU/day^2
            #acc = -2.959e-4 * planet.position / np.sum(planet.position[:3] ** 2) ** (3. / 2)  # in units of AU/day^2
            acc[3] = 0
            planet.velocity += acc * dt


            planet.trace.append(np.array(planet.position))
            if len(planet.trace) > 150:
                planet.trace.pop(0)


        return
