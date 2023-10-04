from typing import List
from sgp4.api import Satrec
from dataclasses import dataclass

@dataclass
class TLE:
    name: str
    line1: str
    line2: str

    # Add more fields as per your requirement to extract and store specific values
    @staticmethod
    def from_string(tle3_string: str):
        lines = tle3_string.strip().split("\n")
        if len(lines) != 3:
            raise ValueError("TLE string must have exactly 3 lines")
        
        name = lines[0].strip()
        line1 = lines[1].strip()
        line2 = lines[2].strip()
        return TLE(name, line1, line2, Satrec.twoline2rv(line1, line2))
    
    @staticmethod
    def tles_from_file(file_path: str):
        with open(file_path, 'r') as file:
            lines = file.readlines()
            tles = []
            for i in range(0, len(lines), 3):
                try:
                    name =  lines[i].strip()
                    line1 = lines[i+1].strip()
                    line2 = lines[i+2].strip()
                    tles.append(TLE(name, line1, line2))
                except (IndexError, ValueError) as e:
                    print(f"Error processing TLE starting at line {i}: {str(e)}")
        return tles
    
    def to_satrec(self):
        """Converts a TLE to a Satrec object for propagation"""
        return Satrec.twoline2rv(self.line1, self.line2)


class Satellite:
    "Satellite class which stores state"
    def __init__(self, name, propagator):

        self.name = name
        self.propagator = propagator
    
    @property
    def orbital_period(self):
        return 60*95

    @classmethod
    def from_tle3_string(cls, tle3_string: str):
        tle = TLE.from_string(tle3_string)
        return Satellite(tle.name, tle.propagator)
    
    @classmethod
    def satellites_from_file(cls, file_path: str):
        tles = TLE.tles_from_file(file_path)
        return [Satellite(tle.name, tle.propagator) for tle in tles]
    
satellites = Satellite.satellites_from_file("data/active_tle.txt")
print(satellites)
