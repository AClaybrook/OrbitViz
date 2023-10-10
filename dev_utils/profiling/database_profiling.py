import os
from backend.services.database.database_operations import insert_tle, query_all_tle, query_tle
from backend.services.data_fetching.celestrak import GROUPS, get_tle_source

# Example Inserting TLEs from files
for g in GROUPS:
    utl, fp = get_tle_source(g)
    print(g)
    insert_tle(fp)

# Query for a specific TLE
name = "ISS (ZARYA)"
result = query_tle(display=True, name=name)
results = query_all_tle(display=False)
