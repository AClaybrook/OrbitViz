from database_setup import TLE, setup_database
import os
# Initialize Session (assuming SQLite for simplicity in this example)
db_path = 'sqlite:///data/tles.sqlite'  # Use an appropriate path and database type for your application.
session = setup_database(db_path)

operator_mapping = {
    "<": "__lt__",
    "<=": "__le__",
    "==": "__eq__",
    "!=": "__ne__",
    ">": "__gt__",
    ">=": "__ge__",
}

def query_tle(session,**kwargs):
    """Queries the database for a TLE with the given parameters"""
    result = session.query(TLE).filter_by(**kwargs).first()
    return result

def query_all_tle(session):
    result = session.query(TLE).all()
    return result

def insert_tle(tle_source, session):
    """Inserts TLE data into the database, replacing existing data if necessary"""
    tles_to_add = []
    
    if os.path.isfile(tle_source):
        # If it's a file, extract all TLEs and add them
        tles_to_add = TLE.tles_from_file(tle_source)
    else:
        # Assuming it's a TLE string and directly adding it
        tles_to_add.append(TLE.from_string(tle_source))
    
    for tle in tles_to_add:
        existing_tle = query_tle(session, satellite_number=tle.satellite_number)
        if existing_tle:
            for column in TLE.__table__.columns:
                field_name = column.name
                if field_name != tle.primary_key:
                    setattr(existing_tle, field_name, getattr(tle, field_name))
        else:
            session.add(tle)
    session.commit()

