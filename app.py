# SOLARAAAAAAA ik hou van jou
import solara
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import contextily as ctx
import time
import threading
import pandas as pd
from collections import Counter
from solara.lab import Tabs, Tab
from run_simulation import model, initialize_model
import plotly.express as px
import matplotlib.colors as mcolors

zones_gdf = gpd.read_file("data/zone.geojson").explode(index_parts=True).reset_index(drop=True)
zones_gdf = zones_gdf.to_crs(epsg=3857)
zone_column = "zone" if "zone" in zones_gdf.columns else "name"
zone_names = zones_gdf[zone_column].unique()
safe_zone_moves = {zone: 0 for zone in zone_names}
flooded_houses = {zone: 0 for zone in zone_names}

colors = {
    "evacuate": "red",
    "mitigate": "purple",
    "do_nothing": "gray",
}

running = solara.reactive(False)
step_count = solara.reactive(0)
water_level_progress = solara.reactive(0.0)
flood_level_progress = solara.reactive(0.0)
threat_level_progress = solara.reactive(0.0)
simulation_logs = solara.reactive([])
scenario_selector = solara.reactive("default")
social_toggle = solara.reactive(True)
threat_threshold = solara.reactive(0.6)
coping_threshold = solara.reactive(0.6)

def add_log(message):
    if len(simulation_logs.value) > 50:
        simulation_logs.value.pop(0)
    simulation_logs.value.append(message)

def reset_simulation():
    global model
    scenario = scenario_selector.value
    model = initialize_model(
        scenario=scenario,
        use_social_ties=social_toggle.value,
        threat_threshold=threat_threshold.value,
        coping_threshold=coping_threshold.value
    )
    model.threat_triggered = False
    step_count.set(0)
    water_level_progress.set(0.0)
    threat_level_progress.set(0.0)
    simulation_logs.set([])
    running.set(False)
    for zone in zone_names:
        safe_zone_moves[zone] = 0
        flooded_houses[zone] = 0

def step_simulation():
    model.step()
    step_count.set(step_count.value + 1)
    flood_df = model.flood_data
    current_step = step_count.value
    flood_levels = flood_df[flood_df["step"] == current_step]
    avg_level = flood_levels["flood_level"].mean() if not flood_levels.empty else 0
    flood_level_progress.set(min(avg_level / 5.0, 1.0))
    water_level_progress.set(model.water_level)

    agent_threats = [a.threat_score for a in model.schedule.agents if getattr(a, "threat_score", None) is not None]
    if agent_threats:
        avg_threat = sum(agent_threats) / len(agent_threats)
        threat_level_progress.set(avg_threat / 5.0)

    if model.water_level >= 0.75:
        add_log("Critical Water Level Reached!")
    if threat_level_progress.value >= 0.75:
        add_log("Threat Level is High!")


def simulation_loop():
    while running.value:
        if not model.threat_triggered:
            if water_level_progress.value < 0.75:
                water_level_progress.set(water_level_progress.value + 0.05)
                time.sleep(0.1)
                continue
            else:
                model.threat_triggered = True
        step_simulation()
        time.sleep(0.5)

