import numpy as np
from datetime import datetime, timedelta
from poliastro.bodies import Earth
from poliastro.twobody import Orbit, sampling, events
from astropy import units as u
from astropy.time import Time
from astropy.coordinates import ITRS, EarthLocation, CartesianRepresentation, TEME
import matplotlib.pyplot as plt
from astropy.coordinates import CartesianDifferential
import plotly.express as px
from scipy.optimize import root_scalar
from scipy.signal import find_peaks
import pytz
from poliastro.twobody.sampling import EpochsArray
from poliastro.util import time_range
from poliastro.examples import iss


"""Takes in a start time, duration, a desired value and a function that returns a value over time.
    Returns the interals when that condition is met"""
# Initial values in astropy units
start_date = Time(datetime(2023, 1, 1, 0, 0, 0, tzinfo=pytz.utc), scale="utc")
duration = 12 * 60 * 60 * u.s
step_size = 60 * u.s
desired_elevation_deg = 10

end_date = start_date + duration

# Ground Station Information (Atlanta, Georgia) in ECEF
latitude = 33.7490 * u.deg
longitude = -84.3880 * u.deg
altitude = 0 * u.m
location = EarthLocation(lat=latitude, lon=longitude, height=altitude)
ground_station_position = location.itrs.cartesian.xyz.to(u.km).value

# Satellite Initial Conditions
a = Earth.R + 500 * u.km
ecc = 0.0 * u.one
inc = 45 * u.deg
raan = 0 * u.deg
argp = 0 * u.deg
nu = 0 * u.deg
epoch = start_date
orbit = Orbit.from_classical(Earth, a, ecc, inc, raan, argp, nu, epoch=epoch)

# Explicit ephemeris from propagation times
steps = int(np.round(duration/(step_size)))+1
epochs = time_range(start_date, end=end_date, periods=steps)
ephems = orbit.to_ephem(strategy=EpochsArray(epochs=epochs))
# Interpolated ephemeris example
# multiple = 3
# epochs_sampled = time_range(start_date, end=end_date, periods=steps*multiple-(multiple+1))
# sampled_ephems = ephems.rv(epochs=epochs_sampled)


def calc_aer(r1, r2):
    r_rel = np.subtract(r1, r2)
    range_ = np.linalg.norm(r_rel)
    elevation = np.arctan2(r_rel[2], np.sqrt(r_rel[0]**2 + r_rel[1]**2))
    azimuth = np.arctan2(r_rel[1], r_rel[0])
    return azimuth, elevation, range_

def get_satellite_state(time, ephems):
    r,v = ephems.rv(epochs=time)
    return r, v

def get_ground_station_position(time, location):
    # TODO: Implement this to work over time
    return location.itrs.cartesian.xyz.to(u.km).value

def evaluate_elevation(time, ephems, location):
    r1, _ = get_satellite_state(time, ephems=ephems)
    r2 = get_ground_station_position(time, location)
    r_rel = np.subtract(r1, r2)
    elevation = np.arctan2(r_rel[2], np.sqrt(r_rel[0]**2 + r_rel[1]**2))
    return elevation

def evaluate(f, desired_value, *args):
    return f(*args) - desired_value

# # Boundary crossing function
result = root_scalar(evaluate, bracket=[start_date, end_date], method='brentq')

# # Initial search where the times sample frequently enough so that boundary crossing is not likely to be missed
def initial_search(times, f, *args):
    return [f(t, *args) for t in times]

search_vals = initial_search(steps,evaluate_elevation, ephems=ephems, location=location)


def crossing_bounds(values):
    crossing_indices = np.where(np.diff(np.sign(values)) != 0)[0]
    return [(i, i+1) for i in crossing_indices]


# for t, val in search_vals:



# # Find boundary crossing and add to the plot
# for i in range(1, len(elevation_angles)):
#     if (elevation_angles[i-1] < desired_elevation_rad and elevation_angles[i] > desired_elevation_rad) or \
#        (elevation_angles[i-1] > desired_elevation_rad and elevation_angles[i] < desired_elevation_rad):
#         boundary_crossing_time = time_array[i]

# # Plot the elevation angle over time
# fig = px.line(x=time_array, y=elevation_angles_deg, labels={'x': 'Time', 'y': 'Elevation Angle (degrees)'})
# fig.update_layout(title='Elevation Angle Over Time')
# fig.add_vline(x=boundary_crossing_time.timestamp()*1000, line_dash="dash", line_color="red", annotation_text=f"Elevation = {desired_elevation_deg} deg")


# # Show plot
# fig.show()

# # Find boundary crossing
# # boundary_crossing_time = find_boundary_crossing(start_time, end_time, evaluate_elevation, desired_elevation_rad)

# # print(f"Boundary crossing time: {boundary_crossing_time}")
