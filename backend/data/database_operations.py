from models import TLE, get_engine
from models import engine, with_session
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
def insert_tle(tle_source, session=None):
    """Inserts TLE data into the database, replacing existing data if necessary"""
    tles_to_add = []
    
    if os.path.isfile(tle_source):
        # If it's a file, extract all TLEs and add them
        tles_to_add = TLE.tles_from_file(tle_source)
    else:
        # Assuming it's a TLE string and directly adding it
        tle = TLE.from_string(tle_source)
        if tle is not None:
            tles_to_add.append(tle)    
    
    if tles_to_add:
        # Query the database for existing TLEs, doing this in bulk is more efficient
        sat_nums = list({tle.satellite_number for tle in tles_to_add})
        existing_tles = session.query(TLE).filter(TLE.satellite_number.in_(sat_nums)).all()
        existing_tles_map = {e.satellite_number: e  for e in existing_tles}
        for tle in tles_to_add:
            if tle.satellite_number in existing_tles_map:
                existing_tles_map[tle.satellite_number] = tle
            else:
                session.add(tle)
                
        session.commit()
