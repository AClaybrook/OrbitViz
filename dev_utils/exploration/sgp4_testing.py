from sgp4.io import twoline2rv
from backend.models.models import TLE

tle_source = "/home/aclaybrook/GithubOnWSL/OrbitViz/data/tles/active.txt"

tles_to_add = TLE.from_file(tle_source)

for tle in tles_to_add:
    print(tle)

# tle_source = "/home/aclaybrook/GithubOnWSL/OrbitViz/data/tles/active.json"

# tles_to_add = TLE.from_file(tle_source)

# for tle in tles_to_add:
#     print(tle)