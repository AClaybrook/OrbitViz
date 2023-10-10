from sqlalchemy import create_engine, Column, Integer, String, Float, Table, PrimaryKeyConstraint, and_
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker, foreign
from sgp4.io import twoline2rv
from sgp4.earth_gravity import wgs72
from typing import Union, Tuple
import math
from contextlib import contextmanager
from functools import wraps
import sqlite3
import os
from config import DB_URI, DB_PATH
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import json
from datetime import datetime

engine = create_engine(DB_URI)

Base = declarative_base()

class TLE(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Three Line TLE Specs: https://celestrak.org/NORAD/documentation/tle-fmt.php
    # TLE Line 0
    name = Column(String(50))
    # TLE Line 1
    # @declared_attr
    # def satellite_number(cls):
    #     return Column(Integer) # Norad ID
    satellite_number = Column(Integer) # Norad ID
    classification = Column(String(1))
    international_designator = Column(String(8))
    epoch_year = Column(Integer)
    epoch_day = Column(Float)
    mean_motion_dot = Column(Float)
    mean_motion_ddot = Column(Float)
    bstar = Column(Float)
    ephemeris_type = Column(Integer)
    element_number = Column(Integer)
    # TLE Line 2
    inclination = Column(Float)
    right_ascension = Column(Float)
    eccentricity = Column(Float)
    argument_of_perigee = Column(Float)
    mean_anomaly = Column(Float)
    mean_motion = Column(Float)
    revolution_number = Column(Integer)
    # Additional fields
    epoch = Column(DateTime)
    
    # Factory methods
    @staticmethod
    def from_string(tle_string):
        """All TLEs should be created using this method.
        All other factory methods should call this method.
        This ensures that the TLE is valid and that the checksums are correct, at the cost of some overhead."""
        try:
            lines = tle_string.strip().split("\n")
            if len(lines) != 3:
                raise ValueError("TLE string must have exactly 3 lines")

            name = lines[0].strip()
            line1 = lines[1].strip()
            line2 = lines[2].strip()

            # Use sgp4 to validate the TLE
            satrec = twoline2rv(line1, line2, wgs72)

            # Creating a mapping of attribute names to their respective values
            attributes = {
                'satellite_number': satrec.satnum,
                'name': name,
                'classification': satrec.classification,
                'international_designator': satrec.intldesg,
                'epoch_year': satrec.epochyr,
                'epoch_day': satrec.epochdays,
                'mean_motion_dot': satrec.ndot,
                'mean_motion_ddot': satrec.nddot,
                'bstar': satrec.bstar,
                'ephemeris_type': satrec.ephtype,
                'element_number': satrec.elnum,
                'inclination': satrec.inclo,
                'right_ascension': satrec.nodeo,
                'eccentricity': satrec.ecco,
                'argument_of_perigee': satrec.argpo,
                'mean_anomaly': satrec.mo,
                'mean_motion': satrec.no_kozai,
                'revolution_number': satrec.revnum,
                'epoch': satrec.epoch
            }
            return TLE(**attributes)
        except Exception as e:
            print(f"Error parsing TLE: {str(e)}")
            return None
    
    @staticmethod
    def from_file(file_path: str):
        try:
            with open(file_path, 'r') as file:
                first_line = file.readline()
                file.seek(0) # Reset file pointer
                if first_line.startswith('{') or first_line.startswith('['):
                    # JSON format
                    return TLE._parse_json_file(file)
                elif ',' in first_line:
                    # CSV format
                    return TLE._parse_csv_file(file)
                else:
                    # Assume TLE format
                    return TLE._parse_tle_file(file)
        except Exception as e:
            print(f"Error parsing file: {str(e)}")
            return []
    
    @staticmethod
    def _parse_tle_file(file):
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
    
    @staticmethod
    def _parse_json_file(file):
        tles = []
        raise NotImplementedError("JSON parsing is not yet implemented")
        # # Load the JSON data only once
        # data = json.load(file)

        # for entry in data:
        #     try:
        #         # Parse the EPOCH in ISO format with timezone
        #         epoch_datetime = datetime.fromisoformat(entry['EPOCH'])
        #         epoch_year = epoch_datetime.year % 100
        #         epoch_day = epoch_datetime.timetuple().tm_yday + epoch_datetime.hour / 24 + epoch_datetime.minute / 1440 + epoch_datetime.second / 86400

        #         # Convert BSTAR to the specific format
        #         bstar = "{:.5e}".format(entry['BSTAR'])
        #         bstar_coefficient, bstar_exponent = bstar.split('e')
        #         bstar_formatted = f"{bstar_coefficient.replace('.','')[:-1]}{int(bstar_exponent):+d}"

        #         # mean motion dot
        #         f"{entry['MEAN_MOTION_DOT']:.8f}".lstrip('0')
        #         # Extract TLE fields
        #         fields = {
        #             'name': entry['OBJECT_NAME'],
        #             'norad_cat_id': entry['NORAD_CAT_ID'],
        #             'classification': entry.get('CLASSIFICATION_TYPE', 'U'),
        #             'int_desig_year': entry['OBJECT_ID'][2:4],
        #             'int_desig_launch_no': entry['OBJECT_ID'][5:8],
        #             'int_desig_piece': entry['OBJECT_ID'][8:],
        #             'epoch_year': epoch_year,
        #             'epoch_day': epoch_day,
        #             'inclination': entry['INCLINATION'],
        #             'right_ascension': entry['RA_OF_ASC_NODE'],
        #             'eccentricity': int(entry['ECCENTRICITY'] * 1e7),
        #             'arg_of_pericenter': entry['ARG_OF_PERICENTER'],
        #             'mean_anomaly': entry['MEAN_ANOMALY'],
        #             'mean_motion': entry['MEAN_MOTION'],
        #             'ephemeris_type': entry['EPHEMERIS_TYPE'],
        #             'element_number': entry['ELEMENT_SET_NO'],
        #             'mean_motion_dot': f"{entry.get('MEAN_MOTION_DOT', 0):.8f}".lstrip('0'),
        #             'bstar': bstar_formatted
        #         }

        #         # Construct TLE lines
        #         tle_line1 = f"1 {fields['norad_cat_id']:05d}{fields['classification']} {fields['int_desig_year']}{fields['int_desig_launch_no']} {fields['int_desig_piece']} {fields['epoch_year']:02d}{fields['epoch_day']:012.8f} {fields['mean_motion_dot']} {fields['bstar']} {fields['ephemeris_type']} {fields['element_number']:04d} 0"
        #         tle_line2 = f"2 {fields['norad_cat_id']:05d} {fields['inclination']:.4f} {fields['right_ascension']:.4f} {fields['eccentricity']:07d} {fields['arg_of_pericenter']:.4f} {fields['mean_anomaly']:.4f} {fields['mean_motion']:.8f}"
        #         tle_string = f"{fields['name']}\n{tle_line1}\n{tle_line2}"
        #         tle = TLE.from_string(tle_string)
        #         tles.append(tle)
        #     except Exception as e:
        #         print(f"Error processing JSON object: {entry} with {str(e)}")

        # return tles

    @staticmethod
    def _parse_csv_file(file):
        tles = []
        # TODO: Implement
        raise NotImplementedError("JSON parsing is not yet implemented")
        return tles
    
    # Instance methods
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

        append("{0: 8.8f}".format(self.mean_motion_dot * xpdotp * 1440).replace("0", "", 1) + " ")

        append("{0: 4.4e}".format(self.mean_motion_ddot * xpdotp * 1440 * 1440 * 10).replace(".", "").replace("e+00", "+0").replace("e-0", "-") + " ")

        # BSTAR
        append("{0: 4.4e}".format(self.bstar * 10).replace(".", "").replace("e+00", "+0").replace("e-0", "-") + " ")

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
    
    def __str__(self):
        return self.to_tle(as_string=True)


class HistoricalTLE(TLE):
    __tablename__ = 'historical_tles'
    satellite_number = Column(Integer, ForeignKey('satellites.satellite_number'))
    satellite = relationship("Satellite", back_populates="historical_tles", foreign_keys=[satellite_number])

    @staticmethod
    def from_tle(tle: TLE):
        """Creates a HistoricalTLE"""
        return HistoricalTLE(**tle.to_dict())
    
class LatestTLE(TLE):
    __tablename__ = 'latest_tles'
    satellite_number = Column(Integer, ForeignKey('satellites.satellite_number'), unique=True)
    satellite = relationship("Satellite", back_populates="latest_tle",foreign_keys=[satellite_number])
    
    @staticmethod
    def from_tle(tle: TLE):
        """Creates a LatestTLE"""
        return LatestTLE(**tle.to_dict())

class Satellite(Base):
    __tablename__ = 'satellites'
    id = Column(Integer, primary_key=True)
    satellite_number = Column(Integer, unique=True)
    name = Column(String)
    # Relationships
    latest_tle = relationship(
        "LatestTLE", 
        uselist=False, 
        back_populates="satellite", 
        foreign_keys=[LatestTLE.satellite_number]
    )
    historical_tles = relationship("HistoricalTLE", back_populates="satellite",  foreign_keys=[HistoricalTLE.satellite_number])
    groups = relationship("Group", secondary="satellite_group_association", back_populates="satellites")

    # TODO: Add more fields from https://celestrak.org/satcat/satcat-format.php
    # Things like launch date, decay date, object type, etc.
    # Possibly add a "category" field to group satellites by type (e.g. weather, communication, etc.)

class Group(Base):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # Relationships
    satellites = relationship("Satellite", secondary="satellite_group_association", back_populates="groups")

# Add a table for many-to-many relationship between satellites and groups
satellite_group_association = Table(
    'satellite_group_association', Base.metadata,
    Column('satellite_id', Integer, ForeignKey('satellites.satellite_number')), 
    Column('group_id', Integer, ForeignKey('groups.id'))
)





