from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sgp4.io import twoline2rv
from sgp4.earth_gravity import wgs72
from typing import Union, Tuple
import math
from contextlib import contextmanager
from functools import wraps
import sqlite3
import os
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
DB_SQLITE_PATH = f"{DATA_DIR}/tles.sqlite"
DB_PATH = f"sqlite:///{DB_SQLITE_PATH}"
engine = create_engine(DB_PATH)

Base = declarative_base()

class TLE(Base):
    __tablename__ = 'tles' 
    satellite_number = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=True)
    classification = Column(String(1), nullable=True)
    international_designator = Column(String(8), nullable=True)
    epoch_year = Column(Integer, nullable=True)
    epoch_day = Column(Float, nullable=True)
    first_time_derivative = Column(Float, nullable=True)
    second_time_derivative = Column(Float, nullable=True)
    bstar_drag_term = Column(Float, nullable=True)
    ephemeris_type = Column(Integer, nullable=True)
    element_number = Column(Integer, nullable=True)
    inclination = Column(Float, nullable=True)
    right_ascension = Column(Float, nullable=True)
    eccentricity = Column(Float, nullable=True)
    argument_of_perigee = Column(Float, nullable=True)
    mean_anomaly = Column(Float, nullable=True)
    mean_motion = Column(Float, nullable=True)
    revolution_number = Column(Integer, nullable=True)

    @property
    def primary_key(self):
        return self.satellite_number
    
    @staticmethod
    def from_string(tle_string):
        try:
            lines = tle_string.strip().split("\n")
            if len(lines) != 3:
                raise ValueError("TLE string must have exactly 3 lines")

            name = lines[0].strip()
            line1 = lines[1].strip()
            line2 = lines[2].strip()

            satrec = twoline2rv(line1, line2, wgs72)

            # Creating a mapping of attribute names to their respective values
            attributes = {
                'satellite_number': satrec.satnum,
                'name': name,
                'classification': satrec.classification,
                'international_designator': satrec.intldesg,
                'epoch_year': satrec.epochyr,
                'epoch_day': satrec.epochdays,
                'first_time_derivative': satrec.ndot,
                'second_time_derivative': satrec.nddot,
                'bstar_drag_term': satrec.bstar,
                'ephemeris_type': satrec.ephtype,
                'element_number': satrec.elnum,
                'inclination': satrec.inclo,
                'right_ascension': satrec.nodeo,
                'eccentricity': satrec.ecco,
                'argument_of_perigee': satrec.argpo,
                'mean_anomaly': satrec.mo,
                'mean_motion': satrec.no_kozai,
                'revolution_number': satrec.revnum
            }
            return TLE(**attributes)
        except Exception as e:
            print(f"Error parsing TLE: {str(e)}")
            return None
    
    @staticmethod
    def tles_from_file(file_path: str):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            tles = []
            for i in range(0, len(lines), 3):
                try:
                    name = lines[i].strip()
                    line1 = lines[i+1].strip()
                    line2 = lines[i+2].strip()
                    tle = TLE.from_string(f"{name}\n{line1}\n{line2}")
                    if tle is not None:
                        tles.append(tle)
                except (IndexError, ValueError) as e:
                    print(f"Error processing TLE starting at line {i}: {str(e)}")
        return tles
    
    def to_tle(self, as_string=False) -> Union[Tuple, str]:
        """
        Converts the stored TLE parameters into a TLE tuple or a string using adapted sgp4's exporter.
        Adapted from sgp4's exporter.py
        """

        deg2rad  =   math.pi / 180.0
        xpdotp   =  1440.0 / (2.0 * math.pi)

        # --------------------- Start generating line 1 ---------------------
        pieces = ["1 "]
        append = pieces.append

        append(str(self.satellite_number).zfill(5))
        append((self.classification.strip() or "U") + " ")
        append(self.international_designator.ljust(8, " ") + " ")
        append(str(self.epoch_year)[-2:].zfill(2) + "{:012.8f}".format(self.epoch_day) + " ")

        append("{0: 8.8f}".format(self.first_time_derivative * xpdotp * 1440).replace("0", "", 1) + " ")

        append("{0: 4.4e}".format(self.second_time_derivative * xpdotp * 1440 * 1440 * 10).replace(".", "").replace("e+00", "+0").replace("e-0", "-") + " ")

        # BSTAR
        append("{0: 4.4e}".format(self.bstar_drag_term * 10).replace(".", "").replace("e+00", "+0").replace("e-0", "-") + " ")

        append("{} ".format(self.ephemeris_type) + str(self.element_number).rjust(4, " "))

        line1 = ''.join(pieces)
        line1 += str(self.compute_checksum(line1))

        # --------------------- Start generating line 2 ---------------------
        pieces = ["2 "]
        append = pieces.append

        append(str(self.satellite_number).zfill(5) + " ")

        append("{0:8.4f}".format(self.inclination / deg2rad).rjust(8, " ") + " ")
        append("{0:8.4f}".format(self.right_ascension / deg2rad).rjust(8, " ") + " ")
        append("{0:7.7f}".format(self.eccentricity).replace("0.", "") + " ")  # keep only the fractional part
        append("{0:8.4f}".format(self.argument_of_perigee / deg2rad).rjust(8, " ") + " ")
        append("{0:8.4f}".format(self.mean_anomaly / deg2rad).rjust(8, " ") + " ")

        # Mean motion: convert revs/minute to revs/day
        append("{0:11.8f}".format(self.mean_motion * xpdotp).rjust(11, " "))
        append(str(self.revolution_number).rjust(5))

        line2 = ''.join(pieces)
        line2 += str(self.compute_checksum(line2))

        if as_string:
            return f"{self.name}\n{line1}\n{line2}"
        else:
            return self.name, line1, line2

    def to_dict(self):
        """Converts the TLE to a dictionary."""
        return {key: value for key, value in vars(self).items() if hasattr(self.__class__, key)}
    
    # @jit
    def compute_checksum(self, line):
        """Compute the TLE checksum for the given line.
        Adapted from sgp4's exporter.py but a bit faster"""
        checksum = 0
        for c in line[0:68]:
            if c.isdigit():
                checksum += int(c)
            elif c == '-':
                checksum += 1
        return checksum % 10
        

    def __repr__(self):
        return f"<TLE(name='{self.name}', satellite_number='{self.satellite_number}')>"

# Database operations
def get_engine(db_path=DB_PATH):
    return create_engine(db_path)

def build_database(db_path=DB_PATH):
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()



@contextmanager
def db_session(engine):
    """
    Context manager to provide a database session.
    
    Args:
        engine (sqlalchemy.engine.base.Engine): The database engine.
    
    Yields:
        sqlalchemy.orm.Session: The database session.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()



def with_session(func):
    """Decorator to provide a database session to a function if it does not exist.
        Passing a session is faster than creating a new one, but it is tedious to pass it every time."""
    @wraps(func)
    def wrapper(*args, session=None, **kwargs):
        if session is None:
            with db_session(engine) as session:
                return func(*args, session=session, **kwargs)
        else:
            return func(*args, session=session, **kwargs)
    return wrapper

class SQLiteConnectionManager:
    def __init__(self):
        self.database_path = DB_SQLITE_PATH
        self.conn = None
        self.connection_count = 0

    def __enter__(self):
        self.conn = sqlite3.connect(self.database_path)
        self.connection_count += 1
        return self.conn

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()
            self.connection_count -= 1

if __name__ == "__main__":
    build_database()
