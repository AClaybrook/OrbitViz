from sgp4.io import twoline2rv
from backend.models.models import TLE
from backend.services.database.database_operations import insert_tle, fetch_latest_tles
from backend.services.database.database_utils import db_session, engine

# tle_source = "/home/aclaybrook/GithubOnWSL/OrbitViz/data/tles/active.txt"

# tles_to_add = TLE.from_file(tle_source)

# for tle in tles_to_add:
#     print(tle)

tle_source = "/home/aclaybrook/GithubOnWSL/OrbitViz/data/tles/iss.txt"
insert_tle(tle_source)


# Check latest tles are quick to query and explore tle and satellite relationship linking
with db_session(engine) as session:
    latest_tles = fetch_latest_tles(session=session)
    for tle in latest_tles:
        print(tle.satellite.satellite_number, tle.satellite.name)

# tle_source = "/home/aclaybrook/GithubOnWSL/OrbitViz/data/tles/active.json"

# tles_to_add = TLE.from_file(tle_source)

# for tle in tles_to_add:
#     print(tle)