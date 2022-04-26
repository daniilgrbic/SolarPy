from astropy.time import Time
from astroquery.jplhorizons import Horizons
import json


def retrieve_data(start_date: str):
    planets = []
    for planet_id in range(1, 10):
        planet = Horizons(
            id=planet_id,
            location="@sun",
            epochs=Time(start_date).jd).vectors()
        print(planet["targetname"].value[0].split()[0])
        planets.append({
            "name": planet["targetname"].value[0].split()[0],
            "position": [planet[ci].value[0] for ci in ['x', 'y', 'z']],
            "velocity": [planet[vi].value[0] for vi in ['vx', 'vy', 'vz']]
        })

    with open("data/{}.json".format(start_date), "w") as f:
        import json
        json.dump({
            "date": start_date,
            "planets": planets
        }, f, indent=4)


def load_data(start_date: str) -> list[dict]:
    from os.path import exists
    if not exists("data/{}.json".format(start_date)):
        retrieve_data(start_date)

    with open("data/{}.json".format(start_date), "r") as f:
        data = json.load(f)
        planets = data["planets"]

    return planets
