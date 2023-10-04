import os 
DATA_DIR = os.path.dirname(__file__)
TLE_DIR = os.path.join(DATA_DIR, 'tles')
os.makedirs(TLE_DIR, exist_ok=True)