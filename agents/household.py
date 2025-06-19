from mesa import Agent
from agents.decision_logic import make_pmt_decision
from shapely.geometry import Point
from utils.map_utils import get_random_point_in_polygon

class Household(Agent):
    def __init__(self, unique_id, model, zone, threat_score, coping_score, ses, agent_type,
             education_level=None, income_level=None, home_ownership=None,
             flood_experience=None, social_network_strength=None):
       super().__init__(unique_id, model)

       self.zone = zone
       self.current_zone = zone
       self.ses = ses
       self.type = agent_type

       self.threat_score = threat_score
       self.coping_score = coping_score

       # Optional demographic fields
       self.education_level = education_level
       self.income_level = income_level
       self.home_ownership = home_ownership
       self.flood_experience = flood_experience
       self.social_network_strength = social_network_strength

       # State tracking
       self.action = None
       self.evacuated = False
       self.early_evacuated = False
       self.was_influenced = False
       self.flooded = False
       self.damaged = False
       self.in_safe_zone = False
       self.alive = True


    def __str__(self):
        return f"Agent {self.unique_id} | Zone: {self.zone} | Action: {self.action}"

    def get_neighbor_agents(self, radius=150):
        my_point = Point(self.pos)
        neighbors = []
        for agent in self.model.schedule.agents:
            if agent.unique_id != self.unique_id and hasattr(agent, "pos"):
                other_point = Point(agent.pos)
                if my_point.distance(other_point) <= radius:
                    neighbors.append(agent)
        return neighbors

    def pre_flood_decision(self, flood_level):
        threat_threshold = getattr(self.model, "threat_threshold", 0.6)
        coping_threshold = getattr(self.model, "coping_threshold", 0.6)
        self.action = make_pmt_decision(self, flood_level, threat_threshold, coping_threshold)

    def apply_social_influence(self, neighbors, social_threshold=None):
        if not self.model.use_social_ties or not neighbors:
            return

        evac_neighbors = [n for n in neighbors if getattr(n, "action", "") == "evacuate"]
        influence_ratio = len(evac_neighbors) / len(neighbors)
        threshold = 0.6 if social_threshold is None else social_threshold  # Can be adjusted

        if influence_ratio > threshold:
            self.action = "mitigate"
            self.was_influenced = True

    def move_to_safe_zone(self):
        if not self.evacuated:
            safe_zone = self.model.zones_gdf[self.model.zones_gdf["zone"].str.lower() == "safezone"]
            if not safe_zone.empty:
                polygon = safe_zone.iloc[0].geometry
                point = get_random_point_in_polygon(polygon)
                self.pos = (point.x, point.y)
                self.current_zone = "SafeZone"
                self.evacuated = True

    def step(self):
        step = self.model.schedule.steps

        flood_data = self.model.flood_data.loc[
            (self.model.flood_data["step"] == step) &
            (self.model.flood_data["zone"] == self.zone),
            "flood_level"]
        flood_level = float(flood_data.iloc[0]) if len(flood_data) > 0 else 0.0

        if not self.model.threat_triggered and self.model.water_level < 0.75:
            self.pre_flood_decision(flood_level)
            return

        if self.model.threat_triggered:
            threat_threshold = getattr(self.model, "threat_threshold", 0.6)
            coping_threshold = getattr(self.model, "coping_threshold", 0.6)
            social_threshold = getattr(self.model, "social_threshold", None)
            self.action = make_pmt_decision(self, flood_level, threat_threshold, coping_threshold)
            neighbors = self.get_neighbor_agents()
            self.apply_social_influence(neighbors, social_threshold=social_threshold)

            if self.action == "evacuate":
                self.move_to_safe_zone()
                if step < 6:
                    self.early_evacuated = True

        if 6 <= step <= 12 and flood_level > 0.6:
            self.flooded = True
        if 13 <= step <= 20 and self.flooded and flood_level > 0.8:
            self.damaged = True
