from model.flood_model import FloodModel

# Function to initialize new model instance with optional parameters
def initialize_model(scenario="default", use_social_ties=True, threat_threshold=0.6, coping_threshold=0.6, social_threshold=None):
    print("[run_simulation] Initializing model with scenario =", scenario)
    return FloodModel(
        width=10,
        height=10,
        N=30,
        scenario=scenario,
        use_social_ties=use_social_ties,
        threat_threshold=threat_threshold,
        coping_threshold=coping_threshold,
        social_threshold=social_threshold
    )

# Do NOT pre-initialize the model here
# Use this variable to store the model initialized in app.py
model = None
