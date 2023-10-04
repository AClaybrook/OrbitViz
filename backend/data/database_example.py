import os
print(os.getcwd())

from database_operations import insert_tle, query_tle, session, query_all_tle

# Example TLE data
example_tle = "/home/aclaybrook/GithubOnWSL/Access2/data/tles/stations.txt"

# Insert TLE data
insert_tle(example_tle, session)

# Query for a specific TLE
satellite_name = "ISS (ZARYA)"
# result = query_tle(satellite_name, session)
result = query_all_tle(session)

# Display or use the queried data
if result:
    # print(result)
    if isinstance(result, list):
        for r in result:
            print(r.to_tle(as_string=True))
    else:
        print(result.to_tle(as_string=True))
else:
    print(f"No TLE found for satellite ID: {satellite_name}")
