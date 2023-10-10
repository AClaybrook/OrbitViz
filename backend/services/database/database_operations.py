from backend.services.database.database_utils import with_session
from backend.models.models import TLE, Satellite, LatestTLE, HistoricalTLE, Group

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
def pre_fetch_existing_data(new_tles, session=None):
    new_sat_nums = {tle.satellite_number for tle in new_tles}

    existing_satellites = (
        session.query(Satellite)
        .filter(Satellite.satellite_number.in_(new_sat_nums))
        .all()
    )

    existing_latest_tles = (
        session.query(LatestTLE)
        .filter(LatestTLE.satellite_number.in_(new_sat_nums))
        .all()
    )

    return {sat.satellite_number: sat for sat in existing_satellites}, {tle.satellite_number: tle for tle in existing_latest_tles}


@with_session
def insert_tle(tle_source, session=None, group=None):
    tles_to_add = []
    
    if os.path.isfile(tle_source):
        tles_to_add = TLE.from_file(tle_source)
    else:
        tle = TLE.from_string(tle_source)
        if tle is not None:
            tles_to_add.append(tle)    
    
    if tles_to_add:
        # Prefetch existing data
        existing_sats, existing_latest_tles = pre_fetch_existing_data(tles_to_add, session=session)
        
        # Process the new TLE data
        for tle in tles_to_add:
            sat_num = tle.satellite_number
            
            # Efficiently check for existing satellite and latest TLE
            satellite = existing_sats.get(sat_num)
            latest_tle = existing_latest_tles.get(sat_num)
            
            # Ensure Satellite exists
            if satellite is None:
                satellite = Satellite(satellite_number=sat_num, name=tle.name)
                session.add(satellite)
                existing_sats[sat_num] = satellite
            
            # Always add to HistoricalTLEs
            historical_tle = HistoricalTLE.from_tle(tle)
            session.add(historical_tle)
            
            # Update LatestTLE if newer or not existing
            # TODO: make a latest function
            if latest_tle is None or tle.timestamp > latest_tle.timestamp:
                if latest_tle is not None:
                    # Option 1: Update existing
                    latest_tle.line1, latest_tle.line2, latest_tle.timestamp = tle.line1, tle.line2, tle.timestamp
                else:
                    # Option 2: Insert new
                    new_latest_tle = LatestTLE.from_tle(tle)
                    session.add(new_latest_tle)
                    existing_latest_tles[sat_num] = new_latest_tle
                    
            # Optionally, associate with a group
            # TODO: make a group function
            if group is not None:
                # Ensure the group exists
                db_group = session.query(Group).filter_by(name=group).one_or_none()
                if db_group is None:
                    db_group = Group(name=group)
                    session.add(db_group)
                
                # Ensure the satellite is associated with the group
                if satellite not in db_group.satellites:
                    db_group.satellites.append(satellite)
                
        session.commit()
