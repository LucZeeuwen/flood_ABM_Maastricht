from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import random

from agents.household import Household
from utils.map_utils import get_random_point_in_polygon
from agents.decision_logic import make_pmt_decision

class FloodModel(Model):
    def __init__(self, width=10, height=10, N=30, scenario="default", use_social_ties=True, threat_threshold=0.6, coping_threshold=0.6, social_threshold=None):
        self.num_agents = N
        self.grid = MultiGrid(width, height, True)
        self.schedule = RandomActivation(self)
        self.current_id = 0

        self.water_level = 0.0
        self.threat_triggered = False
        self.use_social_ties = use_social_ties
        self.selected_scenario = scenario
        self.threat_threshold = threat_threshold
        self.coping_threshold = coping_threshold
        self.social_threshold = social_threshold

        print("Loading survey_analysis.csv...")
        self.survey_df = pd.read_csv("data/survey_analysis.csv", delimiter=";", decimal=",")
        self.survey_df.columns = self.survey_df.columns.str.strip().str.replace(" ", "_")
        print("\nFull CSV data from survey_analysis.csv:")
        print(self.survey_df.to_string(index=False))

        print("Loading zone.geojson...")
        self.zones_gdf = gpd.read_file("data/zone.geojson")
        if self.zones_gdf.crs:
            try:
                self.zones_gdf = self.zones_gdf.to_crs(epsg=3857)
            except Exception as e:
                print(f"CRS conversion failed: {e}")

        if "zones" in self.zones_gdf.columns and "zone" not in self.zones_gdf.columns:
            self.zones_gdf.rename(columns={"zones": "zone"}, inplace=True)
        elif "name" in self.zones_gdf.columns and "zone" not in self.zones_gdf.columns:
            self.zones_gdf.rename(columns={"name": "zone"}, inplace=True)

        self.safe_zone_geometry = self.get_zone_geometry("SafeZone")

        print("Creating agents from survey data...")
        self.create_agents_from_survey()

        print("Loading flood data based on scenario...")
        scenario_file_map = {
            "default": "flood_scenarios.csv",
            "heugem_only": "flood_heugem_only.csv",
            "all_high_threat": "flood_all_high.csv",
            "all_low_threat": "flood_all_low.csv"
        }

        print("Selected scenario:", self.selected_scenario)
        filename = scenario_file_map.get(self.selected_scenario, "flood_scenarios.csv")

        try:
            self.flood_data = pd.read_csv(f"data/{filename}")
            print(f"Loaded flood data from {filename}")
        except FileNotFoundError:
            print(f"{filename} not found.")
            self.flood_data = pd.DataFrame(columns=["step", "zone", "flood_level"])

        self.datacollector = DataCollector(
            agent_reporters={
                "ID": lambda a: a.unique_id,
                "Type": lambda a: a.type,
                "Zone": lambda a: a.zone,
                "CurrentZone": lambda a: a.current_zone,
                "SES": lambda a: a.ses,
                "ThreatScore": lambda a: a.threat_score,
                "CopingScore": lambda a: a.coping_score,
                "Action": lambda a: a.action,
                "Influenced": lambda a: getattr(a, "was_influenced", False),
                "EarlyEvacuated": lambda a: getattr(a, "early_evacuated", False),
                "SocialNetwork": lambda a: getattr(a, "social_network_strength", None),
                "Longitude": lambda a: a.pos[0] if a.pos else None,
                "Latitude": lambda a: a.pos[1] if a.pos else None,
            },
            model_reporters={"Step": lambda m: m.schedule.steps}
        )

    def get_zone_geometry(self, zone_name):
        match = self.zones_gdf[self.zones_gdf["zone"].str.strip().str.lower() == zone_name.strip().lower()]
        if not match.empty:
            return match.iloc[0].geometry
        return None

    def next_id(self):
        self.current_id += 1
        return self.current_id

    def create_agents_from_survey(self):
        zone_map = {1: "Randwyck", 2: "Heugemerveld", 3: "Heugem"}

        for _, row in self.survey_df.iterrows():
            try:
                zone_code = int(float(str(row[[col for col in row.index if "Neighbourhood" in col][0]]).replace(",", ".")))
                zone_name = zone_map.get(zone_code, "Unknown")
                zone_shape = self.zones_gdf[self.zones_gdf["zone"].str.strip().str.lower() == zone_name.strip().lower()]
                if zone_shape.empty:
                    continue

                polygon = zone_shape.iloc[0].geometry

                threat_col = [col for col in row.index if "Threat_score" in col][0]
                coping_col = [col for col in row.index if "Coping_score" in col][0]

                threat_score = float(row[threat_col])
                coping_score = float(row[coping_col])

                # Reduce threat for non-Heugem in heugem_only scenario
                if self.selected_scenario == "heugem_only" and zone_name != "Heugem":
                    threat_score = max(0.0, threat_score - 1.0)

                if self.selected_scenario == "all_high_threat":
                  for agent in self.schedule.agents:
                    if hasattr(agent, "threat_score"):
                       agent.threat_score = 4.5  # High threat to everyone

                if self.selected_scenario == "all_low_threat":
                    for agent in self.schedule.agents:
                       if hasattr(agent, "threat_score"):
                          agent.threat_score = 0.8  # Low threat to all agents



                zses = float(row[[col for col in row.index if "ZSES_score" in col][0]])
                ses = "low" if zses < -0.5 else "high" if zses > 0.5 else "medium"

                social_network = 4 if zone_name == "Heugemerveld" else 2 if ses == "low" else 3

                agent = Household(
                    unique_id=self.next_id(),
                    model=self,
                    zone=zone_name,
                    threat_score=threat_score,
                    coping_score=coping_score,
                    ses=ses,
                    agent_type="agent",
                    education_level=None,
                    income_level=None,
                    home_ownership=None,
                    flood_experience=None,
                    social_network_strength=social_network
                )

                self.schedule.add(agent)
                point = get_random_point_in_polygon(polygon)
                agent.pos = (point.x, point.y)

                print(f"Agent {agent.unique_id} | Zone: {agent.zone} | T={agent.threat_score} C={agent.coping_score}")


            except Exception as e:
                print(f"Error creating agent: {e}")

    def step(self):
        current_step = self.schedule.steps
        print(f"\nStep {current_step + 1}")

        if not self.flood_data.empty:
            for zone in self.flood_data["zone"].unique():
                level = self.flood_data.loc[
                    (self.flood_data["step"] == current_step) &
                    (self.flood_data["zone"] == zone),
                    "flood_level"
                ]
                flood_level = float(level.values[0]) if len(level) > 0 else 0.0
                print(f"Flood Level in {zone}: {flood_level:.2f}")

        current_flood = self.flood_data[self.flood_data["step"] == current_step]
        if not current_flood.empty:
            self.water_level = current_flood["flood_level"].mean()

        if not self.threat_triggered:
            if self.water_level < 0.75:
                print("Pre-Flood Phase Triggered")
                for agent in self.schedule.agents:
                    if agent.type == "agent":
                        agent.pre_flood_decision(self.water_level)
            else:
                self.threat_triggered = True
                print("Threat Triggered -> PMT Decision Phase Begins")

        for agent in self.schedule.agents:
            agent.step()

        self.datacollector.collect(self)
        self.schedule.step()

    def export_agent_data(self, filename="data/agent_data.csv"):
        df = self.datacollector.get_agent_vars_dataframe().reset_index()
        df.to_csv(filename, index=False)
        print(f"Agent data exported to {filename}")

    def summarize_outcomes(self):
        df = self.datacollector.get_agent_vars_dataframe().reset_index()
        latest = df[df["Step"] == df["Step"].max()]
        summary = latest["Action"].value_counts()
        print(summary)
