from backend.services.database.database_utils import with_session
from backend.models.models import TLE, Satellite, Group
from backend.services.calculations.utils import timeit
from sqlalchemy import exists

import os

operator_mapping = {
    "<": "__lt__",
    "<=": "__le__",
    "==": "__eq__",
    "!=": "__ne__",
    ">": "__gt__",
    ">=": "__ge__",
}

@with_session
def query_tle(display=False, session=None, **kwargs):
    """Queries the database for a TLE with the given parameters"""
    result = session.query(TLE).filter_by(**kwargs).first()
    if display:
        display_results(result)
    return result

# Display or use the queried data

def display_results(result):
    """Displays the results of a TLE query
    Most be called by a function that has a session parameter that generated the results"""
    if result:
        if isinstance(result, list):
            for r in result:
                tle_str = r.to_tle(as_string=True)
                # print(tle_str)
            for r in result:
                tle_dict = r.to_dict()
                # print(tle_dict)
        else:
            print(result.to_tle(as_string=True))
    else:
        print(f"No matching TLEs found.")

@with_session
def query_all_tle(display=False, session=None):
    result = session.query(TLE).all()
    if display:
        display_results(result)
    return result

@with_session
def fetch_existing_satelites(new_tles, session=None):
    new_sat_nums = {tle.satellite_number for tle in new_tles}

    existing_satellites = (
        session.query(Satellite)
        .filter(Satellite.satellite_number.in_(new_sat_nums))
        .all()
    )

    return {sat.satellite_number: sat for sat in existing_satellites}

@with_session
def fetch_latest_tles(session=None):
    """Fetches the latest TLEs from the database"""
    result = (
        session.query(Satellite, TLE)
        .join(TLE, Satellite.latest_tle_id == TLE.id)
        .all()
    )
    return [tle for sat, tle in result]

def get_tles_from_source(tle_source):
    """Returns a list of TLEs from a file or a TLE string"""
    tles_to_add = []
    if os.path.isfile(tle_source):
        tles_to_add = TLE.from_file(tle_source)
    else:
        tle = TLE.from_string(tle_source)
        if tle is not None:
            tles_to_add.append(tle) 
    return tles_to_add

# TODO: Make sure this doesn't eat up too much memory, possibly as filter by minimum tle epoch
@with_session
def get_existing_tle_epochs(tles_to_add, session=None):
    existing_tle_epochs = {
        (tle.satellite_number, tle.epoch): tle
        for tle in session.query(TLE)
        .filter(TLE.satellite_number.in_([tle.satellite_number for tle in tles_to_add]))
        .all()
    }
    return existing_tle_epochs


@with_session
@timeit
def insert_tle(tle_source, session=None, group=None):

    tles_to_add = get_tles_from_source(tle_source)
    
    if tles_to_add:
        # Prefetch existing data
        existing_sats = fetch_existing_satelites(tles_to_add, session=session)
        existing_tle_epochs = get_existing_tle_epochs(tles_to_add, session=session)

        # Optionally, associate with a group
        # TODO: make a group function
        if group is not None:
            # Ensure the group exists
            db_group = session.query(Group).filter_by(name=group).one_or_none()
            if db_group is None:
                db_group = Group(name=group)
                session.add(db_group)

        # Process the new TLE data
        for tle in tles_to_add:
            if tle is not None:
                sat_num = tle.satellite_number
                

                # Skip if TLE already exists
                #TODO: Figure out how to make this faster
                # tle_already_exists = session.query(TLE).filter_by(satellite_number=tle.satellite_number, epoch=tle.epoch).one_or_none() # Slow
                # tle_already_exists = session.query(
                #     exists().where(
                #         TLE.satellite_number == tle.satellite_number
                #     ).where(
                #         TLE.epoch == tle.epoch
                #     )
                # ).scalar() # Only slightly faster
                # if not tle_already_exists:
                #     session.add(tle)
                if not (tle.satellite_number, tle.epoch) in existing_tle_epochs:
                    session.add(tle)

                # Efficiently check for existing satellite and latest TLE
                satellite = existing_sats.get(sat_num)
                
                # Ensure Satellite exists
                if satellite is None:
                    satellite = Satellite(satellite_number=sat_num, name=tle.name, latest_tle=tle)
                    session.add(satellite)
                    existing_sats[sat_num] = satellite
                else:
                    # Update latest_tle if the new TLE is more recent
                    if not satellite.latest_tle or tle.epoch > satellite.latest_tle.epoch:
                        satellite.latest_tle = tle
                        
                # Ensure the satellite is associated with the group
                if group is not None and db_group is not None and satellite not in db_group.satellites:
                    db_group.satellites.append(satellite)
                    
        session.commit()