def plot_simulation():
    if model is None or not hasattr(model, "schedule"):
        fig, ax = plt.subplots()
        ax.text(0.5, 0.5, "Please start or reset the simulation.", ha="center", va="center", fontsize=18)
        ax.axis("off")
        return fig

    fig, ax = plt.subplots(figsize=(15, 13))
    zone_threat = {
        zone: sum(a.threat_score for a in model.schedule.agents if getattr(a, "zone", None) == zone and getattr(a, "threat_score", None) is not None) /
              max(1, sum(1 for a in model.schedule.agents if getattr(a, "zone", None) == zone))
        for zone in zone_names
    }

    cmap = plt.cm.Reds
    norm = mcolors.Normalize(vmin=0, vmax=5)

    for _, row in zones_gdf.iterrows():
     gpd.GeoSeries([row.geometry], crs=zones_gdf.crs).plot(
        ax=ax,
        facecolor="none",  # No fill color
        edgecolor="black",  # Keep borders
        linewidth=0.8
    )


    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=zones_gdf.crs)

    for zone in zone_names:
        safe_zone_moves[zone] = 0
        flooded_houses[zone] = 0

    for agent in model.schedule.agents:
        if hasattr(agent, "pos"):
            x, y = agent.pos
            action = getattr(agent, "action", None)
            color = colors.get(action, "gray")
            ax.scatter(x, y, s=120, c=color, marker='o') 
            if getattr(agent, "type", None) == "house" and getattr(agent, "damaged", False):
                flooded_houses[agent.zone] += 1
            elif getattr(agent, "current_zone", None) == "SafeZone":
                safe_zone_moves[agent.zone] += 1

    ax.axis('off')
    ax.set_position([0, 0, 1, 1])
    legend_patches = [mpatches.Patch(color=color, label=label.title()) for label, color in colors.items()]

    ax.legend(handles=legend_patches, loc="lower left", fontsize=9)
    return fig

def action_count_card():
    if model is None or not hasattr(model, "schedule"):
        solara.Text("Please reset the simulation.")
        return

    data = []
    for zone in zone_names:
        for action in colors.keys():
            count = sum(
                1 for a in model.schedule.agents
                if getattr(a, "zone", None) == zone and getattr(a, "action", None) == action
            )
            if count > 0:
                data.append({"Zone": zone, "Action": action.title(), "Count": count})

    if not data:
        solara.Text("No agent actions to display yet.")
        return

    df = pd.DataFrame(data)
    fig = px.bar(df, x="Zone", y="Count", color="Action", title="Agent Actions by Zone", text="Count",
                 color_discrete_map=colors, barmode="stack", height=400)
    solara.FigurePlotly(fig)

def export_csv():
    model.export_agent_data()
    solara.Notification("CSV Exported", timeout=3000)

@solara.component
def Page():
    solara.Title("Flood Simulation Dashboard")

    with solara.Row(gap="1.5rem", style={"height": "100vh", "overflow": "hidden"}):
        with solara.Column(style={"width": "60%", "height": "100%"}):
            solara.FigureMatplotlib(plot_simulation(), format="png")

        with solara.Column(gap="0.75rem", style={"width": "40%", "height": "100%", "overflowY": "auto"}):
            with solara.Row():
                solara.Select("Scenario", value=scenario_selector,
                              values=["default", "heugem_only", "all_high_threat", "all_low_threat"])
                solara.Switch(label="Enable Social Ties", value=social_toggle)
            with solara.Row():
                solara.SliderFloat("Threat Threshold", value=threat_threshold, min=0.0, max=1.0, step=0.01)
                solara.SliderFloat("Coping Threshold", value=coping_threshold, min=0.0, max=1.0, step=0.01)

            with solara.Card("Simulation Controls"):
                with solara.Row():
                    def start():
                        running.set(True)
                        thread = threading.Thread(target=simulation_loop)
                        thread.start()

                    solara.Button("▶ Start", on_click=start, disabled=running.value)
                    solara.Button("⏹ Stop", on_click=lambda: running.set(False), disabled=not running.value)
                    solara.Button("Reset", on_click=reset_simulation)
                    solara.Button("Export CSV", on_click=export_csv)

            with solara.Card("Simulation Status"):
                solara.Text(f"Step: {step_count.value}")
                solara.Text(f"Avg Water Level: {water_level_progress.value * 5:.2f}")
                solara.ProgressLinear(value=int(water_level_progress.value * 100))
                solara.Text(f"Avg Threat Level: {threat_level_progress.value * 5:.2f}")
                solara.ProgressLinear(value=int(threat_level_progress.value * 100))

            with Tabs():
                with Tab("Agent Summary"):
                    action_count_card()
                with Tab("Logs"):
                    for log in simulation_logs.value[::-1]:
                        solara.Text(log)
