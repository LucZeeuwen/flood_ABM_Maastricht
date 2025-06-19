from model.flood_model import FloodModel
from visualization.config import SIMULATION_STEPS, OUTPUT_CSV_PATH

print("Starting simulation...")

model = FloodModel()
for i in range(SIMULATION_STEPS):
    print(f"Step {i+1}")
    model.step()

df = model.datacollector.get_agent_vars_dataframe()
df.reset_index(inplace=True)  # 👈 this brings "Step" and "AgentID" as columns
df.to_csv(OUTPUT_CSV_PATH, index=False)

print(f"Simulation complete. Output saved to: {OUTPUT_CSV_PATH}")
