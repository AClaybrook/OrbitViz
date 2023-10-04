import numpy as np
from astropy.coordinates import GCRS, EarthLocation, ITRS
from astropy import units as u
from astropy.coordinates.builtin_frames.intermediate_rotation_transforms import cirs_to_itrs_mat, gcrs_to_cirs_mat


def get_satellite_state(time, ephems):
    """Returns the position and velocity of the satellite in the GCRS frame at a given time"""
    r,v = ephems.rv(epochs=time)
    return r, v

def get_ground_station_position(time, location):
    """Returns the position of the ground station in the GCRS frame at a given time"""

    # r,v = location.get_gcrs_posvel(obstime=time)
    # return r.xyz.to(u.km), v.xyz.to(u.km/u.s)

    gcrs_coords = location.itrs.transform_to(GCRS(obstime=time))
    r = gcrs_coords.cartesian.xyz.to(u.km)
    return r, r

def calc_elevation(time, ephems, location):
    """Returns the elevation angle of the satellite at a given time"""
    r1, _ = get_satellite_state(time, ephems)
    r2 = r1 - 1000 * u.km
    r2, _ = get_ground_station_position(time, location)
    r_rel = np.subtract(r1, r2)
    elevation = np.arctan2(r_rel[2], np.sqrt(r_rel[0]**2 + r_rel[1]**2)).to(u.deg)
    return elevation

# def get_ground_station_position(time, location):
#     """Returns the position of the ground station in the GCRS frame at a given time"""
#     r,v = location.get_gcrs_posvel(obstime=time)
#     return r.xyz.to(u.km), v.xyz.to(u.km/u.s)

# def calc_elevation(time, ephems, location):
#     """Returns the elevation angle of the satellite at a given time"""
#     r1, _ = get_satellite_state(time, ephems)
#     r2, _ = get_ground_station_position(time, location)
#     r_rel = np.subtract(r1, r2)
#     elevation = np.arctan2(r_rel[2], np.sqrt(r_rel[0]**2 + r_rel[1]**2)).to(u.deg)
#     return elevation

def calc_aer(r1, r2):
    """Returns the azimuth, elevation, and range between two vectors"""
    r_rel = np.subtract(r1, r2)
    range_ = np.linalg.norm(r_rel)
    elevation = np.arctan2(r_rel[2], np.sqrt(r_rel[0]**2 + r_rel[1]**2))
    azimuth = np.arctan2(r_rel[1], r_rel[0])
    return azimuth, elevation, range_