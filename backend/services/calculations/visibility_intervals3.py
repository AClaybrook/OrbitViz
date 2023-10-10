"""Takes in a start time, duration, a desired value and a function that returns a value over time.
    Returns the interals when that condition is met"""
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
from scipy import optimize
from calcs import calc_elevation
from boundary import find_crossings, initial_search, find_crossing_bounds, get_intervals
from poliastro.core.perturbations import J2_perturbation
from poliastro.core.propagation import func_twobody
from poliastro.twobody.propagation import CowellPropagator
from numba import jit, njit
from utils import timeit

# Initial values in astropy units
start_date = Time(datetime(2023, 1, 1, 0, 0, 0, tzinfo=pytz.utc), scale="utc")
duration = 12 * 60 * 60 * u.s
step_size = 180 * u.s
desired_elevation_deg = 10 * u.deg

# Ground Station Information (Atlanta, Georgia) in ECEF
latitude = 33.7490 * u.deg
longitude = -84.3880 * u.deg
altitude = 0 * u.m
location = EarthLocation(lat=latitude, lon=longitude, height=altitude)

# Satellite Initial Conditions
a = Earth.R + 500 * u.km
ecc = 0.0 * u.one
inc = 45 * u.deg
raan = 0 * u.deg
argp = 0 * u.deg
nu = 0 * u.deg
epoch = start_date
orbit = Orbit.from_classical(Earth, a, ecc, inc, raan, argp, nu, epoch=epoch)

def f(t0, state, k, J2=Earth.J2.value, R=Earth.R.to(u.km).value):
    du_kep = func_twobody(t0, state, k)
    ax, ay, az = J2_perturbation(
        t0, state, k, J2=J2, R=R
    )
    du_ad = np.array([0, 0, 0, ax, ay, az])

    return du_kep + du_ad


# Explicit ephemeris from propagation times
end_date = start_date + duration
steps = int(np.round(duration/(step_size)))+1
epochs = time_range(start_date, end=end_date, periods=steps)

@timeit
def propagate_ephems():
    return orbit.to_ephem(strategy=EpochsArray(epochs=epochs, method=CowellPropagator(rtol=1e-6, f=f)))

ephems = propagate_ephems()

# Interpolated ephemeris example
# multiple = 3
# epochs_sampled = time_range(start_date, end=end_date, periods=steps*multiple-(multiple+1))
# sampled_ephems = ephems.rv(epochs=epochs_sampled)

# Provide a function that varies with time as the first arg and returns f(time) at a given time
# Provide additional arguments and keyword arguments
function_of_time = calc_elevation
args = (ephems, location)
desired_val = desired_elevation_deg

def func(time, desired_val, *args):
    return function_of_time(time, *args) - desired_val

# Initial grid search to find potential boundary crossing times
search_vals = initial_search(epochs, func, desired_val, *args)
print(zip(epochs,search_vals))

# Find crossing bounds
crossings_bounds = find_crossing_bounds(epochs, search_vals)

# Refine each bound to a crossing time using scipy optimize
crossings = find_crossings(func, desired_val, crossings_bounds, *args)
print(crossings)
# Output the intervals where elevation is above the desired angle
pos, neg = get_intervals(epochs, func, desired_val, crossings, *args)
print(pos,neg)