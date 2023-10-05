# OrbitViz

This project allows users to interactively visualize satellite orbits and make requests for various satellites, provides some calculations like contact times with some basic constraints such as elevation and lighting times and basic data analytics and plotting for various groups of satelites.

## Project layout
* Backend: Accessed via an api, returns satellite data, performs calculations
* Frontend: Interactive satellite visualizer, allows the user to request data via a GUI
* Other needed files for setup, environment dependancies, etc.
* Tools: pipenv, pyenv, etc.

### Implementation Details

#### Backend
* Built with Python
* Backend webserver (Flask)
    * Provides a RESTful API
* Database (Sqlite, TODO: upgrage to PostGress)
    * Utilizes SqlAlchemy for easier usage
    * Stores TLEs for the satellite catalog
    * Maintains Historical TLEs as well as the latest TLE
* Data fetching (TODO)
    * Handled by cron jobs
* Calculations:
    * Utilizing Skyfield handles various aerospace/physics calculations like coordinate frame transformations and TLE propgation
    * Custom calculations with event finding support and intervals
    
#### Frontend (TODO)
* Built with Javascript
* Utilizing Next.js which is a React framework for building full-stack web applications
* Utlizing Reach for declarative Components
* Utilizing React Bootstrap for prexisting components 
* Satllite vizualization is handled by Resium, which is Cesium for React
* Plots are using react plotly

## TODOs
* Implement front end
* Remove unused files
* Restructure code
* Change database schema to support satellties, a latest tle table, and a historical tle table, also need to add groups which hold many satellites.
* Migrate databse from sqlite to Postgress
