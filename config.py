import os

# Project Directory Configuration
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def setup_directories(dir_names):
    """Defines the directory paths for the project.
    Creates the directories if they don't exist."""
    paths = {}
    for name, rel_path in dir_names.items():
        abs_path = os.path.join(BASE_DIR, rel_path)
        os.makedirs(abs_path, exist_ok=True)
        paths[name] = abs_path
    return paths

DIR_NAMES = {
    "base" : "",
    # Backend
    "backend" : "backend",
    ## API is the interface between the frontend and the backend
    "api" : "backend/api",
    ## Models are for data structures
    "models" : "backend/models",
    ## Servives are the main logic of the backend
    "services" : "backend/services",
    "calculations" : "backend/calculations",
    "data_fetching" : "backend/data_fetching",
    "database_operations" : "backend/database_operations",
    ## Tests
    "backend_tests" : "backend/tests",
    # Frontend
    "frontend" : "frontend",
    # Data which holds caches files for the frontend, tle temporary files, the database, etc.
    "data" : "data",
    "database" : "data/database",
    "cache" : "data/cache",
    "tles" : "data/tles",
}

DIRS = setup_directories(DIR_NAMES)

# Database Configuration
DB_NAME = "tles.sqlite"
DB_PATH = os.path.join(DIRS["database"], DB_NAME)
DB_URI = f"sqlite:///{DB_PATH}"