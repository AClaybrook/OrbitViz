# OrbitViz

OrbitViz is an interactive satellite visualization and analytics project that allows users to explore satellite orbits, make requests for satellite data, and perform calculations such as contact times, elevation, and lighting times. The project is currently under development.

## Project Overview

### Project Layout

The project is organized into the following components:

- **Backend**: Provides data, calculations, and an API.
- **Frontend**: Offers an interactive satellite visualizer with a user-friendly GUI.
- **Other Files**: Contains configuration, setup, and dependency-related files.
- **Tools**: Includes tools like `pipenv`, `pyenv`, and more.

### Implementation Details

#### Backend

The backend is implemented using Python and consists of the following components:

- **Backend Web Server (Flask)**:
  - Provides a RESTful API for data retrieval and calculations.
- **Database**:
  - Initially uses SQLite (with plans to upgrade to PostgreSQL).
  - Utilizes SQLAlchemy for database interactions.
  - Stores Two-Line Element Sets (TLEs) for the satellite catalog.
  - Manages historical and latest TLE data.
- **Data Fetching (TODO)**:
  - Scheduled data fetching handled by cron jobs.
- **Calculations**:
  - Leveraging Skyfield for aerospace and physics calculations.
  - Custom calculations, including event finding and intervals support.

#### Frontend (TODO)

The frontend, built with JavaScript, Next.js (a React framework), and other libraries, will include the following:

- **Interactive Visualizer**:
  - User-friendly GUI for requesting and visualizing satellite data.
- **React Components**:
  - Utilizes React for declarative components.
  - Integrates React Bootstrap for existing UI components.
- **Satellite Visualization**:
  - Utilizes Resium (Cesium for React) for satellite visualization.
- **Plots**:
  - Uses React Plotly for interactive plotting.

## To-Do List

- Implement the frontend.
- Remove unused files.
- Refactor and restructure the codebase.
- Update the database schema to support satellites, latest TLEs, historical TLEs, and satellite groups.
- Migrate the database from SQLite to PostgreSQL.

Please note that this project is a work in progress, and contributions are welcome.

## Getting Started

To get started with this project, follow the installation and setup instructions in the project documentation (coming soon).
