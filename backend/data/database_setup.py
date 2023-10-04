from sqlalchemy import create_engine, Column, Integer, String, Float, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sgp4.io import twoline2rv, compute_checksum
from sgp4.earth_gravity import wgs72
from typing import Union, Tuple
import math
from datetime import datetime, timedelta

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
                    tles.append(TLE.from_string(f"{name}\n{line1}\n{line2}"))
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
        line1 += str(compute_checksum(line1))

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
        line2 += str(compute_checksum(line2))

        if as_string:
            return f"{self.name}\n{line1}\n{line2}"
        else:
            return self.name, line1, line2

    def compute_checksum(self, line):
        """Compute the TLE checksum for the given line."""
        return sum((int(c) if c.isdigit() else c == '-') for c in line[0:68]) % 10
        

    def __repr__(self):
        return f"<TLE(name='{self.name}', satellite_number='{self.satellite_number}')>"


def setup_database(db_path):
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()