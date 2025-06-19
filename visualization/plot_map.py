import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx

# Load zones.geojson
zones = gpd.read_file("data/zoness.geojson")

# Rename zone column if needed
if "zones" in zones.columns and "zone" not in zones.columns:
    zones.rename(columns={"zones": "zone"}, inplace=True)

# Reproject for basemap
zones = zones.to_crs(epsg=3857)

# Load agent data
df = pd.read_csv("output/agent_data.csv")
latest_step = int(df["Step"].max())
latest = df[df.Step == latest_step]

# Create GeoDataFrame
gdf = gpd.GeoDataFrame(
    latest,
    geometry=gpd.points_from_xy(latest["Longitude"], latest["Latitude"]),
    crs="EPSG:3857"
)

# Start plot
fig, ax = plt.subplots(figsize=(14, 14))
zones.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.5)

# Zone names
for _, row in zones.iterrows():
    centroid = row.geometry.centroid
    zone_name = row.get("zone", "Zone")
    ax.text(centroid.x, centroid.y, zone_name, fontsize=11, ha="center", color="darkred")

# Optional flood overlay
try:
    flood_df = pd.read_csv("data/flood_scenarios.csv")
    flood_now = flood_df[flood_df["step"] == latest_step]
    for _, row in flood_now.iterrows():
        zone = row["zone"]
        level = row["flood_level"]
        polygon = zones[zones["zone"].str.lower() == zone.lower()]
        if not polygon.empty:
            alpha = min(level / 4.0, 1.0)
            polygon.plot(ax=ax, color="blue", alpha=alpha)
except Exception as e:
    print("Flood overlay skipped:", e)

# Agent color by action
action_colors = {
    "prepare": "blue",
    "partial_prepare": "lightblue",
    "evacuate": "red",
    "mitigate": "green",
    "recover": "orange",
    "relocate": "purple",
    "fatality": "black",
    "nothing": "gray"
}

if "Action" in gdf.columns:
    for action, group in gdf.groupby("Action"):
        color = action_colors.get(action, "gray")
        group.plot(ax=ax, markersize=50, color=color, label=action, alpha=0.8)

# Basemap
try:
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=13)
except Exception as e:
    print("Basemap failed:", e)

# Zoom & labels
buffer = 1000
ax.set_xlim(zones.total_bounds[0] - buffer, zones.total_bounds[2] + buffer)
ax.set_ylim(zones.total_bounds[1] - buffer, zones.total_bounds[3] + buffer)
ax.set_title(f"PMT Flood Simulation Map – Step {latest_step}", fontsize=16)
ax.legend(title="Legend", loc="upper left", fontsize=10)
plt.axis("off")
plt.tight_layout()

# Export
plt.savefig(f"output/map_step_{latest_step}.png", dpi=300)
plt.show()
