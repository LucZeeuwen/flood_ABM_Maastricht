# Flood Simulation with Protection Motivation Theory (PMT)

This project is an agent-based model built with [Mesa](https://mesa.readthedocs.io) to simulate household decisions in response to flooding. It uses PMT factors to drive agent behaviour.

## Folder structure and important files

Root Level Files:
    app.py - Main Solara web application
    run.py and run_simulation.py - Simulation entry points
    config.py - Configuration settings
Core Directories:
    agents/ - Contains agent definitions and behavior logic
        household.py - Household agent implementation
        decision_logic.py - PMT decision-making logic
    model/ - Main simulation model
        flood_model.py - Core flood simulation model
Data Management:
    data/ - Stores input data files
        Survey data
        Flood scenario data
        Geographic data (GeoJSON files)
    Interface & Visualization:
        server/ - Web interface components
        visualization/ - Visualization modules
        images/ - Static image assets

## Setup and running the model

1. Ensure Python 3.8+ is installed on your machine.

2. Clone the repository:
Open a terminal and run the following commands:
```bash
    git clone https://github.com/your-username/repo-name.git
    cd repo-name
```
3. Install Dependencies
Install the required libraries using the requirements.txt file:
```bash
    pip install -r requirements.txt
```
4. Run the simulation
Initialisation and generation of a static map
```bash
    python visualization/plot_map.py
```
5. Start the web interface
```bash
    solara run app.py
```
6. Open your webbrowser
    http://localhost:8080/proxy/8521/