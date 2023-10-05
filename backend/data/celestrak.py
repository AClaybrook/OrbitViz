import os
import requests
from __init__ import DATA_DIR
from database_operations import insert_tle
from models import get_engine, db_session


CELESTRAK_URL = "https://celestrak.org/NORAD/elements/gp.php?GROUP={}&FORMAT=tle"

GROUPS = [
    "last-30-days", "stations", "visual", "active", "analyst","1982-092", "1999-025", "iridium-33-debris", "cosmos-2251-debris", "weather", "noaa",
    "goes", "resource", "sarsat", "dmc", "tdrss", "argos", "planet", "spire",
    "geo", "intelsat", "ses", "iridium", "iridium-NEXT", "starlink", "oneweb",
    "orbcomm", "globalstar", "swarm", "amateur", "x-comm", "other-comm",
    "satnogs", "gorizont", "raduga", "molniya", "gnss", "gps-ops", "glo-ops",
    "galileo", "beidou", "sbas", "nnss", "musson", "science", "geodetic",
    "engineering", "education", "military", "radar", "cubesat", "other",
]

def get_tle_source(group):
    """Returns the URL and filepath for a given Celestrak group."""
    return CELESTRAK_URL.format(group), os.path.join(DATA_DIR, 'tles', f"{group}.txt")

def get_tles(groups=GROUPS, update=True, add_to_database=True):
    """Gets the TLEs from Celestrak and saves them to the data/tles directory.
        Also adds them to the database if add_to_database is True."""
    for group in groups:

        url, filepath = get_tle_source(group)

        if not update and os.path.exists(filepath):
            print(f"File exists: {group}")
            continue
        response = requests.get(url)
        if response.status_code == 200:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"Succeeded: {group}")
        else:
            print(f"Failed: {group}")

        if add_to_database:
            print("\tAddings to database...")
            insert_tle(filepath)
            print("\tDone adding to database.")

if __name__ == "__main__":
    get_tles(update=True, add_to_database=True)
