from skyfield.api import Loader
from skyfield.api import wgs84
from skyfield.api import EarthSatellite
from typing import List
from data.celestrak import get_tle_source
from skyfield.elementslib import osculating_elements_of
from data import TLE_DIR


# Earth ephem
load = Loader(TLE_DIR)
eph = load('de421.bsp')
ts = load.timescale()

# Get Satellite TLEs
url, filepath = get_tle_source('stations')
satellites = load.tle_file(url=url, filename=filepath)
by_name = {satellite.name: satellite for satellite in satellites}
by_id = {satellite.model.satnum: satellite for satellite in satellites}

# Select a satellite of interest
satellite = by_id[25544]

# Specify time range
t0 = ts.utc(2023, 1, 23)
t1 = ts.utc(2023, 1, 24)

# Specify ground station location
atlanta = wgs84.latlon(33.7490, -84.3880)
el = 10

# Calculate ground station passes
t, events = satellite.find_events(atlanta, t0, t1, altitude_degrees=el)
event_names = f'rise above {el}°', 'culminate', f'set below {el}°'

# Sunlight
sunlit = satellite.at(t).is_sunlit(eph)
sunlit_states = ('shadow', 'sunlit')

geocentric = satellite.at(t)
print(geocentric.position.km)

for ti, event, sunlit_flag in zip(t, events, sunlit):
    name = event_names[event]
    state = sunlit_states[sunlit_flag]
    print(ti.utc_strftime('%Y %b %d %H:%M:%S'), name, state)
