# Flood Simulation with Protection Motivation Theory (PMT)

This project is an agent-based model built with `Mesa` (https://mesa.readthedocs.io) to simulate household decisions in response to flooding. It uses PMT factors to drive agent behaviour.

---

## Folder structure and important files

- **Root Level Files:**
    - `app.py` - Main Solara web application
    - `run.py` and run_simulation.py - Simulation entry points
    - `config.py` - Configuration settings
- **Core Directories:**
    - **agents/** - Contains agent definitions and behavior logic
        - `household.py` - Household agent implementation
        - `decision_logic.py` - PMT decision-making logic
    - **model/** - Main simulation model
        - `flood_model.py` - Core flood simulation model
- **Data Management:**
    - **data/** - Stores input data files
        - **Survey data**
        - **Flood scenario data**
        - **Geographic data** (`GeoJSON` files)
    - **Interface & Visualization:**
        - **server/** - Web interface components
        - **visualization/** - Visualization modules, make graphs here
        - **images/** - Static image assets

---

## Setup and running the model

1. Ensure `Python` 3.8+ is installed on your machine.

2. Clone the repository:
```bash
git clone https://github.com/LucZeeuwen/flood_ABM_Maastricht.git
cd flood_ABM_Maastricht
```
3. Install Dependencies
```bash
pip install -r requirements.txt
```
4. Run the simulation
```bash
python visualization/plot_map.py
```
5. Start the web interface
```bash
solara run app.py
```
6. Open your webbrowser
http://localhost:8080/proxy/8521/
